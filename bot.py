import discord
from discord.ext import commands

from rings.utils.help import NecroBotHelpFormatter
from config import token, dbpass

import random
import sys
import time as t
import asyncio
import traceback
import re
from bs4 import BeautifulSoup
import aiohttp
from PIL import Image
import os
import functools
import psycopg2
import asyncpg
import json

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
    "economy",
    "events",
    "waifu"
]

replyList = [
    "*yawn* What can I do fo... *yawn*... for you?", 
    "NecroBot do that, NecroBot do this, never NecroBot how are y... Oh, hey how can I help?",
    "I wonder how other bots are treated :thinking: Do they also put up with their owners' terrible coding habits?",
    "Second sight ordains it! I mean sure..."
    ]

class NecroBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_pre, description="A bot for moderation and LOTR", formatter=NecroBotHelpFormatter(), case_insensitive=True, owner_id=241942232867799040, activity=discord.Game(name="Bot booting...", type=0))
        self.uptime_start = t.time()
        self.user_data = dict()
        self.server_data = dict()

        self.ERROR_LOG = 351356683231952897
        self.version = 1.5
        self.prefixes = ["n!", "N!", "n@"]
        self.new_commands = ["convert", "blacklist", "ttt", "star"]

        self.bg_task = self.loop.create_task(self.hourly_task())
        self.loop.create_task(self.load_cache())
        self.session = aiohttp.ClientSession(loop=self.loop)
        
        self.cat_cache = []
        self.starred = []
        self.events = {}

        @self.check
        def disabled_check(ctx):
            if ctx.guild is None:
                return True

            return not (ctx.command.name in self.server_data[ctx.message.guild.id]["disabled"] and ctx.prefix != "n@")
                
        self.add_check(disabled_check)

        with open("rings/utils/data/settings.json", "rb") as infile:
            self.settings = json.load(infile) 

        conn = psycopg2.connect(dbname="postgres", user="postgres", password=dbpass)
        cur = conn.cursor()

        #create server cache
        cur.execute("SELECT * FROM necrobot.Guilds;")
        for g in cur.fetchall():
            self.server_data[g[0]] = {
                            "mute": g[1] if g[1] != 0 else "", 
                            "automod":g[2] if g[2] != 0 else "", 
                            "welcome-channel":g[3] if g[3] != 0 else "", 
                            "welcome":g[4], 
                            "goodbye":g[5], 
                            "prefix":g[6],
                            "broadcast-channel":g[7] if g[7] != 0 else "",
                            "broadcast":g[8],
                            "broadcast-time":g[9],
                            "starboard-channel":g[10] if g[10] != 0 else "",
                            "starboard-limit":g[11],
                            "auto-role":g[12] if g[12] != 0 else "",
                            "self-roles":[],
                            "ignore-command":[],
                            "ignore-automod":[],
                            "tags":{},
                            "disabled":[]
                        }

        cur.execute("SELECT * FROM necrobot.SelfRoles;")
        for g in cur.fetchall():
            self.server_data[g[0]]["self-roles"].append(g[1])

        cur.execute("SELECT * FROM necrobot.Disabled;")
        for g in cur.fetchall():
            self.server_data[g[0]]["disabled"].append(g[1])

        cur.execute("SELECT * FROM necrobot.IgnoreAutomod;")
        for g in cur.fetchall():
            self.server_data[g[0]]["ignore-automod"].append(g[1])

        cur.execute("SELECT * FROM necrobot.IgnoreCommand;")
        for g in cur.fetchall():
            self.server_data[g[0]]["ignore-command"].append(g[1])

        cur.execute("SELECT * FROM necrobot.Tags;")
        for g in cur.fetchall():
            self.server_data[g[0]]["tags"][g[1]] = {"content":g[2], "owner":g[3], "counter":g[4], "created":g[5]}

        #create user cache
        cur.execute("SELECT * FROM necrobot.Users;")
        for u in cur.fetchall():
            self.user_data[u[0]] = {
                            "money": u[1],
                            "exp": u[2],
                            "daily": u[3],
                            "badges": u[4].split(",") if u[4] != "" else [],
                            "title":u[5],
                            "perms":{},
                            "waifu":{},
                            "places":{},
                            "warnings":{}
                        }

        cur.execute("SELECT * FROM necrobot.Permissions;")
        for u in cur.fetchall():
            self.user_data[u[1]]["perms"][u[0]] = u[2]
            self.user_data[u[1]]["warnings"][u[0]] = []

        cur.execute("SELECT * FROM necrobot.Warnings;")
        for u in cur.fetchall():
            self.user_data[u[1]]["warnings"][u[3]].append(u[4])

        cur.execute("SELECT * FROM necrobot.Badges;")
        for u in cur.fetchall():
            self.user_data[u[0]]["places"][u[1]] = u[2]

        cur.execute("SELECT * FROM necrobot.Waifu;")
        for u in cur.fetchall():
            self.user_data[u[0]]["waifu"][u[1]] = {
                            "waifu-value":u[2],
                            "waifu-claimer": u[3] if u[3] != 0 else "",
                            "affinity": u[4] if u[4] != 0 else "",
                            "heart-changes":u[5],
                            "divorces":u[6],
                            "flowers":u[7],
                            "waifus":[],
                            "gifts":{}
                        }

        cur.execute("SELECT * FROM necrobot.Waifus;")
        for u in cur.fetchall():
            self.user_data[u[0]]["waifu"][u[1]]["waifus"].append(u[2])

        cur.execute("SELECT * FROM necrobot.Gifts;")
        for u in cur.fetchall():
            self.user_data[u[0]]["waifu"][u[1]]["gifts"][u[2]] = u[3]


    # *****************************************************************************************************************
    #  Internal Function
    # *****************************************************************************************************************
    def _new_server(self):
        return {"mute":"","automod":"","welcome-channel":"", "self-roles":[],"ignore-command":[],"ignore-automod":[],"welcome":"Welcome {member} to {server}!","goodbye":"Leaving so soon? We\'ll miss you, {member}!","tags":{}, "prefix" : "", "broadcast-channel": "", "broadcast": "", "broadcast-time": 1, "disabled": [], "auto-role": "", "starboard-channel":"", "starboard-limit":5} 
    
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

        if user_id in self.server_data[message.guild.id]["ignore-command"] or channel_id in self.server_data[message.guild.id]["ignore-command"] or any(x in role_id for x in self.server_data[message.guild.id]["ignore-command"]):
            return False

        return True

    async def _mu_auto_embed(self, url, message):
        async with self.session.get(url) as resp:
            soup = BeautifulSoup(await resp.text(), "html.parser")

        try:
            header = list(soup.find_all("h3", class_="catbg")[-1].stripped_strings)[1].replace("Thema: ", "").split(" \xa0")
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

    async def _bmp_converter(self, message):
        attachment = message.attachments[0]
        await attachment.save(attachment.filename)

        im = Image.open(attachment.filename)
        im.save('{}.png'.format(attachment.filename))
        ifile = discord.File('{}.png'.format(attachment.filename))
        await message.channel.send(file=ifile)

        os.remove("{}.png".format(attachment.filename))
        os.remove(attachment.filename)

    async def _star_message(self, message):
        embed = discord.Embed(colour=discord.Colour(0x277b0), description = message.content)
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url.replace("webp","jpg"))
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")
        if message.embeds:
            data = message.embeds[0]
            if data.type == 'image':
                embed.set_image(url=data.url)

        if message.attachments:
            file = message.attachments[0]
            if file.url.lower().endswith(('png', 'jpeg', 'jpg', 'gif', 'webp')):
                embed.set_image(url=file.url)
            else:
                embed.add_field(name='Attachment', value=f'[{file.filename}]({file.url})', inline=False)
        
        await self.get_channel(self.server_data[message.guild.id]["starboard-channel"]).send(content="In {}".format(message.channel.mention), embed=embed)
        self.starred.append(message.id)

    # *****************************************************************************************************************
    #  Background Tasks
    # *****************************************************************************************************************
    async def _save(self):
        #upload user cache
        cached_users = self.user_data
        for user in cached_users:
            u = cached_users[user]
            await self.query_executer("UPDATE necrobot.Users SET necroins = $1, exp = $2, badges = $4 WHERE user_id = $3;",
                            u["money"], u["exp"], user, ",".join(u["badges"]))

            for guild in u["waifu"]:
                w = u["waifu"][guild]
                await self.query_executer("UPDATE necrobot.Waifu SET value = $1, flowers = $2 WHERE user_id = $3 AND guild_id = $4;", 
                                w["waifu-value"], w["flowers"], user, guild)

        with open("rings/utils/data/settings.json", "w") as outfile:
            json.dump(self.settings, outfile)
                
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
            await log.send("Initiating hourly save")
            await self._save()
            await log.send("Hourly save at {}".format(t.asctime(t.localtime(t.time()))))

            # background tasks
            for guild in self.server_data:
                hour_mod = counter % self.server_data[guild]["broadcast-time"]
                if self.server_data[guild]["broadcast"] != "" and self.server_data[guild]["broadcast-channel"] != "" and hour_mod == 0:
                    channel = self.get_channel(self.server_data[guild]["broadcast-channel"])
                    await channel.send(self.server_data[guild]["broadcast"])

    async def load_cache(self):
        await self.wait_until_ready()
        await asyncio.sleep(1)

        self.pool = await asyncpg.create_pool(database="postgres", user="postgres", password=dbpass)
        channel = self.get_channel(318465643420712962)
        msg = await channel.send("**Initiating Bot**")

        for guild in self.guilds:
            if guild.id not in self.server_data:
                    self.server_data[guild.id] = self._new_server()
                    await self.query_executer("INSERT INTO necrobot.Guilds VALUES($1, 0, 0, 0, 'Welcome {member} to {server}!', 'Leaving so soon? We''ll miss you, {member}!)', '', 0, '', 1, 0, 5, 0);", guild.id)
        await msg.edit(content="All servers checked")

        members = self.get_all_members()
        for member in members:
            await self.default_stats(member, member.guild)
            
        await msg.edit(content="All members checked")
        await msg.edit(content="**Bot Online**")

        await self.change_presence(game=discord.Game(name="n!help for help", type=0))

    async def query_executer(self, query, *args):
        conn = await self.pool.acquire()
        result = []
        try:
            if query.startswith("SELECT"):
                result = await conn.fetch(query, *args)
            else:
                await conn.execute(query, *args)
        except Exception as error:
            channel = self.get_channel(415169176693506048)
            the_traceback = "```py\n" + " ".join(traceback.format_exception(type(error), error, error.__traceback__, chain=False)) + "\n```"
            embed = discord.Embed(title="DB Error", description=the_traceback, colour=discord.Colour(0x277b0))
            embed.add_field(name='Event', value=error)
            embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")
            await channel.send(embed=embed)
        finally:
            await self.pool.release(conn)
            return result

    # *****************************************************************************************************************
    #  Internal Checks
    # *****************************************************************************************************************
    async def default_stats(self, member, guild):
        if member.id not in self.user_data:
            self.user_data[int(member.id)] = {'money': 200, 'daily': '', 'title': '', 'exp': 0, 'perms': {}, 'badges':[], "waifu":{}, "warnings": {}, 'places':{"1":"", "2":"", "3":"", "4":"", "5":"", "6":"", "7":"", "8":""}}
            await self.query_executer("INSERT INTO necrobot.Users VALUES ($1, 200, 0, '          ', '', '');", member.id)
            await self.query_executer("""INSERT INTO necrobot.Badges VALUES ($1, 1, ''), ($1, 2, ''), ($1, 3, ''),
                                                                            ($1, 4, ''), ($1, 5, ''), ($1, 6, ''),
                                                                            ($1, 7, ''), ($1, 8, '');""", member.id)

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

            await self.query_executer("INSERT INTO necrobot.Permissions VALUES ($1,$2,$3);", guild.id, member.id, self.user_data[member.id]["perms"][guild.id])

        if guild.id not in self.user_data[member.id]["waifu"]:
            self.user_data[member.id]["waifu"][guild.id] = {"waifu-value":50, "waifu-claimer":"", "affinity":"", "heart-changes":0, "divorces":0, "waifus":[], "flowers":0, "gifts":{}}
            await self.query_executer("INSERT INTO necrobot.Waifu VALUES ($1,$2,50,0,0,0,0,0);", member.id, guild.id)

    # *****************************************************************************************************************
    # Events
    # *****************************************************************************************************************
    async def on_ready(self):
        print(self.server_data)
        print('------')
        print("Logged in as {0.user}".format(self))

    async def on_message(self, message):
        user_id = message.author.id
        channel_id = message.channel.id
        regex_match = r"(https://modding-union\.com/index\.php/topic).\d*"

        if message.author.bot or message.author.id in self.settings["blacklist"]:
            return

        url = re.search(regex_match, message.content)
        if not url is None:
            await self._mu_auto_embed(url.group(0), message)

        if message.attachments:
            if ".bmp" in message.attachments[0].filename:
                await self._bmp_converter(message)

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

for extension in extensions:
    try:
        bot.load_extension("rings."+extension)
    except Exception as e:
        print(f'Failed to load extension {extension}.', file=sys.stderr)
        traceback.print_exc()

bot.run(token)
