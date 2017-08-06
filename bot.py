#!/usr/bin/python3.6
# NecroBot: The ultimate moderation bot with some fun commands to keep everybody entertained

# import statements for basic discord bot functionalities
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

# import statements for commands
import csv
import random
import sys
import time as t
import calendar as c
import datetime as d
import asyncio
import traceback
import re
from simpleeval import simple_eval
import inspect
import ast
from rings.help import NecroBotHelpFormatter
from rings.botdata.data import Data


#prefix command
prefixes = ["n!","N!", "<@317619283377258497> "]
async def get_pre(bot, message):
    return prefixes

description = "The ultimate moderation bot which is also the first bot for video game modders and provides a simple economy simple, some utility commands and some fun commands."
bot = commands.Bot(command_prefix=get_pre, description=description, formatter=NecroBotHelpFormatter())

userData = Data.userData
serverData = Data.serverData
superDuperIgnoreList = Data.superDuperIgnoreList
lockedList = list()

extensions = [
    "animals",
    "social",
    "wiki",
    "modding",
    "support",
    "utilities",
    "moderation",
    "profile",
    "tags",
    "server",
    "music"
]

replyList = [
    "*yawn* What can I do fo... *yawn*... for you?", 
    "NecroBot do that, NecroBot do this, never NecroBot how are y... Oh, hey how can I help?",
    "I wonder how other bots are treated :thinking: Do they also put up with their owners' terrible coding habits?"
    ]
# *****************************************************************************************************************
#  Internal Function
# *****************************************************************************************************************

def logit(message):
    with open("logfile.txt","a+") as log:
        localtime = str("\n" + t.asctime(t.localtime(t.time())) + ": ")
        msg = str(localtime + str(message.author) + " used " + message.content)
        log.write(msg)

async def default_stats(member, server):
    if member.id not in userData:
        userData[member.id] = {'money': 200, 'daily': '32','title':'','exp':0,'perms':{},'warnings':[],'lastMessage':'','lastMessageTime':0,'locked':''}

    if server.id not in userData[member.id]["perms"]:
        if member.id == server.owner.id:
            userData[member.id]["perms"][server.id] = 5
            await bot.send_message(server.default_channel, member.name + " perms level set to 5 (Server Owner)")
        elif member.server_permissions.administrator:
            userData[member.id]["perms"][server.id] = 4
            await bot.send_message(server.default_channel, member.name + " perms level set to 4 (Admin)")
        elif any(userData[member.id]["perms"][x] == 6 for x in userData[member.id]["perms"]):
            userData[member.id]["perms"][server.id] = 6
            await bot.send_message(server.default_channel, member.name + " perms level set to 6 (NecroBot Admin)")
        elif any(userData[member.id]["perms"][x] == 7 for x in userData[member.id]["perms"]):
            userData[member.id]["perms"][server.id] = 7
            await bot.send_message(server.default_channel, member.name + " perms level set to 7 (The Bot Smith)")
        else:
            userData[member.id]["perms"][server.id] = 0

def allmentions(cont, msg):
    myList = []
    mentions = msg.split(" ")
    for x in mentions:
        ID = re.sub('[<>!#@]', '', x)
        if not bot.get_channel(ID) is None:
            channel = bot.get_channel(ID)
            myList.append(channel)
        elif not cont.message.server.get_member(ID) is None:
            member = cont.message.server.get_member(ID)
            myList.append(member)
    return myList

# *****************************************************************************************************************
#  Check Functions
# *****************************************************************************************************************
def has_perms(perms_level):
    def predicate(cont):
        return userData[cont.message.author.id]["perms"][cont.message.server.id] >= perms_level
    return commands.check(predicate)

def is_necro():
    def predicate(cont):
        return cont.message.author.id == "241942232867799040"
    return commands.check(predicate)

