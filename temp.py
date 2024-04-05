import clr # the pythonnet module.
import sys
import time
clr.AddReference(r'dll\LibreHardwareMonitorLib') 
# e.g. clr.AddReference(r'OpenHardwareMonitor/OpenHardwareMonitorLib'), without .dll

from LibreHardwareMonitor.Hardware import Computer

computer = Computer()
computer.IsCpuEnabled = True
computer.Open()

import ctypes
is_admin = ctypes.windll.shell32.IsUserAnAdmin()
if (is_admin):
    print("管理者権限で実行されています。")
else:
    print("Error!管理者で実行されていません！")
    sys.exit()

while True:

    for hard_ in range(0, len(computer.Hardware)):
        print(computer.Hardware[hard_].Name)
        computer.Hardware[hard_].Update()

        for sens_ in range(0, len(computer.Hardware[hard_].Sensors)):
            sensor_type = computer.Hardware[hard_].Sensors[sens_].SensorType
            sens_name = computer.Hardware[hard_].Sensors[sens_].Name
            sens_i = computer.Hardware[hard_].Sensors[sens_].Identifier

            val = format(computer.Hardware[hard_].Sensors[sens_].Value, ".2f")
            

            # if ("/temperature" in str(computer.Hardware[hard_].Sensors[sens_].Identifier)):
            print(f"name: {sens_name} ({sens_i}) {sensor_type} val: {val}")

    time.sleep(1)




