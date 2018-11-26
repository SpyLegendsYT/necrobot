import discord
from discord.ext import commands

import re

class Edain:
    """A cog for commands and events solely created for the unofficial Edain Community server"""
    def __init__(self, bot):
        self.bot = bot

    def __local__check(ctx):
        if not ctx.guild:
            return False

        return ctx.guild.id in (327175434754326539, 311630847969198082)

    # @commands.command()
    # async def poll(self, ctx):
    #     """This adds the necessary reactions to a reaction poll created, simply react to the poll with
    #     :white_check_mark:

    #     {usage}"""

    #     regex = r"(:[^ \n]*:|[^\w\s,])"
    #     d = await ctx.send("Waiting for :white_check_mark: reaction")

    #     def check(reaction, user):
    #         return str(reaction.emoji) == "\N{WHITE HEAVY CHECK MARK}" and user == ctx.author

    #     reaction, _ = await self.bot.wait_for("reaction_add", check=check)
    #     await d.delete()
    #     await reaction.message.remove_reaction("\N{WHITE HEAVY CHECK MARK}", ctx.author)

    #     matches = re.findall(regex, reaction.message.content)
    #     await ctx.send(str(matches))

    #     emojis = [emoji for emoji in ctx.guild.emojis if f":{emoji.name}:" in matches]
    #     emojis.extend(matches)

    #     for emoji in emojis:
    #         try:
    #             await reaction.message.add_reaction(emoji)
    #         except (discord.NotFound, discord.InvalidArgument, discord.HTTPException):
    #             pass

    def on_message(self, message):
        if message.channel.id != 504389672945057799:
            return

        regex = r"(:[^ \n]*:|[^\w\s,])"
        matches = re.findall(regex, message.content)
        emojis = [emoji for emoji in message.guild.emojis if f":{emoji.name}:" in matches]
        emojis.extend(matches)

        for emoji in emojis:
            try:
                await message.add_reaction(emoji)
            except (discord.NotFound, discord.InvalidArgument, discord.HTTPException):
                pass



def setup(bot):
    bot.add_cog(Edain(bot))