import discord
from discord.ext import commands

from rings.utils.db import db_gen
from rings.utils.config import token, modio_api
from rings.utils.help import NecroBotHelpFormatter
from rings.utils.var import tutorial_e

import re
import json
import time
import random
import aiohttp
import datetime
import traceback
import async_modio

async def get_pre(bot, message):
    """If the guild has set a custom prefix we return that and the ability to mention alongside regular 
    admin prefixes if not we return the default list of prefixes and the ability to mention."""
    if not isinstance(message.channel, discord.DMChannel):
        guild_pre = bot.server_data[message.guild.id]["prefix"]
        if guild_pre != "":
            prefixes = [guild_pre, *bot.admin_prefixes]
            return commands.when_mentioned_or(*prefixes)(bot, message)

    return commands.when_mentioned_or(*bot.prefixes)(bot, message)

extensions = [
    "social",
    "wiki",
    "modding",
    "support",
    "utilities",
    "moderation",
    "profile",
    "server",
    "admin",
    "decisions",
    "economy",
    "events",
    "waifu",
    "words",
    "misc",
    "tags",
    "meta",
    "edain",
]

class NecroBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=get_pre, 
            description="A bot for moderation and LOTR", 
            formatter=NecroBotHelpFormatter(), 
            case_insensitive=True, 
            owner_id=241942232867799040, 
            activity=discord.Game(name="Bot booting..."),
            max_messages=25000
        )

        self.uptime_start = time.time()
        self.counter = datetime.datetime.now().hour

        self.user_data, self.server_data, self.starred, self.polls, self.games = db_gen()

        self.version = 2.8
        self.ready = False
        self.prefixes = ["n!", "N!", "n@", "N@"]
        self.admin_prefixes = ["n@", "N@"]
        self.new_commands = ["moddb", "modio"]
        self.statuses = ["n!help for help", "currently in {guild} guilds", "with {members} members", "n!report for bug/suggestions"]
        self.perms_name = ["User", "Helper", "Moderator", "Semi-Admin", "Admin", "Server Owner", "NecroBot Admin", "The Bot Smith"]
        
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.modio = async_modio.Client(api_key=modio_api)

        self.cat_cache = []
        self.events = {}
        self.ignored_messages = []

        @self.check
        def disabled_check(ctx):
            """This is the backbone of the disable command. If the command name is in disabled then
            we check to make sure that it's not an admin trying to invoke it with an admin prefix """
            if isinstance(ctx.message.channel, discord.DMChannel):
                return True

            disabled = self.server_data[ctx.message.guild.id]["disabled"]

            if ctx.command.name in disabled and ctx.prefix not in self.admin_prefixes:
                raise commands.CheckFailure("This command has been disabled")

            return True
                
        self.add_check(disabled_check)

        @self.check
        def allowed_summon(ctx):
            if isinstance(ctx.message.channel, discord.DMChannel):
                return True
                
            roles = [role.id for role in ctx.author.roles]
            user_id = ctx.author.id
            guild_id = ctx.guild.id

            if ctx.prefix in self.admin_prefixes:
                if self.user_data[user_id]["perms"][guild_id] > 0:
                    return True
                raise commands.CheckFailure("You are not allowed to use admin prefixes")

            if user_id in self.server_data[guild_id]["ignore-command"]:
                raise commands.CheckFailure("You are being ignored by the bot")

            if ctx.channel.id in self.server_data[guild_id]["ignore-command"]:
                raise commands.CheckFailure("Commands not allowed in this channel.")

            if any(x in roles for x in self.server_data[guild_id]["ignore-command"]):
                roles = [f"**{x.name}**" for x in ctx.author.roles if x.id in self.server_data[guild_id]["ignore-command"]]
                raise commands.CheckFailure(f"Roles {', '.join(roles)} aren't allowed to use commands.")

            return True

        self.add_check(allowed_summon)

        with open("rings/utils/data/settings.json", "rb") as infile:
            self.settings = json.load(infile)
        
        self.tutorial_e = discord.Embed.from_data(tutorial_e)

    async def on_ready(self):
        """If this is the first time the boot is booting then we load the cache and set the
        ready variable to True to signify the bot is ready. Else we assume that it means the
        bot had a hiccup and is resuming."""
        if not self.ready:
            await self.load_cache()
            self.ready = True
            print(self.server_data)
            print('------')
            print(f"Logged in as {self.user}")

    async def on_error(self, event, *args, **kwargs): 
        """Something has gone wrong so we just try to send a helpful traceback to the channel. If
        the traceback is too big we just send the method/event that errored out and hope that
        the error is obvious."""
        channel = self.get_channel(415169176693506048)

        the_traceback = f"```py\n{traceback.format_exc()}\n```"
        embed = discord.Embed(title="Error", description=the_traceback, colour=discord.Colour(0x277b0))
        embed.add_field(name='Event', value=event)
        embed.set_footer(text="Generated by NecroBot", icon_url=self.user.avatar_url_as(format="png", size=128))
        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            await channel.send(f"Bot: Ignoring exception in {event}")

    async def on_message(self, message):
        """Main processing unit for commands. This takes charge of embeding any MU posts, converting .bmp files,
        awarding xp if in a server or showing the tutorial tip if that user hasn't already seen it. Also very important
        we clean up the content of @everyone and @here if the user is less than a Server Semi-Admin because you don't
        need to mention everyone with the bot if you're less."""
        user_id = message.author.id
        regex_match = r"(https://modding-union\.com/index\.php/topic).\d*"
        
        #reject blacklisted users and system messages
        if message.author.bot or user_id in self.settings["blacklist"] or message.type != discord.MessageType.default:
            return

        #set the default stats for users just in case they're not already set
        await self.default_stats(message.author, message.guild)

        #search for mu links
        url = re.search(regex_match, message.content)
        if url:
            await self._mu_auto_embed(url.group(0), message)

        #search for any .bmp files to convert
        if message.attachments:
            if message.attachments[0].filename.endswith(".bmp"):
                await self._bmp_converter(message)

        #if this is on a guild clean the content and award xp
        if not isinstance(message.channel, discord.DMChannel):
            self.user_data[user_id]["exp"] += random.randint(2, 5)

            if self.user_data[user_id]["perms"][message.guild.id] < 3:
                message.content = message.content.replace("@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")
        else:
            #else make sure that they know they can clean up bot messages by reacting to them
            if not self.user_data[user_id]["tutorial"]:
                self.user_data[user_id]["tutorial"] = True
                await message.channel.send(":information_source: | Did you know you can delete my messages in DMs by reacting to them with :wastebasket:? Give it a shot, react to this message with :wastebasket: .")
                await self.query_executer("UPDATE necrobot.Users SET tutorial = 'True' WHERE user_id = $1", user_id)

        await self.process_commands(message)

if __name__ == '__main__':
    bot = NecroBot()

    for extension in extensions:
        bot.load_extension(f"rings.{extension}")   

    bot.run(token)
