from cogs.commands import CommandErrorHandler, LogCommandHandler, SecurityCommandHandler, SystemCommandHandler
from cogs.looped import SystemReporting
import discord
from discord.ext import commands, tasks
import settings
from settings import *
import subprocess


description = """System Monitor"""
bot = commands.Bot(command_prefix='!', description=description)

# Command handlers
bot.add_cog(CommandErrorHandler(bot=bot))
bot.add_cog(LogCommandHandler(bot=bot))
bot.add_cog(SecurityCommandHandler(bot=bot))
bot.add_cog(SystemCommandHandler(bot=bot, url=URL))

# Looped
bot.add_cog(SystemReporting(bot=bot, url=URL, user=USER_ID, channel=CHANNEL_ID))


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def test(ctx):
    """Test command, make sure bot is responding"""
    await ctx.send("%s Test Success" % USER_ID)


@bot.command()
async def showerthought(ctx):
        """Reddit shower thought of the day"""
        data = subprocess.check_output(["showerthought"])
        message = "🚿 r/showerthought of the day 🚿\n> " + data.decode('utf-8')

        await ctx.send(message)


bot.run(TOKEN)
