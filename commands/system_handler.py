from discord import Embed
from discord.ext import commands
import json
import requests
import tabulate
import subprocess


class SystemHandler(commands.Cog, name='System Commands'):
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

                embedlist = Embed(title='System', description='cpu statistics')
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

                embedlist = Embed(title='System', description=str(metric) + ' statistics')
                embedlist.add_field(name='Used', value=str(data['used']) + ' GB')
                embedlist.add_field(name='Free', value=str(data['free']) + ' GB')
                embedlist.add_field(name='Total', value=str(data['total']) + ' GB')

                await ctx.send(embed=embedlist)


    @commands.command(name='supctl')
    async def supctl(self, ctx):
        """Get supervisor status"""
        try:
            data = subprocess.check_output(['supervisorctl', 'status'])
            message = "supervisor status:\n```" + data.decode('utf-8') + "```"
        except:
            message = "supervisor status:\n**not running.**"

        await ctx.send(message)
