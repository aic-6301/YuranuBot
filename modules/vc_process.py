import discord
from modules.yomiage_main import yomiage
from modules.settings import get_setting

async def vc_inout_process(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState, client: discord.Client):
    if (member.bot):##ボットなら無視
        return      

    # #####!!!!!!自動接続関連!!!!!!!!!!########
    # ##接続時に自動接続する
    if after.channel != None:
        auto_channel = get_setting(member.guild.id, "auto_connect")
        if auto_channel == after.channel.id:
            if not member.guild.voice_client or member.guild.voice_client.channel != after.channel:
                await after.channel.connect()
                mess = get_setting(member.guild.id, "vc_connect_message")
                if mess is not None:
                    await yomiage(mess, member.guild, 1)
                return # 接続しましただけを読ませるために終わらせる

    if member.guild.voice_client:
        if before.channel != None:
            members = before.channel.members
            count = 0
            for m in before.channel.members:
                if m.bot:
                    members.pop(count)
                    count -= 1
                count += 1
                
            if len(members) == 0:
                await member.guild.voice_client.disconnect()
                return

    if before.channel != after.channel:
        for bot_client in client.voice_clients:
            ##参加時に読み上げる
            if after.channel is not None:
                if (after.channel.id == bot_client.channel.id):
                    mess = get_setting(after.channel.guild.id, "vc_join_message")#==が参加したのだ
                    if mess is not None:
                        await yomiage(f"{member.display_name}{mess}", member.guild, 3)
                
            ##退席時に読み上げる
            if before.channel is not None:
                if (before.channel.id == bot_client.channel.id):
                    mess = get_setting(before.channel.guild.id, "vc_exit_message")#==が退席したのだ
                    if mess is not None:
                        await yomiage(f"{member.display_name}{mess}", member.guild, 3)       

    #カメラ配信の開始・終了を読み上げる
    if before.self_video != after.self_video:
        if after.self_video:
            await yomiage(f"{member.display_name}がカメラ配信を開始したのだ。", member.guild, 3)
        else:
            await yomiage(f"{member.display_name}がカメラ配信を終了したのだ。", member.guild, 3)
    
    #画面共有の開始・終了を読み上げる
    if before.self_stream != after.self_stream:
        if after.self_stream:
            await yomiage(f"{member.display_name}が画面共有を開始したのだ。", member.guild, 3)
        else:
            await yomiage(f"{member.display_name}が画面共有を終了したのだ。", member.guild, 3)

