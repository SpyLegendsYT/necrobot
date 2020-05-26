import discord
from discord.ext import commands

import re
import asyncio
import datetime
import itertools

class BotError(Exception):
    pass

def check_channel(channel):
    if not channel.permissions_for(channel.guild.me).send_messages:
        raise BotError("I need permissions to send messages in this channel")

def has_welcome(bot, member):
    return bot.guild_data[member.guild.id]["welcome-channel"] and bot.guild_data[member.guild.id]["welcome"]

def has_goodbye(bot, member):
    return bot.guild_data[member.guild.id]["welcome-channel"] and bot.guild_data[member.guild.id]["goodbye"]

def has_automod(bot, message):
    if not bot.guild_data[message.guild.id]["automod"]:
        return False
        
    if message.author.id in bot.guild_data[message.guild.id]["ignore-automod"]:
        return False
        
    if message.channel.id in bot.guild_data[message.guild.id]["ignore-automod"]:
        return False
    
    role_ids = [role.id for role in message.author.roles]
    if any(x in role_ids for x in bot.guild_data[message.guild.id]["ignore-automod"]):
        return False
        
    return True 
    
def has_perms(level):
    async def predicate(ctx):
        if await ctx.bot.db.is_admin(ctx.message.author.id):
            return True 
            
        if ctx.guild is None:
            return False
        
        perms = await ctx.bot.db.get_permission(ctx.message.author.id, ctx.guild.id)
        if perms < level:
            raise commands.CheckFailure(f"You do not have the required NecroBot permissions. Your permission level must be {level}")
        
        return True

    predicate.level = level
    return commands.check(predicate)
    
async def react_menu(ctx, entries, per_page, generator, *, page=0, timeout=300):
    max_pages = max(0, (len(entries)//per_page) - 1)
    
    subset = entries[page*per_page:(page+1)*per_page]
    msg = await ctx.send(embed=generator((page + 1, max_pages + 1), subset[0] if per_page == 1 else subset))
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
            reaction, _ = await ctx.bot.wait_for("reaction_add", check=check, timeout=timeout)
        except asyncio.TimeoutError:
            await msg.clear_reactions()
            return

        if reaction.emoji == "\N{BLACK SQUARE FOR STOP}":
            return await msg.clear_reactions()
            
        if reaction.emoji == "\N{BLACK LEFT-POINTING TRIANGLE}":
            page -= 1
        elif reaction.emoji == "\N{BLACK RIGHT-POINTING TRIANGLE}":
            page += 1

        await msg.clear_reactions()
        
        subset = entries[page*per_page:(page+1)*per_page]
        await msg.edit(embed=generator((page + 1, max_pages + 1), subset[0] if per_page == 1 else subset))


async def get_pre(bot, message):
    """If the guild has set a custom prefix we return that and the ability to mention alongside regular 
    admin prefixes if not we return the default list of prefixes and the ability to mention."""
    if not isinstance(message.channel, discord.DMChannel):
        guild_pre = bot.guild_data[message.guild.id]["prefix"]
        if guild_pre != "":
            guild_pre = map(''.join, itertools.product(*((c.upper(), c.lower()) for c in guild_pre)))
            prefixes = [*guild_pre, *bot.admin_prefixes]
            return commands.when_mentioned_or(*prefixes)(bot, message)

    return commands.when_mentioned_or(*bot.prefixes)(bot, message)
    
def time_converter(argument):
    time = 0

    pattern = re.compile(r"([0-9]+)\s?([dhms])")
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
        
        argument = abs(int(argument))

        if argument < 0:
            raise commands.BadArgument("Amount must be a positive intenger")
        
        money = await ctx.bot.db.get_money(ctx.message.author.id)
        if argument <= money:
            return argument
        
        raise commands.BadArgument("You do not have enough money")

def midnight():
    """Get the number of seconds until midnight."""
    tomorrow = datetime.datetime.now() + datetime.timedelta(1)
    time = datetime.datetime(
        year=tomorrow.year, month=tomorrow.month, 
        day=tomorrow.day, hour=0, minute=0, second=0
    )
    return (time - datetime.datetime.now()).seconds
