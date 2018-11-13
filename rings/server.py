import discord
from discord.ext import commands

from rings.utils.utils import has_perms, react_menu, UPDATE_PERMS, TimeConverter

from typing import Union

class Server():
    """Contains all the commands related to customising Necrobot's behavior on your server and to your server members. Contains
    commands for stuff such as setting broadcast, giving users permissions, ignoring users, getting info on your current settings,
    ect..."""
    def __init__(self, bot):
        self.bot = bot

    def __local_check(self, ctx):
        if ctx.guild:
            return True

        raise commands.CheckFailure(self.bot.t(ctx, "error-nopriv"))

    def _all_lists(self, ctx, key):
        l = []
        for x in self.bot.server_data[ctx.guild.id][key]:
            channel = self.bot.get_channel(x)
            if channel:
                l.append(f"C: {channel.name}")

            member = self.bot.get_member(x)
            if member:
                l.append(f"U: {member.name}")

            role = discord.utils.get(ctx.guild.roles, id=x)
            if role:
                l.append(f"R: {role.name}")

        return l

    @commands.command(aliases=["perms"])
    @has_perms(4)
    async def permissions(self, ctx, user : discord.Member, level : int):
        """Sets the NecroBot permission level of the given user, you can only set permission levels lower than your own. 
        Permissions reset if you leave the server(Permission level required: 4+ (Server Admin))
         
        {usage}
        
        __Example__
        `{pre}permissions @NecroBot 5` - set the NecroBot permission level to 5
        `{pre}perms @NecroBot 5` - set the NecroBot permission level to 5"""
        if level < 0 or level > 7:
            await ctx.send(f":negative_squared_cross_mark: | {self.bot.t(ctx, 'perms-max-min')}")

        if self.bot.user_data[ctx.author.id]["perms"][ctx.guild.id] > level and self.bot.user_data[ctx.author.id]["perms"][ctx.guild.id] > self.bot.user_data[user.id]["perms"][ctx.guild.id]:
            c = self.bot.user_data[user.id]["perms"][ctx.guild.id]
            self.bot.user_data[user.id]["perms"][ctx.guild.id] = level
            await self.bot.query_executer(UPDATE_PERMS, level, ctx.guild.id, user.id)

            if c < level:
                await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'perms-promoted').format(user.display_name, self.bot.perms_name[level], level)}")
            elif c > level:
                await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'perms-demoted').format(user.display_name, self.bot.perms_name[level], level)}")
            else:
                await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'perms-no-change').format(user.display_name)}")
                return

            if level == 6:
                for guild in self.bot.user_data[user.id]["perms"]:
                    self.bot.user_data[user.id]["perms"][guild] = 6
                    await self.bot.query_executer(UPDATE_PERMS, 6, guild, user.id)
        else:
            await ctx.send(f":negative_squared_cross_mark: | {self.bot.t(ctx, 'perms-no-necrobot-perms')}")

    @commands.command()
    @has_perms(4)
    async def promote(self, ctx, member : discord.Member):
        """Promote a member by one on the Necrobot hierarchy scale. Gaining access to additional commands

        {usage}

        __Examples__
        `{pre}promote NecroBot` - promote necrobot by one level
        """
        current = self.bot.user_data[member.id]["perms"][ctx.guild.id]
        await ctx.invoke(self.bot.get_command("permissions"), user=member, level=current + 1)

    @commands.command()
    @has_perms(4)
    async def demote(self, ctx, member : discord.Member):
        """Demote a member by one on the Necrobot hierarchy scale. Losing access to certain commands

        {usage}

        __Examples__
        `{pre}demote NecroBot` - promote necrobot by one level
        """
        current = self.bot.user_data[member.id]["perms"][ctx.guild.id]
        await ctx.invoke(self.bot.get_command("permissions"), user=member, level=current - 1)

    @commands.group(invoke_without_command=True)
    @has_perms(4)
    async def automod(self, ctx, *mentions : Union[discord.Member, discord.TextChannel, discord.Role]):
        """Used to manage the list of channels and user ignored by the bot's automoderation system. If no mentions are 
        given it will print out the list of ignored Users (**U**) and the list of ignored Channels (**C**). The automoderation 
        feature tracks the edits made by users to their own messages and the deleted messages, printing them in the server's automod 
        channel. If mentions are given then it will add any user/channel not already ignored and remove any user/channel already ignored. 
        Set the automod channel using `{pre}settings automod` (Permission level required: 4+ (Server Admin))
         
        {usage}

        __Example__
        `{pre}automod` - prints the list of users/channels ignored by necrobot's automoderation feature
        `{pre}automod @Necro #general` - adds user Necro and channel general to list of users/channels ignored by the necrobot's automoderation
        `{pre}automod @NecroBot #general` - adds user Necrobot to the list of users ignored by the automoderation and removes channel #general 
        from it (since we added it above)
        `{pre}automod @ARole` - adds role ARole to the list of roles ignored by automoderation
        """

        if not mentions:
            await ctx.send(f"{self.bot.t(ctx, 'automod-list')}: ``` {self._all_lists(ctx, 'ignore-automod')} ```")
            return

        for x in mentions:
            if x.id not in self.bot.server_data[ctx.guild.id]["ignore-automod"]:
                self.bot.server_data[ctx.guild.id]["ignore-automod"].append(x.id)
                await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'automod-add').format(x.name)}")
                await self.bot.query_executer("INSERT INTO necrobot.IgnoreAutomod VALUES ($1, $2);", ctx.guild.id, x.id)
            else:
                self.bot.server_data[ctx.guild.id]["ignore-automod"].remove(x.id)
                await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'automod-remove').format(x.name)}")
                await self.bot.query_executer("DELETE FROM necrobot.IgnoreAutomod WHERE guild_id = $1 AND id = $2;", ctx.guild.id, x.id)

    @automod.command(name="channel")
    @has_perms(4)
    async def automod_channel(self, ctx, channel : discord.TextChannel = ""):
        """Sets the automoderation channel to [channel], [channel] argument should be a channel mention. All the 
        auto-moderation related messages will be sent there. (Permission level required: 5+ (Server Owner))
         
        {usage}
        
        __Example__
        `{pre}automod channel #channel` - set the automoderation messages to be sent to channel 'channel'
        `{pre}automod channel` - disables automoderation for the entire server"""
        if channel == "":
            self.bot.server_data[ctx.guild.id]["automod"] = ""
            await self.bot.query_executer("UPDATE necrobot.Guilds SET automod_channel = 0 WHERE guild_id = $1;", ctx.guild.id)
            await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'automod-disable')}")
        else:
            self.bot.server_data[ctx.guild.id]["automod"] = channel.id
            await self.bot.query_executer("UPDATE necrobot.Guilds SET automod_channel = $2 WHERE guild_id = $1;", ctx.guild.id, channel.id)
            await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'automod-channel').format(channel.mention)}")

    @commands.command()
    @has_perms(4)
    async def ignore(self, ctx, *mentions : Union[discord.Member, discord.TextChannel, discord.Role]):
        """Used to manage the list of channels and user ignored by the bot's command system. If no mentions are 
        given it will print out the list of ignored Users (**U**) and the list of ignored Channels (**C**). Being ignored
        by the command system means that user cannot use any of the bot commands on the server. If mentions are given then 
        it will add any user/channel not already ignored and remove any user/channel already ignored. (Permission level required: 4+ (Server Admin))
         
        {usage}

        __Example__
        `{pre}ignore` - prints the list of users/channels ignored by necrobot
        `{pre}ignore @Necro #general` - adds user Necro and channel general to list of users/channels ignored by the necrobot
        `{pre}ignore @NecroBot #general` - adds user Necrobot to the list of users ignored by the bot and removes channel #general 
        from it (since we added it above)
        `{pre}ignore @ARole` - adds role ARole to the list of roles ignored by the bot
        """

        if not mentions:
            await ctx.send(f"{self.bot.t(ctx, 'ignore-list')}: ``` {self._all_lists(ctx, 'ignore-command')} ```")
            return
        
        for x in mentions:
            if x.id not in self.bot.server_data[ctx.guild.id]["ignore-command"]:
                self.bot.server_data[ctx.guild.id]["ignore-command"].append(x.id)
                await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'ignore-add').format(x.name)}")
                await self.bot.query_executer("INSERT INTO necrobot.IgnoreCommand VALUES ($1, $2);", ctx.guild.id, x.id)
            else:
                self.bot.server_data[ctx.guild.id]["ignore-command"].remove(x.id)
                await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'ignore-remove').format(x.name)}")
                await self.bot.query_executer("DELETE FROM necrobot.IgnoreCommand WHERE guild_id = $1 AND id = $2;", ctx.guild.id, x.id)

    @commands.group(aliases=["setting"], invoke_without_command=True)
    @has_perms(4)
    async def settings(self, ctx):
        """Creates a rich embed of the server settings

        {usage}"""
        server = self.bot.server_data[ctx.guild.id] 
        role_obj = discord.utils.get(ctx.guild.roles, id=server["mute"])
        role_obj2 = discord.utils.get(ctx.guild.roles, id=server["auto-role"])

        disabled = self.bot.t(ctx, 'disabled')
        none = self.bot.t(ctx, 'none')

        embed = discord.Embed(title=self.bot.t(ctx, 'settings-title'), colour=discord.Colour(0x277b0), description=self.bot.t(ctx, 'settings-message'))
        embed.add_field(name=self.bot.t(ctx, 'settings-automod'), value=self.bot.get_channel(server["automod"]).mention if server["automod"] != "" else disabled)
        embed.add_field(name=self.bot.t(ctx, 'settings-welcome'), value=self.bot.get_channel(server["welcome-channel"]).mention if server["welcome-channel"] != "" else disabled)
        embed.add_field(name=self.bot.t(ctx, 'settings-welcome-message'), value=server["welcome"][:1024] if server["welcome"] != "" else none, inline=False)
        embed.add_field(name=self.bot.t(ctx, 'settings-goodbye-message'), value=server["goodbye"][:1024] if server["goodbye"] != "" else none, inline=False)
        embed.add_field(name=self.bot.t(ctx, 'settings-mute'), value=role_obj.mention if server["mute"] != "" else disabled)
        embed.add_field(name=self.bot.t(ctx, 'settings-prefix'), value=f'`{server["prefix"]}`' if server["prefix"] != "" else "`n!`")
        embed.add_field(name=self.bot.t(ctx, 'settings-broadcast'), value=self.bot.get_channel(server["broadcast-channel"]).mention if server["broadcast-channel"] != "" else disabled)
        embed.add_field(name=self.bot.t(ctx, 'settings-broadcast-time'), value=f'Every {server["broadcast-time"]} hour(s)' if server["broadcast-time"] != "" else none)
        embed.add_field(name=self.bot.t(ctx, 'settings-broadcast-message'), value=server["broadcast"] if server["broadcast"] != "" else none, inline=False)
        embed.add_field(name=self.bot.t(ctx, 'settings-auto-role'), value= role_obj2.mention if server["auto-role"] != "" else none)
        embed.add_field(name=self.bot.t(ctx, 'settings-auto-role-timer'), value= server["auto-role-timer"] if server["auto-role-timer"] > 0 else none)       
        embed.add_field(name=self.bot.t(ctx, 'settings-starboard'), value = self.bot.get_channel(server["starboard-channel"]).mention if server["starboard-channel"] != "" else disabled)
        embed.add_field(name=self.bot.t(ctx, 'settings-starboard-limit'), value=server["starboard-limit"])
        embed.add_field(name=self.bot.t(ctx, 'settings-language'), value=f'`{server["language"]}`')

        embed.set_footer(text=self.bot.t(ctx, 'generated-necrobot'), icon_url=self.bot.user.avatar_url_as(format="png", size=128))

        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    @has_perms(4)
    async def welcome(self, ctx, *, message=""):
        """Sets the message that will be sent to the designated channel everytime a member joins the server. You 
        can use special keywords to replace certain words by stuff like the name of the member or a mention.
        List of keywords:
        `{mention}` - mentions the member
        `{member}` - name and discriminator of the member
        `{name}` - name of the member
        `{server}` - name of the server
        `{id}` - id of the member that joined

        (Permission level required: 4+ (Server Admin))

        {usage}
        
        __Example__
        `{pre}welcome Hello {member} :wave:` - sets the welcome message to be 'Hello Necrobot#1231 :wave:'.
        `{pre}welcome hey there {mention}, welcome to {server}` - set the welcome message to 'hey there @NecroBot, welcome
        to NecroBot Support Server'
        """
        if message == "":
            await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'welcome-disabled')}")
        else:
            try:
                message = message.format(
                    member=ctx.author, 
                    server=ctx.guild.name,
                    mention=ctx.author.mention,
                    name=ctx.author.name,
                    id=ctx.author.id
                )
                await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'welcome-message-set').format(message)}")
            except KeyError as e:
                await ctx.send(f":negative_squared_cross_mark: | {self.bot.t(ctx, 'message-error').format(e.args[0])}")
                return

        self.bot.server_data[ctx.guild.id]["welcome"] = message
        await self.bot.query_executer("UPDATE necrobot.Guilds SET welcome_message = $1 WHERE guild_id = $2;", message, ctx.guild.id)

    @commands.group(invoke_without_command=True)
    @has_perms(4)
    async def goodbye(self, ctx, *, message= ""):
        """Sets the message that will be sent to the designated channel everytime a member leaves the server. You 
        can use special keywords to replace certain words by stuff like the name of the member or a mention.
        List of keywords:
        `{mention}` - mentions the member
        `{member}` - name and discriminator of the member
        `{name}` - name of the member
        `{server}` - name of the server
        `{id}` - id of the member that left

        (Permission level required: 4+ (Server Admin))

        {usage}
        
        __Example__
        `{pre}goodbye Hello {member} :wave:` - sets the welcome message to be 'Hello Necrobot#1231 :wave:'.
        `{pre}goddbye hey there {mention}, we'll miss you on {server}` - set the welcome message to 'hey 
        there @NecroBot, we'll miss you on NecroBot Support Server'
        """
        if message == "":
            await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'welcome-disabled')}")
        else:
            try:
                message = message.format(
                    member=ctx.author, 
                    server=ctx.guild.name,
                    mention=ctx.author.mention,
                    name=ctx.author.name,
                    id=ctx.author.id
                )
                await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'goodbye-message-set').format(message)}")
            except KeyError as e:
                await ctx.send(f":negative_squared_cross_mark: | {self.bot.t(ctx, 'message-error').format(e.args[0])}")
                return

        self.bot.server_data[ctx.guild.id]["goodbye"] = message
        await self.bot.query_executer("UPDATE necrobot.Guilds SET goodbye_message = $1 WHERE guild_id = $2", message, ctx.guild.id)

    async def channel_set(self, ctx, channel):
        if channel == "":
            self.bot.server_data[ctx.guild.id]["welcome-channel"] = ""
            await self.bot.query_executer("UPDATE necrobot.Guilds SET welcome_channel = 0 WHERE guild_id = $1;", ctx.guild.id)
            await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'message-channe-reset')}")
        else:
            self.bot.server_data[ctx.guild.id]["welcome-channel"] = channel.id
            await self.bot.query_executer("UPDATE necrobot.Guilds SET welcome_channel = $1 WHERE guild_id = $2;", channel.id, ctx.guild.id)
            await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'message-channel-set').format(channel.mention)}")

    @welcome.command(name="channel")
    @has_perms(4)
    async def welcome_channel(self, ctx, channel : discord.TextChannel = ""):
        """Sets the welcome channel to [channel], the [channel] argument should be a channel mention/name/id. The welcome 
        message for users will be sent there. Can be called with either goodbye or welcome, regardless both will use
        the same channel, calling the command with both parent commands but different channel will not make
        messages send to two channels.
        (Permission level required: 5+ (Server Owner))
         
        {usage}
        
        __Example__
        `{pre}welcome channel #channel` - set the welcome messages to be sent to 'channel'
        `{pre}welcome channel` - disables welcome messages"""

        await self.channel_set(ctx, channel)

    @goodbye.command(name="channel")
    @has_perms(4)
    async def goodbye_channel(self, ctx, channel : discord.TextChannel = ""):
        """Sets the welcome channel to [channel], the [channel] argument should be a channel mention. The welcome 
        message for users will be sent there. Can be called with either goodbye or welcome, regardless both will use
        the same channel, calling the command with both parent commands but different channel will not make
        messages send to two channels.
        (Permission level required: 5+ (Server Owner))
         
        {usage}
        
        __Example__
        `{pre}goodbye channel #channel` - set the welcome messages to be sent to 'channel'
        `{pre}goodbye channel` - disables welcome messages"""

        await self.channel_set(ctx, channel)

    @commands.command(name="prefix")
    @has_perms(4)
    async def prefix(self, ctx, *, prefix=""):
        """Sets the bot to only respond to the given prefix. If no prefix is given it will reset it to NecroBot's deafult 
        list of prefixes: `n!`, `N!` or `@NecroBot `. The prefix can't be longer than 15 characters.

        {usage}

        __Example__
        `{pre}prefix bob! potato` - sets the prefix to be `bob! potato ` so a command like `{pre}cat` will now be 
        summoned like this `bob! potato cat`
        `{pre}prefix` - resets the prefix to NecroBot's default list"""
        if len(prefix) > 15:
            await ctx.send(f":negative_squared_cross_mark: | {self.bot.t(ctx, 'prefix-too-long').format(len(prefix))}")
            return

        self.bot.server_data[ctx.guild.id]["prefix"] = prefix
        await self.bot.query_executer("UPDATE necrobot.Guilds SET prefix = $1 WHERE guild_id = $2;", prefix, ctx.guild.id)


        if prefix == "":
            await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'prefix-reset')}")
        else:
            await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'prefix-set').format(prefix)}")

    @commands.command(name="auto-role")
    @has_perms(4)
    async def auto_role(self, ctx, role : discord.Role = None, time : TimeConverter = 0):
        """Sets the auto-role for this server to the given role. Auto-role will assign the role to the member when they join.
        The following times can be used: days (d), hours (h), minutes (m), seconds (s).

        {usage}

        __Example__
        `{pre}auto-role Newcomer 10m` - gives the role "Newcomer" to users to arrive on the server for 10 minutes
        `{pre}auto-role Newcomer 2d10m` - same but the roles stays for 2 days and 10 minutes
        `{pre}auto-role Newcomer 4h45m56s` - same but the role stays for 4 hours, 45 minutes and 56 seconds
        `{pre}auto-role Newcomer` - gives the role "Newcomer" with no timer to users who join the server.
        `{pre}auto-role` - resets and disables the autorole system. """

        if not role:
            self.bot.server_data[ctx.guild.id]["auto-role"] = ""
            await self.bot.query_executer("UPDATE necrobot.Guilds SET auto_role = 0 WHERE guild_id = $1;", ctx.guild.id)
            await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'prefix-reset')}")
        else:
            self.bot.server_data[ctx.guild.id]["auto-role"] = role.id
            self.bot.server_data[ctx.guild.id]["auto-role-timer"] = time
            time_str = {self.bot.t(ctx, 'autorole-time').format(time)} if time > 0 else {self.bot.t(ctx, 'permanently')} 
            await self.bot.query_executer("UPDATE necrobot.Guilds SET auto_role = $1, auto_role_timer = $3 WHERE guild_id = $2;", role.id, ctx.guild.id, time)
            await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'autorole-set').format(role.name)} {time_str}")

    @commands.group(name="broadcast", invoke_without_command=True)
    @has_perms(4)
    async def broadcast(self, ctx, disable):
        """Enables hourly broadcasting on your server, sending the given message at the given channel once every hour if no other time is specified.
        The broadcast will not fire if either the message or channel is missing. You can also disable/reset it through this command, disabling resets
        the channel and message, they will have to be set again to re-enable the broadcast.
        {usage}
        
        __Example__
        `{pre}broadcast channel #general` - sets the broadcast channel to #general
        `{pre}broadcast message test 1 2 3` - sets the broadcast channel to #general
        `{pre}broadcast time 4` - sets the broadcast message to be sent every 4 hour
        `{pre}broadcast disable` - disables broadcasted messages"""
        if disable == "disable":
            await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'broadcast-disabled')}")
            self.bot.server_data[ctx.guild.id]["broadcast-channel"] = ""
            await self.bot.query_executer("UPDATE necrobot.Guilds SET broadcast_channel = 0 WHERE guild_id = $1;", ctx.guild.id)


    @broadcast.command(name="channel")
    @has_perms(4)
    async def broadcast_channel(self, ctx, channel : discord.TextChannel = ""):
        """Used to set the channel the message will be broadcasted into.

        {usage}

        __Example__
        `{pre}broadcast channel #general` - sets the broadcast channel to #general"""
        if channel == "":
            self.bot.server_data[ctx.guild.id]["broadcast-channel"] = ""
            await self.bot.query_executer("UPDATE necrobot.Guilds SET broadcast_channel = 0 WHERE guild_id = $1;", ctx.guild.id)
            await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'broadcast-disabled')}")        
 
        self.bot.server_data[ctx.guild.id]["broadcast-channel"] = channel.id
        await self.bot.query_executer("UPDATE necrobot.Guilds SET broadcast_channel = $1 WHERE guild_id = $2;", channel.id, ctx.guild.id)
        await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'broadcast-channel-set').format(channel.mention)}")        

    @broadcast.command(name="message")
    @has_perms(4)
    async def broadcast_message(self, ctx, *, message = ""):
        """Used to set the message that will be broadcasted

        {usage}

        __Example__
        `{pre}broadcast message test 1 2 3` - sets the broadcast channel to #general"""

        self.bot.server_data[ctx.guild.id]["broadcast"] = message
        await self.bot.query_executer("UPDATE necrobot.Guilds SET broadcast_message = $1 WHERE guild_id = $2;", message, ctx.guild.id)
        
        if message == "":
            await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'broadcast-disabled')}")
            return

        await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'broadcast-message-set').format(message)}")        

    @broadcast.command(name="time")
    @has_perms(4)
    async def broadcast_time(self, ctx, hours : int):
        """Used to set the interval at which the message is broadcasted (in hours)

        {usage}

        __Example__
        `{pre}broadcast time 4` - sets the broadcast message to be sent every 4 hour"""
        if 0 < hours <= 24:
            self.bot.server_data[ctx.guild.id]["broadcast-time"] = hours
            await self.bot.query_executer("UPDATE necrobot.Guilds SET broadcast_time = $1 WHERE guild_id = $2;", hours, ctx.guild.id)
            await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'broadcast-time-set').format(hours)}")        
        else:
            await ctx.send(f":white_check_mark: |  {self.bot.t(ctx, 'broadcast-time-invalid')}")

    @commands.group(invoke_without_command = True)
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def giveme(self, ctx, *, role : discord.Role = ""):
        """Gives the user the role if it is part of this Server's list of self assignable roles. If the user already 
        has the role it will remove it. **Roles names are case sensitive** If no role name is given then it will list
        the self-assignable roles for the server
         
        {usage}
        
        __Example__
        `{pre}giveme Good` - gives or remove the role 'Good' to the user if it is in the list of self assignable roles"""

        if role == "":
            roles = [x.name for x in ctx.guild.roles if x.id in self.bot.server_data[ctx.guild.id]["self-roles"]]
            await ctx.send(self.bot.t(ctx, 'giveme-list').format("\n- ".join(roles)))
            return

        if role.id in self.bot.server_data[ctx.guild.id]["self-roles"]:
            if role not in ctx.author.roles:
                await ctx.author.add_roles(role)
                await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'giveme-add').format(role.name)}")
            else:
                await ctx.author.remove_roles(role)
                await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'giveme-remove').format(role.name)}")

        else:
            await ctx.send(f":negative_squared_cross_mark: | {self.bot.t(ctx, 'giveme-invalid')}")

    @giveme.command(name="add")
    @has_perms(4)
    async def giveme_add(self, ctx, *, role : discord.Role):
        """Adds [role] to the list of the server's self assignable roles. (Permission level required: 4+ (Server Admin))
         
        {usage}
        
        __Example__
        `{pre}giveme add Good` - adds the role 'Good' to the list of self assignable roles"""
        if role.id in self.bot.server_data[ctx.guild.id]["self-roles"]:
            await ctx.send(f":negative_squared_cross_mark: | {self.bot.t(ctx, 'giveme-add-invalid')}")
            return

        await self.bot.query_executer("INSERT INTO necrobot.SelfRoles VALUES ($1, $2);", ctx.guild.id, role.id)
        self.bot.server_data[ctx.guild.id]["self-roles"].append(role.id)
        await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'giveme-add-add').format(role.name)}")

    @giveme.command(name="delete")
    @has_perms(4)
    async def giveme_delete(self, ctx, *, role : discord.Role):
        """Removes [role] from the list of the server's self assignable roles. (Permission level required: 4+ (Server Admin)
        
        {usage}
        
        __Example__
        `{pre}giveme delete Good` - removes the role 'Good' from the list of self assignable roles"""
        if role.id not in self.bot.server_data[ctx.guild.id]["self-roles"]:
            await ctx.send(f":negative_squared_cross_mark: | {self.bot.t(ctx, 'giveme-delete-invalid')}")
            return

        await self.bot.query_executer("DELETE FROM necrobot.SelfRoles WHERE guild_id = $1 AND id = $2;", ctx.guild.id, role.id)
        self.bot.server_data[ctx.guild.id]["self-roles"].remove(role.id)
        await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'giveme-delete-delete').format(role.name)}")
            

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def starboard(self, ctx, member : Union[discord.User, int] = 1):
        """Base of the concept of R.Danny's starboard but simplified. This will post a message in a desired channel once it hits
        a certain number of :star: reactions. Default limit is 5, you can change the limit with `{pre}starboard limit` If no
        subcommand is passed it will return a leaderboard of the top starred users, if a user is passed it will return their 
        total amount of posts on the starboard for this server.

        {usage}

        __Example__
        `{pre}starboard`  - returns users with the most starred posts
        `{pre}starboard @NecroBot` - returns the amount of post starred that Necrobot has
        `{pre}starboard 3` - return the third page of the starboard leaderboard"""
        if isinstance(member, int):
            sql = "SELECT user_id, COUNT(message_id) FROM necrobot.Starred WHERE guild_id = $1 AND user_id IS NOT null GROUP BY user_id ORDER BY COUNT(message_id) DESC"
            results = await self.bot.query_executer(sql, ctx.guild.id)

            def _embed_maker(index):
                embed = discord.Embed(title=self.bot.t(ctx, 'starboard-title'), description=self.bot.t(ctx, 'starboard-descriptions'), colour=discord.Colour(0x277b0))
                embed.set_footer(text=self.bot.t(ctx, 'generated-necrobot'), icon_url=self.bot.user.avatar_url_as(format="png", size=128))
                for row in results[index*15:(index+1)*15]:
                    member = ctx.guild.get_member(row[0])
                    embed.add_field(name=str(member) if member else , value=str(row[1]), inline = False)  

                return embed

            await react_menu(ctx, len(results)//15, _embed_maker, member-1)
        else:
            sql = "SELECT user_id, COUNT(message_id) FROM necrobot.Starred WHERE guild_id = $1 AND user_id = $2 GROUP BY user_id ORDER BY COUNT(message_id)"
            result = await self.bot.query_executer(sql, ctx.guild.id, member.id)
            await ctx.send(f":star: | {self.bot.t(ctx, 'starboard-counter').format(member.display_name, result[0][1])}")


    @starboard.command(name="channel")
    @has_perms(4)
    async def starboard_channel(self, ctx, channel : discord.TextChannel = ""):
        """Sets a channel for the starboard messages, required in order for starboard to be enabled. Call the command
        without a channel to disable starboard.

        {usage}

        __Examples__
        `{pre}starboard channel #a-channel` - sets the starboard channel to #a-channel, all starred messages will be sent to
        there
        `{pre}starboard channel` - disables starboard"""
        if channel == "":
            self.bot.server_data[ctx.guild.id]["starboard-channel"] = ""
            await self.bot.query_executer("UPDATE necrobot.Guilds SET starboard_channel = 0 WHERE guild_id = $1", ctx.guild.id)
            await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'starboard-disabled')}")
            return

        self.bot.server_data[ctx.guild.id]["starboard-channel"] = channel.id
        await self.bot.query_executer("UPDATE necrobot.Guilds SET starboard_channel = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
        await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'starboard-channel-set').format(channel.mention)}")

    @starboard.command(name="limit")
    @has_perms(4)
    async def starboard_limit(self, ctx, limit : int):
        """Sets the amount of stars required to the given intenger. Must be more than 0. 

        {usage}

        __Examples__
        `{pre}starboard limit 4` - set the required amount of stars on a message to 4, once a message hits 4 :star: they
        will be posted if there is a starboard channel set."""
        if limit < 1:
            return

        self.bot.server_data[ctx.guild.id]["starboard-limit"] = limit
        await self.bot.query_executer("UPDATE necrobot.Guilds SET starboard_limit = $1 WHERE guild_id = $2", limit, ctx.guild.id)
        await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'starboard-limit-set').format(limit)}")

    @commands.command()
    @has_perms(5)
    async def language(self, ctx, language : str):
        """Allows you to define a language for you your server, if supported the bot will us that language to communicate.
        Supported languages are `en`, `fr` a,d `de`

        {usage}

        __Examples__
        `{pre}language ` - sets the server language to english
        `{pre}language ` - sets the server language to french
        `{pre}language ` - sets the server language to german"""
        if language not in ["en", "fr", "de"]:
            await ctx.send(f":negative_squared_cross_mark: | {self.bot.t(ctx, 'language-not-supported')}")

        self.bot.server_data[ctx.guild.id]["language"] = language
        await self.bot.query_executer("UPDATE necrobot.Guilds SET lang = $1 WHERE guild_id = $2", language, ctx.guild.id)
        await ctx.send(f":white_check_mark: | {self.bot.t(ctx, 'language-set').format(language)}")

def setup(bot):
    bot.add_cog(Server(bot))
