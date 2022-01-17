'''Entry point'''
import logging

import discord
from discord.ext import tasks, commands

from library import db
from library.detector import process
from library.error import notadmin
from library.links import update

def main():
    '''Start the bot'''
    logging.basicConfig()

    # init
    bot = discord.Bot(activity=discord.Activity(type=discord.ActivityType.listening, name='/'))

    @bot.listen()
    async def on_ready():
        '''Print info when ready'''
        print('Logged in as', bot.user, 'via pycord', discord.__version__, f'({len(bot.guilds)} guilds)')

    # update scam links
    @tasks.loop(hours=24)
    async def update_scamlinks():
        '''Update the scam links periodically'''
        await update()

    update_scamlinks.start()

    # process messages
    @bot.listen()
    async def on_message(message):
        '''Handle messages'''
        await process(message, bot.user)

    @bot.listen()
    async def on_message_edit(previous_message, current_message): # pylint: disable=unused-argument
        '''Handle message edits'''
        await process(current_message, bot.user)

    # commands
    @bot.slash_command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def switchmode(ctx):
        '''Toggle between Timeout mode and Ban mode'''
        mode = await db.getmode(ctx.guild.id)

        match mode:
            case db.MODES.TIMEOUT:
                await db.setbanmode(ctx.guild.id)
                await ctx.respond('Ban mode set', ephemeral=True)
            case db.MODES.BAN:
                await db.set_timeoutmode(ctx.guild.id)
                await ctx.respond('Timeout mode set', ephemeral=True)

    @switchmode.error
    async def switchmode_error(ctx, error):
        '''Handle a lack of the Administrator permission'''
        await notadmin(ctx, error)

    @bot.slash_command()
    @commands.guild_only()
    async def punishments(ctx):
        '''Get the punishment count for this guild'''
        count = await db.get_punishment_count(ctx.guild.id)
        await ctx.respond(f'{count} Timeouts / Bans for this server', ephemeral=True)

    @bot.slash_command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def log(ctx):
        '''Set this channel as the logging channel for punishments'''
        await db.set_logging_channel(ctx.guild.id, ctx.channel.id)
        response = f'{ctx.channel.mention} has been set as the logging channel'
        await ctx.respond(response, ephemeral=True)

    @log.error
    async def log_error(ctx, error):
        '''Handle a lack of the Administrator permission'''
        await notadmin(ctx, error)

    @bot.slash_command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def stoplog(ctx):
        '''Stop logging punishments to a channel'''
        await db.delete_logging_channel(ctx.guild.id)
        await ctx.respond('I will no longer log punishments to a channel', ephemeral=True)

    @stoplog.error
    async def stoplog_error(ctx, error):
        '''Handle a lack of the Administrator permission'''
        await notadmin(ctx, error)

    # authenticate
    with open('token', encoding='utf-8') as token_file:
        token = token_file.read()
    bot.run(token)

if __name__ == '__main__':
    main()
