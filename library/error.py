'''Command error handling'''
async def cantlog(ctx):
    '''Handle a lack of the Send Messages permission'''
    errormessage = 'Failed, I need the `Send Messages` permission in this channel'
    await ctx.respond(errormessage, ephemeral=True)

async def notadmin(ctx):
    '''Handle a lack of the Administrator permission'''
    errormessage = 'Only a member with the `Administrator` permission can run this command'
    await ctx.respond(errormessage, ephemeral=True)
