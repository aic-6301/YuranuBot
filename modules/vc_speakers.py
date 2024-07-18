import logging
from discord import app_commands

spk_list = [
    ["ずんだもん", 3],
    ["春日部つむぎ", 8],
    ["四国めたん", 2],
    ["九州そら", 16],
    ["雨晴はう", 10]
]

spk_choices = []
user_spk_choices = []

# Choiceリストを作る
for spk_name, spk_id in spk_list:
    spk_choices.append(app_commands.Choice(name=spk_name, value=spk_id))
for spk_name, spk_id in spk_list:
    user_spk_choices.append(app_commands.Choice(name=spk_name, value=spk_id))
    
logging.debug(f"vc_speakers -> 話者リスト: {spk_list}")

#ユーザー向けChoiceリスト
user_spk_choices.append(app_commands.Choice(name="サーバーの話者を使用する", value=-1))

logging.debug(f"vc_speakers -> ユーザー話者リスト: {user_spk_choices}")