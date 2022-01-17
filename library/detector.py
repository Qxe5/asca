'''Scam detection and punishment'''
from datetime import timedelta
from string import Template
from urllib.parse import urlparse

from discord import DMChannel, User, Forbidden
from urlextract import URLExtract

from library import db
from library.links import links

permission_error_template = Template('Scam detected, but I need the `$permission` permission')

async def is_scam(message):
    '''Determine and return whether the message is a scam'''
    message = message.lower()

    link_extractor = URLExtract()
    link_extractor.update_when_older(1)
    message = message.replace('http', ' http')
    urls = link_extractor.find_urls(message, with_schema_only=True, only_unique=True)
    nitrolink = 'https://discord.gift'
    message_links = [urlparse(url).netloc for url in urls if not url.startswith(nitrolink)]

    for message_link in message_links:
        if message_link in links:
            return True
        message = message.replace(message_link, '')

    if message_links and 'nitro' in ''.join(message.split()):
        return True
    return False

async def timeout(message, reason):
    '''
    Time outs the author of the message for the reason given,
    and returns whether the timeout was successful
    '''
    try:
        await message.author.timeout_for(timedelta(weeks=1), reason=reason)
        return True
    except Forbidden:
        await message.reply(permission_error_template.substitute(permission='Moderate Members'))
        return False

async def ban(message, reason):
    '''
    Bans the author of the message for the reason given,
    and returns whether the ban was successful
    '''
    try:
        await message.author.ban(delete_message_days=0, reason=reason)
        return True
    except Forbidden:
        await message.reply(permission_error_template.substitute(permission='Ban Members'))
        return False

async def delete(message):
    '''Deletes the message'''
    try:
        await message.delete()
    except Forbidden:
        await message.reply(permission_error_template.substitute(permission='Manage Messages'))

async def punish(message):
    '''Punish the member which sent the message and return whether the punishment was succesfull'''
    if isinstance(message.author, User):
        await delete(message)
        return False

    has_moderate_members = message.author.guild_permissions.moderate_members
    has_ban_members = message.author.guild_permissions.ban_members
    if has_moderate_members or has_ban_members:
        response = 'Scam detected but you have the `Moderate Members` or `Ban Members` permission'
        await message.reply(response)
        return False

    mode = await db.getmode(message.guild.id)
    reason = f'They sent "{message.content}"'

    match mode:
        case db.MODES.TIMEOUT:
            return await timeout(message, reason)
        case db.MODES.BAN:
            return await ban(message, reason)

async def log(message):
    '''Logs the punishment'''
    await db.count_punishment(message.guild.id)

    logging_channel = await db.get_logging_channel(message.guild.id)

    if logging_channel: # logging channel set
        logging_channel = message.guild.get_channel(logging_channel)

        if logging_channel: # logging channel still exists
            scam_message = message.content.replace('`', '').replace('```', '')

            mode = await db.getmode(message.guild.id)

            match mode:
                case db.MODES.TIMEOUT:
                    action = 'Timed out'
                case db.MODES.BAN:
                    action = 'Banned'

            log_message = f'**{action}** {message.author.mention} for ```{scam_message}```'
            try:
                await logging_channel.send(log_message)
            except Forbidden:
                await db.delete_logging_channel(message.guild.id)
        else:
            await db.delete_logging_channel(message.guild.id)

async def process(message, botuser):
    '''Processes a message'''
    if message.author == botuser or isinstance(message.channel, DMChannel):
        return

    if await is_scam(message.content):
        if await punish(message):
            await log(message)
            await delete(message)
