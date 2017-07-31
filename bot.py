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
import json
import async_timeout
from var import *
import traceback
import re
from simpleeval import simple_eval
import inspect


#prefix command
prefixes = ["n!","N!", "<@317619283377258497> "]
async def get_pre(bot, message):
    return prefixes

bot = commands.Bot(command_prefix=get_pre)
userData = dict()
serverData = dict()
lockedList = list()
extensions = ["animals","social","wiki","moddb","support","utilities"]
bot.remove_command("help")

#Permissions Names
permsName = ["User","Helper","Moderator","Semi-Admin","Admin","Server Owner","NecroBot Admin","The Bot Smith"]

# Role List
roleList = [["Helper",discord.Colour.teal()],["Moderator",discord.Colour.orange()],["Semi-Admin",discord.Colour.darker_grey()],["Admin",discord.Colour.blue()],["Server Owner",discord.Colour.magenta()],["NecroBot Admin",discord.Colour.dark_green()],["The Bot Smith",discord.Colour.dark_red()]]

# *****************************************************************************************************************
#  Initialize
# *****************************************************************************************************************

with open("data/userdata.csv","r") as f:
    reader = csv.reader(f)
    for row in reader:
        permsDict = json.loads(row[5].replace("'", "\""))
        userData[row[0]] = {"money":int(row[1]),"daily":row[2],"title":row[3],"exp":int(row[4]),"perms":permsDict,"warnings":row[6].split(","),"lastMessage":"","lastMessageTime":0, "locked":""}

with open("data/setting.csv","r") as f:
    reader = csv.reader(f)
    blacklistList = list(next(reader))
    line = next(reader)
    for row in reader:
        serverData[row[1]] = {"mute":row[2],"automod":row[3],"welcome-channel":row[4], "selfRoles":row[5].split(","),"ignoreCommand":row[6].split(","),"ignoreAutomod":row[7].split(","),"welcome":row[8],"goodbye":row[9]}

# *****************************************************************************************************************
#  Internal Function
# *****************************************************************************************************************

def logit(message):
    with open("data/logfile.txt","a+") as log:
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

def allmentions(cont, arg0):
    myList = []
    mentions = arg0.split(" ")
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
#  Purge Functions
# *****************************************************************************************************************
def is_bot(m):
    return m.author == bot.user

def is_user(m):
    return m.author.id == m.mentions[0].id


# *****************************************************************************************************************
#  Cogs Commands
# *****************************************************************************************************************
@bot.command()
@is_necro()
async def load(extension_name : str):
    try:
        bot.load_extension("rings." + extension_name)
    except (AttributeError,ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} loaded.".format(extension_name))

@bot.command()
@is_necro()
async def unload(extension_name : str):
    bot.unload_extension("rings." + extension_name)
    await bot.say("{} unloaded.".format(extension_name))

@bot.command()
@is_necro()
async def reload(extension_name : str):
    bot.unload_extension("rings." + extension_name)
    try:
        bot.load_extension("rings." + extension_name)
    except (AttributeError,ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} reloaded.".format(extension_name))

# *****************************************************************************************************************
#  Background Task
# *****************************************************************************************************************
async def hourly_save():
    await bot.wait_until_ready()
    while not bot.is_closed:
        with open("data/userdata.csv","w",newline="") as csvfile:
            Awriter = csv.writer(csvfile)
            for x in userData:
                warningList = ",".join(userData[x]["warnings"])
                Awriter.writerow([x,userData[x]["money"],userData[x]["daily"],userData[x]["title"],userData[x]["exp"],userData[x]["perms"],warningList])

        with open("data/setting.csv","w",newline="") as csvfile:
            Awriter = csv.writer(csvfile)
            Awriter.writerow(blacklistList)
            Awriter.writerow(['Server Name','Server','Mute Role','Automod Channel','Welcome Channel',"Self Roles","Automod Ignore","Commands Ignore"])
            for x in serverData:
                selfRolesList = ",".join(serverData[x]["selfRoles"])
                automodList = ",".join(serverData[x]["ignoreAutomod"])
                commandList = ",".join(serverData[x]["ignoreCommand"])
                Awriter.writerow([bot.get_server(x).name,x,serverData[x]["mute"],serverData[x]["automod"],serverData[x]["welcome-channel"],selfRolesList,commandList,automodList,serverData[x]["welcome"],serverData[x]["goodbye"]])

        print("Saved at " + str(t.asctime(t.localtime(t.time()))))
        await asyncio.sleep(3600) # task runs every hour


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
    print("Blacklist: " + str(blacklistList))
    print(serverData)
    print('------')
    await bot.change_presence(game=discord.Game(name='n!help for help'))
    await bot.send_message(bot.get_channel("318465643420712962"), "**Bot Online**")


