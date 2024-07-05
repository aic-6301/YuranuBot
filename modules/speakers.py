from discord.app_commands import Choice

spk_list = [
            Choice(name="ずんだもん",value=3),
            Choice(name="春日部つむぎ",value=8),
            Choice(name="四国めたん",value=2),
            Choice(name="九州そら",value=16),
            Choice(name="雨晴はう", value=10)
]

user_spk_list = spk_list.append(
    Choice(name="★サーバー設定を使用する★",value=-1)
)