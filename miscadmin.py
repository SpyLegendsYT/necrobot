#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from rings.botdata.data import Data

userData = Data.userData
serverData = Data.serverData

class MiscAdmin():
    def __init__(self, bot):
        self.bot = bot

    def has_perms(perms_level):
        def predicate(cont):
            return userData[cont.message.author.id]["perms"][cont.message.server.id] >= perms_level
        return commands.check(predicate)

    def is_necro():
        def predicate(cont):
            return cont.message.author.id == "241942232867799040"
        return commands.check(predicate)

    @commands.command(pass_context = True, hidden=True)
    @has_perms(6)
    async def add(cont, user : discord.Member, *, equation : str):
        """Does the given pythonic equations on the given user's NecroBot balance. (Permission level required: 6+ (NecroBot Admin))"""
        s = str(userData[user.id]["money"]) + equation
        try:
            operation = simple_eval(s)
            userData[user]["money"] = abs(int(operation))
            await bot.say(":atm: | **"+ user.name + "'s** balance is now **"+str(userData[user.id]["money"])+ "** :euro:")
        except (NameError,SyntaxError):
            await bot.say(":negative_squared_cross_mark: | Operation no recognized.")

    @bot.command(pass_context = True)
    async def speak(cont, channel, *, message):
        """Send the given message to the channel mentioned either by id or by mention. Requires the correct permission level on both servers. (Permission level required: 4+ (Server Admin))"""
        channel = allmentions(cont, channel)[0]
        if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4 and userData[cont.message.author.id]["perms"][bot.get_channel(ID).server.id] >= 4:
            await bot.send_message(bot.get_channel(ID), ":loudspeaker: | " + message)
        elif userData[cont.message.author.id]["perms"][bot.get_channel(ID).server.id] < 4:
            await bot.say(":negative_squared_cross_mark: | You do not have the required NecroBot permissions on the server you're trying to send the message to.")
        else:
            await bot.say(":negative_squared_cross_mark: | You do not have the required NecroBot permissions to use this command.")

    @bot.command(pass_context = True, hidden=True)
    @has_perms(6)
    async def pm(cont, ID, *, message):
        """Sends the given message to the user of the given id. It will then wait 5 minutes for an answer and print it to the channel it was called it. (Permission level required: 6+ (NecroBot Admin))"""
        for x in bot.get_all_members():
            if x.id == ID:
                user = x

        send = await bot.send_message(user, message + "\n*You have 5 minutes to reply to the message*")
        await bot.say("Message sent")
        msg = await bot.wait_for_message(author=user, channel=send.channel, timeout=300)
        await bot.send_message(cont.message.channel, ":speech_left: | **User: {0.author}** said :**{0.content}**".format(msg))

    @bot.command(pass_context = True)
    @commands.cooldown(1, 10, BucketType.channel)
    @has_perms(4)
    async def purge(cont, number : int):
        """Removes number of messages from the channel it is called in. That's all it does at the moment but later checks will also be added to allow for more flexible/specific purging (Permission level required: 4+ (Server Admin))"""
        await bot.purge_from(cont.message.channel, limit=number+1)
        message = await bot.say(":wastebasket: | **" + str(number) + "** messages purged.")
        await asyncio.sleep(5)
        await bot.delete_message(message)

    @bot.command(pass_context = True)
    @has_perms(5)
    async def setroles(cont):
        """Sets the NecroBot roles for this server and assigns them to user based on their NecroBot permission level. Permission level required: 5+ (Server Owner))"""
        for x in roleList:
            if discord.utils.get(cont.message.server.roles, name=x[0]) is None:
                new_role = await bot.create_role(cont.message.server, name=x[0], colour=x[1], mentionable=True)
                await bot.say("Role " + x[0] + " created")
            else:
                await bot.say("A role with the name " + x[0] + " already exists.")
        await asyncio.sleep(5)
        await bot.purge_from(bot.get_channel(cont.message.channel.id), limit=8)
        await bot.say("**Roles created**")

        for x in cont.message.server.members:
            role = userData[x.id]["perms"][cont.message.server.id]-1
            await bot.add_roles(x, discord.utils.get(cont.message.server.roles, name=roleList[role][0]))
        await bot.say("**Roles assigned**")


def setup(bot):
    bot.add_cog(MiscAdmin(bot))