# *****************************************************************************************************************
#  Admin Commands
# *****************************************************************************************************************

# Saves all the data and terminates the bot
@bot.command(pass_context = True, aliases=["off"])
@is_necro()
async def kill(cont):
    with open("data/userdata.csv","w",newline="") as csvfile:
        Awriter = csv.writer(csvfile)
        for x in userData:
            warningList = ",".join(userData[x]["warnings"])
            Awriter.writerow([x,userData[x]["money"],userData[x]["daily"],userData[x]["title"],userData[x]["exp"],userData[x]["perms"],warningList])

    with open("data/setting.csv","w",newline="") as csvfile:
        Awriter = csv.writer(csvfile)
        Awriter.writerow(blacklistList)
        Awriter.writerow(['Server Name','Server','Mute Role','Automod Channel','Welcome Channel',"Self Roles","Automod Ignore","Commands Ignore","Welcome Message","Goodbye Message"])
        for x in serverData:
            selfRolesList = ",".join(serverData[x]["selfRoles"])
            automodList = ",".join(serverData[x]["ignoreAutomod"])
            commandList = ",".join(serverData[x]["ignoreCommand"])
            Awriter.writerow([bot.get_server(x).name,x,serverData[x]["mute"],serverData[x]["automod"],serverData[x]["welcome-channel"],selfRolesList,commandList,automodList,serverData[x]["welcome"],serverData[x]["goodbye"]])

    await bot.send_message(bot.get_channel("318465643420712962"), "**Bot Offline**")
    await bot.logout()

# Used to add or subtract money from user accounts
@bot.command(pass_context = True)
@has_perms(6)
async def add(cont, arg0 : discord.Member,*, arg1 : str):
    user = arg0.id
    s = str(userData[user]["money"]) + arg1
    try:
        operation = simple_eval(s)
        userData[user]["money"] = abs(int(operation))
        await bot.say(":atm: | **"+ arg0.name + "'s** balance is now **"+str(userData[user]["money"])+ "** :euro:")
    except (NameError,SyntaxError):
        await bot.say(":negative_squared_cross_mark: | Operation no recognized.")

# Set the stats for individula users that might have slipped through the join system and the setAll command
@bot.command(pass_context = True)
@has_perms(2)
async def setstats(cont, arg0 : discord.Member):
        await default_stats(arg0, cont.message.server)
        await bot.say("Stats set for user")

# set the stats for all the users on the server the message was issued from
@bot.command(pass_context = True)
@has_perms(6)
async def setall(cont):
    membList = cont.message.server.members
    for x in membList:
        await default_stats(x, cont.message.server)

    await bot.say("Stats sets for users")

# set a permission level for a user, permission is only set if user issuing the commands has a higher level than they are issuing and have more than 4
@bot.command(pass_context = True)
async def perms(cont, arg0 : discord.Member, arg1 : int):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4 and userData[cont.message.author.id]["perms"][cont.message.server.id] > arg1:
        userData[arg0.id]["perms"][cont.message.server.id] = arg1
        await bot.say("All good to go, **"+ arg0.name + "** now has permission level **"+ str(arg1) + "**")
    elif userData[cont.message.author.id]["perms"][cont.message.server.id] <= arg1:
        await bot.say(":negative_squared_cross_mark: | You do not have the required NecroBot permission to grant this permission level")
    else:
        await bot.say("::negative_squared_cross_mark: | You do not have the required NecroBot permissions to use this command.")

