from discord.ext import commands
import discord

import asyncio

def has_perms(perms_level):
    def predicate(ctx): 
        if isinstance(ctx.message.channel, discord.DMChannel):
            return False

        if not ctx.bot.user_data[ctx.message.author.id]["perms"][ctx.message.guild.id] >= perms_level:
            raise commands.CheckFailure("You do not have the required NecroBot permissions")
        else:
            return True

    return commands.check(predicate)


async def react_menu(bot, ctx, max, page_generator, page=0):
    msg = await ctx.send(embed=page_generator(page))
    while True:
        react_list = list()
        if page > 0:
            react_list.append("\N{BLACK LEFT-POINTING TRIANGLE}")

        react_list.append("\N{BLACK SQUARE FOR STOP}")

        if page < max:
            react_list.append("\N{BLACK RIGHT-POINTING TRIANGLE}")

        for reaction in react_list:
            await msg.add_reaction(reaction)

        def check(reaction, user):
            return user == ctx.message.author and reaction.emoji in react_list and msg.id == reaction.message.id

        try:
            reaction, user = await bot.wait_for("reaction_add", check=check, timeout=300)
        except asyncio.TimeoutError as e:
            await msg.clear_reactions()

        if reaction.emoji == "\N{BLACK SQUARE FOR STOP}":
            await msg.clear_reactions()
            break
        elif reaction.emoji == "\N{BLACK LEFT-POINTING TRIANGLE}":
            page -= 1
        elif reaction.emoji == "\N{BLACK RIGHT-POINTING TRIANGLE}":
            page += 1

        await msg.clear_reactions()
        await msg.edit(embed=page_generator(page))

class GuildConverter(commands.IDConverter):
    async def convert(self, ctx, argument):
        result = None
        bot = ctx.bot
        guilds = bot.guilds

        result = discord.utils.get(guilds, name=argument)

        if result:
            return result

        if argument.isdigit():
            result = bot.get_guild(int(argument))

            if result:
                return result

        raise commands.BadArgument("Not a known guild")

