#!/usr/bin/python3.6
import discord
from discord.ext import commands
import time
from datetime import timedelta


class Support():
    """All the NecroBot support commands are here to help you enjoy your time with NecroBot """
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def support(self, ctx):
        """Invite to the official NecroBot support server. 
        
        {usage}"""
        await ctx.channel.send("**Join our server for support**: https://discord.gg/Ape8bZt")

    @commands.command()
    async def invite(self, ctx):
        """Link to invite NecroBot to the server you want, given you have the right permission level on that server 
        
        {usage}"""
        await ctx.channel.send("**Invite the bot to your server using this link:** <https://discordapp.com/oauth2/authorize?client_id=317619283377258497&scope=bot&permissions=134737095>")

    @commands.command()
    async def about(self, ctx):
        """Creates a rich embed of the bot's details.

        {usage}"""
        bot_desc = "Hello! :wave: I'm NecroBot, a moderation bot with many commands for a wide variety of server and a high modularity which means you can enable/disable just about every part of me as you wish."
        embed = discord.Embed(title="__**NecroBot**__", colour=discord.Colour(0x277b0), description=bot_desc)
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")
        embed.add_field(name="Version", value=self.bot.version)
        embed.add_field(name="About", value="I'm currently in {} guilds and I can see {} members. I was created using Python and the d.py library. ".format(len(list(self.bot.guilds)), len(list(self.bot.users))))
        uptime = str(timedelta(seconds=time.time() - self.bot.uptime_start)).partition(".")[0].replace(":", "{}")
        embed.add_field(name="Uptime", value=uptime.format("hours, ", "minutes and ") + "seconds")
        await ctx.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Support(bot))