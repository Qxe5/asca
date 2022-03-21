'''Transient management of scam links'''
from library.requester import scamlinks

links = []
pendinglinks = ['gibthub.com']

async def update():
    '''Updates scam links'''
    response = await scamlinks()

    if response:
        links.clear()
        links.extend(response.splitlines())
        links.extend(pendinglinks)
