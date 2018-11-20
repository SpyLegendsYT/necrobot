import discord
from discord.ext import commands

from rings.utils.utils import has_perms, GuildConverter, react_menu, UPDATE_NECROINS, UPDATE_PERMS
from rings.utils.config import github_key

import ast
import json
import psutil
import asyncio
from typing import Union, Optional
from simpleeval import simple_eval

class Admin():
    def __init__(self, bot):
        self.bot = bot
        self.gates = {}
        self.process = psutil.Process()

    def _insert_returns(self, body):
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])

        if isinstance(body[-1], ast.If):
            self._insert_returns(body[-1].body)
            self._insert_returns(body[-1].orelse)

        if isinstance(body[-1], ast.With):
            self._insert_returns(body[-1].body)

    @commands.command()
    @commands.is_owner()
    async def leave(self, ctx, guild : GuildConverter, *, reason : str = "unspecified"):
        """Leaves the specified server. (Permission level required: 7+ (The Bot Smith))
        {usage}"""
        if reason != "unspecified":
            channel = [x for x in guild.text_channels if x.permissions_for(self.bot.user).send_messages][0]
            await channel.send(f"I'm sorry, Necro#6714 has decided I should leave this server, because: {reason}")
        await guild.leave()
        await ctx.send(f":white_check_mark: | Okay Necro, I've left {guild.name}")

    @commands.group()
    async def admin(self, ctx):
        """{usage}"""
        pass

    @admin.command(name="permsissions", aliases=["perms"])
    @commands.is_owner()
    async def admin_perms(self, ctx, server : GuildConverter, user : discord.User, level : int):
        """For when regular perms isn't enough.

        {usage}"""
        self.bot.user_data[user.id]["perms"][server.id] = level
        await self.bot.query_executer("UPDATE necrobot.Permissions SET level = $1 WHERE guild_id = $2 AND user_id = $3;", level, server.id, user.id)
        if level >= 6:
            for guild in self.bot.user_data[user.id]["perms"]:
                self.bot.user_data[user.id]["perms"][guild] = level
                await self.bot.query_executer(UPDATE_PERMS, level, guild, user.id)

        await ctx.send(f":white_check_mark: | All good to go, **{user.display_name}** now has permission level **{level}** on server **{server.name}**")

    @admin.command(name="disable")
    @has_perms(6)
    async def admin_disable(self, ctx, *, command : str):
        """For when regular disable isn't enough. Disables command discord-wide

        {usage}
        """
        command = self.bot.get_command(command)
        if command.enabled:
            command.enabled = False
            await ctx.send(f":white_check_mark: | Disabled **{command.name}**")
        else:
            await ctx.send(f":negative_squared_cross_mark: | Command **{command.name}** already disabled")

    @admin.command(name="enable")
    @has_perms(6)
    async def admin_enable(self, ctx, *, command : str):
        """For when regular enable isn't enough. Re-enables the command discord-wide.

        {usage}
        """
        command = self.bot.get_command(command)
        if command.enabled:
            await ctx.send(f":negative_squared_cross_mark: | Command **{command.name}** already enabled")
        else:
            command.enabled = True
            await ctx.send(f":white_check_mark: | Enabled **{command.name}**")

    @admin.command(name="badges")
    @has_perms(6)
    async def admin_badges(self, ctx, subcommand : str, user : discord.User, badge : str):
        """Used to grant special badges to users. Uses add/delete subcommand

        {usage}
        """
        badges = list(self.bot.cogs["Profile"].badges_d.keys()) + self.bot.cogs["Profile"].special_badges
        if badge not in badges:
            await ctx.send(":negative_squared_cross_mark: | Not a valid badge")
            return
            
        if subcommand not in ("add", "delete"):
            await ctx.send(":negative_squared_cross_mark: | Not a valid subcommand")
            return

        if subcommand == "add" and badge not in self.bot.user_data[user.id]["badges"]:
            self.bot.user_data[user.id]["badges"].append(badge)    
            await ctx.send(f":white_check_mark: | Granted the **{badge}** badge to user **{user}**")
        elif subcommand == "delete" and badge in self.bot.user_data[user.id]["badges"]:
            for key in [key for key, _badge in self.bot.user_data[user.id]["places"].items() if _badge == badge]:
                self.bot.user_data[user.id]["places"][key] = ""
                await self.bot.query_executer("UPDATE necrobot.Badges SET badge = $1 WHERE user_id = $2 AND place = $3", badge, user.id, key)

            self.bot.user_data[user.id]["badges"].remove(badge)    
            await ctx.send(f":white_check_mark: | Reclaimd the **{badge}** badge from user **{user}**")
        else:
            await ctx.send(":negative_squared_cross_mark: | Users has/doesn't have the badge")
            return

        await self.bot.query_executer("UPDATE necrobot.Users SET badges = $2 WHERE user_id = $1", user.id, ",".join(self.bot.user_data[user.id]["badges"]))

    @commands.command()
    @has_perms(6)
    async def add(self, ctx, user : discord.User, *, equation : str):
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
        s = f'{self.bot.user_data[user.id]["money"]}{equation}'
        try:
            operation = simple_eval(s)
        except (NameError, SyntaxError):
            await ctx.send(":negative_squared_cross_mark: | Operation not recognized.")
            return

        msg = await ctx.send(f":white_check_mark: | Operation successful. Change user balace to **{operation}**?")

        await msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        await msg.add_reaction("\N{NEGATIVE SQUARED CROSS MARK}")

        def check(reaction, user):
            return msg.id == reaction.message.id and user == ctx.author and str(reaction.emoji) in ["\N{WHITE HEAVY CHECK MARK}", "\N{NEGATIVE SQUARED CROSS MARK}"]

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", check=check, timeout=300)
        except asyncio.TimeoutError:
            await msg.delete()
            return

        if reaction.emoji == "\N{NEGATIVE SQUARED CROSS MARK}":
            await ctx.send(f":white_check_mark: | Cancelled.")
            await msg.delete()
        elif reaction.emoji == "\N{WHITE HEAVY CHECK MARK}":
            self.bot.user_data[user.id]["money"] = int(operation)
            await self.bot.query_executer(UPDATE_NECROINS, self.bot.user_data[user.id]["money"], user.id)
            await ctx.send(":atm: | **{}'s** balance is now **{:,}** :euro:".format(user.display_name, self.bot.user_data[user.id]["money"]))
            await msg.delete()

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
        await to_edit.edit(content=f":speech_left: | **User: {msg.author}** said :**{msg.content[1950:]}**")
        
    @commands.command()
    @commands.is_owner()
    async def get(self, ctx, obj_id : int):
        """Returns the name of the user or server based on the given id. Used to debug errors. 
        (Permission level required: 7+ (The Bot Smith))
        
        {usage}
        
        __Example__
        `{pre}get 345345334235345` - returns the user or server name with that id"""
        msg = await ctx.send("Scanning...")
        user = self.bot.get_user(obj_id)
        if user:
            await msg.edit(content=f"User: **{user}**")
            return

        await msg.edit(content="User with that ID not found.")

        guild = self.bot.get_guild(obj_id)
        if guild:
            await msg.edit(content=f"Server: **{guild}**")
            return

        await msg.edit(content="Server with that ID not found")

        channel = self.bot.get_channel(obj_id)
        if channel:
            await msg.edit(content=f"Channel: **{channel.name}** on **{channel.guild.name}** ({channel.guild.id})")
            return

        await msg.edit(content="Channel with that ID not found")

        role = discord.utils.get([item for sublist in  [guild.roles for guild in self.bot.guilds] for item in sublist], id=obj_id)
        if role:
            await msg.edit(content=f"Role: **{role.name}** on **{role.guild.name}** ({role.guild.id})")
            return

        await msg.edit(content="Nothing found with that ID")

    @commands.command()
    @commands.is_owner()
    async def invites(self, ctx, *, guild : GuildConverter = None):
        """Returns invites (if the bot has valid permissions) for each server the bot is on if no guild id is specified. 
        (Permission level required: 7+ (The Bot Smith))
        
        {usage}"""
        async def get_invite(guild):
            try:
                channel = [x for x in guild.text_channels if x.permissions_for(guild.me).create_instant_invite][0]
                invite = await channel.create_invite(max_age=86400)
                await ctx.send(f"Server: {guild.name}({guild.id}) - <{invite.url}>")
            except discord.errors.Forbidden:
                await ctx.send(f"I don't have the necessary permissions on {guild.name}({guild.id}). That server is owned by {guild.owner}({guild.id})")
            except IndexError:
                await ctx.send(f"No text channels in {guild.name}({guild.id})")

        if guild:
            await get_invite(guild)
        else:
            for server in self.bot.guilds:
                await get_invite(server)
            
    @commands.command()
    @commands.is_owner()
    async def debug(self, ctx, *, cmd : str):
        """Evaluates code. All credits to Danny for creating a safe eval command (Permission level required: 7+ (The Bot Smith)) 
        
        {usage}
        
        The following global envs are available:
            `bot`: bot instance
            `discord`: discord module
            `commands`: discord.ext.commands module
            `ctx`: Context instance
            `__import__`: allows to import module
            `guild`: guild eval is being invoked in
            `channel`: channel eval is being invoked in
            `author`: user invoking the eval
        """
        fn_name = "_eval_expr"
        cmd = cmd.strip("` ")
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
        body = f"async def {fn_name}():\n{cmd}"
        python = '```py\n{}\n```'

        parsed = ast.parse(body)
        body = parsed.body[0].body
        self._insert_returns(body)

        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__,
            'guild': ctx.guild,
            'channel': ctx.channel,
            'author': ctx.author
        }
        try:
            exec(compile(parsed, filename="<ast>", mode="exec"), env)
            result = (await eval(f"{fn_name}()", env))
            if result:
                await ctx.send(result)
            else:
                await ctx.send(":white_check_mark:")
        except Exception as e:
            await ctx.send(python.format(f'{type(e).__name__}: {e}'))

    @commands.command()
    @has_perms(6)
    async def blacklist(self, ctx, *, thing : Union[GuildConverter, discord.User] = None):
        """Blacklists a guild or user. If it is a guild, the bot will leave the guild. A user will simply be unable to 
        use the bot commands and react. However, they will still be automoderated. Can also be used to print out all the
        blacklisted users and guilds.

        {usage}"

        __Example__
        `{pre}blacklist` - print all blacklisted users
        `{pre}blacklist @Necrobot` - blacklist user Necrobot
        `{pre}blacklist Bad Guild` - blacklist the guild Bad Guild
        """
        if not thing:
            if not self.bot.settings["blacklist"]:
                await ctx.send("**List of blacklisted users/guilds**: **None**")
            else:
                blacklist = []
                for item in self.bot.settings["blacklist"]:
                    thing = self.bot.get_guild(item) or self.bot.get_user(item)
                    blacklist.append(thing.name)

                await ctx.send("**List of blacklisted users/guilds**: {}".format(" - ".join(blacklist)))
            return

        if isinstance(thing, discord.User):
            if thing.id in self.bot.settings["blacklist"]:
                self.bot.settings["blacklist"].remove(thing.id)
                await ctx.send(f":white_check_mark: | User **{thing.name}** pardoned")
            else:
                try:
                    await thing.send(":negative_squared_cross_mark: | You have been blacklisted by NecroBot, if you wish to appeal your ban, join the support server. https://discord.gg/Ape8bZt")
                except discord.Forbidden:
                    pass

                self.bot.settings["blacklist"].append(thing.id)
                await ctx.send(f":white_check_mark: | User **{thing.name}** blacklisted")
        elif isinstance(thing, discord.Guild):
            if thing.id in self.bot.settings["blacklist"]:
                self.bot.settings["blacklist"].remove(thing.id)
                await ctx.send(f":white_check_mark: | Guild **{thing.name}** pardoned")
            else:
                await thing.owner.send(":negative_squared_cross_mark: | Your server has been blacklisted by NecroBot, if you wish to appeal your ban, join the support server. https://discord.gg/Ape8bZt")
                await thing.leave()
                self.bot.settings["blacklist"].append(thing.id)
                await ctx.send(f":white_check_mark: | Guild **{thing.name}** blacklisted")


    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension_name : str):
        """Loads the extension name if in NecroBot's list of rings.
        
        {usage}"""
        try:
            self.bot.load_extension(f"rings.{extension_name}")
        except (AttributeError,ImportError) as e:
            await ctx.send(f"```py\n{type(e).__name__}: {e}\n```")
            return
        await ctx.send(f"{extension_name} loaded.")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, extension_name : str):
        """Unloads the extension name if in NecroBot's list of rings.
         
        {usage}"""
        self.bot.unload_extension(f"rings.{extension_name}")
        await ctx.send(f"{extension_name} unloaded.")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension_name : str):
        """Unload and loads the extension name if in NecroBot's list of rings.
         
        {usage}"""
        self.bot.unload_extension(f"rings.{extension_name}")
        try:
            self.bot.load_extension(f"rings.{extension_name}")
        except (AttributeError,ImportError) as e:
            await ctx.send(f"```py\n{type(e).__name__}: {e}\n```")
            return
        await ctx.send(f"{extension_name} reloaded.")

    @commands.command()
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
            reaction, _ = await self.bot.wait_for("reaction_add", check=check, timeout=300)
        except asyncio.TimeoutError as e:
            msg.clear_reactions()
            e.timer = 300
            return self.bot.dispatch("command_error", ctx, e)

        if reaction.emoji == "\N{NEGATIVE SQUARED CROSS MARK}":
            await msg.delete()
        elif reaction.emoji == "\N{WHITE HEAVY CHECK MARK}":
            await msg.delete()
            await self.bot.change_presence(activity=discord.Game(name="Bot shutting down...", type=0))
            
            with open("rings/utils/data/settings.json", "w") as outfile:
                json.dump(self.bot.settings, outfile)
            
            channel = self.bot.get_channel(318465643420712962)
            await channel.send("**Bot Offline**")
            self.bot.broadcast_task.cancel()
            self.bot.status_task.cancel()
            await self.bot.session.close()
            await self.bot.logout()

    @commands.command()
    @commands.is_owner()
    async def save(self, ctx):
        """Save data but doesn't terminate the bot

        {usage}"""
        await ctx.send(":white_check_mark: | Saving")
        
        with open("rings/utils/data/settings.json", "w") as outfile:
            json.dump(self.bot.settings, outfile)
        
        await ctx.send(":white_check_mark: | Done saving")

    @commands.command()
    @has_perms(6)
    async def log(self, ctx, start : Optional[int] = 0, *arguments):
        """Get a list of commands. SQL arguments can be passed to filter the output.

        {usage}"""
        if arguments:
            raw_args = " AND ".join(arguments)
            sql = f"SELECT user_id, command, guild_id, message, time_used, can_run FROM necrobot.Logs WHERE {raw_args} ORDER BY time_used DESC"
        else:
            sql = "SELECT user_id, command, guild_id, message, time_used, can_run FROM necrobot.Logs ORDER BY time_used DESC"

        results = await self.bot.query_executer(sql)

        def _embed_maker(index):
            embed = discord.Embed(title="Command Log", colour=discord.Colour(0x277b0), description="\u200b")
            embed.set_footer(text="Generated by Necrobot", icon_url=self.bot.user.avatar_url_as(format="png", size=128))
            for row in results[index*5:(index+1)*5]:
                user = self.bot.get_user(row["user_id"])
                guild = self.bot.get_guild(row["guild_id"])
                embed.add_field(name=row["command"], value=f"From {user} ({user.id}) on {guild} ({guild.id}) on {row['time_used']}\n **Message**\n{row['message'][:1000]}")

            return embed

        await react_menu(ctx, len(results)//5, _embed_maker, start)

    @commands.command(name="as")
    @commands.is_owner()
    async def _as(self, ctx, user : discord.Member, *, message : str):
        """Call a command as another user, used for debugging purposes

        {usage}

        __Examples__
        `{pre}as NecroBot n!balance` - calls the balance command as though necrobot had called it (displaying its balance).

        """
        if ctx.command == "as":
            return

        ctx.author = ctx.message.author = user
        ctx.message.content = message

        await self.bot.process_commands(ctx.message)

    @commands.command()
    async def stats(self, ctx):
        """Provides meta data on the bot.

        {usage}"""
        
        headers = {"Authorization": f"token {github_key}"}
        emojis = {"dnd": "<:dnd:509069576160542757>", "idle": "<:away:509069596930736129>", "offline": "<:offline:509069561065111554>", "online": "<:online:509069615494725643>"}
        async with self.bot.session.get("https://api.github.com/repos/ClementJ18/necrobot/commits", headers=headers) as r:
            resp = (await r.json())[:5]

        description = "\n".join([f"[`{c['sha'][:7]}`]({c['url']}) - {c['commit']['message']}" for c in resp])
        embed = discord.Embed(title="Information", colour=discord.Colour(0x277b0), description=description)
        embed.set_footer(text="Generated by Necrobot", icon_url=self.bot.user.avatar_url_as(format="png", size=128))

        members = {x : set() for x in discord.Status if x != discord.Status.invisible}
        for user in self.bot.get_all_members():
            if user.status == discord.Status.invisible:
                continue
            members[user.status].add(user.id)

        embed.add_field(name="Members", value="\n".join([f"{emojis[key.name]} {len(value)}" for key, value in members.items()]))
        memory_usage = self.process.memory_full_info().uss / 1024**2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
        embed.add_field(name='Process', value=f'{memory_usage:.2f} MiB\n{cpu_usage:.2f}% CPU')

        await ctx.send(embed=embed)
            

    @commands.command()
    @has_perms(6)
    async def gate(self, ctx, channel : Union[discord.TextChannel, discord.User]):
        """Connects two channels with a magic gate so that users on bot servers can communicate. Magic:tm:

        {usage}

        """
        if channel == ctx.channel:
            await ctx.send(":negative_squared_cross_mark: | Gate destination cannnot be the same as channel the command is called from")
            return

        await channel.send(":gate: | A warp gate has opened on your server, you are now in communication with a Necrobot admin. Voice any concerns without fear.")
        await ctx.send(f":gate: | I've opened a gate to {channel.mention}")

        self.gates[ctx.channel.id] = channel
        self.gates[channel.id] = ctx.channel

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel and message.content == "exit"


        await self.bot.wait_for("message", check=check)

        await channel.send(":stop: | The NecroBot admin has ended the conversation.")
        await ctx.send(":stop: | Conversation ended")

        del self.gates[ctx.channel.id]
        del self.gates[channel.id]        

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id in self.gates:
            channel = self.gates[message.channel.id]
        elif message.author.id in self.gates:
            channel = self.gates[message.author.id]
        else:
            return
        
        message.content = message.content.replace("@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")
        embed = discord.Embed(title="Message", description=message.content)
        embed.set_author(name=message.author, icon_url=message.author.avatar_url_as(format="png", size=128))
        embed.set_footer(text="Generated by NecroBot", icon_url=self.bot.user.avatar_url_as(format="png", size=128))
        
        await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Admin(bot))
