from discord import Color, Embed
from discord.ext import commands
import subprocess


class MiscHandler(commands.Cog, name="Miscellaneous Commands"):
    def __init__(self, bot, user):
        self.bot = bot
        self.user = user


    @commands.command(name='crypto')
    async def crypto(self, ctx, coin="", rule=""):
        """Fetch crypto price information"""
        process = subprocess.Popen(['sudo', 'cryptocheck', coin], stdout=subprocess.PIPE)
        data = subprocess.check_output(['grep', rule.upper()], stdin=process.stdout)

        embedlist = Embed(title='Cryptocurrency Exchange Rate', description='Price to GBP', color = Color.dark_gold())
        embedlist.add_field(name=str(coin).capitalize(), value=data.decode('UTF-8'))

        await ctx.send(embed=embedlist)