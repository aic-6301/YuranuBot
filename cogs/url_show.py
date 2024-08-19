import discord
import time
import sys
import os
import platform

from discord.ext import commands, tasks
from discord import app_commands

class Discord_URL_Loader( commands.Cog ):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def 