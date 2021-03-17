import os
import json
import asyncio
import requests
import tabulate
import discord
from discord.ext import commands, tasks
import subprocess
import settings

from cogs.maincog import MainCog

URL = os.environ.get('SYSAPI_URL')
TOKEN = os.environ.get('DISCORD_TOKEN')

description = '''System Monitor'''
bot = commands.Bot(command_prefix='!', description=description)
bot.add_cog(MainCog(bot=bot, url=URL))

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def supervisord(ctx, arg):
    data = subprocess.check_output(["supervisorctl", arg])
    print(data)

    await ctx.send("supervisord status: **" + data.decode("utf-8") + '**')

@bot.command()
async def uptime(ctx):
    """Fetch network uptime"""
    response = requests.get(URL)
    system = response.json()
    uptime = system['data']['platform']['uptime']

    message = "Network has been up for " + system['data']['platform']['uptime']

    await ctx.send(message)


@bot.command()
async def top(ctx):
    """Fetch top process consuming most memory"""
    response = requests.get(URL)
    system = response.json()
    process = system['data']['processes'][0]

    message = "Top process is " + process['name'].capitalize() + ' - ' + str(process['mem']) + 'MiB  - Owned by ' + process['username']

    await ctx.send(message)


@bot.command()
async def sys(ctx, metric):
    """Fetch system metrics for cpu, mem or disk"""
    response = requests.get(URL)
    system = response.json()

    if metric == "raw":
        data = json.dumps(system['data'], indent=2)

        await ctx.send('```\n' + data + '\n```')
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

            await ctx.send('```\n' + tabulate.tabulate(rows, header) + '\n```')
        else:
            data = system['data'][metric]

            embedlist = discord.Embed(title='System', description=str(metric) + ' statistics')
            embedlist.add_field(name='Used', value=str(data['used']) + ' GB')
            embedlist.add_field(name='Free', value=str(data['free']) + ' GB')
            embedlist.add_field(name='Total', value=str(data['total']) + ' GB')

            await ctx.send(embed=embedlist)


@bot.command()
async def iptables(ctx):
    """Fetch active iptables rules"""
    data = subprocess.check_output(["sudo", "iptables", "-L"])

    await ctx.send('```\n' + data.decode("utf-8") + '\n```')

    
@bot.command()
async def jailer(ctx, jail, action, ip):
    """Ban/unban an IP address"""
    data = subprocess.check_output(["sudo", "fail2ban-client", "set", jail, action, ip])
    actioned = "banned" if action == "banip" else "unbanned"

    message = "**" + ip + "** has been " + actioned + ", please run `!iptables` to confirm rules"

    await ctx.send(message)


@bot.command()
async def ban(ctx, jail, ip):
    """Ban an IP address (shorthand ban action for !jailer)"""
    data = subprocess.check_output(["sudo", "fail2ban-client", "set", jail, "banip", ip])

    message = "**" + ip + "** has been banned, please run `!iptables` to confirm rules"

    await ctx.send(message)


@bot.command()
async def unban(ctx, jail, ip):
    """Unban an IP address (shorthand unban action for !jailer)"""
    data = subprocess.check_output(["sudo", "fail2ban-client", "set", jail, "unbanip", ip])

    message = "**" + ip + "** has been unbanned, please run `!iptables` to confirm rules"

    await ctx.send(message)


bot.run(TOKEN)
