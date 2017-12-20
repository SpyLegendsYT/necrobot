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
        await ctx.channel.send("I choose **{}**".format(random.choice(choice_list)))

    @commands.command(aliases=["flip"])
    async def coin(self, ctx):
        """Flips a coin and returns the result
        
        {usage}"""
        await ctx.channel.send(random.choice(["<:head:351456287453872135> | **Head**","<:tail:351456234257514496> | **Tail**"]))

    @commands.command()
    async def roll(self, ctx, dices="1d6"):
        """Rolls one or multiple x sided dices and returns the result. Structure of the argument: `[number of die]d[number of faces]` 
        
        {usage}
        
        __Example__
        `{pre}roll 3d8` - roll three 8-sided die
        `{pre}roll` - roll one 6-sided die"""
        await ctx.channel.send(":game_die: | {} rolled {}".format(ctx.message.author.display_name, dice.roll(dices)))

    @commands.command(name="8ball")
    async def ball8(self, ctx, *, message):
        """Uses an 8ball system to reply to the user's question. 
        
        {usage}"""
        await ctx.channel.send("{} \n:8ball: | {}".format(message, random.choice(ball8List)))

def setup(bot):
    bot.add_cog(Decisions(bot))