'''Scam detection and punishment'''
from asyncio import Lock, sleep
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher
from re import search
from string import Template
from urllib.parse import urlparse

from discord import Embed, Colour, DMChannel, User, Forbidden, NotFound, HTTPException
from discord.utils import remove_markdown
from pysafebrowsing import SafeBrowsing
from tldextract import extract
from urlextract import URLExtract

from library import db
from library.links import links
from library.reports import reportmessage
from library.requester import unshorten

@dataclass
class Secrets:
    '''Storage of secrets'''
    safebrowsing : str = None

deletelock = Lock()
permission_error_template = Template('Scam detected, but I need the `$permission` permission '
                                     'or to be placed higher on the `Roles` list')

async def official(link):
    '''Determine and return whether the link is official'''
    official_links = {
        'airhorn.solutions',
        'airhornbot.com',
        'bigbeans.solutions',
        'dis.gd',
        'discord-activities.com',
        'discord.app',
        'discord.co',
        'discord.com',
        'discord.design',
        'discord.dev',
        'discord.gg',
        'discord.gift',
        'discord.gifts',
        'discord.media',
        'discord.new',
        'discord.store',
        'discord.tools',
        'discordactivities.com',
        'discordapp.com',
        'discordapp.io',
        'discordapp.net',
        'discordcdn.com',
        'discordmerch.com',
        'discordpartygames.com',
        'discordsays.com',
        'discordstatus.com',
        'watchanimeattheoffice.com',

        'discordjs.guide',
        'discord.me',
        'discords.com'
    }

    for official_link in official_links:
        if link == official_link or link.endswith(f'.{official_link}'):
            return True

    return False

async def decyrillic(text):
    '''Transform Cyrillic into ASCII and return the transformation'''
    replacements = {
        ('з', '3'),
        ('ч', '4'),
        ('а', 'a'),
        ('в', 'b'),
        ('с', 'c'),
        ('е', 'e'),
        ('н', 'h'),
        ('к', 'k'),
        ('м', 'm'),
        ('о', 'o'),
        ('р', 'p'),
        ('т', 't'),
        ('х', 'x'),
        ('у', 'y')
    }

    for replacement in replacements:
        text = text.replace(*replacement)

    return text

async def slash(message, tlds):
    '''Insert a forward slash into the message after TLDs not succeeded by one and return it'''
    urls = {word for word in message.split(' ') if word.startswith('http')}

    for url in urls:
        match = search(r'^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?', url)

        path = match.group(5)
        if not path:
            domain = match.group(4)
            try:
                tld = sorted((tld for tld in tlds if tld in domain),
                            key=lambda tld, domain=domain : (domain.rfind(tld), len(tld)))[-1]
            except (TypeError, IndexError):
                continue
            newdomain = f'{tld}/'.join(domain.rsplit(tld, maxsplit=1))

            message = message.replace(domain, newdomain)

    return message

async def protocol(url):
    '''Add a protocol to the URL if it does not currently have one and return it'''
    return f'https://{url}' if not url.startswith('http') else url

async def removewhitespace(message):
    '''Remove whitespace from message and return it'''
    return ''.join(message.split())

async def contains_maliciousterm(message):
    '''Determine and return whether the message contains a malicious term'''
    message = await removewhitespace(message)

    terms = {
        'nitro',
        'password:',
        await removewhitespace('who is first?'),
        await removewhitespace('who will catch this gift?'),
        await removewhitespace('take it guys'),
        await removewhitespace('i stopped playing cs:go'),
        await removewhitespace('can you check out the game i created today'),
        await removewhitespace('test my first game'),
        await removewhitespace('i made a game can you test play?'),
        await removewhitespace('i have coded a new game'),
        await removewhitespace('farm cryptocurrency'),
        await removewhitespace('from the crypto market')
    }

    return any(term in message for term in terms)

