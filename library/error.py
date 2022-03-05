'''Command error handling'''
async def cantlog(ctx, attach=False):
    '''Handle a lack of the Send Messages or Attach Files permission'''
    attach_substring = ' / `Attach Files`' if attach else ''
    errormessage = (f'Failed, I need the `Send Messages`{attach_substring} '
                    'permission in this channel')

    await ctx.respond(errormessage, ephemeral=True)

async def notadmin(ctx):
    '''Handle a lack of the Administrator permission'''
    errormessage = 'Only a member with the `Administrator` permission can run this command'
    await ctx.respond(errormessage, ephemeral=True)

async def notowner(ctx):
    '''Handle not being the Bot Owner'''
    errormessage = 'Only the `Bot Owner` can run this command'
    await ctx.respond(errormessage, ephemeral=True)

async def invalid_days(ctx):
    '''Handle an invalid timeout period'''
    errormessage = '`days` must be 1 - 28'
    await ctx.respond(errormessage, ephemeral=True)
