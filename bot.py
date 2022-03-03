'''Entry point'''
from getpass import getpass
import logging
from signal import signal, SIGINT
import sys

import discord
from discord.ext import tasks, commands

from cogs.status import Status
from library import db
from library.detector import process
from library.error import cantlog, notadmin, notowner, invalid_days
from library.links import update
from library.paths import DATABASE, NOTLINKS

signal(SIGINT, lambda signalnumber, stackframe: sys.exit())

logging.basicConfig()

# init
intents = discord.Intents(guilds=True, guild_messages=True)
bot = discord.Bot(intents=intents)

@bot.listen()
async def on_ready():
    '''Print info when ready'''
    print('Logged in as', bot.user, f'({len(bot.guilds)} guilds)')

# tasks
@tasks.loop(minutes=30)
async def update_scamlinks():
    '''Update the scam links periodically'''
    await update()

update_scamlinks.start()

@tasks.loop(hours=24)
async def backup_database(ctx):
    '''Backup the database periodically'''
    with open(DATABASE, mode='rb') as database_file, \
         open(NOTLINKS, mode='rb') as notlinks_file:
        files = [
            discord.File(database_file, filename='database'),
            discord.File(notlinks_file, filename='notlinks')
        ]

        await ctx.respond(files=files)

# process messages
@bot.listen()
async def on_message(message):
    '''Handle messages'''
    await process(message, bot.user)

@bot.listen()
async def on_message_edit(previous_message, current_message):
    '''Handle message edits'''
    if current_message.content != previous_message.content:
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
    if isinstance(error, commands.MissingPermissions):
        await notadmin(ctx)
    else:
        print(type(error), error)

@bot.slash_command()
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def timeoutdays(ctx, days : int):
    '''Set the number of days timeouts are for'''
    if days < 1 or days > 28:
        raise discord.InvalidArgument('Invalid number of days')

    await db.set_timeoutperiod(ctx.guild.id, days)
    await ctx.respond(f'Timeout period set to {days} days', ephemeral=True)

@timeoutdays.error
async def timeoutdays_error(ctx, error):
    '''Handle errors for associated command'''
    if isinstance(error, commands.MissingPermissions):
        await notadmin(ctx)
    elif isinstance(error, discord.ApplicationCommandInvokeError):
        await invalid_days(ctx)
    else:
        print(type(error), error)

@bot.slash_command()
@commands.guild_only()
async def punishments(ctx):
    '''Get the punishment count for this guild'''
    count = await db.get_punishment_count(ctx.guild.id)
    await ctx.respond(f'{count} Timeouts / Bans for this server', ephemeral=True)

@bot.slash_command()
@commands.guild_only()
@commands.bot_has_permissions(send_messages=True)
@commands.has_permissions(administrator=True)
async def log(ctx):
    '''Set this channel as the logging channel for punishments'''
    await db.set_logging_channel(ctx.guild.id, ctx.channel.id)
    response = f'{ctx.channel.mention} has been set as the logging channel'
    await ctx.respond(response, ephemeral=True)

@log.error
async def log_error(ctx, error):
    '''Handle a lack of the Administrator permission'''
    if isinstance(error, commands.BotMissingPermissions):
        await cantlog(ctx)
    elif isinstance(error, commands.MissingPermissions):
        await notadmin(ctx)
    else:
        print(type(error), error)

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
    if isinstance(error, commands.MissingPermissions):
        await notadmin(ctx)
    else:
        print(type(error), error)

@bot.slash_command()
@commands.is_owner()
async def backup(ctx):
    '''Backup the database periodically'''
    backup_database.start(ctx)

@backup.error
async def backup_error(ctx, error):
    '''Handle not being the Bot Owner'''
    if isinstance(error, commands.NotOwner):
        await notowner(ctx)
    else:
        print(type(error), error)

# add cogs
bot.add_cog(Status(bot))

# authenticate
token = getpass(prompt='Token: ')

try:
    bot.run(token)
except discord.LoginFailure as loginfailure:
    print('Invalid Token')
    raise SystemExit(1) from loginfailure
