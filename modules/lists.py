import discord
from discord.ext import commands
from discord import app_commands

class PageView(discord.ui.View):
    def __init__(self, items, page=0):
        super().__init__()
        self.items = items
        self.page = page
        self.update_items()

    async def update_items(self):
        # 現在のページのアイテムを計算
        start_index = self.page * 6
        end_index = min(start_index + 6, len(self.items))
        items_to_display = self.items[start_index:end_index]
        
        # メッセージを更新
        for i, item in enumerate(self.children):
            if isinstance(item, discord.ui.Button):
                if i == 0 and self.page > 0:  # Previous Button
                    item.disabled = False
                elif i == 1 and self.page < (len(self.items) // 6):  # Next Button
                    item.disabled = False
                else:
                    item.disabled = True
            else:
                item.value = "\n".join(items_to_display[i:i+1])  # Update text content

        await self.message.edit(content="", view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_page(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.page += 1
        await self.update_items()
        await interaction.response.defer()

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def prev_page(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.page -= 1
        await self.update_items()
        await interaction.response.defer()