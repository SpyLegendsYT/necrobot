#!/usr/bin/python3.6
# NecroBot: The ultimate moderation bot with some fun commands to keep everybody entertained

# import statements for basic discord bot functionalities
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

# import statements for commands
import re
import csv
import sys
import socket
import random
import logging
import aiohttp
import asyncio
import traceback
import time as t
import calendar as c
import datetime as d
from rings.botdata.data import Data
from rings.help import NecroBotHelpFormatter

userData = Data.userData
serverData = Data.serverData
superDuperIgnoreList = Data.superDuperIgnoreList
lockedList = list()
default_path = ""
starttime = d.datetime.now()
version = "0.4"

#prefix command
prefixes = ["n!","N!", "<@317619283377258497> "]
async def get_pre(bot, message):
    if not message.channel.is_private:
        if serverData[message.server.id]["prefix"] != "":
            return serverData[message.server.id]["prefix"]

    return prefixes

description = "The ultimate moderation bot which is also the first bot for video game modders and provides a simple economy simple, some utility commands and some fun commands."
bot = commands.Bot(command_prefix=get_pre, description=description, formatter=NecroBotHelpFormatter())

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
    "music",
    "casino",
    "admin"
]

replyList = [
    "*yawn* What can I do fo... *yawn*... for you?", 
    "NecroBot do that, NecroBot do this, never NecroBot how are y... Oh, hey how can I help?",
    "I wonder how other bots are treated :thinking: Do they also put up with their owners' terrible coding habits?",
    "Second sight ordains it! I mean sure..."
    ]
# *****************************************************************************************************************
#  Internal Function
# *****************************************************************************************************************

lock_socket = None  # we want to keep the socket open until the very end of
                    # our script so we use a global variable to avoid going
                    # out of scope and being garbage-collected

def is_lock_free():
    global lock_socket
    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        lock_id = "necro.necrobot"   # this should be unique. using your username as a prefix is a convention
        lock_socket.bind('\0' + lock_id)
        logging.debug("Acquired lock %r" % (lock_id,))
        return True
    except socket.error:
        # socket already locked, task must already be running
        logging.info("Failed to acquire lock %r" % (lock_id,))
        return False

#forgive me gods of Python
def startswith_prefix(message):
    return message.content.startswith(tuple(prefixes)) or (serverData[message.server.id]["prefix"] != "" and message.content.startswith(serverData[message.server.id]["prefix"]))

def is_spam(message):
    userID = message.author.id
    channelID = message.channel.id
    return ((message.content.lower() == userData[userID]['lastMessage'].lower() and userData[userID]['lastMessageTime'] > c.timegm(t.gmtime()) + 2) or userData[userID]['lastMessageTime'] > c.timegm(t.gmtime()) + 1) and (userID not in serverData[message.server.id]["ignoreAutomod"] and channelID not in serverData[message.server.id]["ignoreAutomod"]) and not startswith_prefix(message)

def is_allowed_summon(message):
    userID = message.author.id
    channelID = message.channel.id
    return ((channelID not in serverData[message.server.id]["ignoreCommand"] and userID not in serverData[message.server.id]["ignoreCommand"]) or userData[userID]["perms"][message.server.id] >= 4) and startswith_prefix(message)

def logit(message):
    if startswith_prefix(message):
        with open(default_path + "logfile.txt","a+") as log:
            localtime = str("\n" + t.asctime(t.localtime(t.time())) + ": ")
            try: 
                log.write(str(localtime + str(message.author) + " used " + message.content))
            except:
                log.write(str(localtime + str(message.author.id) + " used " + message.content))

def default_stats(member, server):
    if member.id not in userData:
        userData[member.id] = {'money': 200, 'daily': '', 'title': '', 'exp': 0, 'perms': {}, 'warnings': [], 'lastMessage': '', 'lastMessageTime': 0, 'locked': ''}

    if server.id not in userData[member.id]["perms"]:
        if member.id == server.owner.id:
            userData[member.id]["perms"][server.id] = 5
        elif member.server_permissions.administrator:
            userData[member.id]["perms"][server.id] = 4
        elif any(userData[member.id]["perms"][x] == 6 for x in userData[member.id]["perms"]):
            userData[member.id]["perms"][server.id] = 6
        elif any(userData[member.id]["perms"][x] == 7 for x in userData[member.id]["perms"]):
            userData[member.id]["perms"][server.id] = 7
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

