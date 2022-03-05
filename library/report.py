'''Scam reports'''
from library.detector import lognotlink

async def reportmessage(message, reporter):
    '''Log an alleged scam message and who reported it'''
    await lognotlink(f'Report by {reporter}:\n{message}')
