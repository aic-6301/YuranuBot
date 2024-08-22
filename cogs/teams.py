# import os
# import sys
# import dotenv
# import logging
# import discord
# import asyncio
# import subprocess

# from discord import app_commands
# from discord import Object
# from discord.ext import commands

# class TeamsUtility(commands.Cog):
#     def __init__(self, bot: commands.Bot):
#         self.bot = bot

#     team = app_commands.Group(name="team", description="チーム関連のコマンドを実行するのだ")

#     @team.command(name="split", description="チーム分けコマンドを実行するのだ")
#     async def team_split(self, interact: discord.Interaction):
#         try:
#             join_button = discord.ui.Button(label="参加する")
#             start_button = discord.ui.Button(label="チーム分け")

#             embed = discord.Embed(title="チーム分けコマンド",
#                                   description="チーム分けを実行します",
#             )