def save():
    with open(default_path + "rings/botdata/userdata.csv","w",newline="") as csvfile:
        Awriter = csv.writer(csvfile)
        for x in userData:
            warningList = ",".join(userData[x]["warnings"])
            Awriter.writerow([x,userData[x]["money"],userData[x]["daily"],userData[x]["title"],userData[x]["exp"],userData[x]["perms"],warningList])

    with open(default_path + "rings/botdata/setting.csv","w",newline="") as csvfile:
        Awriter = csv.writer(csvfile)
        Awriter.writerow(superDuperIgnoreList)
        Awriter.writerow(['Server Name','Server','Mute Role','Automod Channel','Welcome Channel',"Self Roles","Automod Ignore","Commands Ignore","Welcome Message","Goodbye Message","Tags","Prefix"])
        for x in serverData:
            selfRolesList = ",".join(serverData[x]["selfRoles"])
            automodList = ",".join(serverData[x]["ignoreAutomod"])
            commandList = ",".join(serverData[x]["ignoreCommand"])
            Awriter.writerow([bot.get_server(x).name,x,serverData[x]["mute"],serverData[x]["automod"],serverData[x]["welcome-channel"],selfRolesList,commandList,automodList,serverData[x]["welcome"],serverData[x]["goodbye"],serverData[x]["tags"], serverData[x]["prefix"]])

    print("Saved at " + str(t.asctime(t.localtime(t.time()))))

# *****************************************************************************************************************
#  Background Task
# *****************************************************************************************************************
async def hourly_save():
    await bot.wait_until_ready()
    while not bot.is_closed:
        save()
        await asyncio.sleep(3600) # task runs every hour

# *****************************************************************************************************************
#  Custom Checks
# *****************************************************************************************************************
def has_perms(perms_level):
    def predicate(cont):
        return userData[cont.message.author.id]["perms"][cont.message.server.id] >= perms_level and not cont.message.channel.is_private 
    return commands.check(predicate)

def is_necro():
    def predicate(cont):
        return cont.message.author.id == "241942232867799040"
    return commands.check(predicate)
        

# *****************************************************************************************************************
#  Cogs Commands
# *****************************************************************************************************************
@bot.command(hidden=True)
@is_necro()
async def load(extension_name : str):
    """Loads the extension name if in NecroBot's list of rings.
    
    {usage}"""
    try:
        bot.load_extension("rings." + extension_name)
    except (AttributeError,ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} loaded.".format(extension_name))

@bot.command(hidden=True)
@is_necro()
async def unload(extension_name : str):
    """Unloads the extension name if in NecroBot's list of rings.
     
    {usage}"""
    bot.unload_extension("rings." + extension_name)
    await bot.say("{} unloaded.".format(extension_name))

@bot.command(hidden=True)
@is_necro()
async def reload(extension_name : str):
    """Unload and loads the extension name if in NecroBot's list of rings.
     
    {usage}"""
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
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print("SuperDuperIgnore List: " +  str(superDuperIgnoreList))
    print(serverData)
    print('------')
    await bot.change_presence(game=discord.Game(name='n!help', type=0))
    await bot.send_message(bot.get_channel("318465643420712962"), "**Bot Online**")

    for x in bot.get_all_members():
        default_stats(x, x.server)

    for extension in extensions:
        try:
            bot.load_extension("rings."+extension)
        except Exception as e:
            exc = '{} : {}'.format(type(e).__name__, e)
            print("Failed to load extension {}\n{}".format(extension.exc))

    await bot.send_message(bot.get_channel("318465643420712962"), "All extensions loaded")


# *****************************************************************************************************************
# Commands
# *****************************************************************************************************************
@bot.command(aliases=["off"], hidden=True)
@is_necro()
async def kill():
    """Saves all the data and terminate the bot. (Permission level required: 7+ (The Bot Smith))
     
    {usage}"""
    save()
    await bot.send_message(bot.get_channel("318465643420712962"), "**Bot Offline**")
    await bot.logout()

@bot.command(name="save")
@is_necro()
async def command_save():
    """Saves all the data. (Permission level required: 7+ (The Bot Smith))
     
    {usage}"""
    save()
    await bot.say("**Data saved**")