# mutes a user indefinitely or with a timer
@bot.command(pass_context = True)
@has_perms(2)
async def mute(cont, arg0 : discord.Member, *arg1 : int):
    role = discord.utils.get(cont.message.server.roles, name=serverData[cont.message.server.id]["mute"])
    if role not in arg0.roles and userData[cont.message.author.id]["perms"][cont.message.server.id] > userData[arg0.id]["perms"][cont.message.server.id]:
        await bot.add_roles(arg0, role)
        await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** has been muted".format(arg0.display_name))
    else:
        await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** is already muted or cannot be muted".format(arg0.display_name))
        return

    if arg1:
        await asyncio.sleep(arg1[0])
        if role in arg0.roles:
            await bot.remove_roles(arg0, role)
            await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** has been automatically unmuted".format(arg0.display_name))

# unmutes user
@bot.command(pass_context = True)
@has_perms(2)
async def unmute(cont, arg0 : discord.Member):
    role = discord.utils.get(cont.message.server.roles, name=serverData[cont.message.server.id]["mute"])
    if role in arg0.roles and userData[cont.message.author.id]["perms"][cont.message.server.id] > userData[arg0.id]["perms"][cont.message.server.id]:
        await bot.remove_roles(arg0, role)
        await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** has been unmuted".format(arg0.display_name))
    else:
        await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** is not muted or cannot be unmuted".format(arg0.display_name))

# disable/enable autmoderation for users and channels
@bot.group(pass_context = True)
@has_perms(4)
async def automod(cont):
    if cont.invoked_subcommand is None:
        myList = []
        for x in serverData[cont.message.server.id]["ignoreAutomod"]:
            try:
                myList.append("C: "+bot.get_channel(x).name)
            except AttributeError:
                try:
                    myList.append("U: "+cont.message.server.get_member(x).name)
                except AttributeError:
                    pass

        await bot.say("Channels(**C**) and Users(**U**) ignored by auto moderation: ``` "+str(myList)+" ```")

@automod.command(pass_context = True, name="add")
async def automod_add(cont, *, arg0):
    myList = allmentions(cont, arg0)
    for x in myList:
        if x.id not in serverData[cont.message.server.id]["ignoreAutomod"]:
            serverData[cont.message.server.id]["ignoreAutomod"].append(x.id)
            await bot.say("**"+x.name+"** will be ignored by the bot's automoderation.")
        else:
            await bot.say("**"+x.name+"** is already ignored.")

@automod.command(pass_context = True, name="del")
async def automod_del(cont, *, arg0):
    myList = allmentions(cont, arg0)
    for x in myList:
        if x.id in serverData[cont.message.server.id]["ignoreAutomod"]:
            serverData[cont.message.server.id]["ignoreAutomod"].remove(x.id)
            await bot.say("**"+x.name+"** will no longer be ignored by the bot's automoderation.")
        else:
            await bot.say("**"+x.name+"** is not ignored.")

# enable/disable commands for users and channels
@bot.group(pass_context=True)
@has_perms(4)
async def ignore(cont):
    if cont.invoked_subcommand is None:
        myList = []
        for x in serverData[cont.message.server.id]["ignoreCommand"]:
            try:
                myList.append("C: "+bot.get_channel(x).name)
            except AttributeError:
                try:
                    myList.append("U: "+cont.message.server.get_member(x).name)
                except AttributeError:
                    pass

        await bot.say("Channels(**C**) and Users(**U**) ignored by NecroBot: ``` "+str(myList)+" ```")

@ignore.command(pass_context = True, name="add")
async def ignore_add(cont, *, arg0):
    myList = allmentions(cont, arg0)
    for x in myList:
        if x.id not in serverData[cont.message.server.id]["ignoreCommand"]:
            serverData[cont.message.server.id]["ignoreCommand"].append(x.id)
            await bot.say("**"+x.name+"** will be ignored by the bot.")
        else:
            await bot.say("**"+x.name+"** is already ignored.")

