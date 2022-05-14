'''Command error handling'''
async def nodm(ctx):
    '''Handle a disallowed DM command invocation'''
    errormessage = 'Please use this command in a Server and not via DM'
    await ctx.respond(errormessage, ephemeral=True)

async def cantlog(ctx, attach=False, history=False):
    '''Handle a lack of the Send Messages or Attach Files or Read Message History permission'''
    attach_substring = ' / `Attach Files`' if attach else ''
    history_substring = ' / `Read Message History`' if history else ''
    errormessage = (f'Failed, I need the `Send Messages`{attach_substring}{history_substring} '
                    'permission in this channel')

    await ctx.respond(errormessage, ephemeral=True)

async def notowner(ctx):
    '''Handle not being the Bot Owner'''
    errormessage = 'Only the `Bot Owner` can run this command'
    await ctx.respond(errormessage, ephemeral=True)

async def invalid_days(ctx):
    '''Handle an invalid timeout period'''
    errormessage = '`days` must be 1 - 28'
    await ctx.respond(errormessage, ephemeral=True)
