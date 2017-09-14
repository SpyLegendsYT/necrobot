#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import os
import re
import csv
import sys
import socket
import random
import logging
import asyncio
import traceback
import time as t
import calendar as c
import datetime as d
from rings.botdata.data import Data
from rings.help import NecroBotHelpFormatter

#prefix command
prefixes = ["n!","N!", "<@317619283377258497> "]
async def get_pre(bot, message):
    if not message.channel.is_private:
        if serverData[message.server.id]["prefix"] != "":
            return serverData[message.server.id]["prefix"]
    return prefixes

description = "The ultimate moderation bot which is also the first bot for video game modders and provides a simple economy simple, some utility commands and some fun commands."
bot = commands.Bot(command_prefix=get_pre, description=description, formatter=NecroBotHelpFormatter())

userData = Data.userData
serverData = Data.serverData
superDuperIgnoreList = Data.superDuperIgnoreList
default_path = sys.argv[2]
version = "v0.5"
ERROR_LOG = "351356683231952897"

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

#forgive me gods of Python
def startswith_prefix(message):
    return message.content.startswith(tuple(prefixes)) or (serverData[message.server.id]["prefix"] != "" and message.content.startswith(serverData[message.server.id]["prefix"]))

def is_spam(message):
    userID = userData[message.author.id]
    channelID = message.channel.id
    if serverData[message.server.id]["automod"] == "":
        return False

    return ((message.content.lower() == userID['lastMessage'].lower() and userID['lastMessageTime'] > c.timegm(t.gmtime()) + 2) or userID['lastMessageTime'] > c.timegm(t.gmtime()) + 1) and (userID not in serverData[message.server.id]["ignoreAutomod"] and channelID not in serverData[message.server.id]["ignoreAutomod"]) and not startswith_prefix(message)

def is_allowed_summon(message):
    userID = userData[message.author.id]
    channelID = message.channel.id
    return ((channelID not in serverData[message.server.id]["ignoreCommand"] and message.author.id not in serverData[message.server.id]["ignoreCommand"]) or userID["perms"][message.server.id] >= 4) and startswith_prefix(message)

def logit(message):
    if startswith_prefix(message):
        with open(default_path + "logfile.txt","a+") as log:
            localtime = "\n{}: ".format(t.asctime(t.localtime(t.time())))
            try: 
                author = "{}#{}".format(message.author.name, message.author.discriminator)
            except:
                author = message.author.id

            log.write("{}{} used {}".format(localtime, author, message.content))

def default_stats(member, server):
    if member.id not in userData:
        userData[member.id] = {'money': 200, 'daily': '', 'title': '', 'exp': 0, 'perms': {}, 'warnings': [], 'lastMessage': '', 'lastMessageTime': 0, 'locked': ''}

    if server.id not in userData[member.id]["perms"]:
        if any(userData[member.id]["perms"][x] == 7 for x in userData[member.id]["perms"]):
            userData[member.id]["perms"][server.id] = 7
        elif any(userData[member.id]["perms"][x] == 6 for x in userData[member.id]["perms"]):
            userData[member.id]["perms"][server.id] = 6
        elif member.id == server.owner.id:
            userData[member.id]["perms"][server.id] = 5
        elif member.server_permissions.administrator:
            userData[member.id]["perms"][server.id] = 4
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

async def save():
    with open(default_path + "rings/botdata/userdata.csv","w",newline="") as csvfile:
        Awriter = csv.writer(csvfile)
        for x in userData:
            warningList = ",".join(userData[x]["warnings"])
            Awriter.writerow([x,userData[x]["money"],userData[x]["daily"],userData[x]["title"],userData[x]["exp"],userData[x]["perms"],warningList])

    with open(default_path + "rings/botdata/setting.csv","w",newline="") as csvfile:
        Awriter = csv.writer(csvfile)
        Awriter.writerow(superDuperIgnoreList)
        Awriter.writerow(['Server','Mute Role','Automod Channel','Welcome Channel',"Self Roles","Automod Ignore","Commands Ignore","Welcome Message","Goodbye Message","Tags","Prefix"])
        for x in serverData:
            selfRolesList = ",".join(serverData[x]["selfRoles"])
            automodList = ",".join(serverData[x]["ignoreAutomod"])
            commandList = ",".join(serverData[x]["ignoreCommand"])
            Awriter.writerow([x,serverData[x]["mute"],serverData[x]["automod"],serverData[x]["welcome-channel"],selfRolesList,commandList,automodList,serverData[x]["welcome"],serverData[x]["goodbye"],serverData[x]["tags"], serverData[x]["prefix"]])

    await bot.send_message(bot.get_channel(ERROR_LOG), "Saved at " + str(t.asctime(t.localtime(t.time()))))

