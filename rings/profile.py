#!/usr/bin/python3.6
import discord
from discord.ext import commands

from simpleeval import simple_eval
import datetime as d
import time as t
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from PIL import ImageColor 
import os
import random
import asyncio
from io import BytesIO

#/usr/share/fonts/

#Permissions Names
permsName = ["User","Helper","Moderator","Semi-Admin","Admin","Server Owner","NecroBot Admin","The Bot Smith"]

class Profile():
    def __init__(self, bot):
        self.bot = bot
        self.font20 = ImageFont.truetype("Ringbearer Medium.ttf", 20)
        self.font21 = ImageFont.truetype("Ringbearer Medium.ttf", 21)
        self.font30 = ImageFont.truetype("Ringbearer Medium.ttf", 30)
        self.overlay = Image.open("rings/utils/profile/overlay.png").convert("RGBA")
        self.badges_d = {
            "necrobot": 1000000, "glorfindel" : 1000000, "necro" : 10000000,
            "edain": 5000, "aotr": 5000,
            "rohan": 500, "angmar": 500, "dwarves": 500, "goblins": 500, "gondor": 500, "imladris": 500, "isengard": 500, "lorien": 500, "mordor": 500
        }
        self.badges_coords = [(516, 261, 598, 343), (609, 261, 691, 343), (703, 261, 785, 343), (796, 261, 878, 343), (516, 350, 598, 432), (609, 350, 691, 432), (704, 350, 786, 432), (796, 350, 878, 432)]
        
    def midnight(self):
        """Get the number of seconds until midnight."""
        tomorrow = d.datetime.now() + d.timedelta(1)
        midnight = d.datetime(year=tomorrow.year, month=tomorrow.month, 
                            day=tomorrow.day, hour=0, minute=0, second=0)
        return (midnight - d.datetime.now()).seconds

    @commands.command()
    async def balance(self, ctx, user : discord.Member = None):
        """Prints the given user's NecroBot balance, if no user is supplied then it will print your own NecroBot balance.
        
        {usage}
        
        __Example__
        `{pre}balance @NecroBot` - prints NecroBot's balance
        `{pre}balance` - prints your own balance"""
        if user is not None:
            await ctx.send(f":atm: | **{user.name}** has **{'{:,}'.format(self.bot.user_data[user.id]['money'])}** :euro:")
        else:
            await ctx.send(f":atm: | **{ctx.author.name}** you have **{'{:,}'.format(self.bot.user_data[ctx.author.id]['money'])}** :euro:")

    @commands.command(name="daily")
    async def claim(self, ctx):
        """Adds your daily 200 :euro: to your NecroBot balance. This can be used at anytime once every GMT day.
        
        {usage}"""
        day = str(d.datetime.today().date())
        if day != self.bot.user_data[ctx.author.id]["daily"]:
            await ctx.send(":m: | You have received your daily **200** :euro:")
            self.bot.user_data[ctx.author.id]["money"] += 200
            await self.bot.query_executer("UPDATE necrobot.Users SET necroins = $1 WHERE user_id = $2",self.bot.user_data[ctx.author.id]["money"], ctx.author.id)
            self.bot.user_data[ctx.author.id]["daily"] = day
            await self.bot.query_executer("UPDATE necrobot.Users SET daily=$1 WHERE user_id = $2;", day, ctx.author.id)
        else:
            timer = str(d.timedelta(seconds=self.midnight())).partition(".")[0].replace(":", "{}")
            timer = timer.format("hours, ", "minutes and ") + "seconds"
            await ctx.send(f":negative_squared_cross_mark: | You have already claimed your daily today, you can claim your daily again in **{timer}**")

    @commands.command()
    async def pay(self, ctx, payee : discord.User, amount : int):
        """Transfers the given amount of money to the given user's NecroBot bank account.

        {usage}

        __Example__
        `{pre}pay @NecroBot 200` - pays NecroBot 200 :euro:"""
        amount = abs(amount)
        payer = ctx.author

        msg = await ctx.send(f"Are you sure you want to pay **{amount}** to user **{payee.display_name}**? Press :white_check_mark: to confirm transaction. Press :negative_squared_cross_mark: to cancel the transaction.")
        await msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        await msg.add_reaction("\N{NEGATIVE SQUARED CROSS MARK}")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["\N{WHITE HEAVY CHECK MARK}", "\N{NEGATIVE SQUARED CROSS MARK}"] and msg.id == reaction.message.id

        reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=300)

        if reaction.emoji == "\N{NEGATIVE SQUARED CROSS MARK}":
            await ctx.send(f":white_check_mark: | **{payer.display_name}** cancelled the transaction.")
        elif reaction.emoji == "\N{WHITE HEAVY CHECK MARK}":
            if self.bot.user_data[payer.id]["money"] < amount:
                await ctx.send(":negative_squared_cross_mark: | You don't have enough money")
                await msg.delete()
                return

            await ctx.send(f":white_check_mark: | **{payer.display_name}** approved the transaction.")
            await payee.send(f":euro: | **{payer.display_name}** has transferred **{amount}$** to your profile")
            
            self.bot.user_data[payer.id]["money"] -= amount
            await self.bot.query_executer("UPDATE necrobot.Users SET necroins = $1 WHERE user_id = $2",self.bot.user_data[payer.id]["money"], payer.id)
            self.bot.user_data[payee.id]["money"] += amount
            await self.bot.query_executer("UPDATE necrobot.Users SET necroins = $1 WHERE user_id = $2",self.bot.user_data[payee.id]["money"], payee.id)
            
        await msg.delete()


    @commands.command()
    @commands.guild_only()
    async def info(self, ctx, user : discord.Member = None):
        """Returns a rich embed of the given user's info. If no user is provided it will return your own info.
        
        {usage}
        
        __Example__
        `{pre}info @NecroBot` - returns the NecroBot info for NecroBot
        `{pre}info` - returns your own NecroBot info"""
        if not user:
            user = ctx.author

        server_id = ctx.guild.id
        embed = discord.Embed(title="__" + user.display_name + "__", colour=discord.Colour(0x277b0), description="**Title**: " + self.bot.user_data[user.id]["title"])
        embed.set_thumbnail(url=user.avatar_url.replace("webp","jpg"))
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

        embed.add_field(name="Date Created", value=user.created_at.strftime("%d - %B - %Y %H:%M"))
        embed.add_field(name="Date Joined", value=user.joined_at.strftime("%d - %B - %Y %H:%M"), inline=True)
        embed.add_field(name="Permission Level", value=self.bot.user_data[user.id]["perms"][ctx.guild.id])

        embed.add_field(name="User Name", value=user.name + "#" + user.discriminator)
        embed.add_field(name="Top Role", value=user.top_role.name, inline=True)
        embed.add_field(name="Warning List", value=self.bot.user_data[user.id]["warnings"][ctx.guild.id])

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def profile(self, ctx, *, user : discord.Member = None):
        """Shows your profile information in a picture

        {usage}
            
        __Example__
        `{pre}info @NecroBot` - returns the NecroBot info for NecroBot
        `{pre}info` - returns your own NecroBot info"""
        async with ctx.channel.typing():

            if not user:
                user = ctx.author

            url = user.avatar_url_as(format="png").replace("?size=1024", "")
            async with self.bot.session.get(url) as r:
                image_bytes = await r.read()

            im = Image.open(f"rings/utils/profile/backgrounds/{random.randint(1,147)}.jpg").resize((1024,512)).crop((60,29,964,482)).convert("RGBA")
            draw = ImageDraw.Draw(im)

            pfp = Image.open(BytesIO(image_bytes)).resize((150,150)).convert("RGBA")
            perms_level = Image.open(f"rings/utils/profile/perms_level/{self.bot.user_data[user.id]['perms'][ctx.guild.id]}.png") .resize((50,50)).convert("RGBA")

            im.paste(self.overlay, box=(0, 0, 905, 453), mask=self.overlay)
            im.paste(pfp, box=(75, 132, 225, 282), mask=pfp)
            im.paste(perms_level, box=(125, 25, 175, 75))

            for spot in self.bot.user_data[user.id]["places"]:
                badge = self.bot.user_data[user.id]["places"][spot]
                if badge != "":
                    badge_img = Image.open(f"rings/utils/profile/badges/{badge}.png").convert("RGBA")
                    index = int(spot) - 1
                    im.paste(badge_img, box=self.badges_coords[index], mask=badge_img)


            draw.text((70,85), permsName[self.bot.user_data[user.id]["perms"][ctx.guild.id]], (0,0,0), font=self.font20)
            draw.text((260,125), "{:,}$".format(self.bot.user_data[user.id]["money"]), (0,0,0), font=self.font30)
            draw.text((260,230), "{:,} EXP".format(self.bot.user_data[user.id]["exp"]), (0,0,0), font=self.font30)
            draw.text((43,313), user.display_name, (0,0,0), font=self.font21)
            draw.text((43,356), self.bot.user_data[user.id]["title"], (0,0,0), font=self.font21)
            draw.line((52,346,468,346),fill=(0,0,0), width=2)

            
            output_buffer = BytesIO()
            im.save(output_buffer, "png")
            output_buffer.seek(0)
            ifile = discord.File(output_buffer, filename=f"{user.id}.png")
            await ctx.send(file=ifile)

    @commands.command()
    async def settitle(self, ctx, *, text : str = ""):
        """Sets your NecroBot title to [text]. If no text is provided it will reset it. Limited to max 32 characters.
        
        {usage}
        
        __Example__
        `{pre}settitle Cool Dood` - set your title to 'Cool Dood'
        `{pre}settitle` - resets your title"""
        if text == "":
            await ctx.send(":white_check_mark: | Your title has been reset")
        elif len(text) <= 32:
            await ctx.send(f":white_check_mark: | Great, your title is now **{text}**")
        else:
            await ctx.send(f":negative_squared_cross_mark: | You have gone over the 32 character limit, your title wasn't set. ({len(text)}/32)")
            return

        self.bot.user_data[ctx.author.id]["title"] = text
        await self.bot.query_executer("UPDATE necrobot.Users SET title=$1 WHERE user_id = $2;", text, ctx.author.id)

    @commands.group(invoke_without_command=True, aliases=["badge"])
    async def badges(self, ctx):
        """The badge system allows you to buy badges and place them on profiles. Show the world what your favorite
        games/movies/books/things are. You can see all the badges here: <https://github.com/ClementJ18/necrobot#badges>

        {usage}

        __Examples__
        `{pre}badges` - lists your badges and a link to the list of all badges
        `{pre}badges buy edain` - buy the edain badge, price will appear once you run the command
        `{pre}badges place` - open the menu to reset the badge on a specific grid location
        `{pre}badges place edain` - open the menu to place the edain badge on a specific grid location
        `{pre}badges buy` - sends the link to view the rest of the badges"""
        await ctx.send(f"You have the following badges: {' - '.join(self.bot.user_data[ctx.author.id]['badges'])}\nSee more here: <https://github.com/ClementJ18/necrobot#badges>")

    @badges.command("place")
    async def badges_place(self, ctx, badge : str = ""):
        """Opens the grid menu to allow you to place a badge or reset a badge. Simply supply a badge name to the command to
        place a badge or simply call the command with no bagde name to reset the grid location.

        {usage}

        __Examples__
        `{pre}badges place` - open the menu to reset the badge on a specific grid location
        `{pre}badges place edain` - open the menu to place the edain badge on a specific grid location"""
        badge = badge.lower()
        if badge not in self.bot.user_data[ctx.author.id]["badges"] and badge != "":
            await ctx.send(":negative_squared_cross_mark: | You do not posses this badge")
            return

        def check(message):
            if ctx.author.id != message.author.id:
                return False

            if message.content == "exit":
                return True

            if message.content.isdigit():
                return int(message.content) > 0 and int(message.content) < 9


        msg = await ctx.send("Where would you like to place the badge on your badge board? Enter the grid number of where you would like to place the badge. Or type `exit` to exit the menu.\n```py\n[1] [2] [3] [4]\n[5] [6] [7] [8]\n```")
        
        try:
            reply = await self.bot.wait_for("message", check=check, timeout=300)
        except asyncio.TimeoutError as e:
            await msg.delete()
            return

        if reply.content == "exit":
            await msg.delete()
            return
            
        spot = reply.content
        self.bot.user_data[ctx.author.id]["places"][spot] = badge
        await self.bot.query_executer("UPDATE necrobot.Badges SET badge = $1 WHERE user_id = $2 AND place = $3", badge, ctx.author.id, int(spot))

        if badge == "":
            await ctx.send(f":white_check_mark: | The badge for position **{spot}** has been reset")
        else:
            await ctx.send(f":white_check_mark: | Placed badge **{badge}** on position **{spot}**")

    @badges.command("buy")
    async def badges_buy(self, ctx, badge : str = ""):
        """Allows to buy the given badge or sends a link to access the list of all possible badges. That link can be used
        to preview the badges.

        {usage}

        __Examples__
        `{pre}badges buy edain` - buy the edain badge, price will appear once you run the command
        `{pre}badges buy` - sends the link to view the rest of the badges"""
        badge = badge.lower()
        if badge == "":
            await ctx.send("Click the link to see a list of badges: <https://github.com/ClementJ18/necrobot#badges>\nWant to suggest a new badge? Use n!report and include the link of an image with a 1:1 ratio.")
            return

        if badge not in self.badges_d:
            await ctx.send(":negative_squared_cross_mark: | There is no such badge")
            return

        if badge in self.bot.user_data[ctx.author.id]["badges"]:
            await ctx.send(":negative_squared_cross_mark: | You already posses that badge")
            return

        msg = await ctx.send("Are you sure you want to buy the **{}** badge for **{:,}** Necroins? Press :white_check_mark: to confirm transaction. Press :negative_squared_cross_mark: to cancel the transaction.".format(badge, self.badges_d[badge]))
        await msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        await msg.add_reaction("\N{NEGATIVE SQUARED CROSS MARK}")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["\N{WHITE HEAVY CHECK MARK}", "\N{NEGATIVE SQUARED CROSS MARK}"] and msg.id == reaction.message.id
        
        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=300)
        except asyncio.TimeoutError as e:
            await msg.delete()
            return

        if reaction.emoji == "\N{NEGATIVE SQUARED CROSS MARK}":
            await ctx.send(f":white_check_mark: | **{ctx.author.display_name}** cancelled the transaction.")
        elif reaction.emoji == "\N{WHITE HEAVY CHECK MARK}":
            if self.bot.user_data[ctx.author.id]["money"] < self.badges_d[badge]:
                await ctx.send(":negative_squared_cross_mark: | You don't have enough money")
                await msg.delete()
                return

            self.bot.user_data[ctx.author.id]["money"] -= self.badges_d[badge]
            self.bot.user_data[ctx.author.id]["badges"].append(badge)
            await self.bot.query_executer("UPDATE necrobot.Users SET necroins = $1, badges = $3 WHERE user_id = $2",self.bot.user_data[ctx.author.id]["money"], ctx.author.id, ",".join(self.bot.user_data[ctx.author.id]["badges"]))
            await ctx.send(":white_check_mark: | Badge purchased, you can place it using `n!badges place [badge]`")

            
        await msg.delete()


def setup(bot):
    bot.add_cog(Profile(bot))