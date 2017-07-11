# NecroBot: The ultimate moderation bot with some fun commands to keep everybody entertained

# import statements for basic discord bot functionalities
import discord
from discord.ext import commands

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

bot = commands.Bot(command_prefix='n!')
userData = dict()
serverData = dict()
lockedList = list()
extensions = ["animals","social","wiki","moddb","support"]

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
    ignoreCommandList = list(next(reader))
    ignoreAutomodList = list(next(reader))
    blacklistList = list(next(reader))
    line = next(reader)
    for row in reader:
        serverData[row[1]] = {"mute":row[2],"automod":row[3],"welcome":row[4]}

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print("Ignore commands from: "+ str(ignoreCommandList))
    print("Ignore automod violations from: "+ str(ignoreAutomodList))
    print("Blacklist: " + str(blacklistList))
    print(serverData)
    print('------')
    await bot.change_presence(game=discord.Game(name='n!h for help'))
    await bot.send_message(bot.get_channel("318465643420712962"), "**Bot Online**")

# *****************************************************************************************************************
#  Internal Function
# *****************************************************************************************************************

def logit(message):
    log = open("data/logfile.txt","a+")
    localtime = str("\n" + t.asctime(t.localtime(t.time())) + ": ")
    msg = str(localtime + str(message.author) + " used " + message.content)
    log.write(msg)
    log.close()

def default_stats(ID):
    userData[ID] = {'money': 200, 'daily': '32','title':'','exp':0,'perms':{},'warnings':[],'lastMessage':'','lastMessageTime':0,'locked':''}

# *****************************************************************************************************************
#  Purge Functions
# *****************************************************************************************************************
def is_bot(m):
    return m.author == bot.user

def is_user(m):
    return m.author.id == m.mentions[0].id 


# *****************************************************************************************************************
#  Admin Commands
# *****************************************************************************************************************

# Saves all the data and terminates the bot
@bot.command(pass_context = True)
async def kill(cont):
    if cont.message.author.id == "241942232867799040":
        with open("data/userdata.csv","w",newline="") as csvfile:
            Awriter = csv.writer(csvfile)
            for x in userData:
                warningList = ",".join(userData[x]["warnings"])
                Awriter.writerow([x,userData[x]["money"],userData[x]["daily"],userData[x]["title"],userData[x]["exp"],userData[x]["perms"],warningList])

        with open("data/setting.csv","w",newline="") as csvfile:
            Awriter = csv.writer(csvfile)
            Awriter.writerow(ignoreCommandList)
            Awriter.writerow(ignoreAutomodList)
            Awriter.writerow(blacklistList)
            Awriter.writerow(['Server Name','Server','Mute Role','Autmod Channel','Welcome Channel'])
            for x in serverData:
                Awriter.writerow([bot.get_server(x).name,x,serverData[x]["mute"],serverData[x]["automod"],serverData[x]["welcome"]])

        await bot.send_message(bot.get_channel("318465643420712962"), "**Bot Offline**")
        sys.exit()
    else:
        await bot.say(":negative_squared_cross_mark: | You do not have permission to kill the bot. Your attempt has been logged.")

# Used to add or subtract money from user accounts
@bot.command(pass_context = True)
async def add(cont, arg0 : discord.Member,*, arg1 : str):
    user = arg0.id
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 6:
        s = str(userData[user]["money"]) + arg1
        try:
            operation = eval(s)
            userData[user]["money"] = abs(int(operation))
            await bot.say(":atm: | **"+ arg0.name + "'s** balance is now **"+str(userData[user]["money"])+ "** :euro:")
        except (NameError,SyntaxError):
            await bot.say(":negative_squared_cross_mark: | Operation no recognized.")
    else:
        await bot.say(":negative_squared_cross_mark: | You do not have the permission to use this command.")