# *****************************************************************************************************************
#  Background Task
# *****************************************************************************************************************
async def hourly_save():
    await bot.wait_until_ready()
    while not bot.is_closed:
        with open("rings/botdata/userdata.csv","w",newline="") as csvfile:
            Awriter = csv.writer(csvfile)
            for x in userData:
                warningList = ",".join(userData[x]["warnings"])
                Awriter.writerow([x,userData[x]["money"],userData[x]["daily"],userData[x]["title"],userData[x]["exp"],userData[x]["perms"],warningList])

        with open("rings/botdata/setting.csv","w",newline="") as csvfile:
            Awriter = csv.writer(csvfile)
            Awriter.writerow(superDuperIgnoreList)
            Awriter.writerow(['Server Name','Server','Mute Role','Automod Channel','Welcome Channel',"Self Roles","Automod Ignore","Commands Ignore","Welcome Message","Goodbye Message","Tags"])
            for x in serverData:
                selfRolesList = ",".join(serverData[x]["selfRoles"])
                automodList = ",".join(serverData[x]["ignoreAutomod"])
                commandList = ",".join(serverData[x]["ignoreCommand"])
                Awriter.writerow([bot.get_server(x).name,x,serverData[x]["mute"],serverData[x]["automod"],serverData[x]["welcome-channel"],selfRolesList,commandList,automodList,serverData[x]["welcome"],serverData[x]["goodbye"],serverData[x]["tags"]])

        print("Saved at " + str(t.asctime(t.localtime(t.time()))))
        await asyncio.sleep(3600) # task runs every hour


# *****************************************************************************************************************
#  Cogs Commands
# *****************************************************************************************************************
@bot.command(hidden=True)
@is_necro()
async def load(extension_name : str):
    """Loads the extension name if in NecroBot's list of rings."""
    try:
        bot.load_extension("rings." + extension_name)
    except (AttributeError,ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} loaded.".format(extension_name))

@bot.command(hidden=True)
@is_necro()
async def unload(extension_name : str):
    """Unloads the extension name if in NecroBot's list of rings."""
    bot.unload_extension("rings." + extension_name)
    await bot.say("{} unloaded.".format(extension_name))

@bot.command(hidden=True)
@is_necro()
async def reload(extension_name : str):
    """Unload and loads the extension name if in NecroBot's list of rings."""
    bot.unload_extension("rings." + extension_name)
    try:
        bot.load_extension("rings." + extension_name)
    except (AttributeError,ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} reloaded.".format(extension_name))


# *****************************************************************************************************************
#  on_ready
# *****************************************************************************************************************

@bot.event
async def on_ready():
    for x in bot.get_all_members():
        await default_stats(x, x.server)

    for extension in extensions:
        try:
            bot.load_extension("rings."+extension)
        except Exception as e:
            exc = '{} : {}'.format(type(e).__name__, e)
            print("Failed to load extension {}\n{}".format(extension.exc))

    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print("SuperDuperIgnore List: " +  str(superDuperIgnoreList))
    print(serverData)
    print('------')
    await bot.change_presence(game=discord.Game(name='n!help'))
    await bot.send_message(bot.get_channel("318465643420712962"), "**Bot Online**")


# *****************************************************************************************************************
#  Admin Commands
# *****************************************************************************************************************
@bot.command(pass_context = True, aliases=["off"], hidden=True)
@is_necro()
async def kill(cont):
    """Saves all the data and terminate the bot. (Permission level required: 7+ (The Bot Smith))"""
    with open("rings/botdata/userdata.csv","w",newline="") as csvfile:
        Awriter = csv.writer(csvfile)
        for x in userData:
            warningList = ",".join(userData[x]["warnings"])
            Awriter.writerow([x,userData[x]["money"],userData[x]["daily"],userData[x]["title"],userData[x]["exp"],userData[x]["perms"],warningList])

    with open("rings/botdata/setting.csv","w",newline="") as csvfile:
        Awriter = csv.writer(csvfile)
        Awriter.writerow(superDuperIgnoreList)
        Awriter.writerow(['Server Name','Server','Mute Role','Automod Channel','Welcome Channel',"Self Roles","Automod Ignore","Commands Ignore","Welcome Message","Goodbye Message","Tags"])
        for x in serverData:
            selfRolesList = ",".join(serverData[x]["selfRoles"])
            automodList = ",".join(serverData[x]["ignoreAutomod"])
            commandList = ",".join(serverData[x]["ignoreCommand"])
            Awriter.writerow([bot.get_server(x).name,x,serverData[x]["mute"],serverData[x]["automod"],serverData[x]["welcome-channel"],selfRolesList,commandList,automodList,serverData[x]["welcome"],serverData[x]["goodbye"],serverData[x]["tags"]])

    await bot.send_message(bot.get_channel("318465643420712962"), "**Bot Offline**")
    await bot.logout()

