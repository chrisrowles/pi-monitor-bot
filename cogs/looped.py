import asyncio
import discord
from discord.ext import commands, tasks
import requests

class SystemReporting(commands.Cog):
    def __init__(self, bot, url, user, channel):
        self.index = 0
        self.bot = bot
        self.url = url
        self.user = user
        self.channel = None
        self.channel_id = channel
        self.system.start()


    def cog_unload(self):
        self.system.cancel()


    @tasks.loop(seconds=30)
    async def system(self):
        self.channel = self.bot.get_channel(self.channel_id)

        if self.channel is not None:
            response = requests.get(self.url + 'system/')
            system = response.json()
            data = system['data']

            if len(data['processes']) > 0:
                await self.top(data['processes'][0])
                await asyncio.sleep(5)

            await self.output(data)


    async def top(self, process):
        message = 'Owner: ' + process['username'] + '\nUsing: ' + str(process['mem']) + ' mib'

        embedlist = discord.Embed(title='Top Process', color=discord.Color.purple())
        embedlist.add_field(name=process['name'].capitalize(), value=message)

        await self.channel.send(embed=embedlist)


    async def output(self, data):
        temp = data['cpu']['temp']
        if (temp <= 50):
            color = discord.Color.green()
        elif (temp > 50):
            color = discord.Color.red()
        else:
            color = discord.Color.dark_red()

        embedlist = discord.Embed(title='System', description='Overview', color=color)
        embedlist.add_field(name='Temp', value=str(temp) + ' °c')
        embedlist.add_field(name='CPU', value=str(data['cpu']['usage']) + '%')
        embedlist.add_field(name='Memory', value=str(data['mem']['percent']) + '%')

        await self.channel.send(embed=embedlist)


    @system.before_loop
    async def before_system(self):
        await self.bot.wait_until_ready()