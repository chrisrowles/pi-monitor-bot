from commands.error_handler import ErrorHandler
from commands.misc_handler import MiscHandler
from commands.net_handler import NetHandler
from commands.system_handler import SystemHandler
from discord import Intents
from discord.ext import commands
from settings import *


description = """System Monitor"""
bot = commands.Bot(command_prefix='!', description=description, intents=Intents.all())


async def main():
    await bot.add_cog(ErrorHandler(bot))
    await bot.add_cog(NetHandler(bot))
    await bot.add_cog(SystemHandler(bot, url=URL))
    await bot.add_cog(MiscHandler(bot, user=USER_ID))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    bot.run(TOKEN)
