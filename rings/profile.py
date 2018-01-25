#!/usr/bin/python3.6
import discord
from discord.ext import commands

from simpleeval import simple_eval
import datetime as d
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from PIL import ImageColor 
import os
import aiohttp
import random
import asyncio

#Permissions Names
permsName = ["User","Helper","Moderator","Semi-Admin","Admin","Server Owner","NecroBot Admin","The Bot Smith"]

class Profile():
    def __init__(self, bot):
        self.bot = bot
        self.font20 = ImageFont.truetype("Ringbearer Medium.ttf", 20)
        self.font21 = ImageFont.truetype("Ringbearer Medium.ttf", 21)
        self.font30 = ImageFont.truetype("Ringbearer Medium.ttf", 30)
        self.overlay = Image.open("rings/utils/profile/overlay.png")

    @commands.command()
    async def balance(self, ctx, user : discord.Member = None):
        """Prints the given user's NecroBot balance, if no user is supplied then it will print your own NecroBot balance.
        
        {usage}
        
        __Example__
        `{pre}balance @NecroBot` - prints NecroBot's balance
        `{pre}balance` - prints your own balance"""
        if user is not None:
            await ctx.message.channel.send(":atm: | **"+ str(user.name) +"** has **{:,}** :euro:".format(self.bot.user_data[user.id]["money"]))
        else:
            await ctx.message.channel.send(":atm: | **"+ str(ctx.message.author.name) +"** you have **{:,}** :euro:".format(self.bot.user_data[ctx.message.author.id]["money"]))

    @commands.command(aliases=["daily"])
    async def claim(self, ctx):
        """Adds your daily 200 :euro: to your NecroBot balance. This can be used at anytime once every GMT day.
        
        {usage}"""
        day = str(d.datetime.today().date())
        if day != self.bot.user_data[ctx.message.author.id]["daily"]:
            await ctx.message.channel.send(":m: | You have received your daily **200** :euro:")
            self.bot.user_data[ctx.message.author.id]["money"] += 200
            self.bot.user_data[ctx.message.author.id]["daily"] = day
        else:
            await ctx.message.channel.send(":negative_squared_cross_mark: | You have already claimed your daily today, come back tomorrow.")

    @commands.command()
    async def pay(self, ctx, payee : discord.User, amount : int):
        """Transfers the given amount of money to the given user's NecroBot bank account.

        {usage}

        __Example__
        `{pre}pay @NecroBot 200` - pays NecroBot 200 :euro:"""
        amount = abs(amount)
        payer = ctx.message.author

        msg = await ctx.message.channel.send("Are you sure you want to pay **{}** to user **{}**? Press :white_check_mark: to confirm transaction. Press :negative_squared_cross_mark: to cancel the transaction.".format(amount, payee.display_name))
        await msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        await msg.add_reaction("\N{NEGATIVE SQUARED CROSS MARK}")

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ["\N{WHITE HEAVY CHECK MARK}", "\N{NEGATIVE SQUARED CROSS MARK}"] and msg.id == reaction.message.id

        reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=300)

        if reaction.emoji == "\N{NEGATIVE SQUARED CROSS MARK}":
            await ctx.message.channel.send(":white_check_mark: | **{}** cancelled the transaction.".format(payer.display_name))
        elif reaction.emoji == "\N{WHITE HEAVY CHECK MARK}":
            if self.bot.user_data[payer.id]["money"] < amount:
                await ctx.message.channel.send(":negative_squared_cross_mark: | You don't have enough money")
                await msg.delete()
                return

            await ctx.message.channel.send(":white_check_mark: | **{}** approved the transaction.".format(payer.display_name))
            await payee.send(":money: | **{}** has transferred **{}$** to your profile".format(payer.display_name, amount))
            
            self.bot.user_data[payer.id]["money"] -= amount
            self.bot.user_data[payee.id]["money"] += amount
            
        await msg.delete()


    @commands.command()
    @commands.guild_only()
    async def info(self, ctx, user : discord.Member = None):
        """Returns a rich embed of the given user's info. If no user is provided it will return your own info. **WIP**
        
        {usage}
        
        __Example__
        `{pre}info @NecroBot` - returns the NecroBot info for NecroBot
        `{pre}info` - returns your own NecroBot info"""
        if user is None:
            user = ctx.message.author

        server_id = ctx.message.guild.id
        embed = discord.Embed(title="__**" + user.display_name + "**__", colour=discord.Colour(0x277b0), description="**Title**: " + self.bot.user_data[user.id]["title"])
        embed.set_thumbnail(url=user.avatar_url.replace("webp","jpg"))
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

        embed.add_field(name="**Date Created**", value=user.created_at.strftime("%d - %B - %Y %H:%M"))
        embed.add_field(name="**Date Joined**", value=user.joined_at.strftime("%d - %B - %Y %H:%M"), inline=True)
        embed.add_field(name="**Permission Level", value=self.bot.user_data[user.id]["perms"][ctx.guild.id])

        embed.add_field(name="**User Name**", value=user.name + "#" + user.discriminator)
        embed.add_field(name="**Top Role**", value=user.top_role.name, inline=True)
        embed.add_field(name="Warning List", value=self.bot.user_data[user.id]["warnings"])

        await ctx.message.channel.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def profile(self, ctx, user : discord.Member = None):
        """Shows your profile information in a picture

        {usage}
            
        __Example__
        `{pre}info @NecroBot` - returns the NecroBot info for NecroBot
        `{pre}info` - returns your own NecroBot info"""
        async with ctx.message.channel.typing():

            if user is None:
                user = ctx.message.author

            url = user.avatar_url.replace("webp","jpg")
            async with aiohttp.ClientSession() as cs:
                async with cs.get(url) as r:
                    filename = os.path.basename(url)
                    with open(filename, 'wb') as f_handle:
                        while True:
                            chunk = await r.content.read(1024)
                            if not chunk:
                                break
                            f_handle.write(chunk)
                    await r.release()

            im = Image.open("rings/utils/profile/backgrounds/{}.jpg".format(random.randint(1,139))).resize((1024,512)).crop((59,29,964,482))
            draw = ImageDraw.Draw(im)

            pfp = Image.open(filename).resize((150,150))
            perms_level = Image.open("rings/utils/profile/perms_level/{}.png".format(self.bot.user_data[user.id]["perms"][ctx.message.guild.id])).resize((50,50))

            im.paste(self.overlay, box=(0, 0, 905, 453), mask=self.overlay)
            im.paste(pfp, box=(75, 132, 225, 282))
            im.paste(perms_level, box=(125, 25, 175, 75))


            draw.text((70,85), permsName[self.bot.user_data[user.id]["perms"][ctx.message.guild.id]], (0,0,0), font=self.font20)
            draw.text((260,125), "{:,}$".format(self.bot.user_data[user.id]["money"]), (0,0,0), font=self.font30)
            draw.text((260,230), "{:,} EXP".format(self.bot.user_data[user.id]["exp"]), (0,0,0), font=self.font30)
            draw.text((43,313), user.display_name, (0,0,0), font=self.font21)
            draw.text((43,356), self.bot.user_data[user.id]["title"], (0,0,0), font=self.font21)
            draw.line((52,346,468,346),fill=(0,0,0), width=2)

            im.save('{}.png'.format(user.id))
            ifile = discord.File('{}.png'.format(user.id))
            await ctx.message.channel.send(file=ifile)
            os.remove("{}.png".format(user.id))
            os.remove(filename)

    @commands.command()
    async def settitle(self, ctx, *, text : str = ""):
        """Sets your NecroBot title to [text]. If no text is provided it will reset it. Limited to max 25 characters.
        
        {usage}
        
        __Example__
        `{pre}settitle Cool Dood` - set your title to 'Cool Dood'
        `{pre}settitle` - resets your title"""
        if text == "":
            await ctx.message.channel.send(":white_check_mark: | Your title has been reset")
        elif len(text) <= 25:
            await ctx.message.channel.send(":white_check_mark: | Great, your title is now **" + text + "**")
        else:
            await ctx.message.channel.send(":negative_squared_cross_mark: | You have gone over the 25 character limit, your title wasn't set.")
            return

        self.bot.user_data[ctx.message.author.id]["title"] = text

def setup(bot):
    bot.add_cog(Profile(bot))