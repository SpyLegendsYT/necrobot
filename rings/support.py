#!/usr/bin/python3.6
import discord
from discord.ext import commands

from rings.utils.utils import has_perms, react_menu

import ast
import time
from datetime import timedelta


class Support():
    """All the NecroBot support commands are here to help you enjoy your time with NecroBot """
    def __init__(self, bot):
        self.bot = bot
        self.base_d = {"author": {"name": "Necrobot's Anchorman", "url": "https://discord.gg/Ape8bZt", "icon_url": "https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128"}, "color": 161712, "type": "rich"}

        
    @commands.command(aliases=["support"])
    async def about(self, ctx):
        """Creates a rich embed of the bot's details Also contains link for inviting and support server.

        {usage}"""

        bot_desc = "Hello! :wave: I'm NecroBot, a moderation bot with many commands for a wide variety of server and a high modularity which means you can enable/disable just about every part of me as you wish."
        embed = discord.Embed(title="__**NecroBot**__", colour=discord.Colour(0x277b0), description=bot_desc)
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")
        embed.add_field(name="Version", value=self.bot.version)
        embed.add_field(name="About", value=f"I'm currently in {len(list(self.bot.guilds))} guilds and I can see {len(list(self.bot.users))} members. I was created using Python and the d.py library. ")
        uptime = str(timedelta(seconds=time.time() - self.bot.uptime_start)).partition(".")[0].replace(":", "{}")
        embed.add_field(name="Uptime", value=uptime.format("hours, ", "minutes and ") + "seconds")
        embed.add_field(name="Links", value=f"[Invite bot to your server]({discord.utils.oauth_url(self.bot.user.id, discord.Permissions(permissions=403172599))}) - [Get help with the bot](https://discord.gg/Ape8bZt)", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def report(self, ctx, *, message):
        """Report a bug with the bot or send a suggestion . Please be a specific as you can. Any abusive use will result in
        blacklisting.

        {usage}

        __Examples__
        `{pre}report profile while using profile the picture came out wrong, it was all distorted and stuff and my data on it was wrong.` - report 
        a bug for `profile`
        `{pre}report settings while using the sub-command mute it told me there was no such role when there is indeed` - report a bug for 
        `settings`"""

        embed = discord.Embed(title=":bulb: A report has just came in :bulb:", description=message, colour=discord.Colour(0x277b0))
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Helpful Info", value=f"User: {ctx.author.mention} \nServer: {ctx.guild.name} \nServer ID: {ctx.guild.id}")
        await self.bot.get_channel(398894681901236236).send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def news(self, ctx, index : int = 1):
        """See the latest necrobot news

        {usage}

        __Examples__
        `{pre}news` - get the news starting from the latest
        `{pre}news 4` - get the news starting from the fourth item
        `{pre}news 1` - get the news starting from the first item"""
        news = self.bot.settings["news"]

        if len(news) == 0:
            await ctx.send(":negative_squared_cross_mark: | No news available")
            return

        if not 0 < index <= len(news):
            await ctx.send(f":negative_squared_cross_mark: | Not a valid index, pick a number from 1 to {len(news)}")
            return
        
        def _embed_generator(page):
            return discord.Embed.from_data(news[page])

        await react_menu(self.bot, ctx, len(news) - 1, _embed_generator, index-1)

    @news.command("add")
    @has_perms(6)
    async def news_add(self, ctx, *, news : str):
        """Add a new news item

        {usage}"""
        try:
            news = ast.literal_eval(news)
        except ValueError as e:
            await ctx.send(str(e))
            return

        news_e = {**news , **self.base_d}
        embed = discord.Embed.from_data(news_e)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("\N{NEGATIVE SQUARED CROSS MARK}")
        await msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")

        def check(reaction, user):
            return user == ctx.message.author and reaction.emoji in ["\N{NEGATIVE SQUARED CROSS MARK}", "\N{WHITE HEAVY CHECK MARK}"] and msg.id == reaction.message.id

        reaction, user = await self.bot.wait_for("reaction_add", check=check)

        if reaction.emoji == "\N{WHITE HEAVY CHECK MARK}":
            self.bot.settings["news"] = [news, *self.bot.settings["news"]]
            await ctx.send(f":white_check_mark: | Added **{news['title']}** news")
            channel = self.bot.get_channel(436595183010709514)
            await channel.send(embed=embed)

        await msg.clear_reactions()


    @news.command("delete")
    @has_perms(6)
    async def news_delete(self, ctx, index : int):
        """Remove a news item

        {usage}"""
        if len(self.bot.settings["news"]) == 0:
            await ctx.send(":negative_squared_cross_mark: | No news available")
            return

        if not 0 <= index < len(self.bot.settings["news"]):
            await ctx.send(f":negative_squared_cross_mark: | Not a valid index, pick a number between 1 and {len(self.bot.settings['news'])}")
            return

        news = self.bot.settings["news"].pop(index)
        await ctx.send(f":white_check_mark: | News **{news['title']}** removed")

    @news.command("raw")
    @has_perms(6)
    async def news_raw(self, ctx, index : int):
        """Get the raw dict form of the news

        {usage}"""
        await ctx.send(self.bot.settings["news"][index])

    @news.command("template")
    @has_perms(6)
    async def news_template(self, ctx):
        """Prints the template for news

        {usage}"""
        await ctx.send('{ "fields": [{"inline": False, "name": "Why is good 1", "value": "Because"}], "description": "", "title": ""}')

    @commands.command()
    async def tutorial(self, ctx):
        """Sends an embed with helpful information on Necrobot's features, be warned, it is quite a dense text blob

        {usage}"""
        try:
            await ctx.author.send(embed=self.bot.tutorial_e)
        except discord.errors.Forbidden:
            await ctx.send(":negative_squared_cross_mark: | Looks like you have private messages disabled")

def setup(bot):
    bot.add_cog(Support(bot))