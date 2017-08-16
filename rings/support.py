#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Support():
    """All the NecroBot support commands are here to help you enjoy your time with NecroBot """
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(pass_context = True)
    @commands.cooldown(1, 10, BucketType.server)
    async def support(self, cont):
        """Invite to the official NecroBot support server. 
        
        {usage}"""
        await self.bot.whisper("**Join our server for support**: <https://discord.gg/sce7jmB>")

    @commands.command(pass_context = True)
    @commands.cooldown(1, 10, BucketType.server)
    async def invite(self, cont):
        """Link to invite NecroBot to the server you want, given you have the right permission level on that server 
        
        {usage}"""
        await self.bot.whisper("**Invite the bot to your server using this link:** <https://discordapp.com/oauth2/authorize?client_id=317619283377258497&scope=bot&permissions=8>")

def setup(bot):
    bot.add_cog(Support(bot))