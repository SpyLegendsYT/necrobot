#!/usr/bin/python3.6
import discord
from discord.ext import commands

from rings.utils.utils import has_perms, TimeConverter

import asyncio

class Moderation():
    """All of the tools moderators can use from the most basic such as `nick` to the most complex like `purge`. 
    All you need to keep your server clean and tidy"""
    def __init__(self, bot):
        self.bot = bot
        self.obligatory = ("Moderation", "Server", "Support", "Admin", "Events", "disable", "enable")

    @commands.command()
    @has_perms(1)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def rename(self, ctx, user : discord.Member, *, nickname=None):
        """ Nicknames a user, use to clean up offensive or vulgar names or just to prank your friends. Will return 
        an error message if the user cannot be renamed due to permission issues. (Permission level required: 1+ (Helper))
        
        {usage}
        
        __Example__
        `{pre}nick @NecroBot Lord of All Bots` - renames NecroBot to 'Lord of All Bots'
        `{pre}nick @NecroBot` - will reset NecroBot's nickname"""
        if self.bot.user_data[ctx.message.author.id]["perms"][ctx.message.guild.id] > self.bot.user_data[user.id]["perms"][ctx.message.guild.id]:
            if not nickname:
                msg = f":white_check_mark: | User **{user.display_name}**'s nickname reset"
            else:
                msg = f":white_check_mark: | User **{user.display_name}** renamed to **{nickname}**"

            await user.edit(nick=nickname)
            await ctx.send(msg)
        else:
            await ctx.send(":negative_squared_cross_mark: | You do not have the required NecroBot permissions to rename this user.")

    @commands.group(invoke_without_command = True)
    @has_perms(2)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, user : discord.Member, *, time : TimeConverter = None):
        """Blocks the user from writing in channels by giving it the server's mute role. Make sure an admin has set a 
        mute role using `{pre}settings mute`. The user can either be muted for the given amount of seconds or indefinitely 
        if no amount is given. The following times can be used: days (d), hours (h), minutes (m), seconds (s).
        (Permission level required: 2+ (Moderator))
        
        {usage}

        __Example__
        `{pre}mute @NecroBot` - mute NecroBot until a user with the proper permission level does `{pre}unmute @NecroBot`
        `{pre}mute @NecroBot 30s` - mutes NecroBot for 30 seconds or until a user with the proper permission level does
        `{pre}mute @NecroBot 2m` - mutes NecroBot for 2 minutes
        `{pre}mute @NecroBot 4d2h45m` - mutes NecroBot for 4 days, 2 hours and 45 minutes"""
        if self.bot.server_data[ctx.message.guild.id]["mute"] == "":
            await ctx.send(":negative_squared_cross_mark: | Please set up the mute role with `n!mute role [rolename]` first.")
            return

        role = discord.utils.get(ctx.message.guild.roles, id=self.bot.server_data[ctx.message.guild.id]["mute"])
        if role not in user.roles:
            await user.add_roles(role)
            await ctx.send(f":white_check_mark: | User: **{user.display_name}** has been muted")
        else:
            await ctx.send(f":negative_squared_cross_mark: | User: **{user.display_name}** is already muted", delete_after=5)
            return

        if time:
            await asyncio.sleep(time)
            if role in user.roles:
                await user.remove_roles(role)
                await ctx.send(f":white_check_mark: | User: **{user.display_name}** has been automatically unmuted")

    @mute.command(name="role")
    @has_perms(4)
    async def mute_role(self, ctx, *, role : discord.Role = None):
        """Sets the mute role for this server to [role], this is used for the `mute` command, it is the role assigned by 
        the command to the user. Make sure to spell the role correctly, the role name is case sensitive. It is up to the server 
        authorities to set up the proper permissions for the chosen mute role. Once the role is set up it can be renamed and 
        edited as seen needed, NecroBot keeps the id saved. Unexpect behavior can happen if multiple roles have the same name when
        setting the role.
        (Permission level required: 5+ (Server Owner))
         
        {usage}
        
        __Example__
        `{pre}mute role Token Mute Role` - set the mute role to be the role named 'Token Mute Role'
        `{pre}mute role` - resets the mute role and disables the `mute` command."""
        if not role:
            self.bot.server_data[ctx.message.guild.id]["mute"] = ""
            await self.bot.query_executer("UPDATE necrobot.Guilds SET mute = 0 WHERE guild_id = $1;", ctx.guild.id)
            await ctx.send(":white_check_mark: | Reset mute role")
            return

        await ctx.send(f":white_check_mark: | Okay, the mute role for your server will be {role.mention}")
        self.bot.server_data[ctx.message.guild.id]["mute"] = role.id
        await self.bot.query_executer("UPDATE necrobot.Guilds SET mute = $1 WHERE guild_id = $2;", role.id, ctx.guild.id)


    @commands.command()
    @has_perms(2)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx, user : discord.Member):
        """Unmutes a user by removing the mute role, allowing them once again to write in text channels. 
        (Permission level required: 2+ (Moderator))
        
        {usage}

        __Example__
        `{pre}unmute @NecroBot` - unmutes NecroBot if he is muted"""
        if self.bot.server_data[ctx.message.guild.id]["mute"] == "":
            await ctx.send(":negative_squared_cross_mark: | Please set up the mute role with `n!mute role [rolename]` first.")
            return
            
        role = discord.utils.get(ctx.message.guild.roles, id=self.bot.server_data[ctx.message.guild.id]["mute"])
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.send(f":white_check_mark: | User: **{user.display_name}** has been unmuted")
        else:
            await ctx.send(f":negative_squared_cross_mark: | User: **{user.display_name}** is not muted", delete_after=5)

    @commands.group(invoke_without_command = True)
    @has_perms(1)
    async def warn(self, ctx, user : discord.Member, *, message : str):
        """Adds the given message as a warning to the user's NecroBot profile (Permission level required: 1+ (Server Helper))
        
        {usage}
        
        __Example__
        `{pre}warn @NecroBot For being the best bot` - will add the warning 'For being the best bot' to 
        Necrobot's warning list and pm the warning message to him"""
        await ctx.send(f":white_check_mark: | Warning: **\"{message}\"** added to warning list of user {user.display_name}")
        self.bot.user_data[user.id]["warnings"][ctx.guild.id].append(message)
        await self.bot.query_executer("INSERT INTO necrobot.Warnings (user_id, issuer_id, guild_id, warning_content, date_issued) VALUES ($1, $2, $3, $4, $5);", user.id, ctx.author.id, ctx.guild.id, message, str(ctx.message.created_at))
        try:
            await user.send(f"You have been warned on {ctx.message.guild.name}, the warning is: \n {message}")
        except discord.Forbidden:
            pass

    @warn.command(name="delete")
    @has_perms(3)
    async def warn_delete(self, ctx, user : discord.Member, position : int):
        """Removes the warning from the user's NecroBot system based on the given warning position. 
        (Permission level required: 3+ (Server Semi-Admin)) 
        
        {usage}
        
        __Example__
        `{pre}warn delete @NecroBot 1` - delete the warning in first position of NecroBot's warning list"""
        try:
            message = self.bot.user_data[user.id]["warnings"][ctx.guild.id].pop(position - 1)
        except IndexError:
            await ctx.send(":negative_squared_cross_mark: | Not a valid warning position")
            return
            
        await ctx.send(f":white_check_mark: | Warning: **\"{message}\"** removed from warning list of user {user.display_name}")
        await self.bot.query_executer("DELETE FROM necrobot.Warnings WHERE user_id = $1 AND guild_id = $2 AND warning_content = $3;", user.id, ctx.guild.id, message)

    @commands.command()
    @has_perms(4)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, number : int = 1, check="", extra=""):
        """Removes number of messages from the channel it is called in. That's all it does at the moment 
        but later checks will also be added to allow for more flexible/specific purging (Permission level required: 4+ 
        (Server Admin))
        
        {usage}
        
        __Example__
        `{pre}purge 50` - purges the last 50 messages
        `{pre}purge 15 link` - purges all messages containing links from the previous 15 messages
        `{pre}purge 20 mention @Necro` - purges all messages sent by @Necro from the previous 20 messages
        `{pre}purge 35 bot` - purges all messages sent by the bot from the previous 35 messages"""
        channel = self.bot.server_data[ctx.message.guild.id]["automod"]
        self.bot.server_data[ctx.message.guild.id]["automod"] = ""
        number += 1

        if check == "link":
            deleted = await ctx.message.channel.purge(limit=number, check=lambda m: "http" in m.content)
        elif check == "mention":
            deleted = await ctx.message.channel.purge(limit=number, check=lambda m: m.author.mention == extra)
        elif check == "image":
            deleted = await ctx.message.channel.purge(limit=number, check=lambda m: len(m.attachments) > 0)
        elif check == "bot":
            deleted = await ctx.message.channel.purge(limit=number, check=lambda m: m.author == self.bot.user)
        else:
            deleted = await ctx.message.channel.purge(limit=number)

        await ctx.send(f":wastebasket: | **{len(deleted)-1}** messages purged.", delete_after=5)

        self.bot.server_data[ctx.message.guild.id]["automod"] = channel

    @commands.command()
    @has_perms(3)
    async def speak(self, ctx, channel : discord.TextChannel, *, message : str):
        """Send the given message to the channel mentioned by mention or name. Cannot send to other servers. 
        (Permission level required: 3+ (Semi-Admin))
        
        {usage}
        
        __Example__
        `{pre}speak #general Hello` - sends hello to the mentionned #general channel"""
        await channel.send(f":loudspeaker: | {message}")
        
    @commands.command()
    @has_perms(4)
    async def disable(self, ctx, command=None):
        """Disables a command or cog. Once a command or cog is disabled only admins can use it with the special n@ or N@
        prefix. To re-enable a command or cog call the `enable` comannd on it. Disabling cogs works as a sort of "select all" 
        button which means that all commands will be disabled and individual commands can then be enabled separatly for
        fine tuning.

        {usage}

        __Examples__
        `{pre}disable` - print the list of disabled cogs and commands
        `{pre}disable cat` - disables the cat command, after that the cat command only be used by admins using `n@cat`
        `{pre}disable Animals` - disables every command in the the Animals cog"""
        if not command:
            await ctx.send(f"**Cogs and Commands disabled on the server**: {self.bot.server_data[ctx.message.guild.id]['disabled']}")
            return

        # if command in self.obligatory:
        #     await ctx.send(":negative_squared_cross_mark: | You cannot disable this command/cog", delete_after=5)
        #     return

        disabled = self.bot.server_data[ctx.message.guild.id]["disabled"]
        if command not in self.bot.cogs:
            command_obj = self.bot.get_command(command)

            if not command_obj:
                await ctx.send(":negative_squared_cross_mark: | No such command/cog.", delete_after=5)
                return

            if command in disabled:
                await ctx.send(":negative_squared_cross_mark: | This command is already disabled.")
            else:
                disabled.append(command)
                await self.bot.query_executer("INSERT INTO necrobot.Disabled VALUES ($1, $2)", ctx.guild.id, command)
                await ctx.send(f":white_check_mark: | Command **{command}** is now disabled")

        else:
            all_commands = [x.name for x in self.bot.commands if x.cog_name == command and x.name not in disabled]
            for _command in all_commands:
                disabled.append(_command)
                await self.bot.query_executer("INSERT INTO necrobot.Disabled VALUES ($1, $2)", ctx.guild.id, _command)
            await ctx.send(f":white_check_mark: | All commands in cog **{command}** are now disabled") 

    @commands.command()
    @has_perms(4)
    async def enable(self, ctx, command=None):
        """Enable a command or cog. Once a command or cog is enabled everybody can use it given no other restrictions such 
        as blacklisted or ignored. To disable a command or cog call the `disable` comannd on it. Enabling cogs works as a 
        sort of "select all" button which means that all commands will be enabled and individual commands can then be disabled
        separatly for fine tuning.

        {usage}

        __Examples__
        `{pre}enable` - print the list of disabled cogs and commands
        `{pre}enabled cat` - enable the cat command, after that everybody can use it again freely.
        `{pre}enable Animals` - enables every command in the the Animals cog"""
        if not command:
            await ctx.send(f"**Cogs and Commands disabled on the server**: {self.bot.server_data[ctx.message.guild.id]['disabled']}")
            return

        disabled = self.bot.server_data[ctx.message.guild.id]["disabled"]
        if command not in self.bot.cogs:
            command_obj = self.bot.get_command(command)

            if not command_obj:
                await ctx.send(":negative_squared_cross_mark: | No such command/cog.", delete_after=5)
                return

            if command in disabled:
                disabled.remove(command)
                await self.bot.query_executer("DELETE FROM necrobot.Disabled WHERE guild_id = $1 AND command = $2", ctx.guild.id, command)
                await ctx.send(f":white_check_mark: | Command **{command}** is now enabled")
            else:
                await ctx.send(":negative_squared_cross_mark: | This command is already enabled.")
        else:
            all_commands = [x.name for x in self.bot.commands if x.cog_name == command and x.name in disabled]
            for _command in all_commands:
                disabled.remove(_command)
                await self.bot.query_executer("DELETE FROM necrobot.Disabled WHERE guild_d = $1 AND command = $2", ctx.guild.id, _command)
            await ctx.send(f":white_check_mark: | All commands in cog **{command}** are now enabled")


    @commands.command()
    @has_perms(3)
    async def star(self, ctx, message_id : int = None):
        """Allows to manually star a message that either has failed to be sent to starboard or doesn't have the amount of stars
        required. If a message ID is given then the command **must** be called in the same channel as the message.

        {usage}

        __EXamples__
        `{pre}star 427227137511129098` - gets the message by id and stars it.
        `{pre}star` - initiates the interactive message picking sessions that allows you to react to a message to star it"""
        if self.bot.server_data[ctx.guild.id]["starboard-channel"] == "":
            await ctx.send(":negative_squared_cross_mark: | Please set a starboard first")
            return

        if message_id:
            try:
                message = await ctx.channel.get_message(message_id)
            except commands.CommandInvokeError:
                await ctx.send(":negative_squared_cross_mark: | Message not found, make sure you are in the channel with the message.")
                return

            await self.bot._star_message(message)
        else:
            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) == "\N{WHITE HEAVY CHECK MARK}"

            msg = await ctx.send("React to the message you wish to star with :white_check_mark:")
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=300)
            except asyncio.TimeoutError as e:
                await msg.delete()
                e.timer = 300
                return self.bot.dispatch("command_error", ctx, e)

            await self.bot._star_message(reaction.message)
            await msg.delete()



def setup(bot):
    bot.add_cog(Moderation(bot))
