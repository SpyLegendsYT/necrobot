#!/usr/bin/python3.6
#!/usr/bin/env python -W ignore::DeprecationWarning

import discord
from discord.ext import commands
from simpleeval import simple_eval
import time
import random
import re
import asyncio
import urbandictionary as ud
import googletrans
from PyDictionary import PyDictionary 
from bs4 import BeautifulSoup
from rings.utils.utils import has_perms, react_menu

class NecroBotPyDict(PyDictionary):
    def __init__(self, *args):
        try:
            if isinstance(args[0], list):
                self.args = args[0]
            else:
                self.args = args
        except:
            self.args = args

    @staticmethod
    async def meaning(term):
        if len(term.split()) > 1:
            return None
        else:
            try:
                async with self.bot.session.get("http://wordnetweb.princeton.edu/perl/webwn?s={0}".format(term)) as resp:
                    html = BeautifulSoup(await resp.text(), "html.parser")
                types = html.findAll("h3")
                length = len(types)
                lists = html.findAll("ul")
                out = {}
                for a in types:
                    reg = str(lists[types.index(a)])
                    meanings = []
                    for x in re.findall(r'\((.*?)\)', reg):
                        if 'often followed by' in x:
                            pass
                        elif len(x) > 5 or ' ' in str(x):
                            meanings.append(x)
                    name = a.text
                    out[name] = meanings
                return out
            except Exception as e:
                return None

dictionary = NecroBotPyDict() 
translator = googletrans.Translator()


