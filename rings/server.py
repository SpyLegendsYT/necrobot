#!/usr/bin/python3.6
import discord
from discord.ext import commands
from rings.utils.utils import has_perms
import re

class NecroConverter(commands.IDConverter):

    async def convert(self, ctx, argument):
        message = ctx.message
        bot = ctx.bot
        match = self._get_id_match(argument) or re.match(r'<@!?([0-9]+)>$', argument)
        guild = ctx.guild
        result = None
        if match is None:
            # not a mention...
            if guild:
                result = guild.get_member_named(argument)
            else:
                result = _get_from_guilds(bot, 'get_member_named', argument)
        else:
            user_id = int(match.group(1))
            if guild:
                result = guild.get_member(user_id)
            else:
                result = _get_from_guilds(bot, 'get_member', user_id)

        if not result is None:
            return result

        match = self._get_id_match(argument) or re.match(r'<#([0-9]+)>$', argument)

        if match is None:
            # not a mention
            if guild:
                result = discord.utils.get(guild.text_channels, name=argument)
            else:
                def check(c):
                    return isinstance(c, discord.TextChannel) and c.name == argument
                result = discord.utils.find(check, bot.get_all_channels())
        else:
            channel_id = int(match.group(1))
            if guild:
                result = guild.get_channel(channel_id)
            else:
                result = _get_from_guilds(bot, 'get_channel', channel_id)   

        if not result is None:
            return result 

        if not guild:
            raise NoPrivateMessage()

        match = self._get_id_match(argument) or re.match(r'<@&([0-9]+)>$', argument)
        params = dict(id=int(match.group(1))) if match else dict(name=argument)
        result = discord.utils.get(guild.roles, **params)
        if not result is None:
            return result

        raise commands.BadArgument("Not role/channel/member")    