# Set the stats for individula users that might have slipped through the join system and the setAll command
@bot.command(pass_context = True)
async def setstats(cont,* arg0 : discord.Member):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 2 and len(arg0) > 0:
        for x in arg0:
            if x.id not in userData:
                default_stats(x.id)

            if cont.message.server.id not in userData[x.id]["perms"]:
                userData[x.id]["perms"][cont.message.server.id] = 0

            await bot.say("Stats set for user")
    elif len(arg0) < 1:
        await bot.say(":negative_squared_cross_mark: | Please provide at least one user")
    else:
        await bot.say(":negative_squared_cross_mark: | You do not have sufficent permission to access this command.")

# set the stats for all the users on the server the message was issued from
@bot.command(pass_context = True)
async def setall(cont):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 6:
        membList = cont.message.server.members
        for x in membList:
            if x.id not in userData:
                default_stats(x.id)

            if cont.message.server.id not in userData[x.id]["perms"]:
                userData[x.id]["perms"][cont.message.server.id] = 0
                
        await bot.say("Stats sets for users")

# set a permission level for a user, permission is only set if user issuing the commands has a higher level than they are issuing and have more than 4
@bot.command(pass_context = True)
async def perms(cont, arg0 : discord.Member, arg1 : int):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4 and userData[cont.message.author.id]["perms"][cont.message.server.id] > arg1:
        userData[arg0.id]["perms"][cont.message.server.id] = arg1
        await bot.say("All good to go, **"+ arg0.name + "** now has permission level **"+ str(arg1) + "**")
    elif userData[cont.message.author.id]["perms"][cont.message.server.id] <= arg1:
        await bot.say(":negative_squared_cross_mark: | You do not have sufficient permissions to grant this permission level")
    else:
        await bot.say(":negative_squared_cross_mark: | You do not have sufficient permissions to grant permission levels")

# mutes a user indefinitely or with a timer
@bot.command(pass_context = True)
async def mute(cont, arg0):
    role = discord.utils.get(cont.message.server.roles, name=serverData[cont.message.server.id]["mute"])

    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 2:
        for x in cont.message.mentions:
            if role not in x.roles and userData[cont.message.author.id]["perms"][cont.message.server.id] > userData[x.id]["perms"][cont.message.server.id]:
                await bot.add_roles(x, role)
                await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** has been muted".format(x))
            else:
                await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** is already muted or cannot be muted".format(x))

        try:
            await asyncio.sleep(float(arg0))
            for x in cont.message.mentions:
                if role in x.roles:
                    await bot.remove_roles(x, role)
                    await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** has been automatically unmuted".format(x))
        except ValueError:
            pass
    else:
        await bot.say("You don't have the neccessary permissions to mute this user.")

# unmutes user
@bot.command(pass_context = True)
async def unmute(cont, arg0):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 2:
        role = discord.utils.get(cont.message.server.roles, name=serverData[cont.message.server.id]["mute"])
        for x in cont.message.mentions:
            if role in x.roles and userData[cont.message.author.id]["perms"][cont.message.server.id] > userData[x.id]["perms"][cont.message.server.id]:
                await bot.remove_roles(x, role)
                await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** has been unmuted".format(x))
            else:
                await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** is not muted or cannot be unmuted".format(x))
    else:
        await bot.say("You don't have the neccessary permissions to unmute a user.")

