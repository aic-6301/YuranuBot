import discord
from discord.ext import commands
from discord import app_commands

from modules.checkPc import pc_status


class info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @app_commands.command(name="sbc",description="Shizen Black Companyの説明資料なのだ")#Shizen Black Companyの宣伝
    async def sbc_command(self, interact:discord.Interaction):
        await interact.response.send_message('**～ドライバーの腕が生かせる最高の職場～　Shizen Black Company** https://black.shizen.lol')

    @app_commands.command(name="status",description="Botを稼働しているPCの状態を表示するのだ")#PCの状態
    async def status(self, interact: discord.Interaction):
        ##PCのステータスを送信
        embed = await pc_status(self.bot)
        await interact.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(info(bot))