class Server():
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @has_perms(4)
    async def perms(self, ctx, user : discord.Member, level : int):
        """Sets the NecroBot permission level of the given user, you can only set permission levels lower than your own. Permissions reset if you leave the server(Permission level required: 4+ (Server Admin))
         
        {usage}
        
        __Example__
        `{pre}perms @NecroBot 5` - set the NecroBot permission level to 5"""
        if self.bot.user_data[ctx.message.author.id]["perms"][ctx.message.guild.id] > level and self.bot.user_data[ctx.message.author.id]["perms"][ctx.message.guild.id] > self.bot.user_data[user.id]["perms"][ctx.message.guild.id]:
            self.bot.user_data[user.id]["perms"][ctx.message.guild.id] = level
            await self.bot.query_executer("UPDATE necrobot.Permissions SET level = $1 WHERE guild_id = $2 AND user_id = $3;", level, ctx.guild.id, user.id)
            await ctx.send(":white_check_mark: | All good to go, **"+ user.display_name + "** now has permission level **"+ str(level) + "**")
            if level == 6:
                for guild in self.bot.user_data[user.id]["perms"]:
                    self.bot.user_data[user.id]["perms"][guild] = 6
                    await self.bot.query_executer("UPDATE necrobot.Permissions SET level = 6 WHERE guild_id = $1 AND user_id = $2;", guild, user.id)
        else:
            await ctx.send(":negative_squared_cross_mark: | You do not have the required NecroBot permission to grant this permission level")
    @perms.command(name="help")
    async def perms_help(self, ctx):
        pass

    @commands.command()
    @has_perms(4)
    async def automod(self, ctx, *mentions : NecroConverter):
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
        """

        if len(mentions) < 1:
            myList = []
            for x in self.bot.server_data[ctx.message.guild.id]["ignore-automod"]:
                try:
                    myList.append("C: "+self.bot.get_channel(x).name)
                except AttributeError:
                    try:
                        myList.append("U: "+self.bot.get_member(x).name)
                    except AttributeError:
                        try:
                            role = discord.utils.get(ctx.message.guild.roles, id=x)
                            myList.append("R: " + role.name)
                        except AttributeError:
                            pass

            await ctx.send("Channels(**C**), Users(**U**) and Roles (**R**) ignored by auto moderation: ``` "+str(myList)+" ```")
            return

        for x in mentions:
            if x.id not in self.bot.server_data[ctx.message.guild.id]["ignore-automod"]:
                self.bot.server_data[ctx.message.guild.id]["ignore-automod"].append(x.id)
                await ctx.send(":white_check_mark: | **"+ x.name +"** will be ignored by the bot's automoderation.")
                await self.bot.query_executer("INSERT INTO necrobot.IgnoreAutomod VALUES ($1, $2);", ctx.guild.id, x.id)
            else:
                self.bot.server_data[ctx.message.guild.id]["ignore-automod"].remove(x.id)
                await ctx.send(":white_check_mark: | **"+ x.name +"** will no longer be ignored by the bot's automoderation.")
                await self.bot.query_executer("DELETE FROM necrobot.IgnoreAutomod WHERE guild_id = $1 AND id = $2;", ctx.guild.id, x.id)

    @commands.command()
    @has_perms(4)
    async def ignore(self, ctx, *mentions : NecroConverter):
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
        """

        if len(mentions) < 1:
            myList = []
            for x in self.bot.server_data[ctx.message.guild.id]["ignore-command"]:
                try:
                    myList.append("C: "+self.bot.get_channel(x).name)
                except AttributeError:
                    try:
                        myList.append("U: "+self.bot.get_member(x).name)
                    except AttributeError:
                        try:
                            role = discord.utils.get(ctx.message.guild.roles, id=x)
                            myList.append("R: " + role.name)
                        except AttributeError:
                            pass

            await ctx.send("Channels(**C**), Users(**U**) and Roles (**R**) ignored by NecroBot: ``` "+str(myList)+" ```")
            return
        
        for x in mentions:
            if x.id not in self.bot.server_data[ctx.message.guild.id]["ignore-command"]:
                self.bot.server_data[ctx.message.guild.id]["ignore-command"].append(x.id)
                await ctx.send(":white_check_mark: | **"+ x.name +"** will be ignored by the bot.")
                await self.bot.query_executer("INSERT INTO necrobot.IgnoreCommand VALUES ($1, $2);", ctx.guild.id, x.id)
            else:
                self.bot.server_data[ctx.message.guild.id]["ignore-command"].remove(x.id)
                await ctx.send(":white_check_mark: | **"+ x.name +"** will no longer be ignored by the bot.")
                await self.bot.query_executer("DELETE FROM necrobot.IgnoreCommand WHERE guild_id = $1 AND id = $2;", ctx.guild.id, x.id)

    @commands.group(aliases=["setting"], invoke_without_command=True)
    @has_perms(4)
    async def settings(self, ctx):
        """Creates a rich embed of the server settings, also the gateway to the rest of the commands

        {usage}"""
        server = self.bot.server_data[ctx.message.guild.id]
        role_obj = discord.utils.get(ctx.message.guild.roles, id=server["mute"])
        role_obj2 = discord.utils.get(ctx.message.guild.roles, id=server["auto-role"])
        embed = discord.Embed(title="__**Server Settings**__", colour=discord.Colour(0x277b0), description="Info on the NecroBot settings for this server")
        embed.add_field(name="Automod Channel", value=self.bot.get_channel(server["automod"]).mention if server["automod"] != "" else "Disabled")
        embed.add_field(name="Welcome Channel", value=self.bot.get_channel(server["welcome-channel"]).mention if server["welcome-channel"] != "" else "Disabled")
        embed.add_field(name="Welcome Message", value=server["welcome"] if server["welcome"] != "" else "None", inline=False)
        embed.add_field(name="Goodbye Message", value=server["goodbye"] if server["goodbye"] != "" else "None", inline=False)
        embed.add_field(name="Mute Role", value=role_obj.mention if server["mute"] != "" else "Disabled")
        embed.add_field(name="Prefix", value="`" + server["prefix"] + "`" if server["prefix"] != "" else "`n!`")
        embed.add_field(name="Broadcast Message", value=server["broadcast"] if server["broadcast"] != "" else "None", inline=False)
        embed.add_field(name="Broadcast Channel", value=self.bot.get_channel(server["broadcast-channel"]).mention if server["broadcast-channel"] != "" else "None")
        embed.add_field(name="Broadcast Frequency", value="Every " + str(server["broadcast-time"]) + " hour(s)" if server["broadcast-time"] != "" else "None")
        embed.add_field(name="Auto Role", value= role_obj2.mention if server["auto-role"] != "" else "None", inline=False)
        embed.add_field(name="Starboard", value = self.bot.get_channel(server["starboard-channel"]).mention if server["starboard-channel"] != "" else "Disabled")
        embed.add_field(name="Starboard Limit", value=server["starboard-limit"])

        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

        await ctx.send(embed=embed)

    @settings.command(name="mute")
    @has_perms(4)
    async def settings_mute(self, ctx, *, role : discord.Role = ""):
        """Sets the mute role for this server to [role], this is used for the `mute` command, it is the role assigned by 
        the command to the user. Make sure to spell the role correctly, the role name is case sensitive. It is up to the server 
        authorities to set up the proper permissions for the chosen mute role. Once the role is set up it can be renamed and 
        edited as seen needed, NecroBot keeps the id saved. Unexpect behavior can happen if multiple roles have the same name.
        (Permission level required: 5+ (Server Owner))
         
        {usage}
        
        __Example__
        `{pre}settings mute Token Mute Role` - set the mute role to be the role named 'Token Mute Role'
        `{pre}settings mute` - resets the mute role and disables the `mute` command."""
        if role == "":
            self.bot.server_data[ctx.message.guild.id]["mute"] = ""
            await self.bot.query_executer("UPDATE necrobot.Guilds SET mute = 0 WHERE guild_id = $1;", ctx.guild.id)
            await ctx.send(":white_check_mark: | Reset mute role")
            return

        await ctx.send(":white_check_mark: | Okay, the mute role for your server will be " + role.mention)
        self.bot.server_data[ctx.message.guild.id]["mute"] = role.id
        await self.bot.query_executer("UPDATE necrobot.Guilds SET mute = $1 WHERE guild_id = $2;", role.id, ctx.guild.id)

    @settings.command(name="welcome-channel")
    @has_perms(4)
    async def settings_welcome_channel(self, ctx, channel : discord.TextChannel = ""):
        """Sets the welcome channel to [channel], the [channel] argument should be a channel mention. The welcome 
        message for users will be sent there. (Permission level required: 5+ (Server Owner))
         
        {usage}
        
        __Example__
        `{pre}settings welcome-channel #channel` - set the welcome messages to be sent to 'channel'
        `{pre}settings welcome-channel` - disables welcome messages"""
        if channel == "":
            self.bot.server_data[ctx.message.guild.id]["welcome-channel"] = ""
            await self.bot.query_executer("UPDATE necrobot.Guilds SET welcome_channel = 0 WHERE guild_id = $1;", ctx.guild.id)
            await ctx.send(":white_check_mark: | Welcome/Goodbye messages **disabled**")
        else:
            self.bot.server_data[ctx.message.guild.id]["welcome-channel"] = channel.id
            await self.bot.query_executer("UPDATE necrobot.Guilds SET welcome_channel = $1 WHERE guild_id = $2;", channel.id, ctx.guild.id)
            await ctx.send(":white_check_mark: | Okay, users will get their welcome/goodbye message in " + channel.mention + " from now on.")

    @settings.command(name="automod-channel")
    @has_perms(4)
    async def settings_automod_channel(self, ctx, channel : discord.TextChannel = ""):
        """Sets the automoderation channel to [channel], [channel] argument should be a channel mention. All the 
        auto-moderation related messages will be sent there. (Permission level required: 5+ (Server Owner))
         
        {usage}
        
        __Example__
        `{pre}settings automod-channel #channel` - set the automoderation messages to be sent to channel 'channel'
        `{pre}settings automod-channel` - disables automoderation for the entire server"""
        if channel == "":
            self.bot.server_data[ctx.message.guild.id]["automod"] = ""
            await self.bot.query_executer("UPDATE necrobot.Guilds SET automod_channel = 0 WHERE guild_id = $1;", ctx.guild.id)
            await ctx.send(":white_check_mark: | Auto-moderation **disabled**")
        else:
            self.bot.server_data[ctx.message.guild.id]["automod"] = channel.id
            await self.bot.query_executer("UPDATE necrobot.Guilds SET automod_channel = $2 WHERE guild_id = $1;", ctx.guild.id, channel.id)
            await ctx.send(":white_check_mark: | Okay, all automoderation messages will be posted in " + channel.mention + " from now on.")

    @settings.command(name="welcome")
    @has_perms(4)
    async def settings_welcome(self, ctx, *, message=""):
        r"""Sets the welcome message (aka the message sent to the welcome channel when a new user joins), you can 
        format the message to mention the user and server. `{member}` will be replaced by a mention of the member and `{server}` will be replaced by the server name. To add emojis you need to add a backslash `\` before every semi-colon `:` (e.g `\:smiley_face\:`) (Permission level required: 5+ (Server Owner))
         
        {usage}
        
        __Example__
        `{pre}settings welcome Hello {member} \:wave\:` - sets the welcome message to be 'Hello {member} :wave:' with 
        `{member}` being replaced by the new member's name"""
        self.bot.server_data[ctx.message.guild.id]["welcome"] = message
        await self.bot.query_executer("UPDATE necrobot.Guilds SET welcome_message = $1 WHERE guild_id = $2;", message, ctx.guild.id)

        if message == "":
            await ctx.send(":white_check_mark: | Welcome message reset and disabled")
        else:
            message = message.replace("\\","")
            await ctx.send(":white_check_mark: | Your server's welcome message will be: \n" + message)

    @settings.command(name="goodbye")
    @has_perms(4)
    async def settings_goodbye(self, ctx, *, message):
        r"""Sets the goodbye message (aka the message sent to the welcome channel when a user leaves), you can format 
        the message to mention the user and server. `{member}` will be replaced by a mention of the member and `{server}` will be replaced by the server name. To add emojis you need to add a backslash `\` before every semi-colon `:` (e.g `\:smiley_face\:`) (Permission level required: 5+ (Server Owner))
         
        {usage}
        
        __Example__
        `{pre}settings goodbye Goodbye {member} \:wave\:` - sets the goodbye message to be 'Goodbye {member} :wave:' 
        with `{member}` being replaced by the new member's name"""
        self.bot.server_data[ctx.message.guild.id]["goodbye"] = message
        await self.bot.query_executer("UPDATE necrobot.Guilds SET goodbye_message = $1 WHERE guild_id = $2;", message, ctx.guild.id)

        if message == "":
            await ctx.send(":white_check_mark: | Goodbye message reset and disabled")
        else:
            message = message.replace("\\","")
            await ctx.send(":white_check_mark: | Your server's goodbye message will be: \n" + message)

    @settings.command(name="prefix")
    @has_perms(4)
    async def settings_prefix(self, ctx, *, prefix=""):
        """Sets the bot to only respond to the given prefix. If no prefix is given it will reset it to NecroBot's deafult 
        list of prefixes: `{pre}`, `N!` or `@NecroBot `

        {usage}

        __Example__
        `{pre}settings prefix bob! potato` - sets the prefix to be `bob! potato ` so a command like `{pre}cat` will now be 
        summoned like this `bob! potato cat`
        `{pre}settings prefix` - resets the prefix to NecroBot's default list"""
        self.bot.server_data[ctx.message.guild.id]["prefix"] = prefix
        await self.bot.query_executer("UPDATE necrobot.Guilds SET prefix = $1 WHERE guild_id = $2;", prefix, ctx.guild.id)


        if prefix == "":
            await ctx.send(":white_check_mark: | Custom prefix reset")
        else:
            await ctx.send(":white_check_mark: | Server prefix is now **{}**".format(prefix))

    @settings.command(name="auto-role")
    @has_perms(4)
    async def settings_auto_role(self, ctx, role : discord.Role = None):
        """Sets the auto-role for this server to the given role. Auto-role will assign the role to the member when they join.

        {usage}

        __Example__
        stuff"""

        if role is None:
            self.bot.server_data[ctx.message.guild.id]["auto-role"] = ""
            await self.bot.query_executer("UPDATE necrobot.Guilds SET auto_role = 0 WHERE guild_id = $1;", ctx.guild.id)
            await ctx.send(":white_check_mark: | Auto-Role disabled")
        else:
            self.bot.server_data[ctx.message.guild.id]["auto-role"] = role.id
            await self.bot.query_executer("UPDATE necrobot.Guilds SET auto_role = $1 WHERE guild_id = $2;", role.id, ctx.guild.id)
            await ctx.send(":white_check_mark: | Joining members will now automatically be assigned the role **{}**".format(role.name))

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
            await ctx.send(":white_check_mark: | **Broadcast messages disabled**")
            self.bot.server_data[ctx.message.guild.id]["broadcast"] = ""
            self.bot.server_data[ctx.message.guild.id]["broadcast-channel"] = ""
            await self.bot.query_executer("UPDATE necrobot.Guilds SET broadcast_channel = 0, broadcast_message = '' WHERE guild_id = $1;", ctx.guild.id)


    @broadcast.command(name="channel")
    @has_perms(4)
    async def broadcast_channel(self, ctx, channel : discord.TextChannel = ""):
        """Used to set the channel the message will be broadcasted into.

        {usage}

        __Example__
        `{pre}broadcast channel #general` - sets the broadcast channel to #general"""
        if channel == "":
            self.bot.server_data[ctx.message.guild.id]["broadcast-channel"] = ""
            await self.bot.query_executer("UPDATE necrobot.Guilds SET broadcast_channel = 0 WHERE guild_id = $1;", ctx.guild.id)
            await ctx.send(":white_check_mark: | Broadcast messages disabled")        
 
        self.bot.server_data[ctx.message.guild.id]["broadcast-channel"] = channel.id
        await self.bot.query_executer("UPDATE necrobot.Guilds SET broadcast_channel = $1 WHERE guild_id = $2;", channel.id, ctx.guild.id)
        await ctx.send(":white_check_mark: | Okay, the broadcast message you set through `n!broadcast message` will be broadcasted in {}".format(channel.mention))        

    @broadcast.command(name="message")
    @has_perms(4)
    async def broadcast_message(self, ctx, *, message = ""):
        """Used to set the message that will be broadcasted

        {usage}

        __Example__
        `{pre}broadcast message test 1 2 3` - sets the broadcast channel to #general"""

        self.bot.server_data[ctx.message.guild.id]["broadcast"] = message
        await self.bot.query_executer("UPDATE necrobot.Guilds SET broadcast_message = $1 WHERE guild_id = $2;", message, ctx.guild.id)
        
        if message == "":
            await ctx.send(":white_check_mark: | Broadcast messages disabled")
            return

        await ctx.send(":white_check_mark: | Okay, the following messqge will be broadcasted in the channel you set using `n!broadcast channel` \n {}".format(message))        

    @broadcast.command(name="time")
    @has_perms(4)
    async def broadcast_time(self, ctx, hours : int):
        """Used to set the interval at which the message is broadcasted (in hours)

        {usage}

        __Example__
        `{pre}broadcast time 4` - sets the broadcast message to be sent every 4 hour"""
        if hours > 0 and hours <= 24:
            self.bot.server_data[ctx.message.guild.id]["broadcast-time"] = hours
            await self.bot.query_executer("UPDATE necrobot.Guilds SET broadcast_time = $1 WHERE guild_id = $2;", hours, ctx.guild.id)
            await ctx.send(":white_check_mark: | Okay, the broadcast message you set through `n!broadcast message` will be broadcasted in the channel you set using `n!broadcast channel` every `{}` hour(s)".format(hours))        


    @commands.group(invoke_without_command = True)
    @commands.guild_only()
    async def giveme(self, ctx, *, role : discord.Role = ""):
        """Gives the user the role if it is part of this Server's list of self assignable roles. If the user already 
        has the role it will remove it. **Roles names are case sensitive** If no role name is given then it will list
        the self-assignable roles for the server
         
        {usage}
        
        __Example__
        `{pre}giveme Good` - gives or remove the role 'Good' to the user if it is in the list of self assignable roles"""

        if role == "":
            roles = [x.name for x in ctx.guild.roles if x.id in self.bot.server_data[ctx.message.guild.id]["self-roles"]]
            await ctx.send("List of Self Assignable Roles:\n- " + "\n- ".join(roles))
            return

        if role.id in self.bot.server_data[ctx.message.guild.id]["self-roles"]:
            if role not in ctx.author.roles:
                await ctx.message.author.add_roles(role)
                await ctx.send(":white_check_mark: | Role " + role.name + " added.")
            else:
                await ctx.message.author.remove_roles(role)
                await ctx.send(":white_check_mark: | Role " + role.name + " removed.")

        else:
            await ctx.send(":negative_squared_cross_mark: | Role not self assignable")

    @giveme.command(name="add")
    @has_perms(4)
    async def giveme_add(self, ctx, *, role : discord.Role):
        """Adds [role] to the list of the server's self assignable roles. (Permission level required: 4+ (Server Admin))
         
        {usage}
        
        __Example__
        `{pre}giveme add Good` - adds the role 'Good' to the list of self assignable roles"""
        if role.id in self.bot.server_data[ctx.message.guild.id]["self-roles"]:
            await ctx.send(":negative_squared_cross_mark: | Role already in list of self assignable roles")
            return

        await self.bot.query_executer("INSERT INTO necrobot.SelfRoles VALUES ($1, $2);", ctx.guild.id, role.id)
        self.bot.server_data[ctx.message.guild.id]["self-roles"].append(role.id)
        await ctx.send(":white_check_mark: | Added role **{}** to list of self assignable roles.".format(role.name))

    @giveme.command(name="del")
    @has_perms(4)
    async def giveme_del(self, ctx, *, role : discord.Role):
        """Removes [role] from the list of the server's self assignable roles. (Permission level required: 4+ (Server Admin)
        
        {usage}
        
        __Example__
        `{pre}giveme del Good` - removes the role 'Good' from the list of self assignable roles"""
        if role.id not in self.bot.server_data[ctx.message.guild.id]["self-roles"]:
            await ctx.send(":negative_squared_cross_mark: | Role not in self assignable list")
            return

        await self.bot.query_executer("DELETE FROM necrobot.SelfRoles WHERE guild_id = $1 AND id = $2;", ctx.guild.id, role.id)
        self.bot.server_data[ctx.message.guild.id]["self-roles"].remove(role.id)
        await ctx.send(":white_check_mark: | Role **{}** removed from self assignable roles".format(role.name))
            

    @commands.group()
    @has_perms(4)
    async def starboard(self, ctx):
        """Base of the concept of R.Danny's starboard but simplified. This will post a message in a desired channel once it hits
        a certain number of :star: reactions. Default limit is 5, you can change the limit with `{pre}starboard limit`"""
        pass

    @starboard.command(name="channel")
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
            await self.bot.query_executer("UPDATE necrobot.Guilds SET starboard_channel = 0 WHERE guild_id = $1;", ctx.guild.id)
            await ctx.send(":white_check_mark: | Starboard messages disabled.")
            return

        self.bot.server_data[ctx.guild.id]["starboard-channel"] = channel.id
        await self.bot.query_executer("UPDATE necrobot.Guilds SET starboard_channel = $1 WHERE guild_id = $2;", channel.id, ctx.guild.id)
        await ctx.send(":white_check_mark: | Starboard messages will now be sent to {}".format(channel.mention))

    @starboard.command(name="limit")
    async def starboard_limit(self, ctx, limit : int):
        """Sets the amount of stars required to the given intenger. Must be more than 0. 

        {usage}

        __Examples__
        `{pre}starboard limit 4` - set the required amount of stars on a message to 4, once a message hits 4 :star: they
        will be posted if there is a starboard channel set."""
        if limit < 1:
            return

        self.bot.server_data[ctx.guild.id]["starboard-limit"] = limit
        await self.bot.query_executer("UPDATE necrobot.Guilds SET starboard_limit = $1 WHERE guild_id = $2;", limit, ctx.guild.id)
        await ctx.send(":white_check_mark: | Starred messages will now be posted on the starboard once they hit **{}** stars".format(limit))

    # @starboard.command(name="reaction")
    # async def starboard_reaction(self, ctx, reaction = ""):
    #     if reaction == "":
    #         self.bot.server_data[ctx.guild.id]["starboard-reacton"] = ""
    #         await ctx.send(":white_check_mark: | Starboard reaction reset to :star:.")
    #         return

    #     self.bot.server_data[ctx.guild.id]["starboard-reacton"] = reaction.id
    #     await ctx.send(":white_check_mark: | Messages will now only be counted as \"starred\" if they have the required number of {}".format(reaction))

def setup(bot):
    bot.add_cog(Server(bot))