# *****************************************************************************************************************
#  Background Tasks
# *****************************************************************************************************************
async def hourly_task():
    await bot.wait_until_ready()
    while not bot.is_closed:
        await asyncio.sleep(2700) # task runs every 45 min
        await save()

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
# Commands
# *****************************************************************************************************************
@bot.command(aliases=["off"])
@is_necro()
async def kill():
    """Saves all the data and terminate the bot. (Permission level required: 7+ (The Bot Smith))
     
    {usage}"""
    await save()
    await bot.send_message(bot.get_channel("318465643420712962"), "**Bot Offline**")
    await bot.logout()

@bot.command(name="save")
@is_necro()
async def command_save():
    """Saves all the data. (Permission level required: 7+ (The Bot Smith))
     
    {usage}"""
    msg = await bot.say("**Saving Data...**")
    await save()
    await bot.edit_message(msg, "**Data saved**")

@bot.command(pass_context = True)
async def about(cont):
    """Creates a rich embed of the bot's details.

    {usage}"""
    bot_desc = "Hello! :wave: I'm NecroBot, a moderation bot with many commands for a wide variety of server and a high modularity which means you can enable/disable just about every part of me as you wish. I'm still WIP so please be nice with me, but do enjoy my commands to their fullest."
    embed = discord.Embed(title="__**NecroBot**__", colour=discord.Colour(0x277b0), description=bot_desc)
    embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")
    embed.add_field(name="Version", value=version)
    embed.add_field(name="About", value="I'm currently in {} guilds and I can see {} members. I was created using Python and the d.py library. ".format(len(list(bot.servers)), len(list(bot.get_all_members()))))

    await bot.say(embed=embed)

@bot.command(pass_context = True)
@is_necro()
async def leave(cont, ID, *, reason : str ="unspecified"):
    """Leaves the specified server. (Permission level required: 7+ (The Bot Smith))

    {usage}"""
    server = bot.get_server(ID)
    if not server is None:
        await bot.say(":white_check_mark: | Okay Necro, I'm leaving {}".format(server.name))
        await bot.send_message(list(server.channels)[0], "I'm sorry, Necro#6714 has decided I should leave this server, because: {}".format(reason))
        await bot.leave_server(server)
    else:
        await bot.say(":negative_squared_cross_mark: | I'm not on that server")

# *****************************************************************************************************************
#  Events
# *****************************************************************************************************************
@bot.event
async def on_ready():
    print("SuperDuperIgnore List: {}".format(superDuperIgnoreList))
    print(serverData)
    print('------')
    channel = bot.get_channel("318465643420712962")
    await bot.send_message(channel, "**Initiating Bot**")
    msg = await bot.send_message(channel, "Bot user ready")

    for member in bot.get_all_members():
        default_stats(member, member.server)
    await bot.edit_message(msg, "All members checked")

    for server in bot.servers:
        if server.id not in serverData:
                serverData[server.id] = {"mute":"","automod":"","welcome-channel":"", "selfRoles":[],"ignoreCommand":[],"ignoreAutomod":[],"welcome":"Welcome {member} to {server}!","goodbye":"Leaving so soon? We\'ll miss you, {member}!","tags":{}, "prefix" : ""}

    await bot.edit_message(msg, "All servers checked")

    for extension in extensions:
        try:
            bot.load_extension("rings."+extension)
        except Exception as e:
            exc = '{} : {}'.format(type(e).__name__, e)
            await bot.send_message(bot.get_channel(ERROR_LOG) ,"Failed to load extension {}\n{}".format(extension.exc))
    await bot.edit_message(msg, "All extensions loaded")

    await bot.send_message(channel, "**Bot Online**")
    await bot.delete_message(msg)

    await bot.change_presence(game=discord.Game(name="n!help for help", type=0))

@bot.event
async def on_error(event, *args, **kwargs):
    await bot.send_message(bot.get_channel(ERROR_LOG), 'Ignoring exception in {}'.format(event))
    await bot.send_message(bot.get_channel(ERROR_LOG), traceback.format_exc())


