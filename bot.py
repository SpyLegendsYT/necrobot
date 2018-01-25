import discord
from discord.ext import commands
from rings.utils.help import NecroBotHelpFormatter
import time
import json
import random
from config import *
import sys
import time as t
import asyncio
import traceback
import re
import logging
from bs4 import BeautifulSoup
import aiohttp

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

async def get_pre(bot, message):
    if not isinstance(message.channel, discord.DMChannel):
        if bot.server_data[message.guild.id]["prefix"] != "":
            return [bot.server_data[message.guild.id]["prefix"], "n@"]

    return bot.prefixes

extensions = [
    "hunger",
    "animals",
    "social",
    "wiki",
    "modding",
    "support",
    "utilities",
    "moderation",
    "profile",
    "tags",
    "server",
    "admin",
    "decisions",
    "casino"
]

replyList = [
    "*yawn* What can I do fo... *yawn*... for you?", 
    "NecroBot do that, NecroBot do this, never NecroBot how are y... Oh, hey how can I help?",
    "I wonder how other bots are treated :thinking: Do they also put up with their owners' terrible coding habits?",
    "Second sight ordains it! I mean sure..."
    ]
class NecroBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_pre, description="A bot for moderation and LOTR", formatter=NecroBotHelpFormatter())
        self.uptime_start = time.time()
        self.user_data = dict()
        self.server_data = dict()

        #force typecast to int for all ids
        raw_user_data = json.load(open("rings/utils/data/user_data.json", "r"))
        for user in raw_user_data:
            self.user_data[int(user)] = raw_user_data[user]
            raw_perms = dict()
            for server in raw_user_data[user]["perms"]:
                raw_perms[int(server)] = raw_user_data[user]["perms"][server]

            self.user_data[int(user)]["perms"] = raw_perms
        
        raw_server_data = json.load(open("rings/utils/data/server_data.json", "r"))
        for server in raw_server_data:
            self.server_data[int(server)] = raw_server_data[server]

            if "auto-role" not in self.server_data[int(server)]:
                self.server_data[int(server)]["auto-role"] = ""

            if "disabled" not in self.server_data[int(server)]:
                self.server_data[int(server)]["disabled"] = []

            if "broadcast-time" not in self.server_data[int(server)]:
                self.server_data[int(server)]["broadcast-time"] = 1

        self.ERROR_LOG = 351356683231952897
        self.version = 1.0
        self.prefixes = ["n!", "N!", "n@"]

        self.bg_task = self.loop.create_task(self.hourly_task())

        @self.check
        def disabled_check(ctx):
            if ctx.command.name not in self.server_data[ctx.message.guild.id]["disabled"]:
                return True

            if ctx.command.name in self.server_data[ctx.message.guild.id]["disabled"] and ctx.prefix == "n@":
                return True
            
            if ctx.command.name in self.server_data[ctx.message.guild.id]["disabled"] and ctx.prefix != "n@":
                return False
                
        self.add_check(disabled_check)


    # *****************************************************************************************************************
    #  Internal Function
    # *****************************************************************************************************************

    def _startswith_prefix(self, message):
        if self.server_data[message.guild.id]["prefix"] != "" and message.content.startswith(self.server_data[message.guild.id]["prefix"]):
            return True

        if message.content.startswith(tuple(self.prefixes)):
            return True

        return False

    def _is_allowed_summon(self, message):
        role_id = [role.id for role in message.author.roles]
        user_id = message.author.id
        channel_id = message.channel.id
        if self.user_data[user_id]["perms"][message.guild.id] >= 4 and message.content.startswith("n@"):
            return True

        if user_id in self.server_data[message.guild.id]["ignoreCommand"] or channel_id in self.server_data[message.guild.id]["ignoreCommand"] or any(x in role_id for x in self.server_data[message.guild.id]["ignoreCommand"]):
            return False

        return True

    def logit(self, message):
        if self._startswith_prefix(message):
            with open("rings/utils/data/logfile.txt","a+") as log:
                localtime = "\n{}: ".format(t.asctime(t.localtime(t.time())))
                try: 
                    author = "{}#{}".format(message.author.name, message.author.discriminator)
                except UnicodeEncodeError:
                    author = message.author.id

                log.write("{}{} used {}".format(localtime, author, message.content))

    async def _mu_auto_embed(self, soup, url, message):
        try:
            header = list(soup.find("h3", class_="catbg").stripped_strings)[1].replace("Thema: ", "").split(" \xa0")
            title = header[0]
            read = header[1].replace("Gelesen", "Read**").replace("mal", "**times").replace("(", "").replace(")","")
        except IndexError:
            return

        op = soup.find("div", class_="poster")
        bot_ico = "https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128"
        board = [x.a.string for x in soup.find("div", class_="navigate_section").ul.find_all("li") if "board" in x.a["href"]][0]

        embed = discord.Embed(title=title, url=url, colour=discord.Colour(0x277b0), description="Some information on the thread that was linked \n -Board: **{}** \n -{}".format(board, read))
        if op.a is not None:

            embed.set_author(name="OP: " + op.a.string, url=op.a["href"], icon_url=op.find("img", class_="avatar")["src"] if op.find("img", class_="avatar") is not None else bot_ico)
        else:
            embed.set_author(name="OP: " + list(op.stripped_strings)[0])

        embed.set_footer(text="Generated by NecroBot", icon_url=bot_ico)

        await message.channel.send("Oh. That's a little bare. Here, let me embed that for you.", embed=embed)

    # *****************************************************************************************************************
    #  Background Tasks
    # *****************************************************************************************************************
    async def hourly_task(self):
        await self.wait_until_ready()
        log = bot.get_channel(self.ERROR_LOG)
        counter = 0
        while not self.is_closed():
            if counter >= 24:
                counter = 0
            await asyncio.sleep(3600) # task runs every hour
            counter += 1
            
            #hourly save
            with open("rings/utils/data/server_data.json", "w") as out:
                json.dump(self.server_data, out)

            with open("rings/utils/data/user_data.json", "w") as out:
                json.dump(self.user_data, out)

            await log.send("Hourly save at " + str(t.asctime(t.localtime(t.time()))))

            #background tasks
            #broadcast
            for guild in self.server_data:
                hour_mod = counter % self.server_data[guild]["broadcast-time"]
                if self.server_data[guild]["broadcast"] != "" and self.server_data[guild]["broadcast-channel"] != "" and hour_mod == 0:
                    channel = self.get_channel(self.server_data[guild]["broadcast-channel"])
                    await channel.send(self.server_data[guild]["broadcast"])

    # *****************************************************************************************************************
    #  Internal Checks
    # *****************************************************************************************************************

    def default_stats(self, member, guild):
        if member.id not in self.user_data:
            self.user_data[int(member.id)] = {'money': 200, 'daily': '', 'title': '', 'exp': 0, 'perms': {}, 'warnings': []}

        if guild.id not in self.user_data[member.id]["perms"]:
            if any(self.user_data[member.id]["perms"][x] == 7 for x in self.user_data[member.id]["perms"]):
                self.user_data[member.id]["perms"][guild.id] = 7
            elif any(self.user_data[member.id]["perms"][x] == 6 for x in self.user_data[member.id]["perms"]):
                self.user_data[member.id]["perms"][guild.id] = 6
            elif member.id == guild.owner.id:
                self.user_data[member.id]["perms"][guild.id] = 5
            elif member.guild_permissions.administrator:
                self.user_data[member.id]["perms"][guild.id] = 4
            else:
                self.user_data[member.id]["perms"][guild.id] = 0
                
    def all_mentions(self, ctx, msg):
        mention_list = list()
        for mention in msg:
            id = re.sub('[<>!&#@]', '', mention)
            id = int(id)
            if not self.get_channel(id) is None:
                channel = self.get_channel(id)
                mention_list.append(channel)
            elif not ctx.message.guild.get_member(id) is None:
                member = ctx.message.guild.get_member(id)
                mention_list.append(member)
            elif not discord.utils.get(ctx.message.guild.roles, id=id) is None:
                role = discord.utils.get(ctx.message.guild.roles, id=id)
                mention_list.append(role)

        return mention_list

    # *****************************************************************************************************************
    # Events
    # *****************************************************************************************************************
    async def on_ready(self):
        await self.change_presence(game=discord.Game(name="Bot booting...", type=0))
        channel = self.get_channel(318465643420712962)
        await channel.send("**Initiating Bot**")
        msg = await channel.send("Bot User ready")

        members = self.get_all_members()
        for member in members:
            self.default_stats(member, member.guild)
        await msg.edit(content="All members checked")

        for guild in self.guilds:
            if guild.id not in self.server_data:
                    self.server_data[guild.id] = {"mute":"","automod":"","welcome-channel":"", "selfRoles":[],"ignoreCommand":[],"ignoreAutomod":[],"welcome":"Welcome {member} to {server}!","goodbye":"Leaving so soon? We\'ll miss you, {member}!","tags":{}, "prefix" : "", "broadcast-channel": "", "broadcast": "", "broadcast-time": "", "disabled": [], "auto-role": ""}
        await msg.edit(content="All servers checked")

        for extension in extensions:
            try:
                self.load_extension("rings."+extension)
            except Exception as e:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()
        await msg.edit(content="All extensions loaded")

        await channel.send("**Bot Online**")
        await msg.delete()

        await self.change_presence(game=discord.Game(name="n!help for help", type=0))
        print(self.server_data)
        print('------')
        print("Logged in as {0.user}".format(self))

    async def on_command_error(self, ctx, error):
        """Catches error and sends a message to the user that caused the error with a helpful message."""
        channel = ctx.message.channel
        try:
            ctx.command.name
            if ctx.command.name in self.server_data[ctx.message.guild.id]["disabled"] and ctx.prefix != "n@":
                await ctx.send(":negative_squared_cross_mark: | Command {} cannot be used on this server.".format(ctx.command.name), delete_after=10)
                await ctx.message.delete()
                return
        except AttributeError:
            pass

        if isinstance(error, commands.MissingRequiredArgument):
            await channel.send(":negative_squared_cross_mark: | Missing required argument! Check help guide with `n!help {}`".format(ctx.command.name), delete_after=10)
        elif isinstance(error, commands.CheckFailure):
            await channel.send(":negative_squared_cross_mark: | You do not have the required NecroBot permissions to use this command.", delete_after=10)
        elif isinstance(error, commands.CommandOnCooldown):
            await channel.send(":negative_squared_cross_mark: | This command is on cooldown, retry after **{0:.0f}** seconds".format(error.retry_after), delete_after=10)
        elif isinstance(error, commands.NoPrivateMessage):
            await channel.send(":negative_squared_cross_mark: | This command cannot be used in private messages.", delete_after=10)
        elif isinstance(error, commands.DisabledCommand):
            await channel.send(":negative_squared_cross_mark: | This command is disabled and cannot be used for now.", delete_after=10)
        elif isinstance(error, commands.BadArgument):
            await channel.send(":negative_squared_cross_mark: | Something went wrongs with the arguments you sent, make sure you're sending what is required.", delete_after=10)
        elif isinstance(error, discord.errors.Forbidden):
            await channel.send(":negative_squared_cross_mark: | Something went wrong, check my permission level, it seems I'm not allowed to do that on your guild.", delete_after=10)
        elif isinstance(error, commands.CommandInvokeError):
            print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
            traceback.print_tb(error.original.__traceback__)
            print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)

    async def on_guild_join(self, guild):
        self.server_data[guild.id] = {"mute":"","automod":"","welcome-channel":"", "selfRoles":[],"ignoreCommand":[],"ignoreAutomod":[],"welcome":"Welcome {member} to {server}!","goodbye":"Leaving so soon? We\'ll miss you, {member}!","tags":{}, "prefix" : "", "broadcast-channel": "", "broadcast": "", "broadcast-time": "", "disabled": [], "auto-role": ""}

        for member in guild.members:
            self.default_stats(member, guild)

        await guild.owner.send(":information_source: I've just been invited to a server you own. Everything is good to go, your server has been set up on my side. However, most of my automatic functionalities are disabled by default (automoderation, welcome-messages and mute). You just need to set those up using `n!settings`. Check out the help with `n!help settings`")

    async def on_message_delete(self, message):
        if isinstance(message.channel, discord.DMChannel) or self.server_data[message.guild.id]["automod"] == "" or message.author.bot:
            return

        role_id = [role.id for role in message.author.roles]
        if message.author.id not in self.server_data[message.guild.id]["ignoreAutomod"] and message.channel.id not in self.server_data[message.guild.id]["ignoreAutomod"] and not any(x in role_id for x in self.server_data[message.guild.id]["ignoreAutomod"]):
            fmt = '**Auto Moderation: Deletion Detected!**\n Message by **{0.author}** was deleted in {0.channel.name}, it contained: ``` {0.content} ```'
            channel = self.get_channel(self.server_data[message.guild.id]["automod"])
            await channel.send(fmt.format(message))

    async def on_message_edit(self, before, after):
        if isinstance(before.channel, discord.DMChannel) or self.server_data[before.guild.id]["automod"] == "" or before.author.bot or before.content == after.content:
            return

        role_id = [role.id for role in before.author.roles]
        if before.author.id not in self.server_data[before.guild.id]["ignoreAutomod"] and before.channel.id not in self.server_data[before.guild.id]["ignoreAutomod"] and not any(x in role_id for x in self.server_data[before.guild.id]["ignoreAutomod"]):
            fmt = '**Auto Moderation: Edition Detected!**\n{0.author} edited their message: \n**Before**``` {0.content} ``` \n**After** ``` {1.content} ```'
            channel = self.get_channel(self.server_data[before.guild.id]["automod"])
            await channel.send(fmt.format(before, after))


    async def on_member_join(self, member):
        self.default_stats(member, member.guild)

        if not self.server_data[member.guild.id]["welcome-channel"] == "" and not member.bot and not self.server_data[member.guild.id]["welcome"] == "":
            channel = self.get_channel(self.server_data[member.guild.id]["welcome-channel"])
            message = self.server_data[member.guild.id]["welcome"]
            await channel.send(message.format(member=member.mention, server=member.guild.name))

        if not self.server_data[member.guild.id]["auto-role"] == "":
            role = discord.utils.get(member.guild.roles, id=self.server_data[member.guild.id]["auto-role"])
            await member.add_roles(role)


    async def on_member_remove(self, member):
        if self.user_data[member.id]["perms"][member.guild.id] < 6:
            self.user_data[member.id]["perms"][member.guild.id] = 0

        if self.server_data[member.guild.id]["welcome-channel"] == "" or member.bot or self.server_data[member.guild.id]["goodbye"] == "":
            return

        channel = self.get_channel(self.server_data[member.guild.id]["welcome-channel"])
        message = self.server_data[member.guild.id]["goodbye"]

        await channel.send(message.format(member=member.mention))

    async def on_command(self, ctx):
        self.logit(ctx.message)

    async def on_message(self, message):
        user_id = message.author.id
        channel_id = message.channel.id
        regex_match = r"(https://modding-union\.com/index\.php/topic).\d*"

        if message.author.bot:
            return

        if "https://modding-union.com/index.php/topic" in message.content:
            url = re.search(regex_match, message.content).group(0)
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    soup = BeautifulSoup(await resp.text(), "html.parser")

            await self._mu_auto_embed(soup, url, message)

        if not isinstance(message.channel, discord.DMChannel):
            self.user_data[user_id]["exp"] += random.randint(2,5)

            if not self._is_allowed_summon(message) and self._startswith_prefix(message):
                await message.delete()
                await message.channel.send(":negative_squared_cross_mark: | Commands not allowed in the channel or you are being ignored.", delete_after=5)
                return

            if message.content.startswith(self.user.mention):
                await message.channel.send(random.choice(replyList))

        await self.process_commands(message)


bot = NecroBot()
bot.run(token)