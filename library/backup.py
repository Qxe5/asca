'''Persistent data files backup'''
from discord import File

from library.paths import DATABASE, NOTLINKS

async def backup_db(channel):
    '''Backup files to channel'''
    with open(DATABASE, mode='rb') as database_file, \
         open(NOTLINKS, mode='rb') as notlinks_file:
        files = [
            File(database_file, filename='database'),
            File(notlinks_file, filename='notlinks')
        ]

        await channel.send(files=files)
