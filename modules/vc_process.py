import discord
from modules.yomiage_main import yomiage
from modules.settings import get_server_setting

async def vc_inout_process(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState, bot: discord.Client):
    if (member.bot):##ボットなら無視
        return      

    # #####!!!!!!自動接続関連!!!!!!!!!!########
    # ##接続時に自動接続する
    if after.channel != None:
        auto_channel = get_server_setting(member.guild.id, "auto_connect")
        if auto_channel == after.channel.id:
            if not member.guild.voice_client or member.guild.voice_client.channel != after.channel:
                await after.channel.connect()

                ##接続を知らせるメッセージを送信
                channel_id = get_server_setting(after.channel.guild.id, "speak_channel")
                channel = discord.utils.get(after.channel.guild.channels, id=channel_id)
                length_limit = get_server_setting(after.channel.guild.id, "length_limit")
                yomiage_speed = get_server_setting(after.channel.guild.id, "speak_speed")

                if length_limit == 0:
                    length_limit = f"!!文字数制限なし!!"
                else:
                    length_limit = f"{length_limit}文字"
            
                embed = discord.Embed(
                    title="自動接続したのだ！",
                    description="設定されているVCに自動接続しました！",
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

                await channel.send(embed=embed)
            
                mess = get_server_setting(member.guild.id, "vc_connect_message")
                if mess is not None:
                    await yomiage(mess, member.guild)
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

                ##自動切断を知らせる
                channel_id = get_server_setting(before.channel.guild.id, "speak_channel")
                channel = discord.utils.get(before.channel.guild.channels, id=channel_id)
                embed = discord.Embed(
                    title="切断したのだ！",
                    description="VC内にユーザがいなくなったため、自動切断しました！",
                    color=discord.Color.green()
                )
                await channel.send(embed=embed)

                return

    if before.channel != after.channel:
        for bot_client in bot.voice_clients:
            ##参加時に読み上げる
            if after.channel is not None:
                if (after.channel.id == bot_client.channel.id):
                    mess = get_server_setting(after.channel.guild.id, "vc_join_message")#==が参加したのだ
                    if mess is not None:
                        await yomiage(f"{member.display_name}{mess}", member.guild)
                
            ##退席時に読み上げる
            if before.channel is not None:
                if (before.channel.id == bot_client.channel.id):
                    mess = get_server_setting(before.channel.guild.id, "vc_exit_message")#==が退席したのだ
                    if mess is not None:
                        await yomiage(f"{member.display_name}{mess}", member.guild)       

    #カメラ配信の開始・終了を読み上げる
    if before.self_video != after.self_video:
        if after.self_video:
            if after.guild.voice_client in bot.voice_clients:
                await yomiage(f"{member.display_name}がカメラ配信を開始しました。", member.guild)
            else:
                await yomiage(f"{member.display_name}がカメラ配信を終了しました。", member.guild)
    
    #画面共有の開始・終了を読み上げる
    if before.self_stream != after.self_stream:
        if after.self_stream:
            if after.guild.voice_client in bot.voice_clients:
                await yomiage(f"{member.display_name}が画面共有を開始しました。", member.guild)
            else:
                await yomiage(f"{member.display_name}が画面共有を終了しました。", member.guild)

