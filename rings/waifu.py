#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType, Cooldown, CooldownMapping
from rings.utils.utils import is_waifu_admin

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
        self.gifts_e = {"Cookie" : ":cookie:", "Rose": ":rose:", "LoveLetter":":love_letter:", "Chocolate":":chocolate_bar:", "Rice":":rice:", "MovieTicket":":tickets:", "Book":":notebook_with_decorative_cover:", "Lipstick":":lipstick:", "Laptop":":computer:", "Violin":":violin:", "Ring":":ring:", "Helicopter":":helicopter:"}
        self.gifts_p = {"Cookie" : 10, "Rose": 50, "LoveLetter":100, "Chocolate":200, "Rice":400, "MovieTicket":800, "Book":1500, "Lipstick":3000, "Laptop":5000, "Violin":7500, "Ring":10000, "Helicopter":20000}

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
        self.bot.user_data[ctx.author.id]["flowers"] += coins
        await ctx.send(":white_check_mark: | You exchanged **{}** Necroins for **{}** :cherry_blossom:".format(coins, coins))

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

        embed = discord.Embed(color=discord.Colour(0x277b0), description="{} has **{}** :cherry_blossom:".format(user.name, self.bot.user_data[user.id]["flowers"]))
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

        embed = discord.Embed(color=discord.Colour(0x277b0), title="Waifu {} - ".format(user.name))
        embed.add_field(name="Price", value=self.bot.user_data[user.id]["waifu-value"])
        embed.add_field(name="Claimed by", value=self.bot.get_user(self.bot.user_data[user.id]["waifu-claimer"]).name if self.bot.user_data[user.id]["waifu-claimer"] != "" else "None")
        embed.add_field(name="Likes", value=self.bot.get_user(self.bot.user_data[user.id]["affinity"]).name if self.bot.user_data[user.id]["affinity"] != "" else "None")
        embed.add_field(name="Changes of heart", value=self.bot.user_data[user.id]["heart-changes"])
        embed.add_field(name="Divorces", value=self.bot.user_data[user.id]["divorces"])
        gifts = self.bot.user_data[user.id]["gifts"]
        gift_str = "\n".join(["{}x{}".format(self.gifts_e[x], gifts[x]) for x in gifts if gifts[x] > 0])
        embed.add_field(name="Gifts", value=gift_str if gift_str != "" else "None", inline=False)
        waifus = "\n".join([self.bot.get_user(x).name for x in self.bot.user_data[user.id]["waifus"]])
        embed.add_field(name="Waifus ({})".format(len(self.bot.user_data[user.id]["waifus"])), value=waifus if waifus != "" else "None", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def gifts(self, ctx):
        """Displays the list of gifts that can be gifted.

        {usage}"""

        embed = discord.Embed(color=discord.Colour(0x277b0), title="Waifu gift shop")
        for gift in self.gifts_e:
            embed.add_field(name="{} {}".format(self.gifts_e[gift], gift), value=self.gifts_p[gift])

        await ctx.send(embed=embed)

    @commands.command()
    async def gift(self, ctx, choice, member : discord.Member):
        """Gifts an item from the gift list (`{pre}gifts` to display). The gift increases the value of the waifu by
        a different amount depending on whether or not their affinity is set to the gifter.

        {usage}

        __EXamples__
        `{pre}gift Chocolate @ThirdThot` - gifts a chocolate to the user ThirdThot
        """
        try:
            price = self.gifts_p[choice]
            emoji = self.gifts_e[choice]
        except AttributeError:
            return

        if self.bot.user_data[ctx.author.id]["flowers"] < price:
            await ctx.send(":negative_squared_cross_mark: | Not enough :cherry_blossom:")
            return

        self.bot.user_data[ctx.author.id]["flowers"] -= price
        self.bot.user_data[member.id]["waifu-value"] += price if self.bot.user_data[member.id]["affinity"] == ctx.author.id else price//2
        self.bot.user_data[member.id]["gifts"][choice] += 1 

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
            self.bot.user_data[ctx.author.id]["affinity"] = ""
            await ctx.send(":white_check_mark: | Your affinity has been reset")
        else:
            self.bot.user_data[ctx.author.id]["affinity"] = member.id
            await ctx.send(":white_check_mark: | Your affinity has been set to {}".format(member.display_name))

        self.bot.user_data[ctx.author.id]["heart-changes"] += 1


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
        if member.id in self.bot.user_data[ctx.author.id]["waifus"]:
            await ctx.send(":negative_squared_cross_mark: | You have already claimed this waifu as your own")
            return

        if member.id == ctx.author.id:
            await ctx.send(":negative_squared_cross_mark: | You can't claim yourself!")
            return

        if self.bot.user_data[member.id]["affinity"] == ctx.author.id:
            value = round(self.bot.user_data[member.id]["waifu-value"] * 0.90)
        else:
            value = round(self.bot.user_data[member.id]["waifu-value"] * 1.10)

        if price > value and price <= self.bot.user_data[ctx.author.id]["flowers"]:
            claimer = self.bot.user_data[member.id]["waifu-claimer"]
            if claimer != "":
                self.bot.user_data[claimer]["waifus"].remove(member.id)

            self.bot.user_data[ctx.author.id]["waifus"].append(member.id)
            self.bot.user_data[member.id]["waifu-claimer"] = ctx.author.id
            self.bot.user_data[ctx.author.id]["flowers"] -= price
            self.bot.user_data[member.id]["waifu-value"] = price

            await ctx.send(":white_check_mark: | You've claimed **{}** as your waifu".format(member.display_name))
        elif price <= value:
            await ctx.send(":negative_squared_cross_mark: | You must pay more than {} :cherry_blossom: to claim this waifu".format(value))
        else:
            await ctx.send(":negative_squared_cross_mark: | You don't have enough :cherry_blossom:")

    @commands.command()
    @commands.cooldown(1, 21600, BucketType.user)
    async def divorce(self, ctx, member : discord.Member):
        """Divorce a user and get some money back, sometimes... Can only be used every 9 hours.

        {usage}

        __Examples__
        `{pre}divorce @ThoseLasses` - divorce user ThosLasses
        """
        if member.id not in self.bot.user_data[ctx.author.id]["waifus"]:
            return

        if self.bot.user_data[member.id]["affinity"] != ctx.author.id:
            money_back = self.bot.user_data[member.id]["waifu-value"] // 2
            self.bot.user_data[ctx.author.id]["flowers"] += round(money_back)

        self.bot.user_data[ctx.author.id]["waifus"].remove(member.id)
        self.bot.user_data[member.id]["waifu-claimer"] = ""

        if money_back:
            embed = discord.Embed(color=discord.Colour(0x277b0), title=" ", description="You have divorced a waifu who doesn't like you. You received {} :cherry_blossom: back.".format(money_back))
        else:
            embed = discord.Embed(color=discord.Colour(0x277b0), title=" ", description="You have divorced a waifu")

        await ctx.send(embed=embed)

        self.bot.user_data[ctx.author.id]["divorces"] += 1

    @divorce.error
    async def on_divorce_error(self, ctx, error):
        if not isinstance(error,commands.CommandOnCooldown):
            ctx.command.reset_cooldown(ctx)

        self.bot.dispatch("on_command_error", ctx, error)


    @commands.command()
    async def transfer(self, ctx, member : discord.Member, waifu : discord.Member):
        """Transfer a waifu to another user, you must be able to pay 10% of the waifu's price in order to tranfer them.
        
        {usage}

        __Examples__
        `{pre}transfer @ThatLass @ThisGuy` - transfer waifu ThatGuy to user ThatLass"""
        if self.bot.user_data[waifu.id]["waifu-claimer"] != ctx.author.id:
            await ctx.send(":negative_squared_cross_mark: | This waifu is not yours to give!")
            return

        if self.bot.user_data[ctx.author.id]["flowers"] < round(self.bot.user_data[waifu.id]["waifu-value"] * 0.10):
            await ctx.send(":negative_squared_cross_mark: | You must have at least {} :cherry_blossom: to transfer this waifu".format(round(self.bot.user_data[waifu.id]["waifu-value"] * 0.10)))
            return

        self.bot.user_data[ctx.author.id]["waifus"].remove(waifu.id)
        self.bot.user_data[member.id]["waifus"].append(waifu.id)
        self.bot.user_data[waifu.id]["waifu-claimer"] = member.id
        self.bot.user_data[ctx.author.id]["flowers"] -= round(self.bot.user_data[waifu.id]["waifu-value"] * 0.10)

        embed = discord.Embed(color=discord.Colour(0x277b0),title=" ", description="You have transfered waifu **{}** to **{}**".format(waifu.name, member.name))
        await ctx.send(embed=embed)

    @commands.command()
    @is_waifu_admin()
    async def award(self, ctx, amount : int, member : discord.Member, reason : str = ""):
        """Award :cherry_blossom: currency to a user, admin command.

        {usage}

        __Examples__
        `{pre}award 1000 @APerson` - awards 1000 :cherry_blossom: to user APerson"""
        self.bot.user_data[member.id]["flowers"] += amount
        if reason != "": 
            await ctx.send(":white_check_mark: | Awarded **{}** to **{}** for **{}**".format(amount, member.name), reason)
        else:
            await ctx.send(":white_check_mark:  | Awarded **{}** to **{}**".format(amount, member.name))

    @commands.command()
    @is_waifu_admin()
    async def take(self, ctx, amount : int, member : discord.Member, reason : str = ""):
        """Take :cherry_blossom: currency from a user, admin command.

        {usage}

        __Examples__
        `{pre}take 1000 @APerson` - takes 1000 :cherry_blossom: from user APerson"""
        self.bot.user_data[member.id]["flowers"] -= amount
        if reason != "": 
            await ctx.send(":white_check_mark: | Took **{}** to **{}** for **{}**".format(amount, member.name), reason)
        else:
            await ctx.send(":white_check_mark:  | Took **{}** to **{}**".format(amount, member.name))

    @commands.command()
    @is_waifu_admin()
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
    async def give(self, ctx, amount : int, member : discord.Member, reason : str = ""):
        """Transfer :cherry_blossom: from one user to another.

        {usage}

        __Examples__
        `{pre}give 100 @ThisGuy` - give 100 :cherry_blossom: to user ThisGuy"""
        amount = abs(amount)
        if self.bot.user_data[ctx.author.id]["flowers"] < amount:
            await ctx.send(":negative_squared_cross_mark: | You don't have enough :cherry_blossom:")

        self.bot.user_data[ctx.author.id]["flowers"] -= amount
        self.bot.user_data[member.id]["flowers"] += amount
        await ctx.send(":white_check_mark: | **{}** has gifted **{}** :cherry_blossom: to **{}**".format(ctx.author.name, amount, member.name))


    @commands.command(name="wset", hidden=True)
    @commands.is_owner()
    async def set(self, ctx):
        for x in self.bot.user_data:
            self.bot.user_data[x]["waifu-value"] = 50
            self.bot.user_data[x]["waifu-claimer"] = ""
            self.bot.user_data[x]["affinity"] = ""
            self.bot.user_data[x]["heart-changes"] = 0
            self.bot.user_data[x]["divorces"] = 0
            self.bot.user_data[x]["waifus"] = []
            self.bot.user_data[x]["flowers"] = 0
            self.bot.user_data[x]["gifts"] = self.bot._new_gifts()

        await ctx.send("All data set for waifu system")




def setup(bot):
    bot.add_cog(Waifu(bot))