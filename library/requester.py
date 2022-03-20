'''HTTP requests'''
import aiohttp

async def scamlinks():
    '''Retrieve and return the scam links or None on failure'''
    source = 'https://raw.githubusercontent.com/DevSpen/scam-links/master/src/links.txt'

    async with aiohttp.ClientSession() as client:
        try:
            async with client.get(source) as response:
                if response.ok:
                    return await response.text()
        except aiohttp.ClientConnectionError:
            return None
