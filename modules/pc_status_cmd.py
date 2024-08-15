import platform
import discord
import logging
import psutil
import sys
from modules.exception import sendException
from discord.ext import commands

class PCStatus():
    os_name: str = None

    cpu_name: str = None
    cpu_load: float = None
    cpu_freq: float = None

    ram_use: float = None
    ram_total: float = None
    ram_percent: float = None

    gpu_name: str = None
    gpu_load: float = None
    gpu_mem_use: float = None

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
    computer.IsGpuEnabled = True
    # computer.IsMemoryEnabled = True
    # computer.IsMotherboardEnabled = True
    # computer.IsControllerEnabled = True
    # computer.IsNetworkEnabled = True
    # computer.IsStorageEnabled = True

    computer.Open()

async def pc_status():
    try:
        os_info = platform.uname()
        ram_info = psutil.virtual_memory()
        
        pc = PCStatus()

        if os_info.system == "Windows":
            for hard in computer.Hardware:
                if hard.HardwareType == "Cpu":
                    pc.cpu_name = hard.Name
                if "Gpu" in hard.HardwareType:
                    pc.gpu_name = hard.Name

                for sensor in hard.Sensors:
                    if sensor.Name == "CPU Total":
                        pc.cpu_load = sensor.Value
                    if sensor.Name == "GPU Core":
                        pc.gpu_load = sensor.Value
                    if sensor.Name == "D3D Dedicated Memory Used":
                        pc.gpu_mem_use = sensor.Value
                    
        elif os_info.system == "Linux":
            pc.cpu_name = platform.processor()
            pc.cpu_load = psutil.cpu_percent(percpu=False)

        pc.os_name = os_info.system
        pc.cpu_freq = psutil.cpu_freq().current / 1000
        pc.ram_use = ram_info.used/1024/1024/1024
        pc.ram_total = ram_info.total/1024/1024/1024
        pc.ram_percent = ram_info.percent

        return pc
    
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_no = exception_traceback.tb_lineno
        await sendException(e, filename, line_no)