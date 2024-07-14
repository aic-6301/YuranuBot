import platform
import discord
import logging
import psutil
import sys
from modules.exception import sendException
from discord.ext import commands

##Windowsの場合の処理
if platform.uname().system == "Windows":
    ### LibreHardwareMonitorのライブラリをロード
    import clr
    clr.AddReference(r'dll\LibreHardwareMonitorLib') 

    from LibreHardwareMonitor.Hardware import Computer
    logging.debug("LibreHardWareMonitorLib -> 読み込み完了")

    ### 表示するデータを選択してオープン
    computer = Computer()

    ###LibreHardwareMonitorの設定を格納する
    computer.IsCpuEnabled = True
    # computer.IsGpuEnabled = True
    # computer.IsMemoryEnabled = True
    # computer.IsMotherboardEnabled = True
    # computer.IsControllerEnabled = True
    # computer.IsNetworkEnabled = True
    # computer.IsStorageEnabled = True

    computer.Open()

async def pc_status(bot: commands.Bot):
    try:
        os_info = platform.uname()
        os_bit = platform.architecture()[1]

        cpu_freq = psutil.cpu_freq().current / 1000
        cpu_cores = psutil.cpu_count()
        ram_info = psutil.virtual_memory()
        py_version = platform.python_version()
        py_buildDate = platform.python_build()[1]
        
        ping = bot.latency * 1000

        cpu_Temp = "Not Available    "
        cpu_Power = "Not Available    "
        cpu_Load = "Not Available    "

        if os_info.system == "Windows":

            cpu_name = computer.Hardware[0].Name

            hard_id = 0

            sensor = computer.Hardware[hard_id].Sensors
            computer.Hardware[hard_id].Update()

            if ("AMD" in cpu_name): ### LibreHardwareMonitorを利用して取得
                for a in range(0, len(computer.Hardware[hard_id].Sensors)):
                    if(("Load" in str(sensor[a].SensorType)) and ("Total" in str(sensor[a].Name))):
                        cpu_Load = format(sensor[a].Value, ".1f")
            elif ("Intel" in cpu_name):
                for a in range(0, len(computer.Hardware[hard_id].Sensors)):
                    if ("Load" in str(sensor[a].SensorType) and ("Total" in str(sensor[a].Name))):
                        cpu_Load = format(sensor[a].Value, ".1f")

            if (os_info.system == "Windows"): ### Windowsの場合、表記を変更する
                win32_edition = platform.win32_edition()
                win32_ver = os_info.release

                if (win32_edition == "Professional"):
                    win32_edition = "Pro"
                
                os_name = f"{os_info.system} {win32_ver} {win32_edition}"

        elif os_info.system == "Linux":
            os_name = platform.uname().system
            cpu_name = platform.processor()

            cpu_Load = psutil.cpu_percent(percpu=False)
            
            temp_ = psutil.sensors_temperatures()
            if "coretemp" in temp_:
                for entry in temp_["coretemp"]:
                    if entry.label == "Package id 0":
                        cpu_Temp = f"{entry.current}"

        embed = discord.Embed( ### Embedを定義する
                        title="よしっ、調査完了っと！これが結果なのだ！",# タイトル
                        color=0x00ff00, # フレーム色指定(今回は緑)
                        description=f"「{bot.user}が、PCの情報をかき集めてくれたようです。」", # Embedの説明文 必要に応じて
                        )
        
        embed.set_author(name=bot.user, # Botのユーザー名
                    icon_url=bot.user.avatar.url
                    )

        embed.set_thumbnail(url="https://www.iconsdb.com/icons/download/white/ok-128.png") # サムネイルとして小さい画像を設定できる
    

        embed.add_field(name="**//一般情報//**", inline=False, value=
                        f"> ** OS情報**\n"+
                        f"> [OS名] **{os_name}**\n"+
                        f"> [Architecture] **{os_info.machine}**\n> \n"+
                        
                        f"> **Python情報**\n"+
                        f"> [バージョン] **{py_version}**\n"+
                        f"> [ビルド日時] **{py_buildDate}**\n> \n"+
                        f"> **Discord情報**\n"+
                        f"> [Discord.py] **Version {discord.__version__}**\n"
                        f"> [Ping値] **{ping:.1f}ms**\n"
                        ) # フィールドを追加。
        embed.add_field(name="**//CPU情報//**", inline=False, value=
                        f"> [CPU名] **{cpu_name}**\n"+
                        f"> [コア数] **{cpu_cores} Threads**\n"+
                        f"> [周波数] **{cpu_freq:.2f} GHz**\n"+
                        f"> [使用率] **{cpu_Load}%**\n"
                        )
        embed.add_field(name="**//メモリ情報//**", value=
                        f"> [使用率] **{(ram_info.used/1024/1024/1024):.2f}/{(ram_info.total/1024/1024/1024):.2f} GB"+
                        f" ({ram_info.percent}%)**"
                        ) # フィールドを追加。
        
        embed.set_footer(text="YuranuBot! | Made by yurq_",
                    icon_url=bot.user.avatar.url)

        return embed
    
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_no = exception_traceback.tb_lineno
        await sendException(e, filename, line_no)