class Utilities():
    """A bunch of useful commands to do various tasks."""
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}
        for guild in self.bot.guilds:
            self.queue[guild.id] = {"end": True, "list" : []}

    @commands.command()
    async def calc(self, ctx, *, equation : str):
        """Evaluates a pythonics mathematical equation, use the following to build your mathematical equations:
        `*` - for multiplication
        `+` - for additions
        `-` - for substractions
        `/` - for divisons
        `**` - for exponents
        `%` - for modulo
        More symbols can be used, simply research 'python math symbols'
        
        {usage}
        
        __Example__
        `{pre}calc 2 + 2` - 4
        `{pre}calc (4 + 5) * 3 / (2 - 1)` - 27
        """
        try:
            final = simple_eval(equation)
            await ctx.send(":1234: | **" + str(final) + "**")
        except NameError:
            await ctx.send(":negative_squared_cross_mark: | **Mathematical equation not recognized.**")

    @commands.command(aliases=["pong"])
    async def ping(self, ctx):
        """Pings the user and returns the time it took. 
        
        {usage}"""
        pingtime = time.time()
        pingms = await ctx.send(" :clock1: | Pinging... {}'s location".format(ctx.message.author.display_name))
        ping = time.time() - pingtime
        await pingms.edit(content=":white_check_mark: | The ping time is `% .01f seconds`" % ping)

    #prints a rich embed of the server info it was called in
    @commands.command()
    async def serverinfo(self, ctx):
        """Returns a rich embed of the server's information. 
        
        {usage}"""
        guild = ctx.message.guild
        embed = discord.Embed(title="__**{}**__".format(guild.name), colour=discord.Colour(0x277b0), description="Info on this server")
        embed.set_thumbnail(url=guild.icon_url.replace("webp","jpg"))
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

        embed.add_field(name="**Date Created**", value=guild.created_at.strftime("%d - %B - %Y %H:%M"))
        embed.add_field(name="**Owner**", value=guild.owner.name + "#" + guild.owner.discriminator, inline=True)

        embed.add_field(name="**Members**", value=guild.member_count, inline=True)

        embed.add_field(name="**Region**", value=guild.region)
        embed.add_field(name="**Server ID**", value=guild.id, inline=True)

        channel_list = [channel.name for channel in guild.channels]
        channels = ", ".join(channel_list) if len(", ".join(channel_list)) < 1024 else ""
        role_list = [role.name for role in guild.roles]
        roles = ", ".join(role_list) if len(", ".join(role_list)) < 1024 else ""
        embed.add_field(name="**Channels**", value="{}: {}".format(len(channel_list), channels))
        embed.add_field(name="**Roles**", value="{}: {}".format(len(role_list), roles))

        await ctx.send(embed=embed)

    @commands.command()
    async def avatar(self, ctx,* , user : discord.Member=None):
        """Returns a link to the given user's profile pic 
        
        {usage}
        
        __Example__
        `{pre}avatar @NecroBot` - return the link to NecroBot's avatar"""
        if user is None:
            user = ctx.message.author
        avatar = user.avatar_url_as(format="png")
        await ctx.send(avatar)

    @commands.command()
    async def today(self, ctx, choice : str = None, date : str = None):
        """Creates a rich information about events/deaths/births that happened today or any day you indicate using the 
        `dd/mm` format. The choice argument can be either `events`, `deaths` or `births`.

        {usage}

        __Example__
        `{pre}today` - prints five events/deaths/births that happened today
        `{pre}today 14/02` - prints five events/deaths/births that happened on the 14th of February
        `{pre}today events` - prints five events that happened today
        `{pre}today events 14/02` - prints five events that happened on the 14th of February
        `{pre}today deaths` - prints deaths that happened today
        `{pre}today deaths 14/02` - prints deaths that happened on the 14th of February
        `{pre}today births` - prints births that happened today
        `{pre}today births 14/02` - prints births that happened on the 14th of February"""

        if date:
            r_date = date.split("/")
            date = "/{}/{}".format(r_date[1], r_date[0])
        else:
            date = ""

        if choice:
            choice = choice.lower().title()
        else:
            choice = random.choice(["Deaths", "Births", "Events"])

        if not choice in ["Deaths", "Births", "Events"]:
            await ctx.send(":negative_squared_cross_mark: | Not a correct choice. Correct choices are `Deaths`, `Births` or `Events`.")
            return

        async with self.bot.session.get('http://history.muffinlabs.com/date'+date) as r:
            try:
                res = await r.json()
            except:
                 res = await r.json(content_type="application/javascript")

        def _embed_generator(index):
            embed = discord.Embed(title="__**" + res["date"] + "**__", colour=discord.Colour(0x277b0), url=res["url"], description="Necrobot is proud to present: **{} today in History**\n Page {}/{}".format(choice, index+1, len(res["data"][choice])//5+1))
            embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")
            for event in res["data"][choice][5*index:(index+1)*5]:
                try:
                    if choice == "Events":
                        link_list = "".join(["\n-[{}]({})".format(x["title"], x["link"]) for x in event["links"]])
                        embed.add_field(name="Year {}".format(event["year"]), value="{}\n__Links__{}".format(event["text"], link_list), inline=False)
                    elif choice == "Deaths":
                        embed.add_field(name="Year {}".format(event["year"]), value="[{}]({})".format(event["text"].replace("b.","Birth: "), event["links"][0]["link"]), inline=False)
                    elif choice == "Births":
                        embed.add_field(name="Year {}".format(event["year"]), value="[{}]({})".format(event["text"].replace("d.","Death: "), event["links"][0]["link"]), inline=False)
                except AttributeError:
                    pass

            return embed

        random.shuffle(res["data"][choice])
        await react_menu(self.bot, ctx, len(res["data"][choice])//5, _embed_generator)

    @commands.command(name="ud", aliases=["urbandictionary"])
    async def udict(self, ctx, *, word : str):
        """Searches for the given word on urban dictionnary

        {usage}

        __Example__
        `{pre}ud pimp` - searches for pimp on Urban dictionnary"""
        try:
            defs = ud.define(word)
            definition = defs[0]
        except IndexError:
            await ctx.send(":negative_squared_cross_mark: | Sorry, I didn't find a definition for this word.")
            return

        embed = discord.Embed(title="__**{}**__".format(word.title()), url="http://www.urbandictionary.com/", colour=discord.Colour(0x277b0), description=definition.definition)
        embed.add_field(name="__Examples__", value=definition.example)

        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def translate(self, ctx, lang : str, *, sentence : str):
        """Auto detects the language of the sentence you input and translates it to the desired language.

        {usage}

        __Example__
        `{pre}translate en Bonjour` - detects french and translates to english
        `{pre}translate ne Hello` - detects english and translates to dutch"""
        try:
            translated = translator.translate(sentence, dest=lang)
            await ctx.send("Translated `{0.origin}` from {0.src} to {0.dest}: **{0.text}**".format(translated))
        except ValueError:
            await ctx.send(":negative_squared_cross_mark: | No such language, do `n!translate list` for all languages (Warning: Big text blob)")
    
    @translate.command(name="list")
    async def translate_list(self, ctx):
        """Use to display all possible languages to translate from

        {usage}"""
        text = ", ".join(["**{}**: {}".format(googletrans.LANGUAGES[lang], lang) for lang in googletrans.LANGUAGES])
        await ctx.send(text[:-2])

    @commands.command()
    async def define(self, ctx, word : str):
        """Defines the given word

        {usage}

        __Example__
        `{pre}define sand` - defines the word sand
        `{pre}define life` - defines the word life"""
        meaning = await dictionary.meaning(word)
        if meaning is None:
            await ctx.send(":negative_squared_cross_mark: | **No definition found for this word**")
            return

        embed = discord.Embed(title="__**{}**__".format(word.title()), url="https://en.oxforddictionaries.com/", colour=discord.Colour(0x277b0), description="Information on this word")
        for x in meaning:
            embed.add_field(name=x, value="-" + "\n-".join(meaning[x]))

        await ctx.send(embed=embed)

    @commands.command(enabled=False)
    async def reminder(self, ctx, *, message):
        """Creates a reminder in seconds. Doesn't work at the moment.

        {usage}

        __Examples__
        `{pre}reminder do the dishes in 40` - will remind you to do the dishes in 40 seconds"""
        if "in" not in message:
            await ctx.send(":negative_squared_cross_mark: | Something went wrong, you need to use the format <message> in <time>")

        text = message.split(" in ")[0]
        time =int(message.split(" in ")[1])
        await ctx.send(":white_check_mark: | Okay I will remind you in **{}** seconds of **{}**".format(time, text))

        await asyncio.sleep(time)

        await ctx.send(":alarm_clock: | You asked to be reminded: **{}**".format(text))

    @commands.group(invoke_without_command=True)
    async def q(self, ctx):
        """Displays the content of the queue at the moment.

        {usage}"""
        if len(self.queue[ctx.guild.id]["list"]) > 0:
            queue = ["**" + ctx.guild.get_member(x).display_name + "**" for x in self.queue[ctx.guild.id]["list"]]
            await ctx.send("So far the queue has the following users in it:\n-{}".format("\n-".join(queue)))
        else:
            await ctx.send("So far this queue has no users in it.")

    @q.command(name="start")
    @has_perms(2)
    async def q_start(self, ctx):
        """Starts a queue, if there is already an ongoing queue it will fail. The ongoing queue must be cleared first using `{pre}q clear`.

        {usage}"""
        if len(self.queue[ctx.guild.id]["list"]) > 0:
            await ctx.send(":negative_squared_cross_mark: | A queue is already ongoing, please clear the queue first")
            return

        self.queue[ctx.guild.id] = {"end": False, "list" : []}
        await ctx.send(":white_check_mark: | Queue initialized")

    @q.command(name="end")
    @has_perms(2)
    async def q_end(self, ctx):
        """Ends a queue but does not clear it. Users will no longer be able to use `{pre}q me`

        {usage}"""
        self.queue[ctx.guild.id]["end"] = True
        await ctx.send(":white_check_mark: | Users will now not be able to add themselves to queue")

    @q.command(name="clear")
    @has_perms(2)
    async def q_clear(self, ctx):
        """Ends a queue and clears it. Users will no longer be able to add themselves and the content of the queue will be 
        emptied. Use it in order to start a new queue

        {usage}"""
        self.queue[ctx.guild.id]["list"] = []
        self.queue[ctx.guild.id]["end"] = True
        await ctx.send(":white_check_mark: | Queue cleared and ended. Please start a new queue to be able to add users again")

    @q.command(name="me")
    async def q_me(self, ctx):
        """Queue the user that used the command to the current queue. Will fail if queue has been ended or cleared.

        {usage}"""
        if self.queue[ctx.guild.id]["end"]:
            await ctx.send(":negative_squared_cross_mark: | Sorry, you can no longer add yourself to the queue")
            return

        if ctx.author.id in self.queue[ctx.guild.id]["list"]:
            await ctx.send(":white_check_mark: | You have been removed from the queue")
            self.queue[ctx.guild.id]["list"].remove(ctx.author.id)
            return

        self.queue[ctx.guild.id]["list"].append(ctx.author.id)
        await ctx.send(":white_check_mark: |  You have been added to the queue")

    @q.command(name="next")
    @has_perms(2)
    async def q_next(self, ctx):
        """Mentions the next user and the one after that so they can get ready.
        
        {usage}"""
        if len(self.queue[ctx.guild.id]["list"]) < 1:
            await ctx.send(":negative_squared_cross_mark: | No users left in that queue")
            return

        msg = ":bell: | {}, you're next. Get ready!".format(ctx.guild.get_member(self.queue[ctx.guild.id]["list"][0]).mention)

        if len(self.queue[ctx.guild.id]["list"]) > 1:
            msg += " \n{}, you're right after them. Start warming up!".format(ctx.guild.get_member(self.queue[ctx.guild.id]["list"][1]).mention)
        else:
            msg += "\nThat's the last user in the queue"

        await ctx.send(msg)
        self.queue[ctx.guild.id]["list"].pop(0)

    @commands.command()
    async def convert(self, ctx, measure : float, symbol, conversion = None):
        """The ultimate conversion tool to breach the gap with America/UK and the rest of the world. Can convert most metric
        units to imperial and most imperial units to metric. This works for lenght, temperature and mass measures.

        {usage}

        __Example__
        `{pre}convert 10 ft m` - convert 10 feet into meters
        `{pre}convert 5 km in`  - convert 5 kilometers to inches"""
        def m_to_i(measure, symbol, conversion):
            index = m_values.index(symbol)
            for value in range(0, index+1):
                measure = measure * 10

            measure = measure / 25.4

            index = i_values.index(conversion)
            for value in i_conver[index:]:
                measure = measure / value

            return measure

        def i_to_m(measure, symbol, conversion):
            index = i_values.index(symbol)
            for value in i_conver[index:]:
                measure = measure * value

            measure = measure * 25.4

            index = m_values.index(conversion)
            for value in range(0, index+1):
                measure = measure / 10

            return measure

        def temp(f=None, c=None):
            if c:
                return c * 9/5 + 32

            if f:
                return (f - 32) * 5/9

        def mass_i_to_m(measure, symbol, conversion):
            index = mass_i_values.index(symbol)
            for value in mass_i_conver[index:]:
                measure = measure * value

            measure = measure * 28349.5

            index = mass_m_values.index(conversion)
            for value in range(0, index):
                measure = measure / 10

            return measure

        def mass_m_to_i(measure, symbol, conversion):
            index = mass_m_values.index(symbol)
            for value in range(0, index):
                measure = measure * 10

            measure = measure / 28349.5

            index = mass_i_values.index(conversion)
            for value in mass_i_conver[index:]:
                measure = measure / value

            return measure

        m_values = ['mm', 'cm', 'm', 'km']
        i_values = ["ml", "yd", "ft", "in"]
        i_conver = [1760, 3, 12]

        mass_m_values = ["mg", "g", "kg", "t"]
        mass_i_values = ["t", "lb", "oz"]
        mass_i_conver = [2204.62, 16]

        if symbol in m_values and conversion in i_values:
            measure = m_to_i(measure, symbol, conversion)
        elif symbol in i_values and conversion in m_values:
            measure = i_to_m(measure, symbol, conversion)
        elif symbol in mass_m_values and conversion in mass_i_values:
            measure = mass_m_to_i(measure, symbol, conversion)
        elif symbol in mass_i_values and conversion in mass_m_values:
            measure = mass_i_to_m(measure, symbol, conversion)
        elif symbol == 'c':
            measure = temp(c=measure)
        elif symbol == 'f':
            measure = temp(f=measure)
        else:
            msg = ":negative_squared_cross_mark: | Not a convertible symbol. \nImperial length unit symbols: {}\nImperial weight/mass unit symbols: {}\nMetric length unit symbols: {}\nMetric weight/mass unit symbols: {}\nTemperature unit symbols: c - f"
            await ctx.send(msg.format(" - ".join(i_values), " - ".join(mass_i_values), " - ".join(m_values), " - ".join(mass_m_values)))
            return

        await ctx.send(":white_check_mark: | **{}{}**".format(measure, conversion))

def setup(bot):
    bot.add_cog(Utilities(bot))

