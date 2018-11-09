from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from rings.utils.utils import UPDATE_NECROINS, MoneyConverter
from rings.utils.var import var

import dice
import random

class CoinConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if argument.lower() in ["h, head"]:
            return "h"
        if argument.lower() in ["t", "tail"]:
            return "t"

        raise commands.BadArgument(ctx.bot.t(ctx, "incorrect-coin-choice"))

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
        await ctx.send(self.bot.t(ctx, "choose-choice").format(random.choice(choice_list)))

    @commands.command(aliases=["flip"])
    @commands.cooldown(3, 5, BucketType.user)
    async def coin(self, ctx, choice : CoinConverter = None, bet : MoneyConverter = None):
        """Flips a coin and returns the result. Can also be used to bet money on the result (`h` for head and `t` for tail).
        
        {usage}

        __Example__
        `{pre}coin` - flips a coin
        `{pre}coin h 50` - bet 50 coins on the result being head"""
        outcome = random.choice(self.bot.t(ctx, "coin-choices"))
        
        if bet:
            bet = abs(bet)
            if ("head" in outcome and choice == "h") or ("tail" in outcome and choice == "t"):
                outcome += f"\n{self.bot.t(ctx, 'well-done')}"
                self.bot.user_data[ctx.author.id]["money"] += bet
            else:
                outcome += f"\n{self.bot.t(ctx, 'better-luck')}"
                self.bot.user_data[ctx.author.id]["money"] -= bet

            await self.bot.query_executer(UPDATE_NECROINS, self.bot.user_data[ctx.author.id]["money"], ctx.author.id)

        await ctx.send(outcome)

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

        await ctx.send(self.bot.t(ctx, "die-sum").format(ctx.author.display_name, dice_list, t))

    @commands.command(name="8ball")
    async def ball8(self, ctx, *, message):
        """Uses an 8ball system to reply to the user's question. 
        
        {usage}"""
        ball8_list = var[self.bot.server_data[ctx.guild.id]["language"]].ball8_list
        await ctx.send(f"{message} \n:8ball: | {random.choice(ball8_list)}")

def setup(bot):
    bot.add_cog(Decisions(bot))