@ignore.command(pass_context = True, name="del")
async def ignore_del(cont, *, arg0):
    myList = allmentions(cont, arg0)
    for x in myList:
        if x.id in serverData[cont.message.server.id]["ignoreCommand"]:
            serverData[cont.message.server.id]["ignoreCommand"].remove(x.id)
            await bot.say("**"+x.name+"** will no longer be ignored by the bot.")
        else:
            await bot.say("**"+x.name+"** is not ignored.")

# sends arg1 to the channel with id arg0
@bot.command(pass_context = True)
async def speak(cont, arg0,*, arg1,):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4 and userData[cont.message.author.id]["perms"][bot.get_channel(arg0).server.id] >= 4:
        await bot.send_message(bot.get_channel(arg0), ":loudspeaker: | "+arg1)
    elif userData[cont.message.author.id]["perms"][bot.get_channel(arg0).server.id] < 4:
        await bot.say(":negative_squared_cross_mark: | You do not have the required NecroBot permissions on the server you're trying to send the message to.")
    else:
        await bot.say(":negative_squared_cross_mark: | You do not have the required NecroBot permissions to use this command.")

# pm a user and awaits for a user reply
@bot.command(pass_context = True)
@has_perms(6)
async def pm(cont, arg0,*,arg1):
    for x in bot.get_all_members():
        if x.id == arg0:
            user = x

    send = await bot.send_message(user, arg1 + "\n*You have 5 minutes to reply to the message*")
    await bot.say("Message sent")
    msg = await bot.wait_for_message(author=user, channel=send.channel, timeout=300)
    await bot.send_message(cont.message.channel, ":speech_left: | **User: "+ str(msg.author) + "** said :**" +msg.content+"**")

# Add a warning to the user's warning list
@bot.group(pass_context=True)
async def warn(cont):
    if cont.invoked_subcommand is None:
        await bot.say("Please pass a valid subcommand")

@warn.command(pass_context=True, name="add")
@has_perms(1)
async def warn_add(cont, arg0 : discord.Member, *, arg1):
    await bot.say("Warning: **\"" + arg1 + "\"** added to warning list of user " + arg0.display_name)
    userData[arg0.id]["warnings"].append(arg1 + " by " + str(cont.message.author) + " on server " + cont.message.server.name)
    await bot.send_message(arg0, "You have been warned on " + cont.message.server.name + ", the warning is: \n" + arg1)

@warn.command(pass_context=True, name="del")
@has_perms(3)
async def warn_del(cont, arg0 : discord.Member, arg1 : int):
    await bot.say("Warning position: **\"" + userData[arg0.id]["warnings"][arg1 - 1] + "\"** removed from warning list of user " + arg0.display_name)
    userData[arg0.id]["warnings"].pop(arg1 - 1)

# removes a certain number of messages
@bot.command(pass_context = True)
@commands.cooldown(1, 10, BucketType.channel)
@has_perms(5)
async def purge(cont, arg0 : int):
    await bot.purge_from(bot.get_channel(cont.message.channel.id), limit=arg0+1)
    message = await bot.say(":wastebasket: | **" + str(arg0) + "** messages purged.")
    await asyncio.sleep(5)
    await bot.delete_message(message)

# blacklists a user which means that if they join any server with necrobot they'll be banned
@bot.command(pass_context = True)
@has_perms(6)
async def blacklist(cont, arg0 : discord.Member):
    blacklistList.append(arg0.id)
    await bot.ban(arg0, delete_message_days=7)
    await bot.say("User " + arg0.name + " has been blacklisted")

# set roles
@bot.command(pass_context = True)
@has_perms(5)
async def setroles(cont):
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

