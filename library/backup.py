'''Database backup'''
from discord import File

from library.db import prune
from library.paths import DATABASE

async def backup_db(channel, guilds):
    '''
    Prune the database for guilds the bot is not in
    and then backup the database to the channel
    '''
    await prune(guilds)

    with open(DATABASE, mode='rb') as database_file:
        file = File(database_file, filename='database')
        await channel.send(file=file)
