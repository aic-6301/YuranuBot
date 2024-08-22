import threading
import time
import logging
import os
import sys

def delete_file_latency(file_name, latency):
    task = threading.Thread(target=delete_file_latency_, args=(file_name, latency))
    task.start()

def delete_file_latency_(file_name, latency):
    try:
        time.sleep(latency+2.0)
        os.remove(file_name)
        
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_no = exception_traceback.tb_lineno
        logging.exception(f"ファイル削除エラー： {line_no}行目、 [{type(e)}] {e}")
