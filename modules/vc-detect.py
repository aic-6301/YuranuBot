import threading
import discord
import modules.settings

def yomiage_watcher():
    threading.Thread(target=yomiage_watch, args=())

def yomiage_watch():
    