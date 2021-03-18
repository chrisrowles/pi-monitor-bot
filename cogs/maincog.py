import asyncio
import discord
from discord.ext import commands, tasks
import requests

class MainCog(commands.Cog):
    def __init__(self, bot, url):
        self.index = 0
        self.bot = bot
        self.url = url
        self.user = '<@710218699356766299>' # me 
        self.channel = None
        self.printer.start()


    def cog_unload(self):
        self.printer.cancel()


    @tasks.loop(seconds=1800)
    async def printer(self):
        self.channel = self.bot.get_channel(821440456788541522)

        if self.channel is not None:
            response = requests.get(self.url + 'system/')
            system = response.json()
            data = system['data']

            if len(data['processes']) > 0:
                await self.top(data['processes'][0])
                await asyncio.sleep(5)

            await self.sys(data)


    async def top(self, process):
        message = "Top process is " + process['name'].capitalize() + ' - ' + str(process['mem']) + 'MiB  - Owned by ' + process['username']

        await self.channel.send(message)


    async def sys(self, data):
        embedlist = discord.Embed(title='System', description='Overview')
        embedlist.add_field(name='Temp', value=str(data['cpu']['temp']) + ' °c')
        embedlist.add_field(name='CPU', value=str(data['cpu']['usage']) + '%')
        embedlist.add_field(name='Memory', value=str(data['mem']['percent']) + '%')

        await self.channel.send(embed=embedlist)


    @printer.before_loop
    async def before_printer(self):
        print('waiting...')
        await self.bot.wait_until_ready()