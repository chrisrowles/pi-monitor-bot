import asyncio
import discord
from datetime import datetime
from discord.ext import commands, tasks
import json
import requests
import subprocess
import sys
import tabulate
import traceback

from pprint import pprint

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':
                await ctx.send('I could not find that member. Please try again.')

        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

            await ctx.send('A fucking error occurred.')


class SecurityCommandHandler(commands.Cog, name="Security Commands"):
    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        self.system.cancel()

    @commands.command(name='hibp')
    async def hibp(self, ctx, account):
        await asyncio.sleep(1)

    @tasks.loop(seconds=86400)
    async def breach(self):
        await asyncio.sleep(5)

    @breach.before_loop
    async def before_breach(self):
        await self.bot.wait_until_ready()


class SystemCommandHandler(commands.Cog, name='System Commands'):
    def __init__(self, bot, url):
        self.bot = bot
        self.url = url


    @commands.command(name='uptime')
    async def uptime(self, ctx):
        """Fetch network uptime"""
        response = requests.get(self.url + 'system/')
        system = response.json()

        message = "Network has been up for " + system['data']['platform']['uptime']

        await ctx.send(message)


    @commands.command(name='top')
    async def top(self, ctx):
        """Fetch top process consuming most memory"""
        response = requests.get(self.url + 'system/')
        system = response.json()
        process = system['data']['processes'][0]

        message = "Top process is " + process['name'].capitalize() + ' - ' + str(process['mem']) + 'MiB  - Owned by ' + process['username']

        await ctx.send(message)


    @commands.command(name='sys')
    async def sys(self, ctx, metric):
        """Fetch system metrics for cpu, mem or disk"""
        response = requests.get(self.url + 'system/')
        system = response.json()

        if metric == "raw":
            data = json.dumps(system['data'], indent=2)

            await ctx.send("```\n" + data + "\n```")
        else:
            if metric == "cpu":
                data = system['data']['cpu']

                embedlist = discord.Embed(title='System', description='cpu statistics')
                embedlist.add_field(name='Temp', value=str(data['temp']) + '°c')
                embedlist.add_field(name='Usage', value=str(data['usage']) + '%')
                embedlist.add_field(name='Freq', value=str(data['freq']) + 'MHz')

                await ctx.send(embed=embedlist)
            elif metric == "htop":
                data = system['data']['processes']

                header = data[0].keys()
                rows =  [x.values() for x in data]

                await ctx.send("```\n" + tabulate.tabulate(rows, header) + "\n```")
            else:
                data = system['data'][metric]

                embedlist = discord.Embed(title='System', description=str(metric) + ' statistics')
                embedlist.add_field(name='Used', value=str(data['used']) + ' GB')
                embedlist.add_field(name='Free', value=str(data['free']) + ' GB')
                embedlist.add_field(name='Total', value=str(data['total']) + ' GB')

                await ctx.send(embed=embedlist)


    @commands.command(name='supctl')
    async def supctl(self, ctx):
        """Get supervisor status"""
        # Obviously supervisor is running otherwise the bot wouldn't respond...
        # probably should rename to make it clearer I want a list of what's running.
        try:
            data = subprocess.check_output(['supervisorctl', 'status'])
            message = "supervisor status:\n```" + data.decode('utf-8') + "```"
        except:
            message = "supervisor status:\n**not running.**"

        await ctx.send(message)


class NetCommandHandler(commands.Cog, name="Network Commands"):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='inet')
    async def inet(self, ctx):
        """Fetch network information"""
        process = subprocess.Popen(['hostname', '-I'], stdout=subprocess.PIPE)
        ip = subprocess.check_output(['awk', '{print $1}'], stdin=process.stdout).decode('utf-8')

        process = subprocess.Popen(['ip', '-o', '-f', 'inet', 'addr', 'show'], stdout=subprocess.PIPE)
        subnet = subprocess.check_output(['awk', '/scope global/ {print $4}'], stdin=process.stdout).decode('utf-8')

        process = subprocess.Popen(['ip', 'r'], stdout=subprocess.PIPE)
        gateway = subprocess.check_output(['awk', 'NR==1{print $3}'], stdin=process.stdout).decode('utf-8')

        embedlist = discord.Embed(title='Network', description='network information')
        embedlist.add_field(name='IP', value=ip)
        embedlist.add_field(name='Subnet', value=subnet)
        embedlist.add_field(name='Gateway', value=gateway)

        await ctx.send(embed=embedlist)


    @commands.command(name='dig')
    async def dig(self, ctx, type, site, rule=""):
        """Fetch DNS information"""
        process = subprocess.Popen(['dig', type, site], stdout=subprocess.PIPE)
        data = subprocess.check_output(['grep', rule.upper()], stdin=process.stdout)

        message = "```\n" + data.decode('utf-8') + "\n```"

        await ctx.send(message)


class MiscCommandHandler(commands.Cog, name="Miscellaneous Commands"):
    def __init__(self, bot, user):
        self.bot = bot
        self.user = user


    @commands.command(name='crypto')
    async def crypto(self, ctx, coin="", rule=""):
        """Fetch crypto price information"""
        process = subprocess.Popen(['sudo', 'cryptocheck', coin], stdout=subprocess.PIPE)
        data = subprocess.check_output(['grep', rule.upper()], stdin=process.stdout)

        embedlist = discord.Embed(title='Cryptocurrency Exchange Rate', description='Price to GBP', color = discord.Color.dark_gold())
        embedlist.add_field(name=str(coin).capitalize(), value=data.decode('UTF-8'))

        await ctx.send(embed=embedlist)
