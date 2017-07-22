import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import aiohttp


class Animals():
    def __init__(self, bot):
        self.bot = bot

    #random neko picture
    @commands.command()
    @commands.cooldown(3, 3, BucketType.user)
    async def cat(self):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('http://random.cat/meow') as r:
                res = await r.json()
                await self.bot.say(res['file'])

    #random doggo picture
    @commands.command()
    @commands.cooldown(3, 3, BucketType.user)
    async def dog(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as cs:
            async with cs.get('https://random.dog/woof.json') as r:
                res = await r.json()
                await self.bot.say(res['url'])

def setup(bot):
    bot.add_cog(Animals(bot))