@bot.event
async def on_command_error(error, cont):
    """Catches error and sends a message to the user that caused the error with a helpful message."""
    channel = cont.message.channel
    msg = None

    if isinstance(error, commands.MissingRequiredArgument):
        msg = await bot.send_message(channel, ":negative_squared_cross_mark: | Missing required argument! Check help guide with `n!help {}`".format(cont.command.name))
    elif isinstance(error, commands.CheckFailure):
        msg = await bot.send_message(channel, ":negative_squared_cross_mark: | You do not have the required NecroBot permissions to use this command.")
    elif isinstance(error, commands.CommandOnCooldown):
        msg = await bot.send_message(channel, ":negative_squared_cross_mark: | This command is on cooldown, retry after **{0:.0f}** seconds".format(error.retry_after))
    elif isinstance(error, commands.NoPrivateMessage):
        msg = await bot.send_message(channel, ":negative_squared_cross_mark: | This command cannot be used in private messages.")
    elif isinstance(error, commands.DisabledCommand):
        msg = await bot.send_message(channel, ":negative_squared_cross_mark: | This command is disabled and cannot be used for now.")
    elif isinstance(error, commands.BadArgument):
        msg = await bot.send_message(channel, ":negative_squared_cross_mark: | Something went wrongs with the arguments you sent, make sure you're sending what is required.")
    elif isinstance(error, discord.errors.Forbidden):
        msg = await bot.send_message(channel, ":negative_squared_cross_mark: | Something went wrong, check my permission level, it seems I'm not allowed to do that on your server.")
    elif isinstance(error, commands.CommandInvokeError):
        await bot.send_message(bot.get_channel(ERROR_LOG), 'In {0.command.qualified_name}:'.format(cont))
        await bot.send_message(bot.get_channel(ERROR_LOG),"```" + " ".join(traceback.format_exception(type(error), error, error.__traceback__)) + " ```")
        await bot.send_message(bot.get_channel(ERROR_LOG), '{0.__class__.__name__}: {0}'.format(error.original))

    if not msg is None:
        await asyncio.sleep(10)
        await bot.delete_message(msg)

@bot.event
async def on_server_join(server):
    serverData[server.id] = {"mute":"","automod":"","welcome-channel":"", "selfRoles":[],"ignoreCommand":[],"ignoreAutomod":[],"welcome":"Welcome {member} to {server}!","goodbye":"Leaving so soon? We\'ll miss you, {member}!","tags":{}, "prefix": ""}

    membList = server.members
    for x in membList:
        default_stats(x, server)

    await bot.send_message(server.owner, ":information_source: I've just been invited to a server you own. Everything is good to go, your server has been set up on my side. However, most my automatic functionalities are disabled by default (automoderation, welcome-messages and mute). You just need to set those up using `n!settings`. Check out the help with `n!help settings`")

@bot.event
async def on_server_remove(server):
    del serverData[server.id]

@bot.event
async def on_message_delete(message):
    if message.channel.is_private or serverData[message.server.id]["automod"] == "" or message.author.bot:
        return

    if message.author.id not in serverData[message.server.id]["ignoreAutomod"] and message.channel.id not in serverData[message.server.id]["ignoreAutomod"]:
        fmt = '**Auto Moderation: Deletion Detected!**\n Message by **{0.author}** was deleted in {0.channel.name}, it contained: ``` {0.content} ```'
        await bot.send_message(bot.get_channel(serverData[message.server.id]["automod"]), fmt.format(message))

@bot.event
async def on_message_edit(before, after):
    if before.channel.is_private or serverData[before.server.id]["automod"] == "" or before.author.bot or before.content == after.content:
        return

    if before.author.id not in serverData[before.server.id]["ignoreAutomod"] and before.channel.id not in serverData[before.server.id]["ignoreAutomod"]:
        fmt = '**Auto Moderation: Edition Detected!**\n{0.author} edited their message: ``` {0.content} \n {1.content} ```'
        await bot.send_message(bot.get_channel(serverData[before.server.id]["automod"]), fmt.format(before, after))

@bot.event
async def on_member_join(member):
    default_stats(member, member.server)

    if serverData[member.server.id]["welcome-channel"] == "" or member.bot:
        return

    channel = bot.get_channel(serverData[member.server.id]["welcome-channel"])
    message = serverData[member.server.id]["welcome"]

    await bot.send_message(channel, message.format(member=member.mention, server=member.server.name))

@bot.event
async def on_member_remove(member):
    if userData[member.id]["perms"][member.server.id] < 6:
        userData[member.id]["perms"][member.server.id] = 0

    if serverData[member.server.id]["welcome-channel"] == "" or member.bot:
        return

    channel = bot.get_channel(serverData[member.server.id]["welcome-channel"])
    message = serverData[member.server.id]["goodbye"]

    await bot.send_message(channel, message.format(member=member.mention))

@bot.event
async def on_command(command, cont):
    logit(cont.message)

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

        if not is_allowed_summon(message):
            return

        if message.content.startswith("<@317619283377258497>"):
            await bot.send_message(message.channel, random.choice(replyList))

        
    await bot.process_commands(message)

def run_bot():
    bot.loop.create_task(hourly_task())
    bot.run(sys.argv[1])

try:
    port = int(os.getenv("PORT"))
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((socket.gethostname(), port))
    serversocket.listen(5)
except TypeError:
    pass

run_bot()