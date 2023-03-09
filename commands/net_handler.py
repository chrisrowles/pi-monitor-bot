from discord import Embed
from discord.ext import commands
import subprocess


class NetHandler(commands.Cog, name="Network Commands"):
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

        embedlist = Embed(title='Network', description='network information')
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