async def contains_phonenumber(message):
    '''Determine and return whether the message contains a phone number used by a scammer'''
    message = await removewhitespace(message)

    phone_numbers = {
        await removewhitespace('+1 (256) 482-1848'),
        await removewhitespace('+1 (518) 952-5213'),
        await removewhitespace('+1 (531) 254-0859'),
        await removewhitespace('+1 (559) 666‑3967'),
        await removewhitespace('+1 (757) 861‑3217')
    }

    return any(phone_number in message for phone_number in phone_numbers)

async def spamcache(message, cached_messages, time):
    '''
    Get and return possible spam messages from the current message and the cached messages,
    sent within the time period
    '''
    return {
        cached_message for cached_message in cached_messages
        if datetime.now(timezone.utc) - cached_message.created_at < time
        and message.guild == cached_message.guild
        and message.author == cached_message.author
        and (message.content and message.content == cached_message.content or
            message.stickers and message.stickers == cached_message.stickers)
    }

async def spam(message, cached_messages, maxrepeat=5):
    '''Determine and return whether the message is spam'''
    return len(await spamcache(message, cached_messages, timedelta(seconds=10))) > maxrepeat

async def scam(message, cached_messages): # pylint: disable=too-many-return-statements
    '''Determine and return whether the message is a scam'''
    fmessage = remove_markdown(message.content.replace('http', ' http').replace('://\n', '://'))

    link_extractor = URLExtract()
    link_extractor.update_when_older(1)

    tlds = {tld for tld in link_extractor._load_cached_tlds() if tld in fmessage} # pylint: disable=protected-access
    fmessage = await slash(fmessage, tlds)

    urls = {
        await unshorten(await protocol(url))
        for url in link_extractor.find_urls(fmessage, only_unique=True)
        if not any(url.startswith(entry) for entry in await db.getwhitelist(message.guild.id))
    }

    fmessage = await decyrillic(fmessage.lower())

    message_links = {
        message_link
        for message_link in {urlparse(url).netloc for url in urls}
        if not await official(message_link)
    }
    report = '\n'.join(message_links)

    for message_link in message_links:
        domain = extract(message_link).domain
        ratio = SequenceMatcher(a='discord', b=domain).ratio()
        threshold = 0.85

        if message_link in links:
            return True

        if threshold < ratio < 1:
            await reportmessage(report)
            return True

    for url in urls:
        parsedurl = urlparse(url)
        parsedurl = parsedurl.path + parsedurl.query

        if any(ext in parsedurl for ext in ('.exe', '.msi', '.zip', '.rar')):
            await reportmessage(report)
            return True

        fmessage = fmessage.replace(url, '')

    if message_links:
        if any(
            result['malicious'] for result in
            SafeBrowsing(Secrets.safebrowsing).lookup_urls(tuple(message_links)).values()
        ):
            return True

        if await contains_maliciousterm(fmessage):
            await reportmessage(report)
            return True

        for embed in message.embeds:
            if embed.provider.name and (await decyrillic(embed.provider.name)).lower() == 'discord':
                await reportmessage(report)
                return True

    if await contains_phonenumber(fmessage):
        await reportmessage(report)
        return True

    if await spam(message, cached_messages):
        await reportmessage(report)
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
    except HTTPException:
        await reply(message,
            'Scam detected, but I failed to Timeout this member due to a Discord Server error'
        )
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

async def prune(messages):
    '''Deletes the messages'''
    async with deletelock:
        for message in messages:
            await delete(message)
            await sleep(5)

async def punish(message):
    '''Punish the member which sent the message and return whether the punishment was succesfull'''
    if isinstance(message.author, User):
        await delete(message)
        return False

    has_moderate_members = message.author.guild_permissions.moderate_members
    has_ban_members = message.author.guild_permissions.ban_members
    if has_moderate_members or has_ban_members:
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
            scam_message = message.content.replace('`', '')

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

async def process(message, cached_messages):
    '''Processes a message'''
    if message.author.bot or isinstance(message.channel, DMChannel):
        return

    if await scam(message, cached_messages) and await punish(message):
        await log(message)
        await prune(await spamcache(message, cached_messages, timedelta.max))
