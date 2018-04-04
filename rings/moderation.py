#!/usr/bin/python3.6
import discord
from discord.ext import commands
import asyncio
import re
from rings.utils.utils import has_perms

lockedList = list()


class Moderation():
    """All of the tools moderators can use from the most basic such as `nick` to the most complex like `purge`. 
    All you need to keep your server clean and tidy"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["rename","name"])
    @has_perms(1)
    async def nick(self, ctx, user : discord.Member, *, nickname=None):
        """ Nicknames a user, use to clean up offensive or vulgar names or just to prank your friends. Will return 
        an error message if the user cannot be renamed due to permission issues. (Permission level required: 1+ (Helper))
        
        {usage}
        
        __Example__
        `{pre}nick @NecroBot Lord of All Bots` - renames NecroBot to 'Lord of All Bots'
        `{pre}nick @NecroBot` - will reset NecroBot's nickname"""
        if self.bot.user_data[ctx.message.author.id]["perms"][ctx.message.guild.id] > self.bot.user_data[user.id]["perms"][ctx.message.guild.id]:
            if nickname is None:
                msg = ":white_check_mark: | User **{0.display_name}**'s nickname reset".format(user)
            else:
                msg = ":white_check_mark: | User **{0.display_name}** renamed to **{1}**".format(user, nickname)

            try:
                await user.edit(nick=nickname)
                await ctx.message.channel.send(msg)
            except discord.errors.Forbidden:
                await ctx.message.channel.send(":negative_squared_cross_mark: | You cannot change the nickname of that user.")
        else:
            await ctx.message.channel.send(":negative_squared_cross_mark: | You do not have the required NecroBot permissions to rename this user.")

    @commands.command()
    @has_perms(2)
    async def mute(self, ctx, user : discord.Member, *,seconds : int=False):
        """Blocks the user from writing in channels by giving it the server's mute role. Make sure an admin has set a 
        mute role using `{pre}settings mute`. The user can either be muted for the given amount of seconds or indefinitely 
        if no amount is given. (Permission level required: 2+ (Moderator))
        
        {usage}

        __Example__
        `{pre}mute @NecroBot` - mute NecroBot until a user with the proper permission level does `{pre}unmute @NecroBot`
        `{pre}mute @NecroBot 30` - mutes NecroBot for 30 seconds or until a user with the proper permission level does 
        `{pre}unmute @NecroBot`"""
        if self.bot.server_data[ctx.message.guild.id]["mute"] == "":
            await ctx.message.channel.send(":negative_squared_cross_mark: | Please set up the mute role with `n!settings mute [rolename]` first.")
            return

        role = discord.utils.get(ctx.message.guild.roles, id=self.bot.server_data[ctx.message.guild.id]["mute"])
        if role not in user.roles:
            await user.add_roles(role)
            await ctx.message.channel.send(":white_check_mark: | User: **{0}** has been muted".format(user.display_name))
        else:
            await ctx.message.channel.send(":negative_squared_cross_mark: | User: **{0}** is already muted".format(user.display_name))
            return

        if seconds:
            await asyncio.sleep(seconds)
            if role in user.roles:
                await user.remove_roles(role)
                await ctx.message.channel.send(":white_check_mark: | User: **{0}** has been automatically unmuted".format(user.display_name))

    @commands.command()
    @has_perms(2)
    async def unmute(self, ctx, user : discord.Member):
        """Unmutes a user by removing the mute role, allowing them once again to write in text channels. 
        (Permission level required: 2+ (Moderator))
        
        {usage}

        __Example__
        `{pre}unmute @NecroBot` - unmutes NecroBot if he is muted"""
        if self.bot.server_data[ctx.message.guild.id]["mute"] == "":
            await ctx.message.channel.send(":negative_squared_cross_mark: | Please set up the mute role with `n!settings mute [rolename]` first.")
            return
            
        role = discord.utils.get(ctx.message.guild.roles, id=self.bot.server_data[ctx.message.guild.id]["mute"])
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.message.channel.send(":white_check_mark: | User: **{0}** has been unmuted".format(user.display_name))
        else:
            await ctx.message.channel.send(":negative_squared_cross_mark: | User: **{0}** is not muted".format(user.display_name))

    @commands.group(invoke_without_command = True)
    @has_perms(1)
    async def warn(self, ctx, user : discord.Member, *, message : str):
        """Adds the given message as a warning to the user's NecroBot profile (Permission level required: 1+ (Server Helper))
        
        {usage}
        
        __Example__
        `{pre}warn @NecroBot For being the best bot` - will add the warning 'For being the best bot' to 
        Necrobot's warning list and pm the warning message to him"""
        await ctx.message.channel.send(":white_check_mark: | Warning: **\"" + message + "\"** added to warning list of user " + user.display_name)
        self.bot.user_data[user.id]["warnings"].append(message + " by " + str(ctx.message.author) + " on server " + ctx.message.guild.name)
        await user.send("You have been warned on " + ctx.message.guild.name + ", the warning is: \n" + message)

    @warn.command(name="del")
    @has_perms(3)
    async def warn_del(self, ctx, user : discord.Member, position : int):
        """Removes the warning from the user's NecroBot system based on the given warning position. 
        (Permission level required: 3+ (Server Semi-Admin)) 
        
        {usage}
        
        __Example__
        `{pre}warn del @NecroBot 1` - delete the warning in first position of NecroBot's warning list"""
        await ctx.message.channel.send(":white_check_mark: | Warning: **\"" + self.bot.user_data[user.id]["warnings"][position - 1] + "\"** removed from warning list of user " + user.display_name)
        self.bot.user_data[user.id]["warnings"].pop(position - 1)

    @commands.command()
    @has_perms(4)
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
        ctx.message.delete()
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

        await ctx.message.channel.send(":wastebasket: | **{}** messages purged.".format(len(deleted)-1), delete_after=5)

        self.bot.server_data[ctx.message.guild.id]["automod"] = channel

    @commands.command()
    @has_perms(3)
    async def speak(self, ctx, channel, *, message : str):
        """Send the given message to the channel mentioned either by id or by mention. 
        Requires the correct permission level on both servers. (Permission level required: 3+ (Semi-Admin))
        
        {usage}
        
        __Example__
        `{pre}speak #general Hello` - sends hello to the mentionned #general channel
        `{pre}speak 235426357468543 Hello` - sends hello to the channel with the given ID (if any)"""
        try: 
            channel = self.bot.all_mentions(ctx, [channel])[0]
        except IndexError:
            await ctx.message.channel.send("No channel with that name")
            return
        
        if self.bot.user_data[ctx.message.author.id]["perms"][ctx.message.guild.id] >= 3 and self.bot.user_data[ctx.message.author.id]["perms"][channel.guild.id] >= 3:
            await channel.send(":loudspeaker: | " + message)
        elif self.bot.user_data[ctx.message.author.id]["perms"][channel.guild.id] < 4:
            await ctx.message.channel.send(":negative_squared_cross_mark: | You do not have the required NecroBot permissions on the server you're trying to send the message to.")
        else:
            await ctx.message.channel.send(":negative_squared_cross_mark: | You do not have the required NecroBot permissions to use this command.")

    @commands.command()
    @has_perms(4)
    async def disable(self, ctx, command):
        """Disables a command. Once a command is disabled only admins can use it with the special n@ prefix. To re-enable a command
        call disable on it again.

        {usage}

        __Examples__
        `{pre}disable cat` - disables the cat command, after that the cat command only be used by admins using `n@cat`
        `{pre}disable cat` - reenables the cat command."""
        disabled = self.bot.server_data[ctx.message.guild.id]["disabled"]
        if self.bot.get_command(command) is None:
            await ctx.send(":negative_squared_cross_mark: | No such command.", delete_after=5)
            return

        if command == "disable":
            await ctx.send(":negative_squared_cross_mark: | ... Really?", delete_after=5)
            return

        if command not in disabled:
            disabled.append(command)
            await self.bot.query_executer("INSERT INTO necrobot.Disabled VALUES ($1, $2)", ctx.guild.id, command)
            await ctx.send(":white_check_mark: | Command **{}** will now be ignored".format(command))
        else:
            disabled.remove(command)
            await self.bot.query_executer("DELETE FROM necrobot.Disabled WHERE guild_d = $1 AND command = $2)", ctx.guild.id, command)
            await ctx.send(":white_check_mark: | Command **{}** will no longer be ignored".format(command))

def setup(bot):
    bot.add_cog(Moderation(bot))
