#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Hunger():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True)
    async def fight(self, *tributes : discord.Member):


def setup(bot):
    bot.add_cog(Hunger(bot))