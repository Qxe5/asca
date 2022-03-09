'''Database backup'''
from discord import File

from library.paths import DATABASE

async def backup_db(channel):
    '''Backup database to channel'''
    with open(DATABASE, mode='rb') as database_file:
        file = File(database_file, filename='database')
        await channel.send(file=file)
