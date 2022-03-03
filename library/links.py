'''Transient management of scam links'''
import requests

links = []
pendinglinks = ['discoerd.gift', 'gitvhub.com']

async def update():
    '''Updates scam links'''
    source = 'https://raw.githubusercontent.com/DevSpen/scam-links/master/src/links.txt'
    response = requests.get(source)

    if not response.ok:
        return

    links.clear()
    links.extend(response.text.splitlines())
    links.extend(pendinglinks)
