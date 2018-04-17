#!/usr/bin/python3.6
import discord
from discord.ext import commands
from simpleeval import simple_eval
import inspect
from rings.utils.utils import has_perms
import datetime
import re

class GuildUserConverter(commands.IDConverter):
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

        match = self._get_id_match(argument) or re.match(r'<@!?([0-9]+)>$', argument)
        state = ctx._state

        if match is not None:
            user_id = int(match.group(1))
            result = bot.get_user(user_id)
        else:
            arg = argument
            # check for discriminator if it exists
            if len(arg) > 5 and arg[-5] == '#':
                discrim = arg[-4:]
                name = arg[:-5]
                predicate = lambda u: u.name == name and u.discriminator == discrim
                result = discord.utils.find(predicate, state._users.values())
                if result is not None:
                    return result

            predicate = lambda u: u.name == arg
            result = discord.utils.find(predicate, state._users.values())

        if result:
            return result

        raise commands.BadArgument("Not a known guild/user")


class Admin():
    def __init__(self, bot):
        self.bot = bot  

    # @commands.command()
    # async def x(self, ctx):
    #     def check(thing, author):
    #         if isinstance(thing, discord.Message):
    #             return "$" in thing.content

    #         if isinstance(thing, discord.Reaction):
    #             return str(thing.emoji) == "\N{WASTEBASKET}"

    #         return False

    #     thing, user = await self.bot.wait_for("both", check=check)

    #     if isinstance(thing, discord.Reaction):
    #         await ctx.send("User used reaction menu")
    #     elif isinstance(thing, discord.Message):
    #         await ctx.send("User used text menu")

    # @commands.command()
    # async def y(self, ctx, content):
    #     self.bot.dispatch("both", ctx.message, ctx.message.author)

    # @commands.command()
    # async def z(self, ctx):
    #     reaction, user = await self.bot.wait_for("reaction_add")
    #     self.bot.dispatch("both", reaction, user)

    @commands.command()
    @commands.is_owner()
    async def leave(self, ctx, id : int, *, reason : str ="unspecified"):
        """Leaves the specified server. (Permission level required: 7+ (The Bot Smith))
        {usage}"""
        guild = self.bot.get_guild(id)
        if guild:
            if reason != "unspecified":
                channel = [x for x in guild.text_channels if x.permissions_for(self.bot.user).send_messages][0]
                await channel.send("I'm sorry, Necro#6714 has decided I should leave this server, because: {}".format(reason))
            await guild.leave()
            await ctx.send(":white_check_mark: | Okay Necro, I've left {}".format(guild.name))
        else:
            await ctx.send(":negative_squared_cross_mark: | I'm not on that server")

    @commands.command(name="admin-perms")
    @commands.is_owner()
    async def a_perms(self, ctx, server : int, user : discord.Member, level : int):
        """For when regular perms isn't enough.

        {usage}"""
        self.bot.user_data[user.id]["perms"][server] = level
        await self.bot.query_executer("UPDATE necrobot.Permissions SET level = $1 WHERE guild_id = $2 AND user_id = $3;", level, server, user.id)
        await ctx.send(":white_check_mark: | All good to go, **"+ user.display_name + "** now has permission level **"+ str(level) + "** on server " + self.bot.get_guild(server).name)


    @commands.command()
    @has_perms(2)
    async def set(self, ctx, user : discord.Member):
        """Allows server specific authorities to set the default stats for a user that might have slipped past the 
        on_ready and on_member_join events (Permission level required: 2+ (Moderator))
         
        {usage}
        
        __Example__
        `{pre}setstats @NecroBot` - sets the default stats for NecroBot"""
        if user.id in self.bot.user_data:
            await ctx.send("Stats already set for user")
        else:
            await self.bot.default_stats(user, ctx.message.guild)
            await ctx.send("Stats set for user")

    @commands.command()
    @has_perms(6)
    async def add(self, ctx, user : discord.Member, *, equation : str):
        """Does the given pythonic equations on the given user's NecroBot balance. (Permission level required: 6+ (NecroBot Admin))
        `*` - for multiplication
        `+` - for additions
        `-` - for substractions
        `/` - for divisons
        `**` - for exponents
        `%` - for modulo
        More symbols can be used, simply research 'python math symbols'
        
        {usage}
        
        __Example__
        `{pre}add @NecroBot +400` - adds 400 to NecroBot's balance"""
        s = str(self.bot.user_data[user.id]["money"]) + equation
        try:
            operation = simple_eval(s)
            self.bot.user_data[user.id]["money"] = abs(int(operation))
            await ctx.send(":atm: | **{}'s** balance is now **{:,}** :euro:".format(user.display_name, self.bot.user_data[user.id]["money"]))
        except (NameError,SyntaxError):
            await ctx.send(":negative_squared_cross_mark: | Operation not recognized.")

    @commands.command()
    @has_perms(6)
    async def pm(self, ctx, user : discord.User, *, message : str):
        """Sends the given message to the user of the given id. It will then wait for an answer and 
        print it to the channel it was called it. (Permission level required: 6+ (NecroBot Admin))
        
        {usage}
        
        __Example__
        `{pre}pm 34536534253Z6 Hello, user` - sends 'Hello, user' to the given user id and waits for a reply"""
        await user.send(message)
        to_edit = await ctx.send(":white_check_mark: | **Message sent**")

        def check(m):
            return m.author == user and m.channel == user

        msg = await self.bot.wait_for("message", check=check)
        await to_edit.edit(content=":speech_left: | **User: {0.author}** said :**{0.content}**".format(msg))
        
    @commands.command()
    @commands.is_owner()
    async def get(self, ctx, id : int):
        """Returns the name of the user or server based on the given id. Used to debug the auto-moderation feature. 
        (Permission level required: 7+ (The Bot Smith))
        
        {usage}
        
        __Example__
        `{pre}get 345345334235345` - returns the user or server name with that id"""
        msg = await ctx.send("Scanning...")
        user = self.bot.get_user(id)
        if not user:
            await msg.edit(content="User: **{}#{}**".format(user.name, user.discriminator))
            return

        await msg.edit(content="User with that ID not found.")

        guild = self.bot.get_guild(id)
        if not guild:
            await msg.edit(content="Server: **{}**".format(guild.name))
            return

        await msg.edit(content="Server with that ID not found")

        channel = self.bot.get_channel(id)
        if not channel:
            await msg.edit(content="Channel: **{}** on **{}**".format(channel.name, channel.guild.name))
            return

        await msg.edit(content="Channel with that ID not found")

        role = discord.utils.get([x for x in y.roles for y in self.bot.guilds], id=id)
        if not role:
            await msg.edit(content="Role: **{}** on **{}**".format(role.name, role.guild.name))

        await msg.edit(content="Role with that ID not found")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def invites(self, ctx, *, guild : discord.Guild = None):
        """Returns invites (if the bot has valid permissions) for each server the bot is on if no guild is specified. 
        (Permission level required: 7+ (The Bot Smith))
        
        {usage}"""
        async def get_invite(guild):
            try:
                channel = [x for x in guild.text_channels if x.permissions_for(self.bot.user).create_instant_invite][0]
                invite = await channel.create_invite(max_age=86400)
                await ctx.send("Server: " + guild.name + "(" + str(guild.id) + ") - <" + invite.url + ">")
            except discord.errors.Forbidden:
                await ctx.send("I don't have the necessary permissions on " + guild.name + "(" + str(guild.id) + "). That server is owned by " + guild.owner.name + "#" + str(guild.owner.discriminator) + " (" + str(guild.id) + ")")
            except IndexError:
                await ctx.send("No text channels in " + guild.name + "(" + str(guild.id) + ")")

        if guild:
            await get_invite(guild)
        else:
            for guild in self.bot.guilds:
                await get_invite(guild)
            
    @commands.command()
    @commands.is_owner()
    async def debug(self, ctx, *, code : str):
        """Evaluates code. All credits to Danny for creating a safe eval command (Permission level required: 7+ (The Bot Smith)) 
        
        {usage}
        
        __Example__
        `It's python code, either you know it or you shouldn't be using this command`"""
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'server': ctx.message.guild,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'server_data' : self.bot.server_data,
            'user_data ' : self.bot.user_data
        }

        env.update(globals())

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await ctx.send(python.format(type(e).__name__ + ': {}'.format(e)))
            return

    @commands.command()
    @commands.is_owner()
    async def edit(self, ctx, *, code : str):
        """{usage}"""
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'server': ctx.message.guild,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'server_data' : self.bot.server_data,
            'user_data ' : self.bot.user_data
        }

        env.update(globals())

        try:
            result = exec(code, env)
            await ctx.send(":white_check_mark: | Don't forget to eval an SQL statement for permanent changes")
        except Exception as e:
            await ctx.send(python.format(type(e).__name__ + ': {}'.format(e)))
            return

    @commands.command()
    @commands.is_owner()
    async def sql(self, ctx,*, query : str):
        """{usage}"""
        try:
            self.bot.query_executer(query)
        except Exception as e:
            await ctx.send(python.format(type(e).__name__ + ': {}'.format(e)))
            return

    @commands.group(invoke_without_command=True)
    @has_perms(6)
    async def blacklist(self, ctx, *things : GuildUserConverter):
        """Blacklists a guild or user. If it is a guild, the bot will leave the guild. A user will simply be unable to 
        use the bot commands and react. However, they will still be automoderated.

        {usage}"""
        for thing in things:
            if isinstance(thing, discord.User):
                if thing.id in self.bot.settings["blacklist"]:
                    self.bot.settings["blacklist"].remove(thing.id)
                    await ctx.send(":white_check_mark: | User **{}** pardoned".format(thing.name))
                else:
                    try:
                        await thing.send(":negative_squared_cross_mark: | You have been blacklisted by NecroBot, if you wish to appeal your ban, join the support server. https://discord.gg/Ape8bZt")
                    except discord.Forbidden:
                        pass

                    self.bot.settings["blacklist"].append(thing.id)
                    await ctx.send(":white_check_mark: | User **{}** blacklisted".format(thing.name))
            elif isinstance(thing, discord.Guild):
                if thing.id in self.bot.settings["blacklist"]:
                    self.bot.settings["blacklist"].remove(thing.id)
                    await ctx.send(":white_check_mark: | Guild **{}** pardoned".format(thing.name))
                else:
                    await thing.owner.send(":negative_squared_cross_mark: | Your server has been blacklisted by NecroBot, if you wish to appeal your ban, join the support server. https://discord.gg/Ape8bZt")
                    await thing.leave()
                    self.bot.settings["blacklist"].append(thing.id)
                    await ctx.send(":white_check_mark: | Guild **{}** blacklisted".format(thing.name))

    @blacklist.command(name="list")
    @has_perms(6)
    async def blacklist_list(self, ctx):
        """Prints the list of all blacklisted users/guild

        {usage}"""
        if len(self.bot.settings["blacklist"]) < 1:
            await ctx.send("List of blacklisted users/guilds: **None**")
        else:
            await ctx.send("List of blacklisted users/guilds: {}".format(" - ".join([(await GuildUserConverter().convert(ctx, str(x))).name for x in self.bot.settings["blacklist"]])))


    # *****************************************************************************************************************
    #  Cogs Commands
    # *****************************************************************************************************************
    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, extension_name : str):
        """Loads the extension name if in NecroBot's list of rings.
        
        {usage}"""
        try:
            self.bot.load_extension("rings." + extension_name)
        except (AttributeError,ImportError) as e:
            await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, e))
            return
        await ctx.send("{} loaded.".format(extension_name))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, extension_name : str):
        """Unloads the extension name if in NecroBot's list of rings.
         
        {usage}"""
        self.bot.unload_extension("rings." + extension_name)
        await ctx.send("{} unloaded.".format(extension_name))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, extension_name : str):
        """Unload and loads the extension name if in NecroBot's list of rings.
         
        {usage}"""
        self.bot.unload_extension("rings." + extension_name)
        try:
            self.bot.load_extension("rings." + extension_name)
        except (AttributeError,ImportError) as e:
            await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, e))
            return
        await ctx.send("{} reloaded.".format(extension_name))

    # *****************************************************************************************************************
    # Bot Smith Commands
    # *****************************************************************************************************************
    @commands.command(hidden=True)
    @commands.is_owner()
    async def off(self, ctx):
        """Saves all the data and terminate the bot. (Permission level required: 7+ (The Bot Smith))
         
        {usage}"""
        msg = await ctx.send("Shut down?")
        await msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        await msg.add_reaction("\N{NEGATIVE SQUARED CROSS MARK}")

        def check(reaction, user):
            return user.id == 241942232867799040 and str(reaction.emoji) in ["\N{WHITE HEAVY CHECK MARK}", "\N{NEGATIVE SQUARED CROSS MARK}"] and msg.id == reaction.message.id
        
        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=300)
        except asyncio.TimeoutError:
            return

        if reaction.emoji == "\N{NEGATIVE SQUARED CROSS MARK}":
            await msg.delete()
        elif reaction.emoji == "\N{WHITE HEAVY CHECK MARK}":
            await msg.delete()
            await self.bot.change_presence(activity=discord.Game(name="Bot shutting down...", type=0))
            channel = self.bot.get_channel(318465643420712962)
            msg = await channel.send("**Saving...**")

            await self.bot._save()

            await msg.edit(content="**Saved**")
            await msg.edit(content="**Bot Offline**")
            await self.bot.session.close()
            await self.bot.logout()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def save(self, ctx):
        """Save data but doesn't terminate the bot

        {usage}"""
        await ctx.send(":white_check_mark: | Saving")
        await self.bot._save()
        await ctx.send(":white_check_mark: | Done saving")

def setup(bot):
    bot.add_cog(Admin(bot))