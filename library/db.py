'''Database interface'''
from enum import Enum
import sqlite3

from library.paths import DATABASE

MODES = Enum('MODES', 'TIMEOUT BAN')
DEFAULT_TIMEOUT_DAYS = 7

async def connect():
    '''Connect to the database and return a (connection, cursor) pair'''
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    createdb_script_path = 'create_database.sql'
    with open(createdb_script_path, encoding='utf-8') as createdb_script_file:
        cursor.executescript(createdb_script_file.read())

    return (connection, cursor)

async def disconnect(connection):
    '''Commit changes to the database and disconnect from it'''
    connection.commit()
    connection.close()

async def getmode(guild):
    '''Get and return whether the guild is in Timout or Ban mode'''
    connection, cursor = await connect()

    mode = cursor.execute('select * from modes where guild = ?', (guild,)).fetchone()

    await disconnect(connection)

    if not mode:
        return MODES.TIMEOUT
    return MODES.BAN

async def set_timeoutmode(guild):
    '''Set the punishment mode of the guild to Timeout'''
    connection, cursor = await connect()

    cursor.execute('delete from modes where guild = ?', (guild,))

    await disconnect(connection)

async def setbanmode(guild):
    '''Set the punishment mode of the guild to Ban'''
    connection, cursor = await connect()

    cursor.execute('insert into modes values(?)', (guild,))

    await disconnect(connection)

async def get_timeoutperiod(guild):
    '''Retrieve and return the timeout period for the guild'''
    connection, cursor = await connect()

    days = cursor.execute('select days from periods where guild = ?', (guild,)).fetchone()

    await disconnect(connection)

    if not days:
        return DEFAULT_TIMEOUT_DAYS
    return days[0]

async def set_timeoutperiod(guild, days):
    '''Set the timeout period for the guild'''
    connection, cursor = await connect()

    if days == DEFAULT_TIMEOUT_DAYS:
        cursor.execute('delete from periods where guild = ?', (guild,))
    else:
        cursor.execute('replace into periods values (?, ?)', (guild, days))

    await disconnect(connection)

async def get_punishment_count(guild):
    '''Get and return the timeouts/bans for the guild'''
    connection, cursor = await connect()

    count = cursor.execute('select count from punishments where guild = ?', (guild,)).fetchone()

    await disconnect(connection)

    if not count:
        return 0
    return count[0]

async def count_punishment(guild):
    '''Increment punishment count for the guild'''
    connection, cursor = await connect()

    count = cursor.execute('select count from punishments where guild = ?', (guild,)).fetchone()

    if not count:
        cursor.execute('insert into punishments values (?, ?)', (guild, 1))
    else:
        count = count[0]

        cursor.execute('update punishments set count = ? where guild = ?', (count + 1, guild))

    await disconnect(connection)

async def get_logging_channel(guild):
    '''Get and return the logging channel of the guild (or None if it is not set)'''
    connection, cursor = await connect()

    channel = cursor.execute('select channel from logs where guild = ?', (guild,)).fetchone()

    await disconnect(connection)

    if channel:
        channel = channel[0]

    return channel

async def set_logging_channel(guild, channel):
    '''Sets the logging channel of the guild'''
    connection, cursor = await connect()

    cursor.execute('replace into logs values (?, ?)', (guild, channel))

    await disconnect(connection)

async def delete_logging_channel(guild):
    '''Delete the logging channel of the guild'''
    connection, cursor = await connect()

    cursor.execute('delete from logs where guild = ?', (guild,))

    await disconnect(connection)

async def prune(guilds):
    '''Prune the database for guilds the bot is not in'''
    connection, cursor = await connect()

    tables = {'modes', 'periods', 'punishments', 'logs'}
    placeholders = ', '.join('?' * len(guilds))

    for table in tables:
        cursor.execute(f'delete from {table} where guild not in ({placeholders})', guilds)

    await disconnect(connection)
