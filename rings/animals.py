#!/usr/bin/python3.6
import discord
from discord.ext import commands
import aiohttp
from discord.ext.commands.cooldowns import BucketType
import random

class Animals():
    """Show pictures of cute animals using the power of the internet."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(3, 5, BucketType.channel)
    async def cat(self, ctx):
        """Posts a random cat picture from random.cat
        
        {usage}"""
        async with self.bot.session.get('http://aws.random.cat/meow') as r:
            try:
                res = await r.json()
                await ctx.send(embed=discord.Embed().set_image(url=res['file']))
                self.bot.cat_cache.append(res["file"])
            except aiohttp.ClientResponseError:
                if len(self.bot.cat_cache) > 0:
                    await ctx.send("API overloading, have a cached picture instead.", embed=discord.Embed(colour=discord.Colour(0x277b0)).set_image(url=random.choice(self.bot.cat_cache)))
                else:
                    await ctx.send(":negative_squared_cross_mark: | API overloading and cache empty, looks like you'll have to wait for now.")

    @commands.command()
    async def dog(self, ctx):
        """Posts a random dog picture from random.dog 
        
        {usage}"""
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as cs:
            async with cs.get('https://random.dog/woof.json') as r:
                res = await r.json()
                await ctx.send(embed=discord.Embed().set_image(url=res['url']))

def setup(bot):
    bot.add_cog(Animals(bot))