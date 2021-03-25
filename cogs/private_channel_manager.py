import discord
import json
import os
from discord.ext import commands
from .utils import markdown, command_utils
#🔒

class PrivateChannelManager(commands.Cog, name='Private Channel Manager'):
    DATA_PATH = './data/private_channel_manager.json'
    def __init__(self, bot):
        self.bot = bot
        self.guild_properties = dict() # {guild.id(int) : guild_property} ### self.guild_properties[str(ctx.guild.id)]

        self.bot.loop.create_task(self._load_private_channel_list())
    #
    class GuildProperty:
        def __init__(self):
            self.room_prefix = '🔒'
            self.key_prefix = '🔑'
            self.roomkeys = dict()

    # commands
    @commands.group()
    async def private(self, ctx):
        pass

    @private.command()
    async def create(self, ctx:commands.Context, room_name: str):
        guild = ctx.guild
        if guild.id in self.guild_properties.keys():
            guild_property = self.guild_properties[guild.id]
        else:
            guild_property = self.GuildProperty()
            self.guild_properties[guild.id] = guild_property   
        
        #role(key)生成
        key_prefix = guild_property.key_prefix
        role = await guild.create_role(name = key_prefix + room_name)
        #role(key)配布
        await ctx.message.author.add_roles(role)
        for room_member in ctx.message.mentions:
            await room_member.add_roles(role)
        for role_mention in ctx.message.role_mentions:
            for room_member in role_mention.members:
                await room_member.add_roles(role)

        #category(room)生成
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            ctx.author: discord.PermissionOverwrite(manage_channels=True, manage_permissions=True),
            role: discord.PermissionOverwrite(read_messages=True),
        }
        room_prefix = guild_property.room_prefix
        category = await guild.create_category(room_prefix + room_name, overwrites = overwrites)
        guild_property.roomkeys[category.id] = role.id
        
        #チャンネル生成
        text_channel_name = room_name + '_text channel'
        text_channel = await category.create_text_channel(text_channel_name)
        voice_channel_name = room_name + '_voice channel'
        await category.create_voice_channel(voice_channel_name)
        
        #説明embed
        embed = discord.Embed()

        # color
        embed.color = self.bot.user.color

        # description
        embed.description = '\n'.join([
            'このチャンネルは使い切りのプライベートチャンネルです。',
            '閲覧権限があるのはこのルームキーの役職を持ったユーザーです。',
            'また、discordの仕様上、サーバーの管理者にも閲覧権限があります。',
            '使用後はコマンド入力(/private delete)でルームを削除するようにお願いします。'
        ])

        await text_channel.send(embed=embed)
        return 
    
    def is_private_room(self):
        def check(ctx: commands.Context):
            try: 
                guild_property = self.guild_properties[ctx.guild.id]
                category_id = ctx.channel.category.id
            except:
                return False    

            return category_id in guild_property.roomkeys.keys()
        return check

    @private.command()
    @commands.check(is_private_room)
    async def delete(self, ctx:commands.Context):
        guild = ctx.guild
        category = ctx.channel.category
        guild_property = self.guild_properties[guild.id]
        role_id = guild_property.roomkeys.pop(category.id)
        role = guild.get_role(role_id)
        
        for channel in category.channels:
            await channel.delete()

        # role削除
        await role.delete()

        # ルーム削除
        await category.delete()

    @private.command()
    @commands.has_permissions(administrator=True)
    async def alldelete(self, ctx:commands.Context):
        guild = ctx.guild
        try:
            guild_property = self.guild_properties[guild.id]
        except:
            return

        for room_id, room_key_id in guild_property.roomkeys.items():
            try:
                category = guild.get_channel(room_id)
                for channel in category.channels:
                    await channel.delete()

                role = guild.get_role(room_key_id)
                await role.delete()

                await category.delete()
            except:
                pass
        
        guild_property.roomkeys.clear()


    @command_utils.commands_after_invoke(*private.commands)
    async def _seve_private_channel_list(self, ctx):
        path = os.path.dirname(self.DATA_PATH)
        os.makedirs(path, exist_ok=True)

        #データ作成
        data = dict()
        for guild_id, guild_property in self.guild_properties.items():
            if guild_id not in [guild.id for guild in self.bot.guilds]:
                self.guild_properties.pop(guild_id)
                continue
            property_data = dict()
            property_data['room_prefix'] = guild_property.room_prefix
            property_data['key_prefix'] = guild_property.key_prefix
            roomkeys = dict()
            for room_id, room_key in guild_property.roomkeys.items():
                roomkeys[str(room_id)] = str(room_key)
            property_data['roomkeys'] = roomkeys
            data[str(guild_id)] = property_data

        with open(self.DATA_PATH, 'w') as file:
            json.dump(data, file, indent=4)

    async def _load_private_channel_list(self):
        await self.bot.wait_until_ready()
        try:
            with open(self.DATA_PATH, 'r') as file:
                guild_properties = json.load(file)
        except:
            return

        for guild_id, guild_property_data in guild_properties.items():
            guild_property = self.GuildProperty()
            guild_property.room_prefix = guild_property_data['room_prefix']
            guild_property.key_prefix = guild_property_data['key_prefix']
            for room_id, room_key in guild_property_data['roomkeys'].items():
                guild_property.roomkeys[int(room_id)] = int(room_key)
            self.guild_properties[int(guild_id)] = guild_property

def setup(bot: commands.Bot):
    bot.add_cog(PrivateChannelManager(bot))