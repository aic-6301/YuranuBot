import discord

from discord import app_commands
from discord.ext import commands

class Clock(commands.Bot): 
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    cmd_clk = app_commands.Group(name="alarm", description="時刻お知らせ機能関連のコマンドなのだ")

    # お知らせする時間の追加
    @cmd_clk.command(name="add", description="お知らせする時間を追加するのだ") 
    @app_commands.rename(hour="時", min="分", repeat="繰り返し")
    @app_commands.choices(
        repeat=[
            app_commands.Choice(name="オン(毎日)", value=1),
            app_commands.Choice(name="オフ(1回のみ)", value=0)
        ]
    )
    async def alarm_add(self, interact: discord.Interaction, hour: int, min: int, repeat: int):
        