# disable/enable autmoderation for users and channels
@bot.command(pass_context = True)
async def automod(cont, arg0):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 5:
        myList = []
        for x in cont.message.mentions:
            myList.append(x)
        for x in cont.message.channel_mentions:
            myList.append(x)

        if arg0 == "add":
            for x in myList:
                if x.id not in ignoreAutomodList:
                    ignoreAutomodList.append(x.id)
                    await bot.say("**"+x.name+"** will be ignored by the bot's automoderation.")
                else:
                    await bot.say("**"+x.name+"** is already ignored.")
        elif arg0 == "del":
            for x in myList:
                if x.id in ignoreAutomodList:
                    ignoreAutomodList.remove(x.id)
                    await bot.say("**"+x.name+"** will no longer be ignored by the bot's automoderation.")
                else:
                    await bot.say("**"+x.name+"** is not ignored.")
        elif arg0 is None:
            myList1 = []
            for x in ignoreAutomodList:
                try:
                    myList1.append("C: "+bot.get_channel(x).name)
                except AttributeError:
                    myList1.append("U: "+bot.get_server(cont.message.server.id).get_member(x).name)

            await bot.say("Channels(**C**) and Users(**U**) ignored by auto moderation: ``` "+str(myList1)+" ```")
        else:
            await bot.say("Sub-command not recognized, use either `del` or `add`")
    else:
        await bot.say("You do not have permissions to edit the autmoderation list.")

# enable/disable commands for users and channels
@bot.command(pass_context = True)   
async def ignore(cont, arg0):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4:
        myList = []
        for x in cont.message.mentions:
            myList.append(x)
        for x in cont.message.channel_mentions:
            myList.append(x)

        if arg0 == "add":
            for x in myList:
                if x.id not in ignoreCommandList:
                    ignoreCommandList.append(x.id)
                    await bot.say("**"+x.name+"** will be ignored by the bot.")
                else:
                    await bot.say("**"+x.name+"** is already ignored.")
        elif arg0 == "del":
            for x in myList:
                if x.id in ignoreCommandList:
                    ignoreCommandList.remove(x.id)
                    await bot.say("**"+x.name+"** will no longer be ignored by the bot.")
                else:
                    await bot.say("**"+x.name+"** is not ignored.")
        elif arg0 is None:
            myList2 = []
            for x in ignoreCommandList:
                try:
                    myList2.append("C: "+bot.get_channel(x).name)
                except AttributeError:
                    myList2.append("U: "+bot.get_server(cont.message.server.id).get_member(x).name)

            await bot.say("Channels(**C**) and Users(**U**) ignored by NecroBot: ``` "+str(myList2)+" ```")
        else:
            await bot.say("Sub-command not recognized, use either `del`, `add` or leave it blank to show the list of ignored users/channels")
    else:
        await bot.say("You do not have permissions to edit the commands ignore list.")

# sends arg1 to the channel with id arg0
@bot.command(pass_context = True)
async def speak(cont, arg0,*, arg1,):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4 and userData[cont.message.author.id]["perms"][bot.get_channel(arg0).server.id] >= 4:
        await bot.send_message(bot.get_channel(arg0), ":loudspeaker: | "+arg1)
    elif userData[cont.message.author.id]["perms"][bot.get_channel(arg0).server.id] < 4:
        await bot.say("You do not have the required permission on the server you're trying to send the message to.")
    else:
        await bot.say("You do not have the required permission to use this command.")

# pm a user and awaits for a user reply
@bot.command(pass_context = True)
async def pm(cont, arg0,*,arg1):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 6:
        user = bot.get_server(cont.message.server.id).get_member(arg0)
        await bot.start_private_message(user)
        await bot.send_message(user, arg1)
        await bot.say("Message sent")

        msg = await bot.wait_for_message(author=user, channel=bot.get_channel(user.id))
        await bot.send_message(bot.get_channel("318465643420712962"), ":speech_left: | **User: "+ str(msg.author) + "** said :**" +msg.content+"**")

# Add a warning to the user's warning list
@bot.command(pass_context = True)
async def warn(cont, arg0, arg1,*, arg2):
    if arg0 == "del":
        if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 3:
            await bot.say("Warning position: **\"" + userData[cont.message.mentions[0].id]["warnings"][int(arg2)] + "\"** removed from warning list of user " + str(cont.message.mentions[0].name))
            userData[cont.message.mentions[0].id]["warnings"].pop(int(arg2))
        else:
            await bot.say("You don't have the necessary permissions to remove warnings.")
    elif arg0 == "add":
        if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 1:
            await bot.say("Warning: **\"" + str(arg2) + "\"** added from warning list of user " + str(cont.message.mentions[0].name))
            userData[cont.message.mentions[0].id]["warnings"].append(arg2 + " by " + cont.message.author + " on server " + cont.message.server.name)
        else:
            await bot.say("You don't have the permission to add warnings.")
    else:
        await bot.say("Argument not recognized, you can either add a warning with `n!warn add [@User] [message]` or remove a warning with `n!warn del [@User] [warning position]`")

