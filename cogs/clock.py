import subprocess
import discord
import sys
import os
import platform

from discord.ext import commands
from discord import app_commands

from modules.checkPc import pc_status
from modules.settings import save_server_setting
from modules.exception import sendException
from modules.delete import delete_file_latency

class Clock(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    clock = app_commands.Group(name="clock", description="時計関連のコマンドなのだ")

    @clock.add_command(name="")
    async def 