#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from rings.botdata.data import Data
import asyncio

userData = Data.userData
serverData = Data.serverData

class Moderation():
    def __init__(self, bot):
        self.bot = bot

    def has_perms(perms_level):
        def predicate(cont):
            return userData[cont.message.author.id]["perms"][cont.message.server.id] >= perms_level
        return commands.check(predicate)

    def allmentions(self, cont, msg):
        myList = []
        mentions = msg.split(" ")
        for x in mentions:
            ID = re.sub('[<>!#@]', '', x)
            if not self.bot.get_channel(ID) is None:
                channel = self.bot.get_channel(ID)
                myList.append(channel)
            elif not cont.message.server.get_member(ID) is None:
                member = cont.message.server.get_member(ID)
                myList.append(member)
        return myList

    @commands.command(pass_context = True, aliases=["rename","name"])
    @has_perms(1)
    async def nick(self, cont, user : discord.Member, *, nickname="Necro"):
        """ Nicknames a user, use to clean up offensive or vulgar names or just to prank your friends. Will return an error message if the user cannot be renamed due to permission issues. (Permission level required: 1+ (Helper))"""
        try:
            await self.bot.change_nickname(user, nickname)
            await self.bot.say(":white_check_mark: | User **{0.display_name}** renamed to **{1}**".format(user, nickname))
        except discord.errors.Forbidden:
            await self.bot.say(":negative_squared_cross_mark: | You cannot change the nickname of that user.")

    @commands.command(pass_context = True)
    @has_perms(2)
    async def mute(self, cont, user : discord.Member, *seconds : int):
        """Blocks the user from writing in channels by giving it the server's mute role. Make sure an admin has set a mute role using `n!settings mute`. The user can either be muted for the given amount of seconds or indefinitely if no amount is given. (Permission level required: 2+ (Moderator))"""
        role = discord.utils.get(cont.message.server.roles, name=serverData[cont.message.server.id]["mute"])
        if role not in user.roles:
            await self.bot.add_roles(user, role)
            await self.bot.send_message(self.bot.get_channel(cont.message.channel.id),":white_check_mark: | User: **{0}** has been muted".format(user.display_name))
        else:
            await self.bot.send_message(self.bot.get_channel(cont.message.channel.id),":negative_squared_cross_mark: | User: **{0}** is already muted".format(user.display_name))
            return

        if seconds:
            await asyncio.sleep(seconds[0])
            if role in user.roles:
                await self.bot.remove_roles(user, role)
                await self.bot.send_message(self.bot.get_channel(cont.message.channel.id),":white_check_mark: | User: **{0}** has been automatically unmuted".format(user.display_name))

    @commands.command(pass_context = True)
    @has_perms(2)
    async def unmute(self, cont, user : discord.Member):
        """Unmutes a user by removing the mute role, allowing them once again to write in text channels. (Permission level required: 2+ (Moderator))"""
        role = discord.utils.get(cont.message.server.roles, name=serverData[cont.message.server.id]["mute"])
        if role in user.roles:
            await self.bot.remove_roles(user, role)
            await self.bot.send_message(self.bot.get_channel(cont.message.channel.id),":white_check_mark: | User: **{0}** has been unmuted".format(user.display_name))
        else:
            await self.bot.send_message(self.bot.get_channel(cont.message.channel.id),":negative_squared_cross_mark: | User: **{0}** is not muted".format(user.display_name))

    @commands.group(pass_context=True, invoke_without_command = True)
    @has_perms(1)
    async def warn(self, cont):
        """Useless if no sub-command is provided."""
        await self.bot.say(":negative_squared_cross_mark: | Please enter a valid subcommand, check `n!help warn` for the list of subcommands")

    @warn.command(pass_context=True, name="add")
    @has_perms(1)
    async def warn_add(self, cont, user : discord.Member, *, message):
        """Adds the given message as a warning to the user's NecroBot profile (Permission level required: 1+ (Server Helper))"""
        await self.bot.say(":white_check_mark: | Warning: **\"" + message + "\"** added to warning list of user " + user.display_name)
        userData[user.id]["warnings"].append(message + " by " + str(cont.message.author) + " on server " + cont.message.server.name)
        await self.bot.send_message(user, "You have been warned on " + cont.message.server.name + ", the warning is: \n" + message)

    @warn.command(pass_context=True, name="del")
    @has_perms(3)
    async def warn_del(self, cont, user : discord.Member, position : int):
        """Removes the warning from the user's NecroBot system based on the given warning position. (Permission level required: 3+ (Server Semi-Admin)) """
        await self.bot.say(":white_check_mark: | Warning: **\"" + userData[user.id]["warnings"][position - 1] + "\"** removed from warning list of user " + user.display_name)
        userData[user.id]["warnings"].pop(position - 1)

    @commands.command(pass_context = True)
    @has_perms(3)
    async def lock(self, cont, user : discord.Member):
        """Moves a user back to the voice channel they were locked in every time they try to move to another one (Permission level required: 3+ (Semi-Admin))"""
        if user.id in lockedList:
            lockedList.remove(user.id)
            await self.bot.say(":white_check_mark: | User no longer locked in channel **"+ self.bot.get_channel(userData[user.id]['locked']).name + "**")
            userData[user.id]["locked"] = ""
        else:
            v_channel = user.voice_channel
            userData[user.id]["locked"] = v_channel.id
            lockedList.append(user.id)
            await self.bot.say(":white_check_mark: | User locked in channel **"+ v_channel.name + "**")

    @commands.command(pass_context = True)
    @commands.cooldown(1, 10, BucketType.channel)
    @has_perms(4)
    async def purge(self, cont, number : int):
        """Removes number of messages from the channel it is called in. That's all it does at the moment but later checks will also be added to allow for more flexible/specific purging (Permission level required: 4+ (Server Admin))"""
        await self.bot.purge_from(cont.message.channel, limit=number+1)
        message = await self.bot.say(":wastebasket: | **" + str(number) + "** messages purged.")
        await asyncio.sleep(5)
        await self.bot.delete_message(message)

    @commands.command(pass_context = True)
    async def speak(self, cont, channel, *, message):
        """Send the given message to the channel mentioned either by id or by mention. Requires the correct permission level on both servers. (Permission level required: 4+ (Server Admin))"""
        ID = allmentions(cont, channel)[0].id
        if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4 and userData[cont.message.author.id]["perms"][self.bot.get_channel(ID).server.id] >= 4:
            await self.bot.send_message(bot.get_channel(ID), ":loudspeaker: | " + message)
        elif userData[cont.message.author.id]["perms"][self.bot.get_channel(ID).server.id] < 4:
            await self.bot.say(":negative_squared_cross_mark: | You do not have the required NecroBot permissions on the server you're trying to send the message to.")
        else:
            await self.bot.say(":negative_squared_cross_mark: | You do not have the required NecroBot permissions to use this command.")


def setup(bot):
    bot.add_cog(Moderation(bot))
