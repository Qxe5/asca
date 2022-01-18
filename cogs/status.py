'''Bot status'''
from asyncio import sleep

import discord
from discord.ext import commands, tasks

class Status(commands.Cog):
    '''Represents the status of a bot'''
    def __init__(self, bot):
        '''Initialize the status'''
        self.bot = bot
        self.author = discord.Game('by Dot and friends')
        self.man = discord.Activity(type=discord.ActivityType.listening, name='/')

        self.update_status.start() # pylint: disable=no-member

    @tasks.loop(hours=2)
    async def update_status(self):
        '''Updates the status'''
        await self.bot.wait_until_ready()

        await self.bot.change_presence(activity=self.author)
        await sleep(20)
        await self.bot.change_presence(activity=self.man)
