'''HTTP requests'''
import asyncio
from urllib.parse import urlparse

import aiohttp

async def scamlinks():
    '''Retrieve and return the scam links or None on failure'''
    source = 'https://raw.githubusercontent.com/DevSpen/scam-links/master/src/links.txt'

    async with aiohttp.ClientSession() as client:
        try:
            async with client.get(source) as response:
                if response.ok:
                    return await response.text()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            return None

async def unshorten(url):
    '''Unshorten and return the URL'''
    shorteners = {'bit.ly'}

    if urlparse(url).netloc not in shorteners:
        return url

    async with aiohttp.ClientSession() as client:
        try:
            async with client.head(url, allow_redirects=True, timeout=8) as response:
                if response.ok:
                    return response.url.human_repr()
                return url
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            return url