# removes a certain number of messages
@bot.command(pass_context = True)
async def purge(cont, arg0 : int):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 5:
        await bot.purge_from(bot.get_channel(cont.message.channel.id), limit=arg0+1)
        message = await bot.say(":wastebasket: | **" + str(arg0) + "** messages purged.")
        await asyncio.sleep(5)
        await bot.delete_message(message)
    else:
        await bot.say("You don't have the neccessary permissions to purge messages  .")

# blacklists a user which means that if they join any server with necrobot they'll be banned
@bot.command(pass_context = True)
async def blacklist(cont, arg0 : discord.Member):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 6:
        blacklistList.append(arg0.id)
        await bot.ban(arg0, delete_message_days=7)
        await bot.say("User " + arg0.name + " has been blacklisted")

# set roles
@bot.command(pass_context = True)
async def setroles(cont):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 5:
        for x in roleList:
            new_role = await bot.create_role(cont.message.server, name=x[0], colour=x[1], mentionable=True)

        await bot.say("**Roles created**")

        for x in cont.message.server.members:
            role = userData[x.id]["perms"][cont.message.server.id]-1
            await bot.add_roles(x, discord.utils.get(cont.message.server.roles, name=roleList[role][0]))

        await bot.say("**Roles assigned**")
    else:
        await boy.say("You do not have the necessary permission level to set the NecroBot roles for this server")

# locks someone in a voice chat, everytime they leave that voice chat they will be moved to it
@bot.command(pass_context = True)
async def lock(cont, arg0 : discord.Member, *arg1):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 3:
        if arg1:
            v_channel  = cont.message.channel_mentions[0].id
        else:
            v_channel = arg0.voice_channel.id

        if arg0.id in lockedList:
            lockedList.remove(arg0.id)
            await bot.say("User no longer locked in channel **"+ bot.get_channel(userData[arg0.id]['locked'].name) + "**")
            userData[arg0.id]['locked'] = ''
        else:
            userData[arg0.id]["locked"] = v_channel
            lockedList.append(arg0.id)
            await bot.say("User locked in channel **"+bot.get_channel(userData[arg0.id]['locked'].name) + "**")
    else:
        await bot.say("You do not have the necessary permissions to lock someone in a voice chat.")

# changes user nickname
@bot.command(pass_context = True)
async def nick(cont, arg0 : discord.Member,*, arg1):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 3:
        try:
            await bot.change_nickname(arg0, arg1)
        except discord.errors.Forbidden:
            await bot.say("You cannot change the nickname of that user.")
    else:
        await bot.say("You do not have sufficient permissions to change a nickname.")


# *****************************************************************************************************************
#  Regular Commands
# *****************************************************************************************************************

# ****************** USER DEPENDENT COMMANDS ****************** # 

@bot.command(pass_context = True)
async def balance(cont, *arg0 : discord.Member):
    if arg0:
        user = arg0[0]
        await bot.say(":atm: | **"+ str(user.name) +"** has **"+ str(userData[user.id]["money"]) +"** :euro:")
    else:
        await bot.say(":atm: | **"+ str(cont.message.author.name) +"** you have **"+ str(userData[cont.message.author.id]["money"])+"** :euro:")

@bot.command(pass_context = True)
async def claim(cont):
    aDay = str(d.datetime.today().day)
    if aDay != userData[cont.message.author.id]["daily"]:
        await bot.say(":m: | You have received your daily **200** :euro:")
        userData[cont.message.author.id]["money"] += 200
        userData[cont.message.author.id]["daily"] = aDay
    else:
        await bot.say(":negative_squared_cross_mark: | You have already claimed your daily today, come back tomorrow.")

