import discord
from discord.ext import commands

from rings.utils.utils import has_perms, react_menu, TimeConverter, BotError, check_channel, range_check

from typing import Union
import re
import asyncio

class Server(commands.Cog):
    """Contains all the commands related to customising Necrobot's behavior on your server and to your server members. Contains
    commands for stuff such as setting broadcast, giving users permissions, ignoring users, getting info on your current settings,
    ect..."""
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        if ctx.guild:
            return True

        raise commands.CheckFailure("This command cannot be used in private messages.")

    def get_all(self, ctx, entries):
        l = []
        for x in entries:
            channel = ctx.guild.get_channel(x)
            if channel:
                l.append(f"C: {channel.name}")
                continue

            member = ctx.guild.get_member(x)
            if member:
                l.append(f"U: {member.name}")
                continue

            role = ctx.guild.get_role(x)
            if role:
                l.append(f"R: {role.name}")
                continue

        return l

    @commands.command(aliases=["perms"])
    @has_perms(4)
    async def permissions(self, ctx, user : discord.Member = None, level : int = None):
        """Sets the NecroBot permission level of the given user, you can only set permission levels lower than your own. 
        Permissions reset if you leave the server.
         
        {usage}
        
        __Example__
        `{pre}permissions @NecroBot 5` - set the NecroBot permission level to 5
        `{pre}perms @NecroBot 5` - set the NecroBot permission level to 5"""
        if level is None and user is not None:
            level = await self.bot.db.get_permission(ctx.guild.id, user.id)
            return await ctx.send(f"**{user.display_name}** is level **{level}** ({self.bot.perms_name[level]})")

        if level is None and user is None:
            members = await self.bot.db.query_executer(
                "SELECT user_id, level FROM necrobot.Permissions WHERE level > 0 AND guild_id = $1 ORDER BY level DESC",
                ctx.guild.id    
            )
            
            def _embed_maker(index, entries):
                string = ""
                for member in entries:
                    name = ctx.guild.get_member(member[0]).display_name
                    level = member[1]
                    
                    string += f"\n -**{name}**: {level} ({self.bot.perms_name[level]})"

                embed = discord.Embed(title="Permissions on your server", description=string, colour=discord.Colour(0x277b0))
                embed.set_footer(text="Generated by Necrobot", icon_url=self.bot.user.avatar_url_as(format="png", size=128))
                return embed

            return await react_menu(ctx, members, 10, _embed_maker)

        if level < 0 or level > 7:
            raise BotError("You cannot promote the user any higher/lower")

        if await self.bot.db.compare_user_permission(ctx.author.id, ctx.guild.id, user.id) > 0:
            current_level = await self.bot.db.get_permission(user.id, ctx.guild.id)
            await self.bot.db.update_permission(user.id, ctx.guild.id, update=level)
            
            if current_level < level:
                await ctx.send(f":white_check_mark: | **{user.display_name}** has been promoted to **{self.bot.perms_name[level]}** ({level})")
            else:
                await ctx.send(f":white_check_mark: | **{user.display_name}** has been demoted to **{self.bot.perms_name[level]}** ({level})")
            
        else:
            raise BotError("You do not have the required NecroBot permission to grant this permission level")

    @commands.command()
    @has_perms(4)
    async def promote(self, ctx, member : discord.Member):
        """Promote a member by one on the Necrobot hierarchy scale. Gaining access to additional commands.

        {usage}

        __Examples__
        `{pre}promote NecroBot` - promote necrobot by one level
        """
        current = await self.bot.db.get_permission(member.id, ctx.guild.id)
        await ctx.invoke(self.bot.get_command("permissions"), user=member, level=current + 1)

    @commands.command()
    @has_perms(4)
    async def demote(self, ctx, member : discord.Member):
        """Demote a member by one on the Necrobot hierarchy scale. Losing access to certain commands.

        {usage}

        __Examples__
        `{pre}demote NecroBot` - demote necrobot by one level
        """
        current = await self.bot.db.get_permission(member.id, ctx.guild.id)
        await ctx.invoke(self.bot.get_command("permissions"), user=member, level=current - 1)

    @commands.group(invoke_without_command=True)
    @has_perms(4)
    async def automod(self, ctx, *mentions : Union[discord.Member, discord.TextChannel, discord.Role]):
        """Used to manage the list of channels and user ignored by the bot's automoderation system. If no mentions are 
        given it will print out the list of ignored Users (**U**) and the list of ignored Channels (**C**). The automoderation 
        feature tracks the edits made by users to their own messages and the deleted messages, printing them in the server's automod 
        channel. If mentions are given then it will add any user/channel not already ignored and remove any user/channel already ignored. 
        Set the automod channel using `{pre}settings automod`
         
        {usage}

        __Example__
        `{pre}automod` - prints the list of users/channels ignored by necrobot's automoderation feature
        `{pre}automod @Necro #general` - adds user Necro and channel general to list of users/channels ignored by the necrobot's automoderation
        `{pre}automod @NecroBot #general` - adds user Necrobot to the list of users ignored by the automoderation and removes channel #general 
        from it (since we added it above)
        `{pre}automod @ARole` - adds role ARole to the list of roles ignored by automoderation
        """

        if not mentions:
            ignored = self.bot.guild_data[ctx.guild.id]["ignore-automod"] 
            
            def _embed_maker(index, entries):
                string = '\n- '.join(entries)
                embed = discord.Embed(
                    title=f"Ignored by Automod ({index[0]}/{index[1]})", 
                    colour=discord.Colour(0x277b0), 
                    description=f"Channels(**C**), Users(**U**) and Roles (**R**) ignored by auto moderation:\n- {string}") 
                
                embed.set_footer(text="Generated by Necrobot", icon_url=self.bot.user.avatar_url_as(format="png", size=128))
                return embed
                
            return await react_menu(ctx, self.get_all(ctx, ignored), 10, _embed_maker)                       

        to_add = []
        to_remove = []
        
        for x in mentions:
            if x.id in self.bot.guild_data[ctx.guild.id]["ignore-automod"]:
                to_remove.append(x)
            else:
                to_add.append(x)
        
        if to_add:
            string = ', '.join([f"**{x.name}**" for x in to_add])
            await self.bot.db.insert_automod_ignore(ctx.guild.id, *[x.id for x in to_add])
            await ctx.send(f":white_check_mark: | {string} will now be ignored")
        
        if to_remove:
            string = ', '.join([f"**{x.name}**" for x in to_remove])
            await self.bot.db.delete_automod_ignore(ctx.guild.id, *[x.id for x in to_remove])
            await ctx.send(f":white_check_mark: | {string} will no longer be ignored")

    @automod.command(name="channel")
    @has_perms(4)
    async def automod_channel(self, ctx, channel : discord.TextChannel = 0):
        """Sets the automoderation channel to [channel], [channel] argument should be a channel mention. All the 
        auto-moderation related messages will be sent there.
         
        {usage}
        
        __Example__
        `{pre}automod channel #channel` - set the automoderation messages to be sent to channel 'channel'
        `{pre}automod channel` - disables automoderation for the entire server"""

        if channel:
            check_channel(channel)
            await self.bot.db.update_automod_channel(ctx.guild.id, channel.id)
            await ctx.send(f":white_check_mark: | Okay, all automoderation messages will be posted in {channel.mention} from now on.")
        else:
            await self.bot.db.update_automod_channel(ctx.guild.id)
            await ctx.send(":white_check_mark: | Auto-moderation **disabled**")

    @commands.command()
    @has_perms(4)
    async def ignore(self, ctx, *mentions : Union[discord.Member, discord.TextChannel, discord.Role]):
        """Used to manage the list of channels and user ignored by the bot's command system. If no mentions are 
        given it will print out the list of ignored Users (**U**) and the list of ignored Channels (**C**). Being ignored
        by the command system means that user cannot use any of the bot commands on the server. If mentions are given then 
        it will add any user/channel not already ignored and remove any user/channel already ignored.
         
        {usage}

        __Example__
        `{pre}ignore` - prints the list of users/channels ignored by necrobot
        `{pre}ignore @Necro #general` - adds user Necro and channel general to list of users/channels ignored by the necrobot
        `{pre}ignore @NecroBot #general` - adds user Necrobot to the list of users ignored by the bot and removes channel #general 
        from it (since we added it above)
        `{pre}ignore @ARole` - adds role ARole to the list of roles ignored by the bot
        """

        if not mentions:
            ignored = self.bot.guild_data[ctx.guild.id]["ignore-command"] 
            
            def _embed_maker(index, entries):
                string = '\n- '.join(entries)
                embed = discord.Embed(
                    title=f"Ignored by command ({index[0]}/{index[1]})", 
                    colour=discord.Colour(0x277b0), 
                    description=f"Channels(**C**), Users(**U**) and Roles (**R**) ignored by the bot:\n- {string}") 
                
                embed.set_footer(text="Generated by Necrobot", icon_url=self.bot.user.avatar_url_as(format="png", size=128))
                return embed
                
            return await react_menu(ctx, self.get_all(ctx, ignored), 10, _embed_maker)     
        
        to_add = []
        to_remove = []
        
        for x in mentions:
            if x.id in self.bot.guild_data[ctx.guild.id]["ignore-command"]:
                to_remove.append(x)
            else:
                to_add.append(x)
                
        if to_add:
            string = ', '.join([f"**{x.name}**" for x in to_add])
            await self.bot.db.insert_command_ignore(ctx.guild.id, *[x.id for x in to_add])
            await ctx.send(f":white_check_mark: | {string} will now be ignored")
        
        if to_remove:
            string = ', '.join([f"**{x.name}**" for x in to_remove])
            await self.bot.db.delete_command_ignore(ctx.guild.id, *[x.id for x in to_remove])
            await ctx.send(f":white_check_mark: | {string} will no longer be ignored")

    @commands.command(aliases=["setting"])
    @has_perms(4)
    async def settings(self, ctx):
        """Creates a rich embed of the server settings

        {usage}"""
        server = self.bot.guild_data[ctx.guild.id] 
        role_obj = discord.utils.get(ctx.guild.roles, id=server["mute"])
        role_obj2 = discord.utils.get(ctx.guild.roles, id=server["auto-role"])
        embed = discord.Embed(title="Server Settings", colour=discord.Colour(0x277b0), description="Info on the NecroBot settings for this server")
        embed.add_field(
            name="Automod Channel", 
            value=self.bot.get_channel(server["automod"]).mention if server["automod"] else "Disabled"
        )
        embed.add_field(
            name="Welcome Channel", 
            value=self.bot.get_channel(server["welcome-channel"]).mention if server["welcome-channel"] else "Disabled"
        )
        embed.add_field(
            name="Welcome Message", 
            value=server["welcome"][:1024] if server["welcome"] else "None", 
            inline=False
        )
        embed.add_field(
            name="Goodbye Message", 
            value=server["goodbye"][:1024] if server["goodbye"] else "None", 
            inline=False
        )
        embed.add_field(
            name="Mute Role", 
            value=role_obj.mention if server["mute"] else "Disabled"
        )
        embed.add_field(
            name="Prefix", 
            value=f'`{server["prefix"]}`' if server["prefix"] else "`n!`"
        )
        embed.add_field(
            name="Broadcast Channel", 
            value=self.bot.get_channel(server["broadcast-channel"]).mention if server["broadcast-channel"] else "Disabled"
        )
        embed.add_field(
            name="Broadcast Frequency", 
            value=f'Every {server["broadcast-time"]} hour(s)' if server["broadcast-time"] else "None"
        )
        embed.add_field(
            name="Broadcast Message", 
            value=server["broadcast"] if server["broadcast"] else "None", 
            inline=False
        )
        embed.add_field(
            name="Auto Role", 
            value= role_obj2.mention if server["auto-role"] else "None"
        )
        embed.add_field(
            name="Auto Role Time Limit", 
            value= server["auto-role-timer"] if server["auto-role-timer"] else "Permanent"
        )       
        embed.add_field(
            name="Starboard", 
            value = self.bot.get_channel(server["starboard-channel"]).mention if server["starboard-channel"] else "Disabled"
        )
        embed.add_field(
            name="Starboard Limit", 
            value=server["starboard-limit"]
        )

        embed.set_footer(text="Generated by Necrobot", icon_url=self.bot.user.avatar_url_as(format="png", size=128))

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

        {usage}
        
        __Example__
        `{pre}welcome Hello {member} :wave:` - sets the welcome message to be 'Hello Necrobot#1231 :wave:'.
        `{pre}welcome hey there {mention}, welcome to {server}` - set the welcome message to 'hey there @NecroBot, welcome
        to NecroBot Support Server'
        """
        if message == "":
            await ctx.send(":white_check_mark: | Welcome message reset and disabled")
        else:
            try:
                test = message.format(
                    member=ctx.author, 
                    server=ctx.guild.name,
                    mention=ctx.author.mention,
                    name=ctx.author.name,
                    id=ctx.author.id
                )
                await ctx.send(f":white_check_mark: | Your server's welcome message will be: \n{test}")
            except KeyError as e:
                raise BotError(f"{e.args[0]} is not a valid argument. Check the help guide to see what you can use the command with.")

        await self.bot.db.update_welcome_message(ctx.guild.id, message)
        
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

        {usage}
        
        __Example__
        `{pre}goodbye Hello {member} :wave:` - sets the welcome message to be 'Hello Necrobot#1231 :wave:'.
        `{pre}goddbye hey there {mention}, we'll miss you on {server}` - set the welcome message to 'hey 
        there @NecroBot, we'll miss you on NecroBot Support Server'
        """
        if message == "":
            await ctx.send(":white_check_mark: | Goodbye message reset and disabled")
        else:
            try:
                test = message.format(
                    member=ctx.author, 
                    server=ctx.guild.name,
                    mention=ctx.author.mention,
                    name=ctx.author.name,
                    id=ctx.author.id
                )
                await ctx.send(f":white_check_mark: | Your server's goodbye message will be: \n{test}")
            except KeyError as e:
                raise BotError(f"{e.args[0]} is not a valid argument, you can use either `member` and its reserved keyword or `server`")

        await self.bot.db.update_goodbye_message(ctx.guild.id, message)

    async def channel_set(self, ctx, channel):
        if not channel:
            await self.bot.db.update_greeting_channel(ctx.guild.id)
            await ctx.send(":white_check_mark: | Welcome/Goodbye messages **disabled**")
        else:
            check_channel(channel)
            await self.bot.db.update_greeting_channel(ctx.guild.id, channel.id)
            await ctx.send(f":white_check_mark: | Users will get their welcome/goodbye message in {channel.mention} from now on.")

    @welcome.command(name="channel")
    @has_perms(4)
    async def welcome_channel(self, ctx, channel : discord.TextChannel = 0):
        """Sets the welcome channel to [channel], the [channel] argument should be a channel mention/name/id. The welcome 
        message for users will be sent there. Can be called with either goodbye or welcome, regardless both will use
        the same channel, calling the command with both parent commands but different channel will not make
        messages send to two channels.
         
        {usage}
        
        __Example__
        `{pre}welcome channel #channel` - set the welcome messages to be sent to 'channel'
        `{pre}welcome channel` - disables welcome messages"""

        await self.channel_set(ctx, channel)

    @goodbye.command(name="channel")
    @has_perms(4)
    async def goodbye_channel(self, ctx, channel : discord.TextChannel = 0):
        """Sets the welcome channel to [channel], the [channel] argument should be a channel mention. The welcome 
        message for users will be sent there. Can be called with either goodbye or welcome, regardless both will use
        the same channel, calling the command with both parent commands but different channel will not make
        messages send to two channels.
         
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
            raise BotError(f"Prefix can't be more than 15 characters. {len(prefix)}/15")

        await self.bot.db.update_prefix(ctx.guild.id, prefix)

        if prefix == "":
            await ctx.send(":white_check_mark: | Custom prefix reset")
        else:
            await ctx.send(f":white_check_mark: | Server prefix is now **{prefix}**")

    @commands.command(name="auto-role")
    @has_perms(4)
    async def auto_role(self, ctx, role : discord.Role = 0, time : TimeConverter = 0):
        """Sets the auto-role for this server to the given role. Auto-role will assign the role to the member when they join.
        The following times can be used: days (d), hours (h), minutes (m), seconds (s).

        {usage}

        __Example__
        `{pre}auto-role Newcomer 10m` - gives the role "Newcomer" to users to arrive on the server for 10 minutes
        `{pre}auto-role Newcomer 2d10m` - same but the roles stays for 2 days and 10 minutes
        `{pre}auto-role Newcomer 4h45m56s` - same but the role stays for 4 hours, 45 minutes and 56 seconds
        `{pre}auto-role Newcomer` - gives the role "Newcomer" with no timer to users who join the server.
        `{pre}auto-role` - resets and disables the autorole system. """
        
        self.bot.db.update_auto_role(ctx.guild.id, role.id, time)

        if not role:
            await ctx.send(":white_check_mark: | Auto-Role disabled")
        else:
            time = f"for **{time}** seconds" if time else "permanently"
            await ctx.send(f":white_check_mark: | Joining members will now automatically be assigned the role **{role.name}** {time}")

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
            await self.bot.db.update_broadcast_channel(ctx.guild.id)
            await ctx.send(":white_check_mark: | **Broadcast messages disabled**")

    @broadcast.command(name="channel")
    @has_perms(4)
    async def broadcast_channel(self, ctx, channel : discord.TextChannel = 0):
        """Used to set the channel the message will be broadcasted into.

        {usage}

        __Example__
        `{pre}broadcast channel #general` - sets the broadcast channel to #general"""
        
        if not channel:
            await self.bot.db.update_broadcast_channel(ctx.guild.id)
            await ctx.send(":white_check_mark: | Broadcast messages disabled")        
        else:
            check_channel(channel)
            await self.bot.db.update_broadcast_channel(ctx.guild.id, channel.id)
            await ctx.send(f":white_check_mark: | The broadcast message you set through `n!broadcast message` will be broadcasted in {channel.mention}")        

    @broadcast.command(name="message")
    @has_perms(4)
    async def broadcast_message(self, ctx, *, message = ""):
        """Used to set the message that will be broadcasted

        {usage}

        __Example__
        `{pre}broadcast message test 1 2 3` - sets the broadcast channel to #general"""

        await self.bot.db.update_broadcast_message(ctx.guild.id, message)
        if not message:
            await ctx.send(":white_check_mark: | Broadcast messages disabled")
        else:    
            await ctx.send(f":white_check_mark: | The following message will be broadcasted in the channel you set using `n!broadcast channel` \n {message}")        

    @broadcast.command(name="time")
    @has_perms(4)
    async def broadcast_time(self, ctx, hours : range_check(1, 24)):
        """Used to set the interval at which the message is broadcasted (in hours)

        {usage}

        __Example__
        `{pre}broadcast time 4` - sets the broadcast message to be sent every 4 hour"""
        await self.bot.db.update_broadcast_interval(ctx.guild.id, hours)
        await ctx.send(f":white_check_mark: | The broadcast message you set through `n!broadcast message` will be broadcasted in the channel you set using `n!broadcast channel` every `{hours}` hour(s)")        

    @commands.group(invoke_without_command = True)
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def giveme(self, ctx, *, role : discord.Role = None):
        """Gives the user the role if it is part of this Server's list of self assignable roles. If the user already 
        has the role it will remove it. **Roles names are case sensitive** If no role name is given then it will list
        the self-assignable roles for the server
         
        {usage}
        
        __Example__
        `{pre}giveme Good` - gives or remove the role 'Good' to the user if it is in the list of self assignable roles"""

        if role is None:
            roles = [x.name for x in ctx.guild.roles if x.id in self.bot.guild_data[ctx.guild.id]["self-roles"]]
            
            def _embed_maker(index, entries):
                embed = discord.Embed(
                    title=f"Self Assignable Roles ({index[0]}/{index[1]})", 
                    description='- ' + '\n- '.join(entries), 
                    colour=discord.Colour(0x277b0)
                )
                
                embed.set_footer(text="Generated by Necrobot", icon_url=self.bot.user.avatar_url_as(format="png", size=128))
                return embed
            
            return await react_menu(ctx, roles, 10, _embed_maker)

        if role.id in self.bot.guild_data[ctx.guild.id]["self-roles"]:
            if role not in ctx.author.roles:
                await ctx.author.add_roles(role)
                await ctx.send(f":white_check_mark: | Role {role.name} added.")
            else:
                await ctx.author.remove_roles(role)
                await ctx.send(f":white_check_mark: | Role {role.name} removed.")

        else:
            raise BotError("Role not self assignable")

    @giveme.command(name="add")
    @has_perms(4)
    async def giveme_add(self, ctx, *, role : discord.Role):
        """Adds [role] to the list of the server's self assignable roles.
         
        {usage}
        
        __Example__
        `{pre}giveme add Good` - adds the role 'Good' to the list of self assignable roles"""
        if role.id in self.bot.guild_data[ctx.guild.id]["self-roles"]:
            raise BotError("Role already in list of self assignable roles")

        await self.bot.db.insert_self_roles(ctx.guild.id, role)
        await ctx.send(f":white_check_mark: | Added role **{role.name}** to list of self assignable roles.")

    @giveme.command(name="delete")
    @has_perms(4)
    async def giveme_delete(self, ctx, *, role : discord.Role):
        """Removes [role] from the list of the server's self assignable roles.
        
        {usage}
        
        __Example__
        `{pre}giveme delete Good` - removes the role 'Good' from the list of self assignable roles"""
        if role.id not in self.bot.guild_data[ctx.guild.id]["self-roles"]:
            raise BotError("Role not in self assignable list")

        await self.bot.db.delete_self_roles(ctx.guild.id, role)
        await ctx.send(f":white_check_mark: | Role **{role.name}** removed from self assignable roles")
            

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
            results = await self.bot.db.query_executer(
                """SELECT user_id, COUNT(message_id) FROM necrobot.Starred 
                WHERE guild_id = $1 AND user_id IS NOT null 
                GROUP BY user_id 
                ORDER BY COUNT(message_id) DESC""", 
                ctx.guild.id
            )

            def _embed_maker(index, entries):
                embed = discord.Embed(
                    title=f"Starboard Leaderboard ({index[0]}/{index[1]})", 
                    description="A leaderboard to rank people by the amount of their messages that were starred.", 
                    colour=discord.Colour(0x277b0)
                )
                embed.set_footer(text="Generated by Necrobot", icon_url=self.bot.user.avatar_url_as(format="png", size=128))
                
                for row in entries:
                    member = ctx.guild.get_member(row[0])
                    embed.add_field(
                        name=str(member) if member else "User left server", 
                        value=str(row[1]), 
                        inline=False
                    )  

                return embed

            await react_menu(ctx, results, 15, _embed_maker, page=member-1)
        else:
            result = await self.bot.db.query_executer(
                """SELECT user_id, COUNT(message_id) FROM necrobot.Starred 
                WHERE guild_id = $1 AND user_id = $2 
                GROUP BY user_id 
                ORDER BY COUNT(message_id)""", 
                ctx.guild.id, member.id
            )
            
            await ctx.send(f":star: | User **{member.display_name}** has **{result[0][1]}** posts on the starboard")


    @starboard.command(name="channel")
    @has_perms(4)
    async def starboard_channel(self, ctx, channel : discord.TextChannel = 0):
        """Sets a channel for the starboard messages, required in order for starboard to be enabled. Call the command
        without a channel to disable starboard.

        {usage}

        __Examples__
        `{pre}starboard channel #a-channel` - sets the starboard channel to #a-channel, all starred messages will be sent to
        there
        `{pre}starboard channel` - disables starboard"""
        if not channel:
            await self.bot.db.update_starboard_channel(ctx.guild.id)
            await ctx.send(":white_check_mark: | Starboard messages disabled.")
        else:
            check_channel(channel)
            await self.bot.db.update_starboard_channel(ctx.guild.id, channel.id)
            await ctx.send(f":white_check_mark: | Starboard messages will now be sent to {channel.mention}")

    @starboard.command(name="limit")
    @has_perms(4)
    async def starboard_limit(self, ctx, limit : int):
        """Sets the amount of stars required to the given intenger. Must be more than 0. 

        {usage}

        __Examples__
        `{pre}starboard limit 4` - set the required amount of stars on a message to 4, once a message hits 4 :star: they
        will be posted if there is a starboard channel set."""
        if limit < 1:
            raise BotError("Limit must be at least one")

        await self.bot.db.update_starboard_limit(ctx.guild.id, limit)
        await ctx.send(f":white_check_mark: | Starred messages will now be posted on the starboard once they hit **{limit}** stars")

    async def add_reactions(self, message):
        CUSTOM_EMOJI = r'<:[^\s]+:([0-9]*)>'
        UNICODE_EMOJI = r"[\U0001F1E0-\U0001F1FF\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]+"
        
        custom_emojis = [self.bot.get_emoji(int(emoji)) for emoji in re.findall(CUSTOM_EMOJI, message.content)]
        unicode_emojis = re.findall(UNICODE_EMOJI, message.content)

        emojis = [*custom_emojis, *unicode_emojis]

        for emoji in emojis:
            try:
                await message.add_reaction(emoji)
            except (discord.NotFound, discord.InvalidArgument, discord.HTTPException):
                pass
    
    @commands.command()
    @has_perms(3)
    async def poll(self, ctx, channel : discord.TextChannel, *, message):
        check_channel(channel)
        await self.add_reactions(ctx.message)
        
        msg = await ctx.send("How many options can the users react with? Reply with a number between 1 and 20. Reply with 0 to cancel")
        
        def check(message):
            return message.author.id == ctx.author.id and message.channel.id == ctx.channel.id and message.content.isdigit()

        try:
            reply = await self.bot.wait_for("message", timeout=300, check=check)
        except asyncio.TimeoutError as e:
            e.timer = 300
            raise e
            
        votes = int(reply.content)
        if not votes:
            await message.delete()
            await ctx.message.clear_reactions()
        
        poll = await channel.send(f"{message}\n\n**Maximum votes: {votes}**")
        await self.add_reactions(poll)
        
        self.bot.polls[poll.id] = {'votes': votes, 'voters':[]}
        await self.bot.db.query_executer(
            "INSERT INTO necrobot.Polls VALUES($1, $2, $3, $4)", 
            poll.id, poll.guild.id, poll.jump_url, votes
        )
        
    @commands.command()
    async def results(self, ctx, index = 0):
        """Get the results of a poll

        {usage}
        
        __Examples__
        `{pre}results` - get the results of the polls from this server starting at the first one
        `{pre}results 3` - get the results of the polls from this server stating at the 3rd one.
        """
        results = await self.bot.db.query_executer(
            """
            SELECT p.link, ARRAY_AGG(v.votes)
            FROM necrobot.Polls p, (
                    SELECT message_id, (reaction, COUNT(reaction))::emote_count_hybrid AS votes
                    FROM necrobot.Votes
                    GROUP BY message_id, reaction
                    ORDER BY COUNT(reaction) DESC
                ) v
            WHERE p.guild_id = $1 AND p.message_id = v.message_id
            GROUP BY p.link, p.message_id
            ORDER BY p.message_id""",
            ctx.guild.id    
        )

        def _embed_maker(index, entry):
            def emojify(emoji):
                if re.match(emoji_unicode.RE_PATTERN_TEMPLATE, emoji):
                    return emoji

                return discord.utils.get(ctx.guild.emojis, name=emoji) or emoji

            string = "\n".join([f'{emojify(key)} - {value}' for key, value in entry[1]])
            embed = discord.Embed(
                title=f"Results ({index[0]}/{index[1]})", 
                description=f'[**Link**]({entry[0]})\n\n{string}'
            )
            embed.set_footer(text="Generated by Necrobot", icon_url=self.bot.user.avatar_url_as(format="png", size=128))
            
            return embed

        await react_menu(ctx, results, 1, _embed_maker, page=index)

def setup(bot):
    bot.add_cog(Server(bot))