# locks someone in a voice chat, everytime they leave that voice chat they will be moved to it
@bot.command(pass_context = True)
@has_perms(3)
async def lock(cont, arg0 : discord.Member, *arg1):
    v_channel = arg0.voice_channel

    if arg0.id in lockedList:
        lockedList.remove(arg0.id)
        await bot.say("User no longer locked in channel **"+ bot.get_channel(userData[arg0.id]['locked']).name + "**")
        userData[arg0.id]["locked"] = ""
    else:
        userData[arg0.id]["locked"] = v_channel.id
        lockedList.append(arg0.id)
        await bot.say("User locked in channel **"+ v_channel.name + "**")

# changes user nickname
@bot.command(pass_context = True)
@has_perms(3)
async def nick(cont, arg0 : discord.Member,*, arg1):
    try:
        await bot.change_nickname(arg0, arg1)
        await bot.say("User renamed to " + arg1)
    except discord.errors.Forbidden:
        await bot.say("You cannot change the nickname of that user.")

#edit list of self assignable roles
@bot.group(pass_context=True)
@has_perms(4)
async def giveme_roles(cont):
    if cont.invoked_subcommand is None:
        await bot.say("Please pass a valid subcommand (add or del)")

@giveme_roles.command(pass_context=True, name="add")
async def giveme_roles_add(cont, *, arg0):
    if not discord.utils.get(cont.message.server.roles, name=arg0) is None:
        serverData[cont.message.server.id]["selfRoles"].append(arg0)
        await bot.say("Added role " + arg0 + " to list of self assignable roles.")
    else:
        await bot.say("No such role exists")

@giveme_roles.command(pass_context = True, name="del")
async def giveme_roles_del(cont, *, arg0):
    if arg0 in serverData[cont.message.server.id]["selfRoles"]:
        serverData[cont.message.server.id]["selfRoles"].remove(arg0)
        await bot.say("Role " + arg0 + " removed from self assignable roles")
    else:
        await bot.say("Role not in self assignable list")

@bot.command(pass_context = True)
@is_necro()
async def test(cont, arg0):
    for x in bot.get_all_members():
        if x.id == arg0:
            await bot.say(x.name + "#" + str(x.discriminator))

@bot.command(pass_context = True)
@is_necro()
async def invites(cont):
    for server in bot.servers:
        try:
            invite = await bot.create_invite(server)
            await bot.say("Server: " + server.name + " - " + invite.url)
        except:
            await bot.say("I don't have the necessary permissions on " + server.name)

@bot.command(pass_context=True)
@is_necro()
async def debug(cont, *, arg0 : str):
    """Evaluates code."""
    code = arg0.strip('` ')
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

@bot.group(pass_context = True)
@has_perms(4)
async def settings(cont):
    if cont.invoked_subcommand is None:
        await bot.say("Please pass in a valid subcommand. (welcome, welcome-channel, goodbye, mute, automod)")

@settings.command(pass_context = True, name="mute")
async def settings_mute(cont, *, arg0):
    if not discord.utils.get(cont.message.server.roles, name=arg0) is None:
        await bot.say("Okay, the mute role for your server will be " + arg0)
        serverData[cont.message.server.id]["mute"] = arg0
    else:
        await bot.say("No such role")

@settings.command(pass_context = True, name="welcome-channel")
async def settings_welcome_channel(cont, arg0 : discord.Channel):
    await bot.say("Okay, users will get their welcome message in " + arg0.name + " from now on.")
    serverData[cont.message.server.id]["welcome-channel"] = arg0.id

@settings.command(pass_context = True, name="automod-channel")
async def settings_automod_channel(cont, arg0 : discord.Channel):
    await bot.say("Okay, all automoderation messages will be posted in " + arg0.name + " from now on.")
    serverData[cont.message.server.id]["automod"] = arg0.id

@settings.command(pass_context = True, name="welcome")
async def settings_welcome(cont, *, arg0):
    arg0 = arg0.replace("\\","")
    await bot.say("Your server's welcome message will be: \n" + arg0)
    serverData[cont.message.server.id]["welcome"] = arg0

