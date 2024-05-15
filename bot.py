import discord
import os
import logging
import sys

from discord.ext import commands
from dotenv import load_dotenv
from modules.checkPc import pc_status
from modules.yomiage_main import yomiage
from modules.vc_process import vc_inout_process
from modules.settings import db_load, db_init, get_setting, save_setting
from modules.exception import sendException, exception_init
from modules.vc_dictionary import dictionary_load, delete_dictionary, save_dictionary

##ロギングのレベルを設定
logging.basicConfig(level=logging.DEBUG)

ROOT_DIR = os.path.dirname(__file__)
SCRSHOT = os.path.join(ROOT_DIR, "scrshot", "scr.png")

### 管理者権限を確認する。なければ終了する。
# import ctypes
# is_admin = ctypes.windll.shell32.IsUserAnAdmin()
# if (is_admin):
#     logging.debug("管理者権限を確認しました")
# else:
#     logging.error("管理者権限で実行されていません！")
#     sys.exit()

###データベースの読み込み
db_data = db_load("database.db")
db_init()

dic_data = dictionary_load("dictionary.db")


if db_data==False:
    logging.warn("サーバー「設定」データベースの読み込みに失敗しました")
    sys.exit()

if dic_data==False:
    logging.warn("サーバー「辞書」データベースの読み込みに失敗しました")
    sys.exit()

### インテントの生成
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
logging.debug("discord.py -> インテント生成完了")

### クライアントの生成
# bot = discord.Client(intents=intents, activity=discord.Game(name="起きようとしています..."))
bot = commands.Bot(command_prefix='!', intents=intents)
logging.debug("discord.py -> クライアント生成完了")

##sendExceptionが利用できるようにする
exception_init(bot)

### コマンドツリーの作成
tree = bot.tree
logging.debug("discord.py -> ツリー生成完了")



@bot.event
async def on_ready():
    print(f'{bot.user}に接続しました！')
    await tree.sync()
    print("コマンドツリーを同期しました")



@tree.command(name="vc-start", description="ユーザーが接続しているボイスチャットに接続するのだ")
async def vc_command(interact: discord.Interaction):
    try:
        if (interact.user.voice is None):
            await interact.response.send_message("ボイスチャンネルに接続していないのだ...")
            return
        if (interact.guild.voice_client is not None):
            await interact.response.send_message("すでにほかのボイスチャンネルにつながっているのだ...")
            return
        
        await interact.user.voice.channel.connect()
        
        ##接続を知らせるメッセージを送信
        channel_id = get_setting(interact.guild_id, "speak_channel")
        channel = discord.utils.get(interact.guild.channels, id=channel_id)
        length_limit = get_setting(interact.guild_id, "length_limit")
        yomiage_speed = get_setting(interact.guild_id, "speak_speed")

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
            name="**VOICEVOXを使用しています！**",
            value="**[VOICEVOX、音声キャラクターの利用規約](<https://voicevox.hiroshiba.jp/>)を閲覧のうえ、正しく使うのだ！**",
            inline=False
        )
        embed.add_field(
            name="読み上げの機能性向上のために、ほかの方にもご協力してもらっています！",
            value="自然係さん、ぬーんさんありがとうなのだ",
            inline=False
            )
        embed.set_footer(text="YuranuBot! | Made by yurq_", icon_url=bot.user.avatar.url)

        await interact.response.send_message(embed=embed)

        ##読み上げるチャンネルが存在しない場合に警告文を送信
        channel = get_setting(interact.guild.id, "speak_channel") 

        if (channel is None):
            embed = discord.Embed(
                color=discord.Color.red(),
                title="読み上げるチャンネルがわからないのだ...",
                description="読み上げを開始するには読み上げるチャンネルを設定してください！"
            )
            
            await interact.channel.send(embed=embed)

        ##参加時の読み上げ
        mess = get_setting(interact.guild_id, "vc_connect_message")
        if mess is not None:
            await yomiage(mess, interact.guild, 1)


    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_no = exception_traceback.tb_lineno
        await sendException(e, filename, line_no)


@tree.command(name="yomiage-channel", description="読み上げるチャンネルを変更するのだ")
async def yomiage_channel(interact: discord.Interaction, channel: discord.TextChannel):
    try:
        result = save_setting(interact.guild_id, "speak_channel", channel.id)
        if result is None:
            await interact.response.send_message(f"☑**「{channel}」**を読み上げるのだ！")
            return
        
        await interact.response.send_message(f"設定に失敗したのだ...")

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_no = exception_traceback.tb_lineno
        await sendException(e, filename, line_no)


@tree.command(name="yomiage-dictionary-add", description="サーバー辞書に単語を追加するのだ")
async def vc_dictionary(interact: discord.Interaction, text: str, reading: str):
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


@tree.command(name="yomiage-dictionary-delete", description="サーバー辞書の単語を削除するのだ")
async def vc_dictionary(interact: discord.Interaction, text: str):
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


