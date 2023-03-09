from cogs.commands import *
from cogs.looped import *
from discord import Intents
from discord.ext import commands
from settings import *

description = """System Monitor"""
bot = commands.Bot(command_prefix='!', description=description, intents=Intents.all())

async def main():
    await bot.add_cog(CommandErrorHandler(bot))
    await bot.add_cog(NetCommandHandler(bot))
    await bot.add_cog(SystemCommandHandler(bot, url=URL))
    await bot.add_cog(MiscCommandHandler(bot, user=USER_ID))

    # Looped
    # await bot.add_cog(SystemReporting(bot=bot, url=URL, user=USER_ID, channel=CHANNEL_ID))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    bot.run(TOKEN)