@settings.command(pass_context = True, name="goodbye")
async def settings_goodbye(cont, *, arg0):
    arg0 = arg0.replace("\\","")
    await bot.say("Your server's goodbye message will be: \n" + arg0)
    serverData[cont.message.server.id]["goodbye"] = arg0

# *****************************************************************************************************************
#  Regular Commands
# *****************************************************************************************************************

# ****************** USER DEPENDENT COMMANDS ****************** #
#prints user's necrobot balance
@bot.command(pass_context = True)
@commands.cooldown(3, 10, BucketType.user)
async def balance(cont, *arg0 : discord.Member):
    if arg0:
        user = arg0[0]
        await bot.say(":atm: | **"+ str(user.name) +"** has **"+ str(userData[user.id]["money"]) +"** :euro:")
    else:
        await bot.say(":atm: | **"+ str(cont.message.author.name) +"** you have **"+ str(userData[cont.message.author.id]["money"])+"** :euro:")

#allow user to claim daily necrobot bonus
@bot.command(pass_context = True)
@commands.cooldown(1, 5, BucketType.user)
async def claim(cont):
    aDay = str(d.datetime.today().day)
    if aDay != userData[cont.message.author.id]["daily"]:
        await bot.say(":m: | You have received your daily **200** :euro:")
        userData[cont.message.author.id]["money"] += 200
        userData[cont.message.author.id]["daily"] = aDay
    else:
        await bot.say(":negative_squared_cross_mark: | You have already claimed your daily today, come back tomorrow.")

#prints a rich embed of the user's server and necrobot info
@bot.command(pass_context = True)
@commands.cooldown(3, 5, BucketType.user)
async def info(cont, *arg0 : discord.Member):
    if arg0:
        user = arg0[0]
    else:
        user = cont.message.author

    serverID = cont.message.server.id
    embed = discord.Embed(title="__**" + user.display_name + "**__", colour=discord.Colour(0x277b0), description="**Title**: " + userData[user.id]["title"])
    embed.set_thumbnail(url=user.avatar_url.replace("webp","jpg"))
    embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

    embed.add_field(name="**Date Created**", value=user.created_at.strftime("%d - %B - %Y %H:%M"))
    embed.add_field(name="**Date Joined**", value=user.joined_at.strftime("%d - %B - %Y %H:%M"), inline=True)

    embed.add_field(name="**User Name**", value=user.name + "#" + user.discriminator)
    embed.add_field(name="**Top Role**", value=user.top_role.name, inline=True)

    embed.add_field(name="**NecroBot Data**", value="__Permission Level__ - " + permsName[userData[user.id]["perms"][serverID]] + "   \n__Balance__ - " + str(userData[user.id]["money"]) + " :euro:   \n__Experience__  - " + str(userData[user.id]["exp"]))
    embed.add_field(name="Warning List", value=userData[user.id]["warnings"])

    await bot.say(embed=embed)


# ****************** STANDALONE COMMANDS ******************* #

#allows user to assign themselves certain roles (not tested)
@bot.command(pass_context = True)
@commands.cooldown(4, 3, BucketType.user)
async def giveme(cont,*, arg0 : str):
    if arg0 == "info":
        await bot.say("List of Self Assignable Roles:" + "\n- ".join(serverData[cont.message.server.id]["selfRoles"]))
    else:
        if arg0 in serverData[cont.message.server.id]["selfRoles"]:
            role = discord.utils.get(cont.message.server.roles, name=arg0)
            await bot.add_roles(cont.message.author, role)
            await bot.say("Role " + role.name + " added.")

        else:
            await bot.say("You cannot assign yourself that role.")


    ##STANDALONE COMMANDS HAVE ALL BEEN SHIFTED TO RINGS##
        #moddb
        #cat           #dog
        #play
        #dadjoke       #riddle        #tarot        #rr        #lotrfact
        #support       #invite        #h
        #edain         #lotr          #wiki
        #ping          #serverinfo    #calc

