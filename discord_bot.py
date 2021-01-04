from discord.ext import commands
import os
import time

TOKEN_PATH = 'TEST_BOT.token'
CONSOLE_ID = 625271680184483853

bot = commands.Bot(command_prefix='/')

## 接続時の処理
@bot.event
async def on_ready():
    print('---------------------------------------------------')
    print('ログインしました', time.strftime("%Y/%m/%d %H:%M", time.strptime(time.ctime())))
    print('---------------------------------------------------')
    return

## メッセージ処理
@bot.event
async def on_message(message):
    # 例外

    if bot.user in message.mentions:
        return await on_mention(message)


async def on_mention(message):
    await message.channel.send('現在調整中...')
    pass


## 切断時の処理
@bot.event
async def on_disconnect():
    print('---------------------------------------------------')
    print('切断しました', time.strftime("%Y/%m/%d %H:%M", time.strptime(time.ctime())))
    print('---------------------------------------------------')
    return


## token の取得
if os.path.isfile(TOKEN_PATH):
    with open(TOKEN_PATH) as f:
        TOKEN = f.read()
else:
    print('トークンファイルが見つかりませんでした。')
    exit()

bot.run(TOKEN)