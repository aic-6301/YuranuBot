import discord
import time
import sys
import re
import platform

from modules.db_settings import save_server_setting, get_server_setting
from discord.ext import commands, tasks
from discord import app_commands

URL_REGEX = re.compile(r"https?://(?:ptb.)discord(?:app)?\.com/channels/(\d+)/(\d+)/(\d+)")

class Discord_URL_Loader( commands.Cog ):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="discord-url-load", description="DiscordのメッセージURLからメッセージを取得するのだ")
    @app_commands.rename(use="速度")
    @app_commands.choices(use=[
        app_commands.Choice(name="使用する", value=1),
        app_commands.Choice(name="使用しない", value=0)
    ])
    async def discord_url_load(self, interact: discord.Interaction, use: int):
        result = save_server_setting(interact.guild.id, "discord_url_load", use)
        if result == None:
            use_str:str = None
            if use == 1:
                use_str = "使用する"
            else:
                use_str = "使用しない"
            
            interact.response.send_message(f"Discord URL Loaderを**「{use_str}」**に設定したのだ！")
            return
        
        interact.response.send_message("設定に失敗したのだ...")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        #サーバー設定を読み込み、この機能を使用するかを検出
        use = get_server_setting(message.guild.id,"discord_url_load")
        if use == 1:
            if message.author == self.bot.user:
                return
            
            # 正規表現でDiscordメッセージURLを検出
            search = URL_REGEX.search(message.content)

            if search:
                #URLからそれぞれを検出
                guild_id, channel_id, message_id = search.groups()
                
                #ギルドとチャンネルを取得
                guild = self.bot.get_guild(int(guild_id))
                channel = guild.get_channel(int(channel_id))

                #↑からメッセージを検索
                tar_message = await channel.fetch_message(int(message_id))

                if guild != None and channel!= None and tar_message != None:
                    #Embedでいろいーろ
                    embed=discord.Embed(
                        #メッセージの送信者
                        title=f"{tar_message.author.name}",
                        #メッセージの内容
                        description=f"{tar_message.content}",

                        color=discord.Color.brand_green()
                    )
                    #サーバーアイコンとどこのやつか表示
                    embed.set_author(icon_url=guild.icon.url, name=f"Message ({guild.name} | {channel.name})")
                    #送信元のユーザーアイコン
                    embed.set_thumbnail(url=tar_message.author.avatar.url)

                    # 埋め込みがある場合はそれも読み込む
                    if tar_message.attachments:
                        for attach in tar_message.attachments:
                            attach: discord.Attachment
                            #画像の場合は画像を埋め込む
                            if attach.content_type == "image":
                                embed.set_image(url=attach.url)

async def setup(bot: commands.Bot ) -> None:
    await bot.add_cog(Discord_URL_Loader(bot))
                                

                