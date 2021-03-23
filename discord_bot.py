import discord
from discord.ext import commands
import os
import time


TOKEN_PATH = 'TEST_BOT.token'
CONSOLE_ID = {'guild_id': 588391471493808139, 'chanel_id': 625271680184483853}

cog_list = [
    'cogs.note_channel_manager'
]

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console_id = kwargs.get('console_id')
    

    # 接続時の処理
    async def on_ready(self):
        time_str = time.strftime("%Y/%m/%d %H:%M", time.strptime(time.ctime()))
        print('---------------------------------------------------')
        print('ログインしました', time_str)
        print('---------------------------------------------------')
        return

    # # メッセージ処理
    # async def on_message(self, message:discord.Message):
    #     # 例外
    #     if message.author.bot: return

    #     # メンション処理
    #     if bot.user in message.mentions:
    #         return await on_mention(message)

    #     return

    # メンション処理
    async def on_mention(self, message):
        await message.channel.send('現在調整中...', reference=message)
        pass

    # 切断時の処理
    async def on_disconnect(self):
        time_str = time.strftime("%Y/%m/%d %H:%M", time.strptime(time.ctime()))
        print('---------------------------------------------------')
        print('切断しました', time_str)
        print('---------------------------------------------------')
        return


    def is_console_channel(self, message: discord.Message):
        channel = message.channel
        result = all([
            channel.guild.id == CONSOLE_ID['guild_id'],
            channel.id == CONSOLE_ID['channel_id']
        ])
        return result

# token の取得
def get_token(TOKEN_PATH):
    if os.path.isfile(TOKEN_PATH):
        with open(TOKEN_PATH) as f:
            TOKEN = f.read()
        return TOKEN
    else:
        print('トークンファイルが見つかりませんでした。')
        exit()

if __name__ == '__main__':
    bot = Bot(command_prefix='/')
    # cog のロード
    for cog in cog_list:
        bot.load_extension(cog)
    
    TOKEN = get_token(TOKEN_PATH)
    bot.run(TOKEN)