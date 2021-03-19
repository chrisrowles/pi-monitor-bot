from datetime import datetime
import discord
from discord.ext import commands
import json
import requests
import subprocess
import sys
import tabulate
import traceback

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


class LogCommandHandler(commands.Cog, name="Log Monitoring Comamnds"):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='showlog', aliases=['tail'])
    async def showlog(self, ctx, log, date=None):
        """Fetch log data"""
        today = datetime.today().strftime('%Y-%m-%d')
        if date is not None:
            today = date

        if log == "dpkg":
            process = subprocess.Popen(['grep', today + '.*. install ', '/var/log/dpkg.log'], stdout=subprocess.PIPE)
            data = subprocess.check_output(['awk', '-F', '" "', '"{print $1 " " $2 " " $4}"'], stdin=process.stdout)
        elif log == "auth":
            process = subprocess.Popen(['tail', '/var/log/auth.log'], stdout=subprocess.PIPE)
            data = subprocess.check_output(['grep', 'sshd'], stdin=process.stdout)

        message = "```\n" + data.decode('utf-8') + "\n```"

        await ctx.send(message)


class SecurityCommandHandler(commands.Cog, name="Security Commands"):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='iptables', aliases=['firewall', 'rules'])
    async def iptables(self, ctx):
        """Fetch active iptables rules"""
        data = subprocess.check_output(['sudo', 'iptables', '-L'])

        message = "```\n" + data.decode('utf-8') + "\n```"

        await ctx.send(message)


    @commands.command(name='ban')
    async def ban(self, ctx, jail, ip):
        """Ban an IP address"""
        data = subprocess.check_output(['sudo', 'fail2ban-client', 'set', jail, 'banip', ip])

        message = "**" + ip + "** has been banned, please check #jail for confirmation."

        await ctx.send(message)


    @commands.command(name='unban')
    async def unban(self, ctx, jail, ip):
        """Unban an IP address"""
        data = subprocess.check_output(['sudo', 'fail2ban-client', 'set', jail, 'unbanip', ip])

        message = "**" + ip + "** has been unbanned, please check #jail for confirmation."

        await ctx.send(message)


class SystemCommandHandler(commands.Cog, name='System Monitoring Commands'):
    def __init__(self, bot, url):
        self.bot = bot
        self.url = url
    

    @commands.command(name='uptime')
    async def uptime(self, ctx):
        """Fetch network uptime"""
        response = requests.get(self.url + 'system/')
        system = response.json()
        uptime = system['data']['platform']['uptime']

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


    @commands.command(name='supervisord')
    async def supervisor(self, ctx):
        """Get supervisor status"""
        # Obviously supervisor is running otherwise the bot wouldn't respond...
        # probably should rename to make it clearer I want a list of what's running.
        try:
            data = subprocess.check_output(['supervisorctl', 'status'])
            message = "supervisor status:\n```" + data.decode('utf-8') + "```"
        except:
            message = "supervisor status:\n**not running.**"

        await ctx.send(message)


class MiscCommandHandler(commands.Cog, name="Miscellaneous Commands"):
    def __init__(self, bot, user):
        self.bot = bot
        self.user = user

    @commands.command(name="showerthought")
    async def showerthought(ctx):
        """Reddit shower thought of the day"""
        data = subprocess.check_output(["showerthought"])
        message = "🚿 r/showerthought of the day 🚿\n> " + data.decode('utf-8')

        await ctx.send(message)