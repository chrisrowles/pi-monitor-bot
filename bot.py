from cogs.commands import *
from cogs.looped import *
from discord.ext import commands, tasks
from settings import *


description = """System Monitor"""
bot = commands.Bot(command_prefix='!', description=description)

# Command handlers
bot.add_cog(CommandErrorHandler(bot))
bot.add_cog(NetCommandHandler(bot))
bot.add_cog(SecurityCommandHandler(bot))
bot.add_cog(SystemCommandHandler(bot, url=URL))
bot.add_cog(MiscCommandHandler(bot, user=USER_ID))

# Looped
bot.add_cog(SystemReporting(bot=bot, url=URL, user=USER_ID, channel=CHANNEL_ID))


@bot.command()
async def test(ctx):
    """Test command, make sure bot is responding"""
    await ctx.send("%s Test Success" % USER_ID)


bot.run(TOKEN)
