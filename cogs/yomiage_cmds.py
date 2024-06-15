import discord
from discord.ext import commands
from discord import app_commands

import sys
import logging

from modules.checkPc import pc_status
from modules.yomiage_main import yomiage
from modules.vc_process import vc_inout_process
from modules.settings import db_load, db_init, get_server_setting, save_server_setting, save_user_setting
from modules.exception import sendException, exception_init
from modules.vc_dictionary import dictionary_load, delete_dictionary, save_dictionary, get_dictionary
import modules.lists as Page

zunda_conn_message =[
    "よっと、こんにちはなのだ！",
    "今日も元気に読み上げするのだー！",
    "ゆらぬぼっとの登場なのだー！"
]

conn_message = [
    "よっと、こんにちは！",
    "今日も元気に読み上げします！",
    "ゆらぬぼっとです！接続しました！"
]

class yomiage_cmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    yomi = app_commands.Group(name="yomiage", description="読み上げ関連のコマンドを実行するのだ")
        
    
    @app_commands.command(name="vc-start", description="ユーザーが接続しているボイスチャットに接続するのだ")
    async def vc_command(self, interact: discord.Interaction):
        try:
            if (interact.user.voice is None):
                await interact.response.send_message("ボイスチャンネルに接続していないのだ...")
                return
            if (interact.guild.voice_client is not None):
                await interact.response.send_message("すでにほかのボイスチャンネルにつながっているのだ...")
                return
            
            await interact.user.voice.channel.connect()
            
            ##接続を知らせるメッセージを送信
            channel_id = get_server_setting(interact.guild_id, "speak_channel")
            channel = discord.utils.get(interact.guild.channels, id=channel_id)
            length_limit = get_server_setting(interact.guild_id, "length_limit")
            yomiage_speed = get_server_setting(interact.guild_id, "speak_speed")

            if length_limit == 0:
                length_limit = f"!!文字数制限なし!!"
            else:
                length_limit = f"{length_limit}文字"
        
            embed = discord.Embed(
                title="接続したのだ！",
                description="ボイスチャンネルに参加しました！",
                color=discord.Color.green()
            )
            embed.add_field(
                name="読み上げるチャンネル",
                value=channel
            )
            embed.add_field(
                name="読み上げ文字数の制限",
                value=length_limit,
                inline=False
            )
            embed.add_field(
                name="読み上げスピード",
                value=yomiage_speed,
                inline=False
            )
            embed.add_field(
                name="**VOICEVOXを使用しています!**",
                value="**[VOICEVOX、音声キャラクターの利用規約](<https://voicevox.hiroshiba.jp/>)を閲覧のうえ、正しく使うのだ！**",
                inline=False
            )
            embed.add_field(
                name="読み上げの機能性向上のために、ほかの方にもご協力してもらっています！",
                value="自然係さん、ぬーんさんありがとうなのだ",
                inline=False
                )
            embed.set_footer(text="YuranuBot! | Made by yurq.", icon_url=self.bot.user.avatar.url)

            await interact.response.send_message(embed=embed)

            ##読み上げるチャンネルが存在しない場合に警告文を送信
            channel = get_server_setting(interact.guild.id, "speak_channel") 

            if (channel is None):
                embed = discord.Embed(
                    color=discord.Color.red(),
                    title="読み上げるチャンネルがわからないのだ...",
                    description="読み上げを開始するには読み上げるチャンネルを設定してください！"
                )

                await interact.channel.send(embed=embed)

            ##参加時の読み上げ
            spkID = get_server_setting(interact.guild.id, "vc_speaker")
            if spkID is 3:
                mess = conn_message
                await yomiage(mess, interact.guild)


        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)


    @yomi.command(name="channel", description="読み上げるチャンネルを変更するのだ")
    async def yomiage_channel(self, interact: discord.Interaction, channel: discord.TextChannel):
        try:
            result = save_server_setting(interact.guild_id, "speak_channel", channel.id)
            if result is None:
                await interact.response.send_message(f"☑**「{channel}」**を読み上げるのだ！")
                return
            
            await interact.response.send_message(f"設定に失敗したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)


    @yomi.command(name="dictionary-add", description="サーバー辞書に単語を追加するのだ")
    @app_commands.rename(text="単語", reading="かな")
    async def vc_dictionary(self, interact: discord.Interaction, text: str, reading: str):
        try:
            result = save_dictionary(interact.guild.id, text, reading, interact.user.id)
            if result is None:
                embed = discord.Embed(
                    title="正常に登録したのだ！",
                    description="サーバー辞書に単語を登録しました！",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="登録した単語",
                    value=text
                )
                embed.add_field(
                    name="読み仮名",
                    value=reading
                )
                await interact.response.send_message(embed=embed)
                return
            
            await interact.response.send_message(f"設定に失敗したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)
    

    @yomi.command(name="dictionary-list", description="サーバー辞書の単語を表示するのだ")
    async def vc_dictionary(self, interact: discord.Interaction):
        try:
            result = get_dictionary(interact.guild.id)
            if result:
                embeds = []
                embed = discord.Embed(
                    title="サーバー辞書の単語を表示するのだ！",
                    description="サーバー辞書の単語を表示するのだ！",
                    color=discord.Color.green()
                )
                for i in range(len(result)):
                    embed.add_field(
                        name=f"単語{i+1}",
                        value=f"単語: {result[i][0]}\n読み仮名: {result[i][1]}\n登録者: <@{result[i][2]}>"
                    )
                    if (i+1) % 10 == 0:  # Create a new embed every 10 words
                        embeds.append(embed)
                        embed = discord.Embed(
                            title="サーバー辞書の単語を表示するのだ！",
                            description="サーバー辞書の単語を表示するのだ！",
                            color=discord.Color.green()
                        )
                if len(embed.fields) > 0:  # Add the last embed if there are remaining fields
                    embeds.append(embed)

                await Page.Simple().start(interact, pages=embeds)
                return
            else:
                await interact.response.send_message("登録されている単語はないのだ...")
                return

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)


    @yomi.command(name="dictionary-delete", description="サーバー辞書の単語を削除するのだ")
    async def vc_dictionary(self, interact: discord.Interaction, text: str):
        try:
            result = delete_dictionary(interact.guild.id, text)
            if result is None:
                embed = discord.Embed(
                    title="正常に削除したのだ！",
                    description="サーバー辞書の単語を削除しました！",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="削除した単語",
                    value=text
                )

                await interact.response.send_message(embed=embed)
                return
            
            await interact.response.send_message(f"設定に失敗したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)

    @yomi.command(name="server-speaker", description="サーバーの読み上げ話者を設定するのだ")
    @app_commands.rename(id="話者")
    @app_commands.choices(
        id=[
            app_commands.Choice(name="ずんだもん",value=3),
            app_commands.Choice(name="春日部つむぎ",value=8),
            app_commands.Choice(name="四国めたん",value=2),
            app_commands.Choice(name="九州そら",value=16),
            app_commands.Choice(name="雨晴はう", value=10)
        ]
    )
    async def yomiage_server_speaker(self, interact:discord.Interaction,id:int):
        try:
            read_type = "vc_speaker"
            result = save_server_setting(interact.guild.id, read_type, id)

            if result is None:
                await interact.response.send_message(f"サーバー話者を変更したのだ！")
                return
            
            await interact.response.send_message("エラーが発生したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)


    @yomi.command(name="user-speaker", description="ユーザーの読み上げ話者を設定するのだ(どのサーバーでも同期されるのだ)")
    @app_commands.rename(id="話者")
    @app_commands.choices(
        id=[
            app_commands.Choice(name="ずんだもん",value=3),
            app_commands.Choice(name="春日部つむぎ",value=8),
            app_commands.Choice(name="四国めたん",value=2),
            app_commands.Choice(name="九州そら",value=16),
            app_commands.Choice(name="雨晴はう", value=10),
            app_commands.Choice(name="サーバーのデフォルト設定を利用する", value=-1)
        ]
    )
    async def yomiage_user_speaker(self, interact:discord.Interaction,id:int):
        try:
            read_type = "vc_speaker"
            result = save_user_setting(interact.user.id, read_type, id)

            if result is None:
                await interact.response.send_message(f"ユーザー話者を変更したのだ！")
                return
            
            await interact.response.send_message("エラーが発生したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)


    @yomi.command(name="speed", description="読み上げの速度を変更するのだ")
    @app_commands.rename(speed="速度")
    async def yomiage_speed(self, interact: discord.Interaction, speed: float):
        try:
            read_type = "speak_speed"
            result = save_server_setting(interact.guild.id, read_type, speed)

            if result is None:
                await interact.response.send_message(f"読み上げ速度を**「{speed}」**に変更したのだ！")
                return
            
            await interact.response.send_message("エラーが発生したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)


    @yomi.command(name="length-limit", description="読み上げ文字数を制限するのだ")
    async def yomiage_speed(self, interact: discord.Interaction, limit: float):
        try:
            read_type = "length_limit"
            result = save_server_setting(interact.guild.id, read_type, limit)

            if result is None:
                await interact.response.send_message(f"読み上げ文字数を**「{limit}文字」**に変更したのだ！")
                return
            
            await interact.response.send_message("エラーが発生したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)

    @yomi.command(name="join-message", description="参加時の読み上げ内容を変更するのだ<<必ず最初にユーザー名が来るのだ>>")
    async def change_vc_join_message(self, interact: discord.Interaction, text: str):
        try:
            res = save_server_setting(interact.guild_id, "vc_join_message", text)
            if res is None:
                await interact.response.send_message("**参加時の読み上げ内容を変更したのだ！**")
                return
            
            await interact.response.send_message("設定に失敗したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)
            
    @yomi.command(name="exit-message", description="退出時の読み上げ内容を変更するのだ<<必ず最初にユーザー名が来るのだ>>")
    async def change_vc_exit_message(self, interact: discord.Interaction, text: str):
        try:
            res = save_server_setting(interact.guild.id, "vc_exit_message", text)
            if res is None:
                await interact.response.send_message("**退出時の読み上げ内容を変更したのだ！**")
                return
            
            await interact.response.send_message("設定に失敗したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)

    @yomi.command(name="connect-message", description="読み上げ接続時の読み上げ内容を変更するのだ")
    async def change_vc_exit_message(self, interact: discord.Interaction, text: str):
        try:
            read_type = "vc_connect_message"
            res = save_server_setting(interact.guild.id, read_type, text)
            if res is None:
                await interact.response.send_message("**読み上げ接続時の読み上げ内容を変更したのだ！**")
                return
            
            await interact.response.send_message("設定に失敗したのだ...")  
            logging.warning(res)  

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)


    @yomi.command(name="auto-channel", description="設定したVCに自動接続するのだ(現在入っているVCが対象なのだ)")
    async def auto_connect(self, interact: discord.Interaction, bool: bool):
        try:
            if bool is True:
                if interact.user.voice is not None: ##設定するユーザーがチャンネルに入っていることを確認するのだ
                    res = save_server_setting(interact.guild_id, "auto_connect", interact.user.voice.channel.id)
                
                else: ##ユーザーがボイスチャットに入っていない場合
                    await interact.response.send_message("自動接続したいチャンネルに入ってから実行するのだ！")
                    return
            else:
                save_server_setting(interact.guild_id, "auto_connect", 0)
                await interact.response.send_message("自動接続を無効化したのだ！")
                return

            await interact.response.send_message(f"「{interact.user.voice.channel.name}」に自動接続を設定したのだ！")
            
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)

    
    @app_commands.command(name="vc-stop", description="ボイスチャンネルから退出するのだ")
    async def vc_disconnect_command(self, interact: discord.Interaction):
        try:
            if ((interact.guild.voice_client is None)):
                await interact.response.send_message("私はボイスチャンネルに接続していないのだ...")
                return
            
            elif((interact.user.voice is None)):
                await interact.response.send_message("ボイスチャンネルに接続していないのだ...入ってから実行するのだ")
                return
            elif interact.user.voice.channel != interact.guild.voice_client.channel:
                await interact.response.send_message("入ってるボイスチャンネルと違うチャンネルなのだ...実行してるチャンネルでやるのだ")
                return
            
            await interact.guild.voice_client.disconnect()
            await interact.response.send_message("切断したのだ")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)
    

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(yomiage_cmds(bot))