#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType, Cooldown, CooldownMapping
from rings.utils.utils import has_perms
import asyncio

# bypassablecooldown = Cooldown(1, 1800, BucketType.user)
# bypassablecooldownmapping = CooldownMapping(bypassablecooldown)

# def bypassablecooldown(ctx):
#     if bypassablecooldownmapping.get


class Waifu():
    """This is based off the Nadeko bot's waifu module. The reason I copied it was to be able to run it on the same
    system as this bot and to be able to modify and customize. For the newcomers, the waifu system is kind of like a
    wedding system, where users can \"marry \" each other. Just don't take it too seriously and have fun """
    def __init__(self, bot):
        self.bot = bot
        self.gifts_e = {"cookie" : ":cookie:", "rose": ":rose:", "loveletter":":love_letter:", "chocolate":":chocolate_bar:", "rice":":rice:", "movieticket":":tickets:", "book":":notebook_with_decorative_cover:", "lipstick":":lipstick:", "laptop":":computer:", "violin":":violin:", "ring":":ring:", "helicopter":":helicopter:"}
        self.gifts_p = {"cookie" : 10, "rose": 50, "loveletter":100, "chocolate":200, "rice":400, "movieticket":800, "book":1500, "lipstick":3000, "laptop":5000, "violin":7500, "ring":10000, "helicopter":20000}

    @commands.command()
    async def trade(self, ctx, coins : int):
        """Trades your hard earned Necroins for :cherry_blossom: with a 1:1 exchange ration.

        {usage}

        __Examples__
        `{pre}trade 400` - trade 400 Necroins for 400 :cherry_blossom:
        """

        coins = abs(coins)

        if self.bot.user_data[ctx.author.id]["money"] < coins:
            await ctx.send(":negative_squared_cross_mark: | You don't have enough Necroins")
            return

        self.bot.user_data[ctx.author.id]["money"] -= coins
        self.bot.user_data[ctx.author.id][ctx.guild.id]["flowers"] += coins
        await ctx.send(":white_check_mark: | You exchanged **{}** Necroins for **{}** :cherry_blossom: on this server".format(coins, coins))

    @commands.command(name="$")
    async def balance(self, ctx, user: discord.Member = None):
        """Check your or a user's balance of :cherry_blossom:

        {usage}

        __Examples__
        `{pre}$` - check you own balance
        `{pre}$ @Thot` - check the user Thot's balance
        """

        if user is None:
            user = ctx.author

        embed = discord.Embed(color=discord.Colour(0x277b0), description="{} has **{}** :cherry_blossom:".format(user.name, self.bot.user_data[user.id][ctx.guild.id]["flowers"]))
        await ctx.send(embed=embed)

    @commands.command()
    async def waifuinfo(self, ctx, user : discord.Member = None):
        """Display your or a user's waifu info.

        {usage}

        __Examples__
        `{pre}waifuinfo` - check your own waifu info
        `{pre}waifuinfo @AnotherThot` - check user AnotherThot's waifu info"""
        if user is None:
            user = ctx.author

        count = self.bot.user_data[user.id][ctx.guild.id]["heart-changes"]
        if count < 1:
            title = "Pure"
        elif count < 2:
            title = "Faithful"
        elif count < 4:
            title = "Defiled"
        elif count < 5:
            title = "Cheater"
        elif count < 6:
            title = "Tainted"
        elif count < 11:
            title = "Corrupted"
        elif count < 13:
            title = "Lewd"
        elif count < 15:
            title = "Sloot"
        elif count < 17:
            title = "Depraved"
        else:
            title = "Harlot"

        count = len(self.bot.user_data[user.id][ctx.guild.id]["waifus"])
        if count == 0:
            title_a = "Lonely"
        elif count == 1:
            title_a = "Devoted"
        elif count < 4:
            title_a = "Rookie"
        elif count < 6:
            title_a = "Schemer"
        elif count < 8:
            title_a = "Dilettante"
        elif count < 10:
            title_a = "Intermediate"
        elif count < 12:
            title_a = "Seducer"
        elif count < 15:
            title_a = "Expert"
        elif count < 17:
            title_a = "Veteran"
        elif count < 25:
            title_a = "Incubis"
        elif count < 50:
            title_a = "Harem King"
        else:
            title_a = "Harem God"


        embed = discord.Embed(color=discord.Colour(0x277b0), title="Waifu {} - {}".format(user.name, title_a))
        embed.add_field(name="Price", value=self.bot.user_data[user.id][ctx.guild.id]["waifu-value"])
        embed.add_field(name="Claimed by", value=self.bot.get_user(self.bot.user_data[user.id][ctx.guild.id]["waifu-claimer"]).name if self.bot.user_data[user.id][ctx.guild.id]["waifu-claimer"] != "" else "None")
        embed.add_field(name="Likes", value=self.bot.get_user(self.bot.user_data[user.id][ctx.guild.id]["affinity"]).name if self.bot.user_data[user.id][ctx.guild.id]["affinity"] != "" else "None")
        embed.add_field(name="Changes of heart", value="{} the {}".format(self.bot.user_data[user.id][ctx.guild.id]["heart-changes"], title))
        embed.add_field(name="Divorces", value=self.bot.user_data[user.id][ctx.guild.id]["divorces"])
        gifts = self.bot.user_data[user.id][ctx.guild.id]["gifts"]
        gift_str = "\n".join(["{}x{}".format(self.gifts_e[x.lower()], gifts[x]) for x in gifts if gifts[x] > 0])
        embed.add_field(name="Gifts", value=gift_str if gift_str != "" else "None", inline=False)
        waifus = "\n".join([self.bot.get_user(x).name for x in self.bot.user_data[user.id][ctx.guild.id]["waifus"]])
        embed.add_field(name="Waifus ({})".format(len(self.bot.user_data[user.id][ctx.guild.id]["waifus"])), value=waifus if waifus != "" else "None", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def gifts(self, ctx):
        """Displays the list of gifts that can be gifted.

        {usage}"""

        embed = discord.Embed(color=discord.Colour(0x277b0), title="Waifu gift shop")
        for gift in self.gifts_e:
            embed.add_field(name="{} {}".format(self.gifts_e[gift], gift.title()), value=self.gifts_p[gift])

        await ctx.send(embed=embed)

    @commands.command()
    async def gift(self, ctx, choice, member : discord.Member):
        """Gifts an item from the gift list (`{pre}gifts` to display). The gift increases the value of the waifu by
        a different amount depending on whether or not their affinity is set to the gifter.

        {usage}

        __EXamples__
        `{pre}gift Chocolate @ThirdThot` - gifts a chocolate to the user ThirdThot
        """
        choice = choice.lower()
        if choice not in self.gifts_e:
            await ctx.send(":negative_squared_cross_mark: | No such gift")
            return

        price = self.gifts_p[choice]
        emoji = self.gifts_e[choice]

        if self.bot.user_data[ctx.author.id][ctx.guild.id]["flowers"] < price:
            await ctx.send(":negative_squared_cross_mark: | Not enough :cherry_blossom:")
            return

        self.bot.user_data[ctx.author.id][ctx.guild.id]["flowers"] -= price
        self.bot.user_data[member.id][ctx.guild.id]["waifu-value"] += price if self.bot.user_data[member.id][ctx.guild.id]["affinity"] == ctx.author.id else price//2
        self.bot.user_data[member.id][ctx.guild.id]["gifts"][choice.title()] += 1 

        embed = discord.Embed(color=discord.Colour(0x277b0), title=" ", description="{} gifted **{}** {} to {}".format(ctx.author.display_name, choice, emoji, member.display_name))

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 1800, BucketType.user)
    async def affinity(self, ctx, member : discord.Member = ""):
        """Set your affinity to a user, has a 30 min cooldown. This will make things are cheaper and more effective, gift from
        your affinity will increase your value more and you will be cheaper to claim by your affinity.

        {usage}

        __Examples__
        `{pre}affinity @ThisLass` - set your affinity to the user ThisLass
        `{pre}affinity` - resets your affinity to no one"""
        if member.id == ctx.author.id:
            await ctx.send(":negative_squared_cross_mark: | You narcissist...")
            return

        if member == "":
            self.bot.user_data[ctx.author.id][ctx.guild.id]["affinity"] = ""
            await ctx.send(":white_check_mark: | Your affinity has been reset")
        else:
            self.bot.user_data[ctx.author.id][ctx.guild.id]["affinity"] = member.id
            await ctx.send(":white_check_mark: | Your affinity has been set to {}".format(member.display_name))

        self.bot.user_data[ctx.author.id][ctx.guild.id]["heart-changes"] += 1

        count = self.bot.user_data[ctx.author.id][ctx.guild.id]["heart-changes"]


    @affinity.error
    async def on_affinity_error(self, ctx, error):
        if not isinstance(error,commands.CommandOnCooldown):
            ctx.command.reset_cooldown(ctx)

        self.bot.dispatch("on_command_error", ctx, error)
            

    @commands.command(name="wclaim")
    async def claim_waifu(self, ctx, price : int, member : discord.Member):
        """Claim a user as your waifu, a user can only be claimed by one person but can have many waifus. You
        must propose and amount superior to the current price of the waifu.

        {usage}

        __Examples__
        `{pre}wclaim 500 @ThisLass` - claim use ThisLass for 500

        """
        if member.id in self.bot.user_data[ctx.author.id][ctx.guild.id]["waifus"]:
            await ctx.send(":negative_squared_cross_mark: | You have already claimed this waifu as your own")
            return

        if member.id == ctx.author.id:
            await ctx.send(":negative_squared_cross_mark: | You can't claim yourself!")
            return

        if self.bot.user_data[member.id][ctx.guild.id]["affinity"] == ctx.author.id:
            value = round(self.bot.user_data[member.id][ctx.guild.id]["waifu-value"] * 0.90)
        else:
            value = round(self.bot.user_data[member.id][ctx.guild.id]["waifu-value"] * 1.10)

        if price > value and price <= self.bot.user_data[ctx.author.id][ctx.guild.id]["flowers"]:
            claimer = self.bot.user_data[member.id][ctx.guild.id]["waifu-claimer"]
            if claimer != "":
                self.bot.user_data[claimer][ctx.guild.id]["waifus"].remove(member.id)

            self.bot.user_data[ctx.author.id][ctx.guild.id]["waifus"].append(member.id)
            self.bot.user_data[member.id][ctx.guild.id]["waifu-claimer"] = ctx.author.id
            self.bot.user_data[ctx.author.id][ctx.guild.id]["flowers"] -= price
            self.bot.user_data[member.id][ctx.guild.id]["waifu-value"] = price

            await ctx.send(":white_check_mark: | You've claimed **{}** as your waifu".format(member.display_name))
        elif price <= value:
            await ctx.send(":negative_squared_cross_mark: | You must pay more than {} :cherry_blossom: to claim this waifu".format(value))
        else:
            await ctx.send(":negative_squared_cross_mark: | You don't have enough :cherry_blossom:")

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 21600, BucketType.user)
    async def divorce(self, ctx, member : discord.Member):
        """Divorce a user and get some money back, sometimes... Can only be used every 9 hours.

        {usage}

        __Examples__
        `{pre}divorce @ThoseLasses` - divorce user ThosLasses
        """
        if member.id not in self.bot.user_data[ctx.author.id][ctx.guild.id]["waifus"]:
            return

        if self.bot.user_data[member.id][ctx.guild.id]["affinity"] != ctx.author.id:
            money_back = self.bot.user_data[member.id][ctx.guild.id]["waifu-value"] // 2
            self.bot.user_data[ctx.author.id][ctx.guild.id]["flowers"] += round(money_back)

        self.bot.user_data[ctx.author.id][ctx.guild.id]["waifus"].remove(member.id)
        self.bot.user_data[member.id][ctx.guild.id]["waifu-claimer"] = ""

        if money_back:
            embed = discord.Embed(color=discord.Colour(0x277b0), title=" ", description="You have divorced a waifu who doesn't like you. You received {} :cherry_blossom: back.".format(money_back))
        else:
            embed = discord.Embed(color=discord.Colour(0x277b0), title=" ", description="You have divorced a waifu")

        await ctx.send(embed=embed)

        self.bot.user_data[ctx.author.id][ctx.guild.id]["divorces"] += 1

    @divorce.command(name="admin")
    @has_perms(4)
    async def divorce_admin(self, ctx, waifu : discord.Member):
        """Admin command. Divorces a waifu from their claimer.

        {usage}

        __Examples__
        `{pre}divorce @ThoseLasses` - divorce user ThosLasses
        """
        claimer = self.bot.user_data[waifu.id][ctx.guild.id]["waifu-claimer"]
        self.bot.user_data[claimer][ctx.guild.id]["waifus"].remove(waifu.id)
        self.bot.user_data[waifu.id][ctx.guild.id]["waifu-claimer"] = ""

        embed = discord.Embed(color=discord.Colour(0x277b0), title=" ", description="**ADMIN**: You have divorced a waifu")
        await ctx.send(embed=embed)

    @divorce.error
    async def on_divorce_error(self, ctx, error):
        if not isinstance(error,commands.CommandOnCooldown):
            ctx.command.reset_cooldown(ctx)

        self.bot.dispatch("on_command_error", ctx, error)


    @commands.group(invoke_without_command=True)
    async def transfer(self, ctx, member : discord.Member, waifu : discord.Member):
        """Transfer a waifu to another user, you must be able to pay 10% of the waifu's price in order to tranfer them.
        
        {usage}

        __Examples__
        `{pre}transfer @ThatLass @ThisGuy` - transfer waifu ThatGuy to user ThatLass"""
        if self.bot.user_data[waifu.id][ctx.guild.id]["waifu-claimer"] != ctx.author.id:
            await ctx.send(":negative_squared_cross_mark: | This waifu is not yours to give!")
            return

        if self.bot.user_data[ctx.author.id][ctx.guild.id]["flowers"] < round(self.bot.user_data[waifu.id][ctx.guild.id]["waifu-value"] * 0.10):
            await ctx.send(":negative_squared_cross_mark: | You must have at least {} :cherry_blossom: to transfer this waifu".format(round(self.bot.user_data[waifu.id][ctx.guild.id]["waifu-value"] * 0.10)))
            return

        self.bot.user_data[ctx.author.id][ctx.guild.id]["waifus"].remove(waifu.id)
        self.bot.user_data[member.id][ctx.guild.id]["waifus"].append(waifu.id)
        self.bot.user_data[waifu.id][ctx.guild.id]["waifu-claimer"] = member.id
        self.bot.user_data[ctx.author.id][ctx.guild.id]["flowers"] -= round(self.bot.user_data[waifu.id][ctx.guild.id]["waifu-value"] * 0.10)

        embed = discord.Embed(color=discord.Colour(0x277b0),title=" ", description="You have transfered waifu **{}** to **{}**".format(waifu.name, member.name))
        await ctx.send(embed=embed)

    @transfer.command(name="admin")
    @has_perms(4)
    async def transfer_admin(self, ctx, member : discord.Member, waifu : discord.Member):
        """Admin command. Transfers a waifu to another user regardless of owner ship.

        {usage}

        __Examples__
        `{pre}transfer @ThatLass @ThisGuy` - transfer waifu ThatGuy to user ThatLass"""
        claimer = self.bot.user_data[waifu.id][ctx.guild.id]["waifu-claimer"]
        if claimer != "":
            self.bot.user_data[claimer][ctx.guild.id]["waifus"].remove(waifu.id)

        self.bot.user_data[member.id][ctx.guild.id]["waifus"].append(waifu.id)
        self.bot.user_data[waifu.id][ctx.guild.id]["waifu-claimer"] = member.id

        embed = discord.Embed(color=discord.Colour(0x277b0),title=" ", description="**ADMIN**: You have transfered waifu **{}** to **{}**".format(waifu.name, member.name))
        await ctx.send(embed=embed)


    @commands.command()
    @has_perms(4)
    async def award(self, ctx, amount : int, member : discord.Member,*, reason : str = ""):
        """Award :cherry_blossom: currency to a user, admin command.

        {usage}

        __Examples__
        `{pre}award 1000 @APerson` - awards 1000 :cherry_blossom: to user APerson"""
        self.bot.user_data[member.id][ctx.guild.id]["flowers"] += amount
        if reason != "": 
            await ctx.send(":white_check_mark: | Awarded **{}** :cherry_blossom: to **{}** for **{}**".format(amount, member.name), reason)
        else:
            await ctx.send(":white_check_mark:  | Awarded **{}** :cherry_blossom: to **{}**".format(amount, member.name))

    @commands.command()
    @has_perms(4)
    async def take(self, ctx, amount : int, member : discord.Member,*, reason : str = ""):
        """Take :cherry_blossom: currency from a user, admin command.

        {usage}

        __Examples__
        `{pre}take 1000 @APerson` - takes 1000 :cherry_blossom: from user APerson"""
        self.bot.user_data[member.id][ctx.guild.id]["flowers"] -= amount
        if reason != "": 
            await ctx.send(":white_check_mark: | Took **{}** :cherry_blossom: from **{}** for **{}**".format(amount, member.name), reason)
        else:
            await ctx.send(":white_check_mark:  | Took **{}** :cherry_blossom: from **{}**".format(amount, member.name))

    @commands.command()
    @has_perms(4)
    async def flowerevent(self, ctx, amount : int):
        """Create a 24hr message, if reacted to, the use who reacted will be granted :cherry_blossom:

        {usage}

        __Examples__
        `{pre}flowerevent 1500` - creates a 24hr event that awards 1500 on reaction."""
        embed = discord.Embed(color=discord.Colour(0x277b0), title="Flower Event", description="React with :cherry_blossom: to gain **{}** :cherry_blossom: This event will last 24hr".format(amount))
        msg = await ctx.send(embed=embed, delete_after=86400)
        await msg.add_reaction("\N{CHERRY BLOSSOM}")
        self.bot.events[msg.id] = {"users":[], "amount":amount}


    @commands.command()
    async def give(self, ctx, amount : int, member : discord.Member,*, reason : str = ""):
        """Transfer :cherry_blossom: from one user to another.

        {usage}

        __Examples__
        `{pre}give 100 @ThisGuy` - give 100 :cherry_blossom: to user ThisGuy"""
        amount = abs(amount)
        if self.bot.user_data[ctx.author.id][ctx.guild.id]["flowers"] < amount:
            await ctx.send(":negative_squared_cross_mark: | You don't have enough :cherry_blossom:")

        self.bot.user_data[ctx.author.id][ctx.guild.id]["flowers"] -= amount
        self.bot.user_data[member.id][ctx.guild.id]["flowers"] += amount
        await ctx.send(":white_check_mark: | **{}** has gifted **{}** :cherry_blossom: to **{}**".format(ctx.author.name, amount, member.name))

    @commands.command(name="reset")
    @has_perms(4)
    async def waifu_reset(self, ctx, waifu : discord.Member, amount : int = 50):
        """Reset the value of a waifu to a given value or to 50 if no value is given

        {usage}

        __Examples__
        `{pre}reset @ThisUser 500` - reset the value of the waifu to 500
        `{pre}reset @ThisUser` - reset the value of the waifu to 50"""

        self.bot.user_data[waifu.id][ctx.guild.id]["waifu-value"] = amount
        await ctx.send(":white_check_mark: | Value of waifu {} reset to {}".format(waifu.name, amount))





def setup(bot):
    bot.add_cog(Waifu(bot))