# *****************************************************************************************************************
#  Moderation Features
# *****************************************************************************************************************
@bot.event
async def on_command_error(error, cont):
    channel = cont.message.channel
    if isinstance(error, commands.MissingRequiredArgument):
        await bot.send_message(channel, "Missing required argument, check the help guide with `n!h [command]`")
    elif isinstance(error, commands.CheckFailure):
        await bot.send_message(channel, ":negative_squared_cross_mark: | You do not have the required NecroBot permissions to use this command.")
    elif isinstance(error, commands.CommandOnCooldown):
        await bot.send_message(channel, "This command is on cooldown, retry after **{0:.0f}** seconds".format(error.retry_after))
    elif isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(channel, "This command cannot be used in private messages.")
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(channel, "This command is disabled and cannot be used for now.")
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

    await bot.send_message(server.default_channel, "Stats sets for users")
    serverData[server.id] = {"mute":"","automod":"","welcome-channel":"", "selfRoles":[],"ignoreCommand":[],"ignoreAutomod":[],"welcome":"","goodbye":""}
    invite = await bot.create_invite(server)
    await bot.send_message(bot.get_channel("241942232867799040"),"I was just invited in the server: " + server.name + ". Join me: " + invite.url)

#automod
@bot.event
async def on_message_delete(message):
    try:
        ChannelId = serverData[message.server.id]["automod"]
    except KeyError:
        ChannelId = "318828760331845634"

    if message.author.id not in serverData[message.server.id]["ignoreAutomod"] and message.channel.id not in serverData[message.server.id]["ignoreAutomod"]:
        fmt = '**Auto Moderation: Deletion Detected!**\n Message by **{0.author}** was deleted, it contained: ```{0.content} ```'
        await bot.send_message(bot.get_channel(ChannelId), fmt.format(message))

#automod
@bot.event
async def on_message_edit(before, after):
    try:
        ChannelId = serverData[before.server.id]["automod"]
    except KeyError:
        ChannelId = "318828760331845634"

    if before.author.id not in serverData[before.server.id]["ignoreAutomod"] and before.channel.id not in serverData[before.server.id]["ignoreAutomod"]:
        fmt = '**Auto Moderation: Edition Detected!**\n{0.author} edited their message: ```{0.content}\n{1.content} ```'
        await bot.send_message(bot.get_channel(ChannelId), fmt.format(before, after))

#welcomes and set stats
@bot.event
async def on_member_join(member):
    if member.id in blacklistList:
        await bot.ban(member, delete_message_days=0)

    server = member.server
    if serverData[member.server.id]["welcome-channel"] != "":
        channel = bot.get_channel(serverData[member.server.id]["welcome-channel"])
    else:
        channel = member.server.default_channel

    if serverData[member.server.id]["welcome"] != "":
        message = serverData[member.server.id]["welcome"]
    else:
        message = 'Welcome {member} to {server}!'

    server = member.server
    await bot.send_message(channel, message.format(member=member.mention, server=server.name))
    await default_stats(member, server)

#says goodbye and resets perms level if less than NecroBot Admin
@bot.event
async def on_member_remove(member):
    if serverData[member.server.id]["welcome-channel"] != "":
        channel = bot.get_channel(serverData[member.server.id]["welcome-channel"])
    else:
        channel = member.server.default_channel

    if serverData[member.server.id]["goodbye"] != "":
        message = serverData[member.server.id]["goodbye"]
    else:
        message = 'Leaving so soon? We\'ll miss you, {member}!'

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

    if message.author.bot:
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
                    command = message.content.split()[1]
                    try:
                        reply = random.choice(starterList) + " Ah yes, the **" + command +"** command. " + replyDict[command]
                    except KeyError:
                        reply = "Wait... That's not one of my commands."
                    await bot.send_message(message.channel, reply)

                logit(message)
                await bot.process_commands(message)
    elif message.content.startswith(tuple(prefixes)) and message.channel.is_private:
        await bot.send_message(message.channel, "Sorry, due to the way the bot works you cannot use commands in DMs")

bot.loop.create_task(hourly_save())
token = open("data/token.txt", "r").read()
bot.run(token)
