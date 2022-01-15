'''Command error handling'''
from discord.ext import commands

async def notadmin(ctx, error):
    '''Handle a lack of the Administrator permission'''
    if isinstance(error, commands.MissingPermissions):
        errormessage = 'Only a member with the `Administrator` permission can run this command'
        await ctx.respond(errormessage, ephemeral=True)
    else:
        print(type(error), error)
