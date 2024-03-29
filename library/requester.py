'''HTTP requests'''
import asyncio
from urllib.parse import urlparse

import aiohttp

async def scamlinks():
    '''Retrieve and return the scam links or None on failure'''
    source = 'https://raw.githubusercontent.com/Discord-AntiScam/scam-links/main/list.txt'

    async with aiohttp.ClientSession(raise_for_status=True) as client:
        try:
            async with client.get(source) as response:
                return await response.text()
        except (aiohttp.ClientConnectionError, aiohttp.ClientResponseError, asyncio.TimeoutError):
            return None

async def unshorten(client, url):
    '''Unshorten and return the URL via the client'''
    shorteners = {'7r6.com', 'bit.ly', 'goo.su', 'rb.gy', 'shorturl.at', 'u.to'}

    if urlparse(url).netloc not in shorteners:
        return url

    try:
        async with client.head(url, allow_redirects=True, timeout=8) as response:
            return response.url.human_repr()
    except (aiohttp.ClientConnectionError, aiohttp.ClientResponseError, asyncio.TimeoutError):
        return url

async def redirect(urls):
    '''Unshorten and return the URLs'''
    async with aiohttp.ClientSession(raise_for_status=True) as client:
        return {await unshorten(client, url) for url in urls}
