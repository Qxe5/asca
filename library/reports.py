'''Transient management of scam message reports'''
log = []

async def reportmessage(message):
    '''Log an alleged scam message'''
    if message and message not in log:
        log.append(message)

async def getreport():
    '''Return the next report'''
    if not log:
        return 'None'

    return log.pop(0)
