import discord
import os
import logging
import platform
import sys

from discord.ext import commands
from dotenv import load_dotenv
from modules.checkPc import pc_status
from modules.yomiage_main import yomiage
from modules.vc_process import vc_inout_process
from modules.settings import db_load, db_init, get_server_setting, save_server_setting, save_user_setting
from modules.exception import sendException, exception_init
from modules.vc_dictionary import dictionary_load, delete_dictionary, save_dictionary

ROOT_DIR = os.path.dirname(__file__)
SCRSHOT = os.path.join(ROOT_DIR, "scrshot", "scr.png")

logging.basicConfig(level=logging.INFO)

# 管理者権限を確認する。なければ終了する。
if platform.uname().system == "Windows":
    import ctypes
    is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    if (is_admin):
        logging.debug("管理者権限を確認しました")
    else:
        logging.error("管理者権限で実行されていません！")

###データベースの読み込み
db_load("database.db")
db_data = db_init()

dic_data = dictionary_load("dictionary.db")


if db_data==False:
    logging.warning("サーバー「設定」データベースの読み込みに失敗しました")
    sys.exit()

if dic_data==False:
    logging.warning("サーバー「辞書」データベースの読み込みに失敗しました")
    sys.exit()

### インテントの生成
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
logging.debug("discord.py -> インテント生成完了")

### クライアントの生成
# bot = discord.Client(intents=intents, activity=discord.Game(name="起きようとしています..."))
bot = commands.Bot(command_prefix='yr!', intents=intents)
logging.debug("discord.py -> クライアント生成完了")

##sendExceptionが利用できるようにする
exception_init(bot)

### コマンドツリーの作成
tree = bot.tree
logging.debug("discord.py -> ツリー生成完了")

@bot.event
async def on_ready():
    ##cogファイルを読み込む
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{file[:-3]}")
                logging.info(f'Loaded cogs: {file[:-3]}')
            except Exception as e:
                logging.error(f'Failed to load extension {file[:-3]}.')
                logging.error(e)
    try:
        ##jishakuを読み込む
        await bot.load_extension('jishaku')
        logging.info(f'Loaded cogs: jishaku')
    except Exception as e:
        logging.error(f'Failed to load extension jishaku.')
        logging.error(e)

    print(f'{bot.user}に接続しました！')
    await tree.sync()
    print("コマンドツリーを同期しました")

##入室通知
@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    channel = get_server_setting(guild.id, "welcome_server")
    embed = discord.Embed(title=f"「{guild.name}」へようこそなのだ！", description=f"「{member.display_name}」がやってきました！", color= discord.Color.green())
    embed.set_footer(text="YuranuBot! | Made by yurq_", icon_url=bot.user.avatar.url) 

    if channel != 0:
        for chn in guild.text_channels:
            if chn.id == channel:
                await chn.send(embed=embed)
                return

load_dotenv()
TOKEN = os.getenv("TOKEN")

# クライアントの実行
bot.run(TOKEN)
