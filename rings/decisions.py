#!/usr/bin/python3.6
import discord
from discord.ext import commands
import dice
import random


ball8List = ["It is certain"," It is decidedly so"," Without a doubt","Yes, definitely","You may rely on it","As I see it, yes"," Most likely","Outlook good","Yes","Signs point to yes","Reply hazy try again","Ask again later","Better not tell you now"," Cannot predict now","Concentrate and ask again","Don't count on it"," My reply is no","My sources say no","Outlook not so good","Very doubtful"]


class Decisions():
    """Helpful commands to help you make decisions"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def choose(self, ctx, *, choices):
        """Returns a single choice from the list of choices given. Use `,` to seperate each of the choices.
        
        {usage}
        
        __Example__
        `{pre}choose Bob, John Smith, Mary` - choose between the names of Bob, John Smith, and Mary
        `{pre}choose 1, 2` - choose between 1 and 2 """
        choice_list = [x.strip() for x in choices.split(",")]
        await ctx.send("I choose **{}**".format(random.choice(choice_list)))

    @commands.command(aliases=["flip"])
    async def coin(self, ctx, choice : str = None, bet : int = None):
        """Flips a coin and returns the result. Can also be used to bet money on the result (`h` for head and `t` for tail).
        
        {usage}

        __Example__
        `{pre}coin` - flips a coin
        `{pre}coin h 50` - bet 50 coins on the result being head"""
        msg = await ctx.send(random.choice(["<:head:351456287453872135> | **Head**","<:tail:351456234257514496> | **Tail**"]))

        if choice is None and bet is None:
            return

        if bet is None:
            bet = 0
        else:
            bet = abs(bet)

        if bet >  self.bot.user_data[ctx.author.id]["money"]:
            await ctx.send(":negative_squared_cross_mark: | Not enough money", delete_after=5)
            return

        if "head" in msg.content:
            if choice == "h":
                await ctx.send("Well done!")
                self.bot.user_data[ctx.author.id]["money"] += bet
            elif choice == "t":
                await ctx.send("Better luck next time")
                self.bot.user_data[ctx.author.id]["money"] -= bet
        elif "tail" in msg.content:
            if choice == "t":
                await ctx.send("Well done!")
                self.bot.user_data[ctx.author.id]["money"] += bet
            elif choice == "h":
                await ctx.send("Better luck next time")
                self.bot.user_data[ctx.author.id]["money"] -= bet

    @commands.command()
    async def roll(self, ctx, dices="1d6"):
        """Rolls one or multiple x sided dices and returns the result. 
        Structure of the argument: `[number of die]d[number of faces]`. Uses the newest quantum number generator. 
        
        {usage}
        
        __Example__
        `{pre}roll 3d8` - roll three 8-sided die
        `{pre}roll` - roll one 6-sided die"""
        dice_list = dice.roll(dices)
        try:
            t = sum(dice_list)
        except TypeError:
            t = dice_list

        await ctx.send(":game_die: | **{}** rolled {} for a total of: **{}**".format(ctx.message.author.display_name, dice_list, t))

    @commands.command(name="8ball")
    async def ball8(self, ctx, *, message):
        """Uses an 8ball system to reply to the user's question. 
        
        {usage}"""
        await ctx.send("{} \n:8ball: | {}".format(message, random.choice(ball8List)))

def setup(bot):
    bot.add_cog(Decisions(bot))