@bot.command(pass_context = True)
async def info(cont, *arg0 : discord.Member):
    if arg0:
        user = arg0[0]
    else:
        user = cont.message.author

    serverID = cont.message.server.id
    embed = discord.Embed(title="__**" + user.display_name + "**__", colour=discord.Colour(0x277b0), description="**Title**: " + userData[userID]["title"])
    embed.set_thumbnail(url=user.avatar_url.replace("webp","jpg"))
    embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

    embed.add_field(name="**Date Created**", value=user.created_at.strftime("%d - %B - %Y %H:%M"))
    embed.add_field(name="**Date Joined**", value=user.joined_at.strftime("%d - %B - %Y %H:%M"), inline=True)
    
    embed.add_field(name="**User Name**", value=user.name + "#" + user.discriminator)
    embed.add_field(name="**Top Role**", value=user.top_role.name, inline=True)

    embed.add_field(name="**NecroBot Data**", value="__Permission Level__ - " + permsName[userData[user.id]["perms"][serverID]] + "   \n__Balance__ - " + str(userData[userID]["money"]) + " :euro:   \n__Experience__  - " + str(userData[user.id]["exp"]))
    embed.add_field(name="Warning List", value=userData[user.id]["warnings"])

    await bot.say(embed=embed)

#WIP
@bot.command(pass_context = True)
async def serverinfo(cont):
    server = cont.message.server
    embed = discord.Embed(title="__**" + server.name + "**__", colour=discord.Colour(0x277b0), description="Info on this server")
    embed.set_thumbnail(url=server.icon_url.replace("webp","jpg"))
    embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")
    
    embed.add_field(name="**Date Created**", value=server.created_at.strftime("%d - %B - %Y %H:%M"))
    embed.add_field(name="**Owner**", value=server.owner.name + "#" + server.owner.discriminator, inline=True)

    embed.add_field(name="**Default Channel**", value=server.default_channel)
    embed.add_field(name="**Members**", value=server.member_count, inline=True)

    embed.add_field(name="**Region**", value=server.region)
    embed.add_field(name="**Server ID**", value=server.id, inline=True)

    channelList = [channel.name for channel in server.channels]
    roleList = [role.name for role in server.roles]
    embed.add_field(name="**Channels**", value=str(len(channelList)) + ": " + ", ".join(channelList))
    embed.add_field(name="**Roles**", value=str(len(roleList) - 1) + ": " + ", ".join(roleList[1:]))

    await bot.say(embed=embed)


# ****************** STANDALONE COMMANDS ******************* #

    ##STANDALONE COMMANDS HAVE ALL BEEN SHIFTED TO RINGS##
        #moddb
        #cat           #dog
        #play
        #dadjoke       #riddle        #calc        #tarot        #rr        #lotrfact
        #support       #invite        #h
        #edain         #lotr          #wiki

# *****************************************************************************************************************
#  Moderation Features
# *****************************************************************************************************************

@bot.event
async def on_server_join(server):
    await bot.send_message(server.default_channel, helpVar)

@bot.event
async def on_role_create(role):
    if any([x.name for x in role.server.roles]) == role.name:
        await bot.send_message(role.server.default_channel, "A role with the same name is alread present, are you sure you wish to create another one? Y/N")
        msg = await bot.wait_for_message(channel=role.server.default_channel, timeout=15)
        if msg.content == "N":
            await bot.delete_role(role.server, role)
            await bot.send_message(msg.channel, "Role deleted.")
        else:
            await bot.send_message(msg.channel, "Role created.")

