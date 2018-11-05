import discord
from discord.ext import commands

import re
import asyncio
import datetime as d

def has_welcome(bot, member):
    return bot.server_data[member.guild.id]["welcome-channel"] != "" and bot.server_data[member.guild.id]["welcome"] != ""

def has_goodbye(bot, member):
    return bot.server_data[member.guild.id]["welcome-channel"] != "" and bot.server_data[member.guild.id]["goodbye"] != ""

def has_automod(bot, message):
    role_id = [role.id for role in message.author.roles]
    return message.author.id not in bot.server_data[message.guild.id]["ignore-automod"] and message.channel.id not in bot.server_data[message.guild.id]["ignore-automod"] and not any(x in role_id for x in bot.server_data[message.guild.id]["ignore-automod"]) and bot.server_data[message.guild.id]["automod"] != ""

UPDATE_NECROINS = "UPDATE necrobot.Users SET necroins = $1 WHERE user_id = $2"
UPDATE_FLOWERS  = "UPDATE necrobot.Waifu SET flowers = $1 WHERE user_id = $2 AND guild_id = $3"
UPDATE_PERMS    = "UPDATE necrobot.Permissions SET level = $1 WHERE guild_id = $2 AND user_id = $3"
UPDATE_VALUE    = "UPDATE necrobot.Waifu SET value = $1 WHERE user_id = $2 AND guild_id = $3"

def has_perms(perms_level):
    def predicate(ctx):
        if any(x >= 6 for x in ctx.bot.user_data[ctx.message.author.id]["perms"].values()):
            return True 
            
        if isinstance(ctx.message.channel, discord.DMChannel):
            return False

        if not ctx.bot.user_data[ctx.message.author.id]["perms"][ctx.message.guild.id] >= perms_level:
            raise commands.CheckFailure("You do not have the required NecroBot permissions")
        else:
            return True

    return commands.check(predicate)


async def react_menu(ctx, max_pages, page_generator, page=0):
    msg = await ctx.send(embed=page_generator(page))
    while True:
        react_list = []
        if page > 0:
            react_list.append("\N{BLACK LEFT-POINTING TRIANGLE}")

        react_list.append("\N{BLACK SQUARE FOR STOP}")

        if page < max_pages:
            react_list.append("\N{BLACK RIGHT-POINTING TRIANGLE}")

        for reaction in react_list:
            await msg.add_reaction(reaction)

        def check(reaction, user):
            return user == ctx.message.author and reaction.emoji in react_list and msg.id == reaction.message.id

        try:
            reaction, _ = await ctx.bot.wait_for("reaction_add", check=check, timeout=300)
        except asyncio.TimeoutError:
            await msg.clear_reactions()
            return

        if reaction.emoji == "\N{BLACK SQUARE FOR STOP}":
            await msg.clear_reactions()
            return
        elif reaction.emoji == "\N{BLACK LEFT-POINTING TRIANGLE}":
            page -= 1
        elif reaction.emoji == "\N{BLACK RIGHT-POINTING TRIANGLE}":
            page += 1

        await msg.clear_reactions()
        await msg.edit(embed=page_generator(page))

def time_converter(argument):
    time = 0

    pattern = re.compile(r"([0-9]+)([dhms])")
    matches = re.findall(pattern, argument)

    convert = {
        "d" : 86400,
        "h" : 3600,
        "m" : 60,
        "s" : 1
    }

    for match in matches:
        time += convert[match[1]] * int(match[0])

    return time

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

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        return time_converter(argument)

class MoneyConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.isdigit():
            raise commands.BadArgument("Not a valid intenger")
        else:
            argument = abs(int(argument))

        if argument <= ctx.bot.user_data[ctx.author.id]["money"]:
            return argument
        else:
            raise commands.BadArgument("You do not have enough money")

def midnight():
    """Get the number of seconds until midnight."""
    tomorrow = d.datetime.now() + d.timedelta(1)
    midnight = d.datetime(year=tomorrow.year, month=tomorrow.month, 
                          day=tomorrow.day, hour=0, minute=0, second=0)
    return (midnight - d.datetime.now()).seconds
