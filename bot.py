import asyncio
from cogs.maincog import MainCog
import discord
from discord.ext import commands, tasks
import json
import os
import requests
import settings
from settings import URL, TOKEN, USER_ID, CHANNEL_ID, BACKUP_CHANNEL_ID
import subprocess
import tabulate

description = '''System Monitor'''
bot = commands.Bot(command_prefix='!', description=description)
bot.add_cog(MainCog(bot=bot, url=URL, user=USER_ID, channel=CHANNEL_ID))

# TODO fix this shit-tip file
#   Fix security vulnerabilities (as much as you can when building something like this anyways..)
#   Fix structure
#   Fix consistency
#   
#   Integrate sqlite for storing netauth tokens n shit

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def good(ctx, arg):
    if arg == "bot":
        message = "🤖"
    else:
        message = "👀"

    await ctx.send(message)


@bot.command()
async def test(ctx):
    await ctx.send('%s Test Success' % USER_ID)


@bot.command()
async def backup(ctx):
    await ctx.send('%s Triggering backup process now. Check #backup for status.' % USER_ID)

    subprocess.check_output(["sudo", "bash", "/home/pi/pimonitor_bot/cron/backup.sh"])


@bot.command()
async def uptime(ctx):
    """Fetch network uptime"""
    response = requests.get(URL + 'system/')
    system = response.json()
    uptime = system['data']['platform']['uptime']

    message = "Network has been up for " + system['data']['platform']['uptime']

    await ctx.send(message)


@bot.command()
async def top(ctx):
    """Fetch top process consuming most memory"""
    response = requests.get(URL + 'system/')
    system = response.json()
    process = system['data']['processes'][0]

    message = "Top process is " + process['name'].capitalize() + ' - ' + str(process['mem']) + 'MiB  - Owned by ' + process['username']

    await ctx.send(message)


@bot.command()
async def netauth(ctx, arg):
    """Fetch top process consuming most memory"""
    token = str(arg)
    response = requests.get(URL + 'network/wifi', headers={'Authorization': token})
    network = response.json()
    data = json.dumps(network['data'], indent=2)

    await ctx.send('```\n' + data + '\n```')

@bot.command()
async def sys(ctx, metric):
    """Fetch system metrics for cpu, mem or disk"""
    response = requests.get(URL + 'system/')
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
async def supervisor(ctx):
    """Get supervisor status"""
    # Obviously supervisor is running otherwise the bot wouldn't respond...
    # probably should rename to make it clearer I want a list of what's running.
    try:
        data = subprocess.check_output(['supervisorctl', 'status'])
        message = "supervisor status:\n**" + data.decode("utf-8") + "**"
    except:
        message = "supervisor status:\n**not running.**"

    await ctx.send(message)

@bot.command()
async def iptables(ctx):
    """Fetch active iptables rules"""
    data = subprocess.check_output(["sudo", "iptables", "-L"])

    await ctx.send('```\n' + data.decode("utf-8") + '\n```')


@bot.command()
async def ban(ctx, jail, ip):
    """Ban an IP address"""
    data = subprocess.check_output(["sudo", "fail2ban-client", "set", jail, "banip", ip])

    message = "**" + ip + "** has been banned, please check #jail for confirmation."

    await ctx.send(message)


@bot.command()
async def unban(ctx, jail, ip):
    """Unban an IP address"""
    data = subprocess.check_output(["sudo", "fail2ban-client", "set", jail, "unbanip", ip])

    message = "**" + ip + "** has been unbanned, please check #jail for confirmation."

    await ctx.send(message)


bot.run(TOKEN)
