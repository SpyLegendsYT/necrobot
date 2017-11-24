#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import aiohttp

class Animals():
    """Show pictures of cute animals us the power of the internet."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(3, 3, BucketType.user)
    async def cat(self, ctx):
        """Posts a random cat picture from random.cat
        
        {usage}"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('http://random.cat/meow') as r:
                res = await r.json()
                await ctx.channel.send(res['file'])

    @commands.command()
    @commands.cooldown(3, 3, BucketType.user)
    async def dog(self, ctx):
        """Posts a random dog picture from random.dog 
        
        {usage}"""
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as cs:
            async with cs.get('https://random.dog/woof.json') as r:
                res = await r.json()
                await ctx.channel.send(res['url'])

def setup(bot):
    bot.add_cog(Animals(bot))