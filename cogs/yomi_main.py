import discord
from discord.ext import commands
from discord import app_commands

from modules.yomiage_main import yomiage
from modules.vc_process import vc_inout_process
from modules.settings import get_server_setting


class yomi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        ###ボイスチャンネル内で変化があった時の処理
        await vc_inout_process(member, before, after, self.bot)


    @commands.Cog.listener() ##読み上げ用のイベント
    async def on_message(self, message: discord.Message):
        if (message.guild.voice_client is None): ##ギルド内に接続していない場合は無視
            return

        if message.author.bot: ##ボットの内容は読み上げない
            return
        
        channel = get_server_setting(message.guild.id, "speak_channel") ##読み上げるチャンネルをデータベースから取得
        
        if (message.channel.id == channel): ##ChannelIDが読み上げ対象のIDと一致しているか
            await yomiage(message, message.guild) ##難なくエラーをすり抜けたチャンネルにはもれなく読み上げ

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(yomi(bot))