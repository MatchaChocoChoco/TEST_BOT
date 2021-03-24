from discord.ext import commands
import discord
import asyncio
from .utils import markdown, command_utils

class ToArchive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.archive_channel = None
        self.wait_message_list = []


    class UnknownArchiveOption(commands.CommandError):
        pass

    class ArchiveOption(commands.Converter):
        async def convert(self, ctx, argument):
            option = {'-f': 'front', '--front': 'front', '-r': 'rear', '--rear': 'rear'}
            argument = command_utils.split(argument)
            kwargs = {'front': '', 'rear': ''}
            for option_key, value in zip(argument[::2], (argument+[''])[1::2]):
                try:
                    key = option[option_key]
                except KeyError as error:
                    raise ToArchive.UnknownArchiveOption(f'{ctx.command.name} コマンドに {markdown.code(str(error)[1:-1])} オプションはありません')
                kwargs[key] = value 

            return kwargs


    @commands.command(name='toArchive')
    @commands.has_permissions(manage_channels=True)
    async def to_archive(self, ctx: commands.Context, 
                        target_category: discord.CategoryChannel, 
                         archive_category: discord.CategoryChannel,
                         *, option: ArchiveOption={'front': '', 'rear': ''}):
        
        if len(target_category.channels) == 0:
            error_message = (
                markdown.code(f'{target_category.name} (id:{target_category.id})') 
                + 'には移動可能なチャンネルがありません')
            raise ValueError(error_message)

        # Enbed
        embed = command_utils.get_embed(ctx, '以下の設定で実行します')
        
        ## field 1
        name = 'アーカイブカテゴリー：'
        value = f'{archive_category.name} id: {markdown.code(str(archive_category.id))}'
        embed.add_field(name=name, value=value, inline=False)

        ## field 2
        name = 'アーカイブに送るカテゴリー：'
        value = f'{target_category.name} id: {markdown.code(str(target_category.id))}\n'
        for channel in target_category.channels:
            value += f' {channel.mention} id: {markdown.code(str(channel.id))}\n'
        
        embed.add_field(name=name, value=value, inline=False)

        ## field 3 (option)
        front = option['front']
        rear = option['rear']
        if any([front, rear]):
            name = 'チャンネル名は次のように変更します'  
            
            channel = target_category.channels[0]
            channel = await target_category.create_text_channel(name=(front+channel.name+rear), reason=f'`{ctx.author}`コマンド処理')
            value = channel.name
            await channel.delete(reason=f'`{ctx.author}`コマンド処理')

            embed.add_field(name=name, value=value, inline=False)

        ## field 4
        name = '以上の設定で実行する場合は:o:、しない場合は:x:のリアクションをつけてください'
        value = '⬇️⬇️⬇'
        embed.add_field(name=name, value=value, inline=False)


        # reply
        replied_message = await ctx.reply(embed=embed)

        emojis = ['⭕', '❌']
        await replied_message.add_reaction(emojis[0])
        await replied_message.add_reaction(emojis[1])

        def check(reaction, user):
            return user == ctx.author and reaction.emoji in emojis
        
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0*5, check=check)
        except asyncio.TimeoutError:
            ctx.command_failed = True
            content = 'タイムアウトしました\nコマンドをもう一度実行してください'
            embed = command_utils.get_embed(ctx, content)
            await replied_message.edit(embed=embed)
            # await ctx.send('タイムアウトしました\nコマンドをもう一度実行してください\nタイムアウトしたコマンド：' + ctx.message.jump_url)
            return

        if reaction.emoji == emojis[0]:
            name = f'{target_category.name}のチャンネルを{archive_category.name}カテゴリーに移動中...'
            index = len(embed.fields) - 1
            size = len(target_category.channels)
            count = 0
            for channel in target_category.channels:
                await channel.edit(name=front + channel.name + rear, category=archive_category)
                
                count += 1
                percentage = count/size * 100
                
                gauge = ''.join(['█' if (n/50 * 100) <= percentage else ' ' for n in range(50)])
                value = markdown.code_block(f'|{gauge}| {int(percentage)}%')
                embed.set_field_at(index, name=name, value=value)
                await replied_message.edit(embed=embed)
                await asyncio.sleep(0.5)
            
            embed.description = '以下の設定で実行しました'
            embed.set_field_at(index, name='終了しました', value=f'計:{size}')
            await replied_message.edit(embed=embed)

        else:
            content = '終了しました'
            embed = command_utils.get_embed(ctx, content)
            await replied_message.edit(embed=embed)

        return

    @to_archive.error
    async def archive_error(self, ctx, error):
        await command_utils.reply(ctx, str(error))


def setup(bot: commands.Bot):
    bot.add_cog(ToArchive(bot))