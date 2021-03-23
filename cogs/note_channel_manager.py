import discord
import json
import os
from discord.ext import commands
from .utils import command_utils

class NoteChannelManager(commands.Cog, name='Note Channel Manager'):
    DATA_PATH = './data/note_channel_manager.json'
    DISCORD_LOGO_URL = 'https://discord.com/assets/fc0b01fe10a0b8c602fb0106d8189d9b.png'
    DISCORD_ICON_URL = 'https://discord.com/assets/2c21aeda16de354ba5334551a883b481.png'
    def __init__(self, bot):
        self.bot = bot
        self.note_channels = []
        bot.loop.create_task(self._load_note_channel_list())

    # listener
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        for channel in message.channel_mentions:
            if channel not in self.note_channels:
                continue
            embed = discord.Embed()

            # color
            embed.color = message.author.color

            # thumbnail
            embed.set_thumbnail(url=self.DISCORD_LOGO_URL)
            
            # author
            name = message.author.display_name
            icon_url = message.author.avatar_url
            embed.set_author(name=name, icon_url=icon_url)

            # description
            embed.description = message.content + '\n\n' + message.jump_url

            # footer
            embed.set_footer(text=f'Discord', icon_url=self.DISCORD_ICON_URL)

            # timestamp
            embed.timestamp = message.created_at

            # files
            files = []
            for attachment in message.attachments:
                if attachment.filename.lower().split('.')[-1] in ['jpeg', 'jpg', 'gif', 'png']:
                    embed.set_image(url=attachment.url)
                else:
                    files.append(await attachment.to_file())

            await channel.send(embed=embed, files=files)


    # commands
    @commands.group()
    @commands.has_permissions(administrator=True)
    async def note(self, ctx):
        pass

    @note.command()
    async def show(self, ctx:commands.Context):
        if len(self.note_channels) == 0:
            content = '現在リストに登録されているチャンネルはありません'
            await command_utils.reply(ctx, content)
            return
        guild = ctx.guild
        content = ''
        index = 1
        for channel in self.note_channels:
            if channel.guild == guild:               
                content += str(index) + ': ' + channel.mention + ' (id: ' + str(channel.id) + ')\n'
                index += 1
            else:
                pass
        await command_utils.reply(ctx, content)

    @show.before_invoke
    async def show_before(self, ctx):
        all_channels = self.bot.get_all_channels()
        for channel in self.note_channels:
            if channel not in all_channels:
                self.note_channels.remove(channel)

    @note.command()
    async def add(self, ctx: commands.Context, channel: discord.TextChannel):
        if not channel in self.note_channels:
            self.note_channels.append(channel)
            
            content = f'{channel.mention} をリストに追加しました'
            await command_utils.reply(ctx, content)
        else:
            raise ValueError(f'{channel.mention} はすでにリストに追加されています')

    @note.command()
    async def remove(self, ctx: commands.Context, channel: discord.TextChannel):
        try:
            self.note_channels.remove(channel)
        except:
            raise ValueError(f'{channel.mention} はリストに含まれていません')

        content = f'{channel.mention} をリストから削除しました'
        await command_utils.reply(ctx, content)

    @note.command()
    async def create(self, ctx: commands.Context, channel_name: str, category: discord.CategoryChannel = None):
        # if category is not None:
        #     category: commands.CategoryChannelConverter = category

        guild = ctx.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=False)
        }
        reason = f'{ctx.author.name} さんが /note create コマンドを実行したため'
        channel = await ctx.guild.create_text_channel(channel_name, overwrites=overwrites, category=category, reason=reason)

        self.note_channels.append(channel)

        content = f'{channel.mention} を作成し、リストに追加しました'
        await command_utils.reply(ctx, content)

    @command_utils.commands_error(*note.commands)
    async def note_error(self, ctx, error):
        if isinstance(error, commands.ChannelNotFound):
            content = 'チャンネルが見つかりませんでした'
            await command_utils.reply(ctx, content)
        elif isinstance(error, commands.BadArgument):
            content = 'コマンドの引数に渡された値の解析、または変換に失敗しました'
            await command_utils.reply(ctx, content)
        elif isinstance(error, ValueError):
            await command_utils.reply(ctx, str(error))
        else:
            raise error
    
    @command_utils.commands_after_invoke(*note.commands)
    async def _save_note_channel_list(self, ctx):
        path = os.path.dirname(self.DATA_PATH)
        os.makedirs(path, exist_ok=True)
        
        with open(self.DATA_PATH, 'w') as file:
            json.dump([channel.id for channel in self.note_channels], file)

    async def _load_note_channel_list(self):
        await self.bot.wait_until_ready()
        try:
            
            with open(self.DATA_PATH, 'r') as file:
                list_ = json.load(file)
        except:
            return

        for id in list_:
            id = int(id)
            channel  = self.bot.get_channel(id)
            if channel is not None:
                self.note_channels.append(channel)


def setup(bot: commands.Bot):
    bot.add_cog(NoteChannelManager(bot))