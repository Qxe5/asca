'''UI components'''
import discord
from urlextract import URLExtract

from library import db

class Whitelist(discord.ui.Modal):
    '''A representation of a whitelist modal'''
    def __init__(self, whitelist, *args, **kwargs):
        '''Initialize the modal from a whitelist'''
        super().__init__(*args, **kwargs)

        self.add_item(
            discord.ui.InputText(
                label='Enter the URLs you wish to whitelist',
                style=discord.InputTextStyle.long,
                placeholder='URLs must include http(s)://',
                value='\n'.join(whitelist)
            )
        )

    async def callback(self, interaction):
        '''Process the form submission'''
        link_extractor = URLExtract()
        urls = link_extractor.find_urls(
            self.children[0].value,
            with_schema_only=True,
            only_unique=True
        )

        if not urls:
            await interaction.response.send_message('No valid URLs found', ephemeral=True)
        else:
            await db.clearwhitelist(interaction.guild_id)

            for url in urls:
                await db.addwhitelist(interaction.guild_id, url)

            await interaction.response.send_message(
                'Done. Run the command again to check your whitelist.',
                ephemeral=True
            )
