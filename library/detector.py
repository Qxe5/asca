'''Scam detection and punishment'''
from datetime import timedelta
from difflib import SequenceMatcher
from string import Template
from urllib.parse import urlparse

from discord import Embed, Colour, DMChannel, User, Forbidden, NotFound, HTTPException
from tldextract import extract
from urlextract import URLExtract

from library import db
from library.links import links
from library.reports import reportmessage

permission_error_template = Template('Scam detected, but I need the `$permission` permission '
                                     'or to be placed higher on the `Roles` list')

async def official(link):
    '''Determine and return whether the link is official'''
    official_links = [
        'discord.com',
        'discord.gg',
        'discord.gift',
        'discordapp.com',
        'cdn.discordapp.com',
        'discordstatus.com',
        'dis.gd'
    ]

    if link in official_links:
        return True
    return False

async def decyrillic(text):
    '''Transform Cyrillic into ASCII and return the transformation'''
    replacements = (
        ('а', 'a'),
        ('с', 'c'),
        ('е', 'e'),
        ('о', 'o'),
        ('у', 'y')
    )

    for replacement in replacements:
        text = text.replace(*replacement)

    return text

async def removewhitespace(message):
    '''Remove whitespace from message'''
    return ''.join(message.split())

async def contains_maliciousterm(message):
    '''Determine and return whether the message contains a malicious term'''
    message = await removewhitespace(message)

    terms = [
        'nitro',
        await removewhitespace('who is first?'),
        await removewhitespace('who will catch this gift?'),
        await removewhitespace('take it guys'),
        await removewhitespace('i stopped playing cs:go'),
        await removewhitespace('can you check out the game i created today'),
        await removewhitespace('test my first game?'),
        await removewhitespace('i made a game can you test play?')
    ]

    for term in terms:
        if term in message:
            return True
    return False

async def is_scam(message):
    '''Determine and return whether the message is a scam'''
    original_message = message.content
    embeds = message.embeds

    message = original_message.lower().replace('http', ' http').replace('://\n', '://')
    message = await decyrillic(message)

    link_extractor = URLExtract()
    link_extractor.update_when_older(1)
    urls = link_extractor.find_urls(message, with_schema_only=True, only_unique=True)
    message_links = [urlparse(url).netloc for url in urls]
    message_links = [
        message_link for message_link in message_links if not await official(message_link)
    ]
    message_links_string = '\n'.join(message_links)

    for message_link in message_links:
        domain = extract(message_link).domain
        ratio = SequenceMatcher(a='discord', b=domain).ratio()
        threshold = 0.85

        if message_link in links:
            return True

        if threshold < ratio < 1:
            await reportmessage(message_links_string)
            return True

    for url in urls:
        message = message.replace(url, '')

    if message_links:
        if await contains_maliciousterm(message):
            await reportmessage(original_message)
            return True

        for embed in embeds:
            if embed.provider.name and (await decyrillic(embed.provider.name)).lower() == 'discord':
                await reportmessage(message_links_string)
                return True

    return False

async def reply(message, replymessage):
    '''Reply to a message with a reply'''
    try:
        await message.reply(replymessage, mention_author=False)
    except (Forbidden, HTTPException):
        pass

async def timeout(message, reason):
    '''
    Time outs the author of the message for the reason given,
    and returns whether the timeout was successful
    '''
    days = await db.get_timeoutperiod(message.guild.id)

    try:
        await message.author.timeout_for(timedelta(days=days), reason=reason)
        return True
    except Forbidden:
        await reply(message, permission_error_template.substitute(permission='Moderate Members'))
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
        await reply(message, permission_error_template.substitute(permission='Ban Members'))
        return False

async def delete(message):
    '''Deletes the message'''
    try:
        await message.delete()
    except Forbidden:
        await reply(message, permission_error_template.substitute(permission='Manage Messages'))
    except NotFound:
        pass

async def punish(message):
    '''Punish the member which sent the message and return whether the punishment was succesfull'''
    if isinstance(message.author, User):
        await delete(message)
        return False

    has_moderate_members = message.author.guild_permissions.moderate_members
    has_ban_members = message.author.guild_permissions.ban_members
    if has_moderate_members or has_ban_members:
        response = 'Scam detected but you have the `Moderate Members` or `Ban Members` permission'
        await reply(message, response)
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

            description = f'**Message**```\n{scam_message}```'
            logembed = Embed(colour=Colour.red(), description=description)

            title = f'{action} {message.author}'
            logembed.set_author(icon_url=message.author.display_avatar.url, name=title)

            logembed.add_field(name='Mention', value=message.author.mention)

            icon_url = ('https://cdn.discordapp.com'
                        '/attachments/936463189237977139/937011660487544902/icon.png')
            logembed.set_footer(icon_url=icon_url, text=message.author.id)

            try:
                await logging_channel.send(embed=logembed)
            except Forbidden:
                await db.delete_logging_channel(message.guild.id)
        else:
            await db.delete_logging_channel(message.guild.id)

async def process(message, botuser):
    '''Processes a message'''
    if message.author == botuser or isinstance(message.channel, DMChannel):
        return

    if await is_scam(message) and await punish(message):
        await log(message)
        await delete(message)
