import discord
import sys

from discord.ext import commands
from discord import app_commands

from modules.checkPc import pc_status
from modules.settings import save_server_setting
from modules.exception import sendException


class utils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="sbc",description="Shizen Black Companyの説明資料なのだ")#Shizen Black Companyの宣伝
    async def sbc_command(self, interact:discord.Interaction):
        await interact.response.send_message('**～ドライバーの腕が生かせる最高職場～　Shizen Black Company** https://black.shizen.lol')

    @app_commands.command(name="status",description="Botを稼働しているPCの状態を表示するのだ")#PCの状態
    async def status(self, interact: discord.Interaction):
        ##PCのステータスを送信
        embed = await pc_status(self.bot)
        await interact.response.send_message(embed=embed)

    @app_commands.command(name="serv-join-message", description="サーバー参加者へメッセージを送信するチャンネルを設定するのだ！")
    @app_commands.rename(activate="メッセージ送信のオンオフ")
    @app_commands.describe(activate="メッセージを送信する？(コマンドを実行した場所が送信場所になるのだ)")
    @app_commands.choices(
        activate=[
            discord.app_commands.Choice(name="送信する",value=1),
            discord.app_commands.Choice(name="送信しない",value=0)
        ])
    async def serv_join_message(self, interact: discord.Interaction, activate: int):
        try:
            ##管理者のみ実行可能
            if interact.user.guild_permissions.administrator:
                channel = interact.channel
                read_type = "welcome_server"

                if activate == 1:
                    result = save_server_setting(interact.guild.id, read_type, channel.id)
                    if result is None:
                        await interact.response.send_message(f"**{channel.name}に参加メッセージを設定したのだ！**")
                        return
                    
                elif activate == 0:
                    result = save_server_setting(interact.guild.id, read_type, 0)
                    if result is None:
                        await interact.response.send_message(f"**参加メッセージ機能を使わないのだ！**")
                        return
                
                await interact.response.send_message("エラーが発生したのだ...")
                return
            
            await interact.response.send_message("このコマンドは管理者のみ実行できるのだ！")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)
    
    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(utils(bot))