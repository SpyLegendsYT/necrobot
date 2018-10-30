#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from rings.utils.utils import UPDATE_NECROINS
from rings.utils.var import choice_list

import dice
import random

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
        await ctx.send(f"I choose **{random.choice(choice_list)}**")

    @commands.command(aliases=["flip"])
    @commands.cooldown(3, 5, BucketType.user)
    async def coin(self, ctx, choice : str = None, bet : int = None):
        """Flips a coin and returns the result. Can also be used to bet money on the result (`h` for head and `t` for tail).
        
        {usage}

        __Example__
        `{pre}coin` - flips a coin
        `{pre}coin h 50` - bet 50 coins on the result being head"""
        msg = await ctx.send(random.choice(["<:head:351456287453872135> | **Head**","<:tail:351456234257514496> | **Tail**"]))

        if choice not in ["t", "h"]:
            return

        bet = abs(bet)

        if bet >  self.bot.user_data[ctx.author.id]["money"]:
            await ctx.send(":negative_squared_cross_mark: | Not enough money", delete_after=5)
            return

        if "head" in msg.content and choice == "h":
            await ctx.send("Well done!")
            self.bot.user_data[ctx.author.id]["money"] += bet
        elif "tail" in msg.content and choice == "t":
            await ctx.send("Well done!")
            self.bot.user_data[ctx.author.id]["money"] += bet
        else:
            await ctx.send("Better luck next time")
            self.bot.user_data[ctx.author.id]["money"] -= bet

        await self.bot.query_executer(UPDATE_NECROINS, self.bot.user_data[ctx.author.id]["money"], ctx.author.id)

    @commands.command()
    async def roll(self, ctx, dices="1d6"):
        """Rolls one or multiple x sided dices and returns the result. 
        Structure of the argument: `[number of die]d[number of faces]`. 
        
        {usage}
        
        __Example__
        `{pre}roll 3d8` - roll three 8-sided die
        `{pre}roll` - roll one 6-sided die"""
        dice_list = dice.roll(dices)
        try:
            t = sum(dice_list)
        except TypeError:
            t = dice_list

        await ctx.send(f":game_die: | **{ctx.author.display_name}** rolled {dice_list} for a total of: **{t}**")

    @commands.command(name="8ball")
    async def ball8(self, ctx, *, message):
        """Uses an 8ball system to reply to the user's question. 
        
        {usage}"""
        await ctx.send(f"{message} \n:8ball: | {random.choice(choice_list)}")

def setup(bot):
    bot.add_cog(Decisions(bot))
