#!/usr/bin/python3.6
import discord
from discord.ext import commands
from rings.utils.utils import has_perms


class Server():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @has_perms(4)
    async def perms(self, ctx, user : discord.Member, level : int):
        """Sets the NecroBot permission level of the given user, you can only set permission levels lower than your own. Permissions reset if you leave the server(Permission level required: 4+ (Server Admin))
         
        {usage}
        
        __Example__
        `{pre}perms @NecroBot 5` - set the NecroBot permission level to 5"""
        if self.bot.user_data[ctx.message.author.id]["perms"][ctx.message.guild.id] > level and self.bot.user_data[ctx.message.author.id]["perms"][ctx.message.guild.id] > self.bot.user_data[user.id]["perms"][ctx.message.guild.id]:
            self.bot.user_data[user.id]["perms"][ctx.message.guild.id] = level
            await ctx.message.channel.send(":white_check_mark: | All good to go, **"+ user.display_name + "** now has permission level **"+ str(level) + "**")
            if level == 6:
                for guild in self.bot.user_data[user.id]["perms"]:
                    self.bot.user_data[user.id]["perms"][guild] = 6
        else:
            await ctx.message.channel.send(":negative_squared_cross_mark: | You do not have the required NecroBot permission to grant this permission level")

    @commands.command()
    @has_perms(4)
    async def automod(self, ctx, *mentions):
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
            for x in self.bot.server_data[ctx.message.guild.id]["ignoreAutomod"]:
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

            await ctx.message.channel.send("Channels(**C**), Users(**U**) and Roles (**R**) ignored by auto moderation: ``` "+str(myList)+" ```")
        else:
            myList = self.bot.all_mentions(ctx, mentions)
            for x in myList:
                if x.id not in self.bot.server_data[ctx.message.guild.id]["ignoreAutomod"]:
                    self.bot.server_data[ctx.message.guild.id]["ignoreAutomod"].append(x.id)
                    await ctx.message.channel.send(":white_check_mark: | **"+ x.name +"** will be ignored by the bot's automoderation.")
                else:
                    self.bot.server_data[ctx.message.guild.id]["ignoreAutomod"].remove(x.id)
                    await ctx.message.channel.send(":white_check_mark: | **"+ x.name +"** will no longer be ignored by the bot's automoderation.")

    @commands.command()
    @has_perms(4)
    async def ignore(self, ctx, *mentions):
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
            for x in self.bot.server_data[ctx.message.guild.id]["ignoreCommand"]:
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

            await ctx.message.channel.send("Channels(**C**), Users(**U**) and Roles (**R**) ignored by NecroBot: ``` "+str(myList)+" ```")
        else:
            myList = self.bot.all_mentions(ctx, mentions)
            for x in myList:
                if x.id not in self.bot.server_data[ctx.message.guild.id]["ignoreCommand"]:
                    self.bot.server_data[ctx.message.guild.id]["ignoreCommand"].append(x.id)
                    await ctx.message.channel.send(":white_check_mark: | **"+ x.name +"** will be ignored by the bot.")
                else:
                    self.bot.server_data[ctx.message.guild.id]["ignoreCommand"].remove(x.id)
                    await ctx.message.channel.send(":white_check_mark: | **"+ x.name +"** will no longer be ignored by the bot.")

    @commands.group(aliases=["setting"], invoke_without_command=True)
    @has_perms(4)
    async def settings(self, ctx):
        """Creates a rich embed of the server settings, also the gateway to the rest of the the rest of the commands

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
        embed.add_field(name="Broadcast Interval", value="Every " + str(server["broadcast-time"]) + " hour(s)" if server["broadcast-time"] != "" else "None")
        embed.add_field(name="Auto Role", value= role_obj2.mention if server["auto-role"] != "" else "None", inline=False)
        embed.add_field(name="Starboard", value = self.bot.get_channel(server["starboard-channel"]).mention if server["starboard-channel"] != "" else "Disabled")
        embed.add_field(name="Starboard Limit", value=server["starboard-limit"])

        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

        await ctx.message.channel.send(embed=embed)

    @settings.command(name="mute")
    @has_perms(4)
    async def settings_mute(self, ctx, *, role=""):
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
            await ctx.message.channel.send(":white_check_mark: | Reset mute role")
            return
        role_obj = discord.utils.get(ctx.message.guild.roles, name=role)
        if not role_obj is None:
            await ctx.message.channel.send(":white_check_mark: | Okay, the mute role for your server will be " + role_obj.mention)
            self.bot.server_data[ctx.message.guild.id]["mute"] = role_obj.id
        else:
            await ctx.message.channel.send(":negative_squared_cross_mark: | No such role, make sure the role is spelled correctly, the role name is case-sensitive")

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
            await ctx.message.channel.send(":white_check_mark: | Welcome/Goodbye messages **disabled**")
        else:
            await ctx.message.channel.send(":white_check_mark: | Okay, users will get their welcome/goodbye message in " + channel.mention + " from now on.")
            self.bot.server_data[ctx.message.guild.id]["welcome-channel"] = channel.id

    @settings.command(name="automod")
    @has_perms(4)
    async def settings_automod_channel(self, ctx, channel : discord.TextChannel = ""):
        """Sets the automoderation channel to [channel], [channel] argument should be a channel mention. All the 
        auto-moderation related messages will be sent there. (Permission level required: 5+ (Server Owner))
         
        {usage}
        
        __Example__
        `{pre}settings automod #channel` - set the automoderation messages to be sent to channel 'channel'
        `{pre}settings automod` - disables automoderation for the entire server"""
        if channel == "":
            self.bot.server_data[ctx.message.guild.id]["automod"] = ""
            await ctx.message.channel.send(":white_check_mark: | Auto-moderation **disabled**")
        else:
            await ctx.message.channel.send(":white_check_mark: | Okay, all automoderation messages will be posted in " + channel.mention + " from now on.")
            self.bot.server_data[ctx.message.guild.id]["automod"] = channel.id

    @settings.command(name="welcome")
    @has_perms(4)
    async def settings_welcome(self, ctx, *, message=""):
        r"""Sets the welcome message (aka the message sent to the welcome channel when a new user joins), you can 
        format the message to mention the user and server. `{member}` will be replaced by a mention of the member and `{server}` will be replaced by the server name. To add emojis you need to add a backslash `\` before every semi-colon `:` (e.g `\:smiley_face\:`) (Permission level required: 5+ (Server Owner))
         
        {usage}
        
        __Example__
        `{pre}settings welcome Hello {member} \:wave\:` - sets the welcome message to be 'Hello {member} :wave:' with 
        `{member}` being replaced by the new member's name"""
        if message == "":
            await ctx.message.channel.send(":white_check_mark: | Welcome message reset and disabled")
        else:
            message = message.replace("\\","")
            await ctx.message.channel.send(":white_check_mark: | Your server's welcome message will be: \n" + message)

        self.bot.server_data[ctx.message.guild.id]["welcome"] = message

    @settings.command(name="goodbye")
    @has_perms(4)
    async def settings_goodbye(self, ctx, *, message):
        r"""Sets the goodbye message (aka the message sent to the welcome channel when a user leaves), you can format 
        the message to mention the user and server. `{member}` will be replaced by a mention of the member and `{server}` will be replaced by the server name. To add emojis you need to add a backslash `\` before every semi-colon `:` (e.g `\:smiley_face\:`) (Permission level required: 5+ (Server Owner))
         
        {usage}
        
        __Example__
        `{pre}settings goodbye Goodbye {member} \:wave\:` - sets the goodbye message to be 'Goodbye {member} :wave:' 
        with `{member}` being replaced by the new member's name"""
        
        if message == "":
            await ctx.message.channel.send(":white_check_mark: | Goodbye message reset and disabled")
        else:
            message = message.replace("\\","")
            await ctx.message.channel.send(":white_check_mark: | Your server's goodbye message will be: \n" + message)

        self.bot.server_data[ctx.message.guild.id]["goodbye"] = message

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
        if prefix == "":
            self.bot.server_data[ctx.message.guild.id]["prefix"] = ""
            await ctx.message.channel.send(":white_check_mark: | Custom prefix reset")
        else:
            self.bot.server_data[ctx.message.guild.id]["prefix"] = prefix
            await ctx.message.channel.send(":white_check_mark: | Server prefix is now **{}**".format(prefix))

    @settings.command(name="auto-role")
    @has_perms(4)
    async def settings_auto_role(self, ctx, role : discord.Role = None):
        """Sets the auto-role for this server to the given role. Auto-role will assign the role to the member when they join.

        {usage}

        __Example__
        stuff"""

        if role is None:
            self.bot.server_data[ctx.message.guild.id]["auto-role"] = ""
            await ctx.message.channel.send(":white_check_mark: | Auto-Role disabled")
        else:
            self.bot.server_data[ctx.message.guild.id]["auto-role"] = role.id
            await ctx.message.channel.send(":white_check_mark: | Joining members will now automatically be assigned the role **{}**".format(role.name))

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
            await ctx.message.channel.send(":white_check_mark: | **Broadcast messages disabled**")
            self.bot.server_data[ctx.message.guild.id]["broadcast"] = ""
            self.bot.server_data[ctx.message.guild.id]["broadcast-channel"] = ""


    @broadcast.command(name="channel")
    @has_perms(4)
    async def broadcast_channel(self, ctx, channel : discord.TextChannel = ""):
        """{usage}"""
        self.bot.server_data[ctx.message.guild.id]["broadcast-channel"] = channel.id
        await ctx.message.channel.send(":white_check_mark: | Okay, the broadcast message you set through `n!broadcast message` will be broadcasted in {}".format(channel.mention))        

    @broadcast.command(name="message")
    @has_perms(4)
    async def broadcast_message(self, ctx, *, message = ""):
        """{usage}"""
        self.bot.server_data[ctx.message.guild.id]["broadcast"] = message
        await ctx.message.channel.send(":white_check_mark: | Okay, the following messqge will be broadcasted in the channel you set using `n!broadcast channel` \n {}".format(message))        

    @broadcast.command(name="time")
    @has_perms(4)
    async def broadcast_time(self, ctx, hours : int):
        """{usage}"""
        if hours > 0:
            self.bot.server_data[ctx.message.guild.id]["broadcast-time"] = hours
            await ctx.message.channel.send(":white_check_mark: | Okay, the broadcast message you set through `n!broadcast message` will be broadcasted in the channel you set using `n!broadcast channel` every `{}` hour(s)".format(hours))        


    @commands.group(invoke_without_command = True)
    @commands.guild_only()
    async def giveme(self, ctx, *, role=""):
        """Gives the user the role if it is part of this Server's list of self assignable roles. If the user already 
        has the role it will remove it. **Roles names are case sensitive** If no role name is given then it will list
        the self-assignable roles for the server
         
        {usage}
        
        __Example__
        `{pre}giveme Good` - gives or remove the role 'Good' to the user if it is in the list of self assignable roles"""

        if role == "":
            await ctx.message.channel.send("List of Self Assignable Roles:\n-" + "\n- ".join(self.bot.server_data[ctx.message.guild.id]["selfRoles"]))
            return

        if role in self.bot.server_data[ctx.message.guild.id]["selfRoles"]:
            role_obj = discord.utils.get(ctx.message.guild.roles, name=role)
            if discord.utils.get(ctx.message.author.roles, name=role) is None:
                await ctx.message.author.add_roles(role_obj)
                await ctx.message.channel.send(":white_check_mark: | Role " + role_obj.name + " added.")
            else:
                await ctx.message.author.remove_roles(role_obj)
                await ctx.message.channel.send(":white_check_mark: | Role " + role_obj.name + " removed.")

        else:
            await ctx.message.channel.send(":negative_squared_cross_mark: | Role not self assignable")

    @giveme.command(name="add")
    @has_perms(4)
    async def giveme_add(self, ctx, *, role):
        """Adds [role] to the list of the server's self assignable roles. (Permission level required: 4+ (Server Admin))
         
        {usage}
        
        __Example__
        `{pre}giveme add Good` - adds the role 'Good' to the list of self assignable roles"""
        if not discord.utils.get(ctx.message.guild.roles, name=role) is None:
            self.bot.server_data[ctx.message.guild.id]["selfRoles"].append(role)
            await ctx.message.channel.send(":white_check_mark: | Added role " + role + " to list of self assignable roles.")
        else:
            await ctx.message.channel.send(":negative_squared_cross_mark: | No such role exists")

    @giveme.command(name="del")
    @has_perms(4)
    async def giveme_del(self, ctx, *, role):
        """Removes [role] from the list of the server's self assignable roles. (Permission level required: 4+ (Server Admin)
        
        {usage}
        
        __Example__
        `{pre}giveme del Good` - removes the role 'Good' from the list of self assignable roles"""
        if role in self.bot.server_data[ctx.message.guild.id]["selfRoles"]:
            self.bot.server_data[ctx.message.guild.id]["selfRoles"].remove(role)
            await ctx.message.channel.send(":white_check_mark: | Role " + role + " removed from self assignable roles")
        else:
            await ctx.message.channel.send(":negative_squared_cross_mark: | Role not in self assignable list")

    @commands.group()
    @has_perms(4)
    async def starboard(self, ctx):
        pass

    @starboard.command(name="channel")
    async def starboard_channel(self, ctx, channel : discord.TextChannel = ""):
        if channel == "":
            self.bot.server_data[ctx.guild.id]["starboard-channel"] = ""
            await ctx.send(":white_check_mark: | Starboard messages disabled.")
            return

        self.bot.server_data[ctx.guild.id]["starboard-channel"] = channel.id
        await ctx.send(":white_check_mark: | Starboard messages will now be sent to {}".format(channel.mention))

    @starboard.command(name="limit")
    async def starboard_limit(self, ctx, limit : int):
        self.bot.server_data[ctx.guild.id]["starboard-limit"] = limit
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