@tree.command(name="yomiage-speed", description="読み上げの速度を変更するのだ")
async def yomiage_speed(interact: discord.Interaction, speed: float):
    try:
        read_type = "speak_speed"
        result = save_setting(interact.guild.id, read_type, speed)

        if result is None:
            await interact.response.send_message(f"読み上げ速度を**「{speed}」**に変更したのだ！**")
            return
        
        await interact.response.send_message("エラーが発生したのだ...")

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_no = exception_traceback.tb_lineno
        await sendException(e, filename, line_no)

@tree.command(name="yomiage-join-message", description="参加時の読み上げ内容を変更するのだ<<必ず最初にユーザー名が来るのだ>>")
async def change_vc_join_message(interact: discord.Interaction, text: str):
    try:
        res = save_setting(interact.guild_id, "vc_join_message", text)
        if res is None:
            await interact.response.send_message("**参加時の読み上げ内容を変更したのだ！**")
            return
        
        await interact.response.send_message("設定に失敗したのだ...")

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_no = exception_traceback.tb_lineno
        await sendException(e, filename, line_no)
        
@tree.command(name="yomiage-exit-message", description="退出時の読み上げ内容を変更するのだ<<必ず最初にユーザー名が来るのだ>>")
async def change_vc_exit_message(interact: discord.Interaction, text: str):
    try:
        res = save_setting(interact.guild.id, "vc_exit_message", text)
        if res is None:
            await interact.response.send_message("**退出時の読み上げ内容を変更したのだ！**")
            return
        
        await interact.response.send_message("設定に失敗したのだ...")

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_no = exception_traceback.tb_lineno
        await sendException(e, filename, line_no)

@tree.command(name="yomiage-connect-message", description="読み上げ接続時の読み上げ内容を変更するのだ")
async def change_vc_exit_message(interact: discord.Interaction, text: str):
    try:
        read_type = "vc_connect_message"
        res = save_setting(interact.guild.id, read_type, text)
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


@tree.command(name="yomiage-auto-channel", description="設定したVCに自動接続するのだ(現在入っているVCが対象なのだ)")
async def auto_connect(interact: discord.Interaction, bool: bool):
    try:
        if bool is True:
            if interact.user.voice is not None: ##設定するユーザーがチャンネルに入っていることを確認するのだ
                res = save_setting(interact.guild_id, "auto_connect", interact.user.voice.channel.id)
            
            else: ##ユーザーがボイスチャットに入っていない場合
                await interact.response.send_message("自動接続したいチャンネルに入ってから実行するのだ！")
                return
        else:
            save_setting(interact.guild_id, "auto_connect", 0)
            await interact.response.send_message("自動接続を無効化したのだ！")
            return

        await interact.response.send_message(f"「{interact.user.voice.channel.name}」に自動接続を設定したのだ！")

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_no = exception_traceback.tb_lineno
        await sendException(e, filename, line_no)


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    ###ボイスチャンネル内で変化があった時の処理
    await vc_inout_process(member, before, after, bot)


@bot.event ##読み上げ用のイベント
async def on_message(message: discord.Message):
    if (message.guild.voice_client is None): ##ギルド内に接続していない場合は無視
        return

    if message.author.bot: ##ボットの内容は読み上げない
        return
    
    channel = get_setting(message.guild.id, "speak_channel") ##読み上げるチャンネルをデータベースから取得
    
    if (message.channel.id == channel): ##ChannelIDが読み上げ対象のIDと一致しているか
        await yomiage(message, message.guild, 3) ##難なくエラーをすり抜けたチャンネルにはもれなく読み上げ

@tree.command(name="vc-stop", description="ボイスチャンネルから退出するのだ")
async def vc_disconnect_command(interact: discord.Interaction):
    try:
        if ((interact.guild.voice_client is None)):
            await interact.response.send_message("私はボイスチャンネルに接続していないのだ...")
            return
        
        elif((interact.user.voice is None)):
            await interact.response.send_message("ボイスチャンネルに接続していないのだ...入ってから実行するのだ")
            return
        
        await interact.guild.voice_client.disconnect()
        await interact.response.send_message("切断したのだ")
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_no = exception_traceback.tb_lineno
        await sendException(e, filename, line_no)

@tree.command(name="sbc",description="Shizen Black Companyの説明資料なのだ")#Shizen Black Companyの宣伝
async def sbc_command(interact:discord.Interaction):
    await interact.response.send_message('**～ドライバーの腕が生かせる最高の職場～　Shizen Black Company** https://black.shizen.lol')

@tree.command(name="status",description="Botを稼働しているPCの状態を表示するのだ")#PCの状態
async def status(interact: discord.Interaction):
    ##PCのステータスを送信
    await pc_status(interact, bot)

load_dotenv()
TOKEN = os.getenv("TOKEN")

# クライアントの実行
bot.run(TOKEN)
