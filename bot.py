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

##ロギングのレベルを設定
logging.basicConfig(level=logging.INFO)

ROOT_DIR = os.path.dirname(__file__)
SCRSHOT = os.path.join(ROOT_DIR, "scrshot", "scr.png")

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

load_dotenv()
TOKEN = os.getenv("TOKEN")

# クライアントの実行
bot.run(TOKEN)
