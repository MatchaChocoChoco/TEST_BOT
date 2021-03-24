import discord
from discord.ext import commands
from enum import Enum


async def reply(ctx: commands.Context, content: str) -> discord.Message:
    embed = get_embed(ctx, content)
    return await ctx.reply(embed=embed)

async def send(ctx: commands.Context, content: str) -> discord.Message:
    embed = get_embed(ctx, content)
    return await ctx.send(embed=embed)

def get_embed(ctx: commands.Context, content: str) -> discord.Embed:
    class Color(Enum):
        PRIMARY = 0x4D84F4
        ERROR = 0xf5414f

    color = Color.PRIMARY if not ctx.command_failed else Color.ERROR
    embed = discord.Embed(description=content, color=color.value)
    footer_text = ctx.command.cog_name
    footer_text += ' (' + ctx.command.name + ')'
    embed.set_footer(text=footer_text)
    
    return embed

def commands_after_invoke(*commands: commands.Command):
    def decorator(coro):
        for command in commands:
            command.after_invoke(coro)
    return decorator

def commands_error(*commands: commands.command):
    def decorator(coro):
        for command in commands:
            command.error(coro)
    return decorator

def commands_befor_invoke(*commands: commands.Command):
    def decorator(coro):
        for command in commands:
            command.before_invoke(coro)
    return decorator

def split(text:str, sep: str = ' ') -> list:
    """
        引用付(`"`)で囲まれた文字列を避け、`sep`でスプリットした値を返します
    """
    text = text.split('"')
    result = []
    for index, arg in enumerate(text):
        if index%2 == 0:
            result += [s for s in arg.split(sep) if s != '']
        elif index == (len(text)-1):
            result += f'"{arg}'.split(sep)
        else:
            result.append(arg)
    
    return result