@bot.event
async def on_message_delete(message):
    try:
        ChannelId = serverData[message.server.id]["automod"]
    except KeyError:
        ChannelId = "318828760331845634"

    if message.author.id not in ignoreAutomodList and message.channel.id not in ignoreAutomodList:
        fmt = '**Auto Moderation: Deletion Detected!**\n Message by **{0.author}** was deleted, it contained: ``` {0.content} ```'
        await bot.send_message(bot.get_channel(ChannelId), fmt.format(message))

@bot.event
async def on_message_edit(before, after):
    try:
        ChannelId = serverData[before.server.id]["automod"]
    except KeyError:
        ChannelId = "318828760331845634"

    if before.author.id not in ignoreAutomodList and before.channel.id not in ignoreAutomodList:
        fmt = '**Auto Moderation: Edition Detected!**\n{0.author} edited their message: ``` {1.content}\n{0.content} ```'
        await bot.send_message(bot.get_channel(ChannelId), fmt.format(after, before))

@bot.event
async def on_member_join(member):
    if member.id in blacklistList:
        await bot.ban(member, delete_message_days=0)

    try:
        channel = bot.get_channel(serverData[member.server.id]["welcome"])
    except AttributeError:
        channel = member.server.default_channel

    server = member.server
    await bot.send_message(channel, 'Welcome {0.mention} to {1.name}!'.format(member, server))
    await bot.change_nickname(member, str(member.name))

    if member.id not in userData:
        default_stats(member.id)
    if server.id not in userData[member.id]["perms"]:
        userData[member.id]["perms"][server.id] = 0

@bot.event
async def on_member_remove(member):
    try:
        channel = bot.get_channel(serverData[member.server.id]["welcome"])
    except AttributeError:
        channel = member.server.default_channel

    await bot.send_message(channel,"Leaving us so soon, {0.mention}? We'll miss you...".format(member))

@bot.event
async def on_voice_state_update(before, after):
    if before.id in lockedList:
        await bot.move_member(before, bot.get_channel(userData[before.id]["locked"]))

@bot.event
async def on_message(message):
    userID = message.author.id
    channelID = message.channel.id

    if ((message.content == userData[userID]['lastMessage'] and userData[userID]['lastMessageTime'] > c.timegm(t.gmtime()) + 2) or userData[userID]['lastMessageTime'] > c.timegm(t.gmtime())) and (userID not in ignoreAutomodList and channelID not in ignoreAutomodList) and message.content.startswith("n!") == False:
        try:
            ChannelId = serverData[message.server.id]["automod"]
        except KeyError:
            ChannelId = "318828760331845634"

        await bot.send_message(bot.get_channel(ChannelId), "User: {0.author} spammed message: ``` {0.content} ```".format(message))
        await bot.delete_message(message)
        userData[userID]['lastMessage'] = message.content
        userData[userID]['lastMessageTime'] = int(c.timegm(t.gmtime()) + 1)
    else:
        userData[userID]['lastMessage'] = message.content
        userData[userID]['lastMessageTime'] = int(c.timegm(t.gmtime()) + 1)

        if len(message.content) > 0:
            if message.content[0] != "n!":
                userData[userID]["exp"] += random.randint(1,5)

        if message.content.startswith("<!@317619283377258497>"):
            await bot.send_message(message.channel, replyList[random.randint(0,len(replyList)-1)].format(message.author))

        if (channelID in ignoreCommandList or userID in ignoreCommandList) and message.content.startswith("n!"):
            await bot.send_message(bot.get_channel("318828760331845634"), "User: **{0.author}** attempted to summon bot in channel **{0.channel.name}** with arguments: ``` {0.content} ```".format(message))
            await bot.delete_message(message)
        elif message.content.startswith("n!"):
            logit(message)
            await bot.process_commands(message)

if __name__ == "__main__":
    for extension in extensions:
        try:
            bot.load_extension("rings."+extension)
        except Exception as e:
            exc = '{} : {}'.format(type(e).__name__, e)
            print("Failed to load extension {}\n{}".format(extension.exc))

token = open("data/token.txt", "r").read()
bot.run(token)
