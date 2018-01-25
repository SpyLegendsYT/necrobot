#!/usr/bin/python3.6
import discord
from discord.ext import commands
from simpleeval import simple_eval
import inspect
from rings.utils.utils import has_perms
import json



class Admin():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def leave(self, ctx, id : int, *, reason : str ="unspecified"):
        """Leaves the specified server. (Permission level required: 7+ (The Bot Smith))
        {usage}"""
        guild = self.bot.get_guild(id)
        if not guild is None:
            channel = guild.text_channels[1]
            await channel.send("I'm sorry, Necro#6714 has decided I should leave this server, because: {}".format(reason))
            await guild.leave()
            await ctx.message.channel.send(":white_check_mark: | Okay Necro, I've left {}".format(guild.name))
        else:
            await ctx.message.channel.send(":negative_squared_cross_mark: | I'm not on that server")

    @commands.command(name="admin-perms")
    @commands.is_owner()
    async def a_perms(self, ctx, server : int, user : discord.Member, level : int):
        self.bot.user_data[user.id]["perms"][server] = level
        await ctx.message.channel.send(":white_check_mark: | All good to go, **"+ user.display_name + "** now has permission level **"+ str(level) + "** on server " + self.bot.get_guild(server).name)


    @commands.command()
    @has_perms(2)
    async def set(self, ctx, user : discord.Member):
        """Allows server specific authorities to set the default stats for a user that might have slipped past the on_ready and on_member_join events (Permission level required: 2+ (Moderator))
         
        {usage}
        
        __Example__
        `{pre}setstats @NecroBot` - sets the default stats for NecroBot"""
        if user.id in self.bot.user_data:
            await ctx.message.channel.send("Stats already for user")
        else:
            self.bot.default_stats(user, ctx.message.guild)
            await ctx.message.channel.send("Stats set for user")

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
            await ctx.message.channel.send(":atm: | **{}'s** balance is now **{:,}** :euro:".format(user.display_name, self.bot.user_data[user.id]["money"]))
        except (NameError,SyntaxError):
            await ctx.message.channel.send(":negative_squared_cross_mark: | Operation not recognized.")

    @commands.group()
    @has_perms(6)
    async def modify(self, ctx):
        pass

    @modify.command()
    async def modify_server(self, ctx, setting, *, value):
        try:
            self.bot.server_data[ctx.message.guild.id][setting] = value
            await ctx.message.channel.send(":white_check_mark: | `{}` for this server will now be `{}`".format(setting, value))
        except KeyError:
            await ctx.message.channel.send(":negative_squared_cross_mark: | Setting not found")

    @modify.command()
    async def modify_user(self, ctx, user:discord.Member, setting, *, value):
        try:
            self.bot.user_data[user.id][setting] = value
            await ctx.message.channel.send(":white_check_mark: | `{}` for this user will now be `{}`".format(setting, value))
        except KeyError:
            await ctx.message.channel.send(":negative_squared_cross_mark: | Setting not found")


    @commands.command()
    @has_perms(6)
    async def pm(self, ctx, id : int, *, message : str):
        """Sends the given message to the user of the given id. It will then wait 5 minutes for an answer and print it to the channel it was called it. (Permission level required: 6+ (NecroBot Admin))
        
        {usage}
        
        __Example__
        `{pre}pm 34536534253Z6 Hello, user` - sends 'Hello, user' to the given user id and waits for a reply"""
        user = self.bot.get_user(id)
        if not user is None:
            send = await user.send(message + "\n*You have 5 minutes to reply to the message*")
            to_edit = await ctx.message.channel.send(":white_check_mark: | **Message sent**")

            def check(m):
                return m.author == user and m.channel == send.channel

            msg = await self.bot.wait_for("message", check=check, timeout=300)
            await to_edit.edit(":speech_left: | **User: {0.author}** said :**{0.content}**".format(msg))
        else:
            await ctx.message.channel.send(":negative_squared_cross_mark: | No such user.")

    @commands.command()
    @commands.is_owner()
    async def test(self, ctx, id : int):
        """Returns the name of the user or server based on the given id. Used to debug the auto-moderation feature. (Permission level required: 7+ (The Bot Smith))
        
        {usage}
        
        __Example__
        `{pre}test 345345334235345` - returns the user or server name with that id"""
        user = self.bot.get_user(id)
        if not user is None:
            await ctx.message.channel.send("User: **{}#{}**".format(user.name, user.discriminator))
            return

        await ctx.message.channel.send("User with that ID not found.")

        guild = self.bot.get_guild(id)
        if not guild is None:
            await ctx.message.channel.send("Server: **{}**".format(guild.name))
            return

        await ctx.message.channel.send("Server with that ID not found")

        channel = self.bot.get_channel(id)
        if not channel is None:
            await ctx.message.channel.send("Channel: **{}** on **{}**".format(channel.name, channel.guild.name))
            return

        await ctx.message.channel.send("Channel with that ID not found")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def invites(self, ctx):
        """Returns invites (if the bot has valid permissions) for each server the bot is on. (Permission level required: 7+ (The Bot Smith))
        
        {usage}"""
        for guild in self.bot.guilds:
            try:
                channel = guild.text_channels[1]
                invite = await channel.create_invite(max_age=86400)
                await ctx.message.author.send("Server: " + guild.name + "(" + str(guild.id) + ") - <" + invite.url + ">")
            except discord.errors.Forbidden:
                await ctx.message.author.send("I don't have the necessary permissions on " + guild.name + "(" + str(guild.id) + "). That server is owned by " + guild.owner.name + "#" + str(guild.owner.discriminator) + " (" + str(guild.id) + ")")
            except IndexError:
                await ctx.message.author.send("No text channels in " + guild.name + "(" + str(guild.id) + ")")

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
            await ctx.message.channel.send(python.format(type(e).__name__ + ': ' + str(e)))
            return

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
            await ctx.channel.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return
        await ctx.channel.send("{} loaded.".format(extension_name))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, extension_name : str):
        """Unloads the extension name if in NecroBot's list of rings.
         
        {usage}"""
        self.bot.unload_extension("rings." + extension_name)
        await ctx.channel.send("{} unloaded.".format(extension_name))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, extension_name : str):
        """Unload and loads the extension name if in NecroBot's list of rings.
         
        {usage}"""
        self.bot.unload_extension("rings." + extension_name)
        try:
            self.bot.load_extension("rings." + extension_name)
        except (AttributeError,ImportError) as e:
            await ctx.channel.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return
        await ctx.channel.send("{} reloaded.".format(extension_name))

    # *****************************************************************************************************************
    # Bot Smith Commands
    # *****************************************************************************************************************
    @commands.command(hidden=True)
    @commands.is_owner()
    async def off(self, ctx):
        """Saves all the data and terminate the self. (Permission level required: 7+ (The Bot Smith))
         
        {usage}"""
        channel = self.bot.get_channel(318465643420712962)
        msg = await channel.send("**Saving...**")

        with open("rings/utils/data/server_data.json", "w") as out:
            json.dump(self.bot.server_data, out)

        with open("rings/utils/data/user_data.json", "w") as out:
            json.dump(self.bot.user_data, out)

        await msg.edit(content="**Saved**")
        await channel.send("**Bot Offline**")
        await self.bot.logout()

def setup(bot):
    bot.add_cog(Admin(bot))