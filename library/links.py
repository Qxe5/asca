'''Transient management of scam links'''
from library.requester import scamlinks

links = set()
pendinglinks = {'gibthub.com'}

async def update():
    '''Updates scam links'''
    response = await scamlinks()

    if response:
        links.clear()
        links.update(response.splitlines())
        links.update(pendinglinks)
