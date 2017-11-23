#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import dice
import random

ball8List = ["It is certain"," It is decidedly so"," Without a doubt","Yes, definitely","You may rely on it","As I see it, yes"," Most likely","Outlook good","Yes","Signs point to yes","Reply hazy try again","Ask again later","Better not tell you now"," Cannot predict now","Concentrate and ask again","Don't count on it"," My reply is no","My sources say no","Outlook not so good","Very doubtful"]


class Decisions():
    """Helpful commands to help you make decisions"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(5, 5, BucketType.user)
    async def choose(self, *, choices):
        """Returns a single choice from the list of choices given. Use `|` to seperate each of the choices.
        
        {usage}
        
        __Example__
        `{pre}choose Bob | John | Mary` - choose between the names of Bob, John, and Mary
        `{pre}choose 1 | 2` - choose between 1 and 2 """
        choiceList = [x.strip() for x in choices.split("|")]
        await self.bot.say("I choose **" + random.choice(choiceList) + "**")

    @commands.command(aliases=["flip"])
    @commands.cooldown(5, 5, BucketType.user)
    async def coin(self):
        """Flips a coin and returns the result
        
        {usage}"""
        await self.bot.say(random.choice(["<:head:351456287453872135> | **Head**","<:tail:351456234257514496> | **Tail**"]))

    @commands.command(pass_context = True)
    @commands.cooldown(5, 5, BucketType.user)
    async def roll(self, cont, dices="1d6"):
        """Rolls one or multiple x sided dices and returns the result. Structure of the argument: `[number of die]d[number of faces]` 
        
        {usage}
        
        __Example__
        `{pre}roll 3d8` - roll three 8-sided die
        `{pre}roll` - roll one 6-sided die"""
        await self.bot.say(":game_die: | {} rolled {}".format(cont.message.author.display_name, dice.roll(dices)))

    @commands.command(name="8ball")
    @commands.cooldown(3, 5, BucketType.user)
    async def ball8(self):
        """Uses an 8ball system to reply to the user's question. 
        
        {usage}"""
        await self.bot.say(":8ball: | " + random.choice(ball8List))

def setup(bot):
    bot.add_cog(Decisions(bot))