@bot.command(pass_context = True)
@has_perms(2)
async def setstats(self, cont, user : discord.Member):
    """Allows server specific authorities to set the default stats for a user that might have slipped past the on_ready and on_member_join events (Permission level required: 2+ (Moderator))"""
    await default_stats(user, cont.message.server)
    await bot.say("Stats set for user")

@bot.command(pass_context = True, hidden=True)
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

@bot.command(pass_context = True, hidden=True)
@has_perms(6)
async def pm(cont, ID, *, message):
    """Sends the given message to the user of the given id. It will then wait 5 minutes for an answer and print it to the channel it was called it. (Permission level required: 6+ (NecroBot Admin))"""
    for x in bot.get_all_members():
        if x.id == ID:
            user = x

    send = await bot.send_message(user, message + "\n*You have 5 minutes to reply to the message*")
    to_edit = await bot.say(":white_check_mark: | **Message sent**")
    msg = await bot.wait_for_message(author=user, channel=send.channel, timeout=300)
    await bot.edit_message(to_edit, ":speech_left: | **User: {0.author}** said :**{0.content}**".format(msg))

@bot.command(pass_context = True, hidden = True)
@is_necro()
async def test(cont, ID):
    """Returns the name of the user based on the given id. Used to debug the auto-moderation feature"""
    for x in bot.get_all_members():
        if x.id == ID:
            await bot.say(x.name + "#" + str(x.discriminator))

@bot.command(pass_context = True, hidden=True)
@is_necro()
async def invites(cont):
    """Returns invites (if the bot has valid permissions) for each server the bot is on."""
    for server in bot.servers:
        try:
            invite = await bot.create_invite(server)
            await bot.send_message(cont.message.author, "Server: " + server.name + " - " + invite.url)
        except:
            await bot.send_message(cont.message.author, "I don't have the necessary permissions on " + server.name)

@bot.command(pass_context=True, hidden=True)
@is_necro()
async def debug(cont, *, code : str):
    """Evaluates code."""
    code = code.strip('` ')
    python = '```py\n{}\n```'
    result = None

    env = {
        'bot': bot,
        'cont': cont,
        'message': cont.message,
        'server': cont.message.server,
        'channel': cont.message.channel,
        'author': cont.message.author
    }

    env.update(globals())

    try:
        result = eval(code, env)
        if inspect.isawaitable(result):
            result = await result
    except Exception as e:
        await bot.say(python.format(type(e).__name__ + ': ' + str(e)))
        return

    await bot.say(python.format(result))


# *****************************************************************************************************************
#  Moderation Features
# *****************************************************************************************************************
@bot.event
async def on_command_error(error, cont):
    """Catches error and sends a message to the user that caused the error with a helpful message."""
    channel = cont.message.channel
    if isinstance(error, commands.MissingRequiredArgument):
        await bot.send_message(channel, ":negative_squared_cross_mark: | Missing required argument, check the help guide with `n!h {0}`".format(cont.command.name))
    elif isinstance(error, commands.CheckFailure):
        await bot.send_message(channel, ":negative_squared_cross_mark: | You do not have the required NecroBot permissions to use this command.")
    elif isinstance(error, commands.CommandOnCooldown):
        await bot.send_message(channel, ":negative_squared_cross_mark: | This command is on cooldown, retry after **{0:.0f}** seconds".format(error.retry_after))
    elif isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(channel, ":negative_squared_cross_mark: | This command cannot be used in private messages.")
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(channel, ":negative_squared_cross_mark: | This command is disabled and cannot be used for now.")
    elif isinstance(error, commands.BadArgument):
        await bot.send_message(channel, ":negative_squared_cross_mark: | Something went wrongs with the arguments you sent, make sure you're sending what is required.")
    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(cont), file=sys.stderr)
        traceback.print_tb(error.original.__traceback__)
        print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)

#sends help text to default channel and sets default for all users present
@bot.event
async def on_server_join(server):
    membList = server.members
    for x in membList:
        await default_stats(x, server)

    msg = " do `n!help settings` to find out what you need to do to get NecroBot up and running to its full potential on your server"
    await bot.send_message(server.default_channel, "Stats sets for users \n " + server.owner.mention + msg)
    serverData[server.id] = {"mute":"","automod":"","welcome-channel":server.default_channel.id, "selfRoles":[],"ignoreCommand":[],"ignoreAutomod":[],"welcome":"Welcome {member} to {server}!","goodbye":"Leaving so soon? We\'ll miss you, {member}!","tags":{}}
    await bot.send_message(bot.get_channel("241942232867799040"),"I was just invited in the server: " + server.name)