# *****************************************************************************************************************
#  Moderation Features
# *****************************************************************************************************************
@bot.event
async def on_command_error(error, cont):
    """Catches error and sends a message to the user that caused the error with a helpful message."""
    channel = cont.message.channel
    if isinstance(error, commands.MissingRequiredArgument):
        await bot.send_message(channel, ":negative_squared_cross_mark: | Missing required argument! Check help guide with `n!help {}`".format(cont.command.name))
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
    elif isinstance(error, discord.errors.Forbidden):
        await bot.send_message(channel, ":negative_squared_cross_mark: | Something went wrong, check my permission level, it seems I'm not allowed to do that on your server.")
    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(cont), file=sys.stderr)
        traceback.print_tb(error.original.__traceback__)
        print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)

#sends help text to default channel and sets default for all users present
@bot.event
async def on_server_join(server):
    serverData[server.id] = {"mute":"","automod":"","welcome-channel":"", "selfRoles":[],"ignoreCommand":[],"ignoreAutomod":[],"welcome":"Welcome {member} to {server}!","goodbye":"Leaving so soon? We\'ll miss you, {member}!","tags":{}}

    membList = server.members
    for x in membList:
        default_stats(x, server)

    await bot.send_message(server.owner, ":information_source: I've just been invited to a server you own. Everything is good to go, your server has been set up on my side. However, most my automatic functionalities are disabled by default (automoderation, welcome-messages and mute). You just need to set those up using `n!settings`. Check out the help with `n!help settings`")

#automod
@bot.event
async def on_message_delete(message):
    if message.channel.is_private or serverData[message.server.id]["automod"] == "":
        return

    if message.author.id not in serverData[message.server.id]["ignoreAutomod"] and message.channel.id not in serverData[message.server.id]["ignoreAutomod"]:
        fmt = '**Auto Moderation: Deletion Detected!**\n Message by **{0.author}** was deleted in {0.channel.name}, it contained: ``` {0.content} ```'
        await bot.send_message(bot.get_channel(serverData[message.server.id]["automod"]), fmt.format(message))

#automod
@bot.event
async def on_message_edit(before, after):
    if before.channel.is_private or serverData[before.server.id]["automod"] == "":
        return

    if before.author.id not in serverData[before.server.id]["ignoreAutomod"] and before.channel.id not in serverData[before.server.id]["ignoreAutomod"]:
        fmt = '**Auto Moderation: Edition Detected!**\n{0.author} edited their message: ``` {0.content} \n {1.content} ```'
        await bot.send_message(bot.get_channel(serverData[before.server.id]["automod"]), fmt.format(before, after))

#welcomes and set stats
@bot.event
async def on_member_join(member):
    if serverData[member.server.id]["welcome-channel"] == "" or member.bot:
        return

    channel = bot.get_channel(serverData[member.server.id]["welcome-channel"])
    message = serverData[member.server.id]["welcome"]

    await bot.send_message(channel, message.format(member=member.mention, server=member.server.name))
    default_stats(member, member.server)

#says goodbye and resets perms level if less than NecroBot Admin
@bot.event
async def on_member_remove(member):
    if serverData[member.server.id]["welcome-channel"] == "" or member.bot:
        return

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

    if message.author.bot or channelID in superDuperIgnoreList:
        return

    if not message.channel.is_private:
        if is_spam(message) and serverData[message.server.id]["automod"] != "":
            await bot.delete_message(message)
            await bot.send_message(bot.get_channel(serverData[message.server.id]["automod"]), "User: {0.author} spammed message: ``` {0.content} ```".format(message))

        userData[userID]['lastMessage'] = message.content
        userData[userID]['lastMessageTime'] = int(c.timegm(t.gmtime()))
        userData[userID]["exp"] += random.randint(2,5)

        #check if allowed bot summon
        if not is_allowed_summon(message):
            return

        if message.content.startswith("<@317619283377258497>"):
            await bot.send_message(message.channel, random.choice(replyList))

    if message.content.startswith(tuple(prefixes)) or message.content.startswith(serverData[message.server.id]["prefix"]):
        logit(message)
        await bot.process_commands(message)

def run_bot():
    bot.loop.create_task(hourly_save())
    token = open(default_path + "token.txt", "r").read()
    bot.run(token)

# if not is_lock_free():
#     sys.exit()

run_bot()