#automod
@bot.event
async def on_message_delete(message):
    if serverData[message.server.id]["automod"] != "":
        ChannelId = serverData[message.server.id]["automod"]
    else:
        ChannelId = "318828760331845634"

    if message.author.id not in serverData[message.server.id]["ignoreAutomod"] and message.channel.id not in serverData[message.server.id]["ignoreAutomod"]:
        fmt = '**Auto Moderation: Deletion Detected!**\n Message by **{0.author}** was deleted in {0.channel.name}, it contained: ``` {0.content} ```'
        await bot.send_message(bot.get_channel(ChannelId), fmt.format(message))

#automod
@bot.event
async def on_message_edit(before, after):
    if serverData[before.server.id]["automod"] != "":
        ChannelId = serverData[before.server.id]["automod"]
    else:
        ChannelId = "318828760331845634"

    if before.author.id not in serverData[before.server.id]["ignoreAutomod"] and before.channel.id not in serverData[before.server.id]["ignoreAutomod"]:
        fmt = '**Auto Moderation: Edition Detected!**\n{0.author} edited their message: ``` {0.content} \n {1.content} ```'
        await bot.send_message(bot.get_channel(ChannelId), fmt.format(before, after))

#welcomes and set stats
@bot.event
async def on_member_join(member):
    server = member.server
    channel = bot.get_channel(serverData[member.server.id]["welcome-channel"])
    message = serverData[member.server.id]["welcome"]
    server = member.server

    await bot.send_message(channel, message.format(member=member.mention, server=server.name))
    await default_stats(member, server)

#says goodbye and resets perms level if less than NecroBot Admin
@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(serverData[member.server.id]["welcome-channel"])
    message = serverData[member.server.id]["goodbye"]

    await bot.send_message(channel, message.format(member=member.mention))
    if userData[member.id]["perms"][member.server.id] < 6:
        userData[member.id]["perms"][member.server.id] = 0

#used for lock command
@bot.event
async def on_voice_state_update(before, after):
    if before.id in lockedList:
        await bot.move_member(before, bot.get_channel(userData[before.id]["locked"]))


#spam control and ignore
@bot.event
async def on_message(message):
    userID = message.author.id
    channelID = message.channel.id

    if message.author.bot or message.channel.id in superDuperIgnoreList:
        return

    if not message.channel.is_private:
        #check if spam
        if ((message.content == userData[userID]['lastMessage'] and userData[userID]['lastMessageTime'] > c.timegm(t.gmtime()) + 2) or userData[userID]['lastMessageTime'] > c.timegm(t.gmtime()) + 1) and (userID not in serverData[message.server.id]["ignoreAutomod"] and channelID not in serverData[message.server.id]["ignoreAutomod"]) and not message.content.startswith(tuple(prefixes)):
            await bot.delete_message(message)
            try:
                ChannelId = serverData[message.server.id]["automod"]
            except KeyError:
                ChannelId = "318828760331845634"

            await bot.send_message(bot.get_channel(ChannelId), "User: {0.author} spammed message: ``` {0.content} ```".format(message))
            userData[userID]['lastMessage'] = message.content
            userData[userID]['lastMessageTime'] = int(c.timegm(t.gmtime()))
        else:
            userData[userID]['lastMessage'] = message.content
            userData[userID]['lastMessageTime'] = int(c.timegm(t.gmtime()))
            userData[userID]["exp"] += random.randint(2,5)

            #check if allowed bot summon
            if ((channelID not in serverData[message.server.id]["ignoreCommand"] and userID not in serverData[message.server.id]["ignoreCommand"]) or userData[message.author.id]["perms"][message.server.id] >= 4) and message.content.startswith(tuple(prefixes)):
                if message.content.startswith("<@317619283377258497>"):
                    await bot.send_message(message.channel, random.choice(replyList))

                logit(cont.message)
                await bot.process_commands(message)

    elif message.content.startswith(tuple(prefixes)) and message.channel.is_private:
        await bot.send_message(message.channel, "Sorry, due to the way the bot works you cannot use commands in DMs")

def bot_run():
    bot.loop.create_task(hourly_save())
    token = open("token.txt", "r").read()
    bot.run(token)

bot_run()