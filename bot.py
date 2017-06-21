import discord
from discord.ext import commands

import csv
import random
import sys
import os
import time as t
import calendar as c
import datetime as d
from var import *
import wikia
import asyncio
import json
import html
import pyglet
import urllib.request
import aiohttp
import async_timeout
import aiofiles


bot = commands.Bot(command_prefix='!')
log = open("data/logfile.txt","a+")
userData = dict()
serverData = dict()
lockedList = list()
selfDel = True

#Role List
roleList = [["User",discord.Colour.default()],["Helper",discord.Colour.teal()],["Moderator",discord.Colour.orange()],["Semi-Admin",discord.Colour.darker_grey()],["Admin",discord.Colour.blue()],["Server Owner",discord.Colour.magenta()],["NecroBot Admin",discord.Colour.dark_green()],["The Bot Smith",discord.Colour.dark_red()]]


#*****************************************************************************************************************
# Initialize
#*****************************************************************************************************************

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
        serverData[row[1]] = {"mute":row[2],"automod":row[3]}

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
    await bot.change_presence(game=discord.Game(name='!h for help'))
    await bot.send_message(bot.get_channel("318465643420712962"), "**Bot Online**")
    # await bot.send_message(bot.get_channel("319640180241727490"), "**Bot Online**")
    # await bot.send_message(bot.get_channel("287420616930492416"), "**Bot Online**")


#*****************************************************************************************************************
# Internal Function
#*****************************************************************************************************************

def close_player(filename):
    os.remove(filename)

def logit(cont, func):
    localtime = str("\n" + t.asctime(t.localtime(t.time())) + ": ")
    msg = str(localtime + str(cont.message.author) + " used !" + func)

    if len(cont.message.content[len(func)+2:]) > 0:
        msg2 = str(" with " + str(cont.message.content[len(func)+2:]))
        log.write(msg + msg2)
    else:
        log.write(msg)


#*****************************************************************************************************************
# Purge Functions
#*****************************************************************************************************************
def is_bot(m):
    return m.author == bot.user

def is_user(m):
    return m.author.id == m.mentions[0].id 


#*****************************************************************************************************************
# Admin Commands
#*****************************************************************************************************************

#Saves all the data and terminates the bot
@bot.command(pass_context = True)
async def kill(cont):
    logit(cont, "kill")
    if cont.message.author.id == "241942232867799040":
        log.close()
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
            Awriter.writerow(['Server Name','Server','Mute Role','Autmod Channel'])
            for x in serverData:
                Awriter.writerow([bot.get_server(x).name,x,serverData[x]["mute"],serverData[x]["automod"]])

        await bot.send_message(bot.get_channel("318465643420712962"), "**Bot Offline**")
        # await bot.send_message(bot.get_channel("319640180241727490"), "**Bot Offline**")
        # await bot.send_message(bot.get_channel("287420616930492416"), "**Bot Offline**")
        sys.exit()
    else:
        await bot.say(":negative_squared_cross_mark: | You do not have permission to kill the bot. Your attempt has been logged.")

#Used to add or subtract money from user accounts
@bot.command(pass_context = True)
async def add(cont, arg0 : str, arg1 : int, arg2 : discord.Member):
    logit(cont,"add")
    user = arg2.id

    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 6:
        if arg0 == "+":
            userData[user]["money"] += arg1
            await bot.say(":atm: | New user balance is **"+str(userData[user]["money"])+ "** :euro:")
        elif arg0 == "-":
            userData[user]["money"] -= arg1
            await bot.say(":atm: | New user balance is **"+str(userData[user]["money"])+ "** :euro:")
        else:
            await bot.say(":negative_squared_cross_mark: | Operation no recognized.")
    else:
        await bot.say(":negative_squared_cross_mark: | You do not have the permission to use this command.")

#Set the stats for individula users that might have slipped through the join system and the setAll command
@bot.command(pass_context = True)
async def setStats(cont, arg0 : discord.Member):
    logit(cont,"setStats")
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 2:
        if arg0.id not in userData:
            userData[arg0.id] = {'money': 200, 'daily': '32','title':'','exp':0,'perms':{},'warnings':[],'lastMessage':'','lastMessageTime':0,'locked':''}
        if cont.message.server.id not in userData[cont.message.author.id]["perms"]:
            userData[arg0.id]["perms"][cont.message.server.id] = 0
        await bot.say("Stats set for user")
    else:
        await bot.say(":negative_squared_cross_mark: | You do not have sufficent permission to access this command.")

#set a permission level for a user, permission is only set if user issuing the commands has a higher level than they are issuing and have more than 4
@bot.command(pass_context = True)
async def perms(cont, arg0 : discord.Member, arg1 : int):
    logit(cont,"perms")
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4 and userData[cont.message.author.id]["perms"][cont.message.server.id] > arg1:
        userData[arg0]["perms"][cont.message.server.id] = arg1
        await bot.say("All good to go, **"+ arg0 + "** now has permission level **"+ str(userData[arg0]["perms"][cont.message.server.id]) + "**")
    elif userData[cont.message.author.id]["perms"][cont.message.server.id] <= arg1:
        await bot.say(":negative_squared_cross_mark: | You do not have sufficient permissions to grant this permission level")
    else:
        await bot.say(":negative_squared_cross_mark: | You do not have sufficient permissions to grant permission levels")

#set the stats for all the users on the server the message was issued from
@bot.command(pass_context = True)
async def setAll(cont):
    logit(cont,"setAll")
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 6:
        membersServer = cont.message.server.members
        for x in membersServer:
            if x.id not in userData:
                try: 
                    log.write(time()+" set stats for "+str(x.name))
                except Exception:
                    log.write(time()+" set stats for user id:"+str(x.id))

                userData[x.id] = {'money': 2000, 'daily': '32','title':' ','exp':0,'perms':{},'warnings':[],'lastMessage':'','lastMessageTime':0,'locked':''}
            if cont.message.server.id not in userData[x.id]["perms"]:
                userData[x.id]["perms"][cont.message.server.id] = 0
                
        await bot.say("Stats sets for users")

#list of users/channels ignored by the bot and by the autmoderation
@bot.command(pass_context = True)
async def ignored(cont):
    logit(cont,"ignored")
    myList = []
    for x in ignoreAutomodList:
        try:
            myList.append("C: "+bot.get_channel(x).name)
        except Exception:
            myList.append("U: "+bot.get_server(cont.message.server.id).get_member(x).name)
    
    await bot.say("Channels/Users ignored by auto moderation: ``` "+str(myList)+" ``` ")

    myList = []
    for x in ignoreCommandList:
        try:
            myList.append("C: "+bot.get_channel(x).name)
        except Exception:
            myList.append("U: "+bot.get_server(cont.message.server.id).get_member(x).name)

    await bot.say("Channels/Users ignored by NecroBot: ``` "+str(myList)+" ``` ")


#mutes a user indefinitely or with a timer
@bot.command(pass_context = True)
async def mute(cont, arg0):
    logit(cont,"mute")
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
        except Exception:
            pass
    else:
        await bot.say("You don't have the neccessary permissions to mute this user.")

#unmutes user
@bot.command(pass_context = True)
async def unmute(cont, arg0):
    logit(cont,"unmute")
    role = discord.utils.get(cont.message.server.roles, name=serverData[cont.message.server.id]["mute"])
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 2:
        for x in cont.message.mentions:
            if role in x.roles and userData[cont.message.author.id]["perms"][cont.message.server.id] > userData[x.id]["perms"][cont.message.server.id]:
                await bot.remove_roles(x, role)
                await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** has been unmuted".format(x))
            else:
                await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** is not muted or cannot be unmuted".format(x))
    else:
        await bot.say("You don't have the neccessary permissions to unmute a user.")

#disable/enable autmoderation for users and channels
@bot.command(pass_context = True)
async def automod(cont, arg0):
    logit(cont,"automod")
    myList = []

    for x in cont.message.mentions:
        myList.append(x)
    for x in cont.message.channel_mentions:
        myList.append(x)

    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 5:
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
        else:
            await bot.say("Sub-command not recognized, use either `del` or `add`")
    else:
        await bot.say("You do not have permissions to edit the autmoderation list.")

#enable/disable commands for users and channels
@bot.command(pass_context = True)   
async def ignore(cont, arg0):
    logit(cont,"ignore")
    myList = []

    for x in cont.message.mentions:
        myList.append(x)
    for x in cont.message.channel_mentions:
        myList.append(x)

    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4:
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
        else:
            await bot.say("Sub-command not recognized, use either `del` or `add`")
    else:
        await bot.say("You do not have permissions to edit the commands ignore list.")

#sends arg1 to the channel with id arg0
@bot.command(pass_context = True)
async def speak(cont, arg0,*, arg1,):
    logit(cont,"speak")
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4:
        await bot.send_message(bot.get_channel(arg0), ":loudspeaker: | "+arg1)

#pm a user
@bot.command(pass_context = True)
async def pm(cont, arg0,*,arg1):
    logit(cont,"pm")
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
    logit(cont,"warn")
    if arg0 == "del":
        if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 3:
            await bot.say("Warning position: **\"" + userData[cont.message.mentions[0].id]["warnings"][int(arg2)] + "\"** removed from warning list of user " + str(cont.message.mentions[0].name))
            userData[cont.message.mentions[0].id]["warnings"].pop(int(arg2))
        else:
            await bot.say("You don't have the necessary permissions to remove warnings.")
    elif arg0 == "add":
        if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 1:
            await bot.say("Warning: **\"" + str(arg2) + "\"** added from warning list of user " + str(cont.message.mentions[0].name))
            userData[cont.message.mentions[0].id]["warnings"].append(arg2)
        else:
            await bot.say("You don't have the permission to add warnings.")
    else:
        await bot.say("Argument not recognized, you can either add a warning with `!warn add [@User] [message]` or remove a warning with `!warn del [@User] [warning position]`")

#removes a certain number of messages
@bot.command(pass_context = True)
async def purge(cont, arg0 : int):
    logit(cont,"purge")
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 5:
        await bot.purge_from(bot.get_channel(cont.message.channel.id), limit=arg0+1)

        message = await bot.say(":wastebasket: | **" + str(arg0) + "** messages purged.")
        await asyncio.sleep(5)
        await bot.delete_message(message)
    else:
        await bot.say("You don't have the neccessary permissions to purge messages  .")

#blacklists a user which means that if they join any server with necrobot they'll be banned
@bot.command(pass_context = True)
async def blacklist(cont):
    logit(cont,"blacklist")
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 6:
        blacklistList.append(cont.message.mentions[0].id)
        await bot.ban(bot.get_server(cont.message.server.id).get_member(cont.message.mentions[0].id), delete_message_days=7)
#set roles
@bot.command(pass_context = True)
async def setRoles(cont):
    logit(cont,"setRoles")
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 5:
        log.write(time()+str(cont.message.author)+" used setRoles")
        for x in roleList:
            new_role = await bot.create_role(cont.message.server, name=x[0], colour=x[1], mentionable=True)

        await bot.say("**Roles created**")

        for x in cont.message.server.members:
            role = userData[x.id]["perms"][cont.message.server.id]
            await bot.add_roles(x, discord.utils.get(cont.message.server.roles, name=roleList[role][0]))

        await bot.say("**Roles assigned**")
    else:
        await boy.say("You do not have the necessary permission level to set the NecroBot roles for this server")

#locks someone in a voice chat, everytime they leave that voice chat they will be moved to it
@bot.command(pass_context = True)
async def lock(cont, arg0 : discord.Member, *arg1):
    logit(cont,"lock")
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 3:
        if arg0.id in lockedList:
            lockedList.remove(arg0.id)
        else:
            v_channel = arg0.voice_channel.id
            userData[arg0.id]["locked"] = v_channel
            lockedList.append(arg0.id)
    else:
        await bot.say("You do not have the necessary permissions to lock someone in a voice chat.")

#changes user nickname
@bot.command(pass_context = True)
async def nick(cont, arg0 : discord.Member,*, arg1):
    logit(cont,"nick")
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4:
        try:
            await bot.change_nickname(arg0, arg1)
        except discord.errors.Forbidden:
            await bot.say("You cannot change the nickname of that user.")
    else:
        await bot.say("You do not have sufficient permissions to change a nickname.")


#*****************************************************************************************************************
# Regular Commands
#*****************************************************************************************************************

#****************** USER DEPENDENT COMMANDS ******************#

@bot.command(pass_context = True)
async def balance(cont, *arg0 : discord.Member):
    logit(cont,"balance")
    if arg0:
        user = arg0[0]
        await bot.say(":atm: | **"+ str(user.name) +"** has **"+ str(userData[user.id]["money"]) +"** :euro:")
    else:
        await bot.say(":atm: | **"+ str(cont.message.author.name) +"** you have **"+ str(userData[cont.message.author.id]["money"])+"** :euro:")

@bot.command(pass_context = True)
async def claim(cont):
    logit(cont,"claim")
    aDay = str(d.datetime.today().day)
    if aDay != userData[cont.message.author.id]["daily"]:
        await bot.say(":m: | You have received your daily **200** :euro:")
        userData[cont.message.author.id]["money"] += 200
        userData[cont.message.author.id]["daily"] = aDay
    else:
        await bot.say(":negative_squared_cross_mark: | You have already claimed your daily today, come back tomorrow.")

@bot.command(pass_context = True)
async def info(cont, *arg0 : discord.Member):
    logit(cont,"info")
    warningList = []
    if arg0:
        userID = arg0[0].id
        user = arg0[0]
    else:
        userID = str(cont.message.author.id)
        user = cont.message.author

    await bot.say(":id: User Info :id:\n**User Title**: " + userData[userID]["title"] + "\n**User Perms Level**: " + str(userData[userID]["perms"]) + "\n**User Balance**: " + str(userData[userID]["money"]) + "\n**User ID**: " + str(userID) + "\n**User XP**: " + str(userData[userID]["exp"]) + "\n**User Warnings**:" + str(userData[userID]["warnings"]) + "\n**User Nick**: "+ str(user.nick))

#****************** STANDALONE COMMANDS *******************

#general help command (could be outdated)
@bot.command(pass_context = True)
async def h(cont, *arg0 : str):
    logit(cont,"h")
    if arg0:
        helpRequest = arg0[0]
        await bot.say(":information_source: **The `" + helpRequest + "` command** :information_source:\n \n" + helpDict[helpRequest] + "\n ```Markdown \n>>> The bot usually has a response system so if there is no answer to your command it is either broken, offline or you haven't written the right command \n>>> Do not attempt to break the bot if possible \n>>> More commands and features will come later... \n```")
    else:
        await bot.say(helpVar)

# evaluates the the argument as a mathematical equation
@bot.command(pass_context = True)
async def calc(cont,*, arg : str):
    logit(cont,"calc")
    try:
        final = eval(arg)
        await bot.say(final)
    except NameError:
        await bot.say(":negative_squared_cross_mark: | **Mathematical equation not recognized.**")

# reads the user "fate" in the cards
@bot.command(pass_context = True)
async def tarot(cont):
    logit(cont,"tarot")
    myList = random.sample(range(0,44),3)

    await bot.say(":white_flower: | Settle down now and let Necro see your future my dear "+ cont.message.author.name + "...\n**Card #1:** " + tarotList[myList[0]] +"\n**Card #2:** " + tarotList[myList[1]] +"\n**Card #3:** " + tarotList[myList[2]] +"\n__*That is your fate, none can change it for better or worst.*__\n(**Not to be taken seriously**) ")

# good old game of russian roulette
@bot.command(pass_context = True)
async def rr(cont, *arg0 : int):
    logit(cont,"rr")
    try:
        num  = int(arg0[0])
        if num > 0 and num <= 6:
            bullets = num
        else:
            bullets = 1
    except Exception as e:
        bullets = 1

    await bot.say(":gun: | You insert "+ str(bullets) + " bullets, give the barrel a good spin and put the gun against your temple... \n:persevere: | You take a deep breath... and pull the trigger!")

    if random.randint(1,7) <= bullets:
        await bot.say(":boom: | You weren't so lucky this time. Rest in peace my friend.")
    else:
        await bot.say(":ok: | Looks like you'll last the night, hopefully your friends do too.")

@bot.command(pass_context = True)
async def lotrfact(cont):
    logit(cont,"lotrfact")
    num1 = random.randint(0,len(lotrList)-1)
    await bot.say(":trident: | **Fact #"+str(num1)+"**: "+lotrList[num1])

@bot.command(pass_context = True)
async def edain(cont,*,arg0 : str):
    logit(cont,"edain")
    try:
        article = wikia.page("Edain", arg0)
        url = article.url.replace(" ","_")
        related ="- " + "\n- ".join(article.related_pages[:3])

        embed = discord.Embed(title="__**" + article.title + "**__", colour=discord.Colour(0x277b0), url=url, description=article.section(article.sections[0]))

        embed.set_thumbnail(url=article.images[0]+"?size=400")
        embed.set_author(name=article.sub_wikia + " Wiki", url="http://edain.wikia.com/", icon_url="http://i.imgur.com/lPPQzRg.png")
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

        if len(article.section("Abilities")) < 2048 :
            embed.add_field(name="Abilities", value=article.section("Abilities"))
        else:
            for x in article.sections[1:]:
                if len(x) < 2048:
                    embed.add_field(name=x, value=article.section(x))
                    break

        embed.add_field(name="More Pages:", value=related)
        embed.add_field(name="Quotes", value="Get all the sound quotes for units/heroes [here](http://edain.wikia.com/wiki/Edain_Mod_Soundsets)")

        await bot.say(embed=embed)

    except Exception:
        try:
            article = wikia.search("Edain", arg0)
            await bot.say("Article: **"+ arg0 +"** not found, performing search instead, please search again using one of the possible relevant articles below:\n - " + "\n - ".join(article))
        except Exception:
            await bot.say("Article not found, and search didn't return any results. Please try again with different terms.")

@bot.command(pass_context = True)
async def lotr(cont,*,arg0 : str):
    logit(cont,"lotr")
    try:
        article = wikia.page("lotr", arg0)
        url = article.url.replace(" ","_")
        related ="- " + "\n- ".join(article.related_pages[:3])

        embed = discord.Embed(title="__**" + article.title + "**__", colour=discord.Colour(0x277b0), url=url, description=article.section(article.sections[0]))

        embed.set_thumbnail(url=article.images[0]+"?size=400")
        embed.set_author(name="LOTR Wiki", url="http://lotr.wikia.com/", icon_url="http://i.imgur.com/YWn19eW.png")
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

        embed.add_field(name="More Pages:", value=related)

        await bot.say(embed=embed)
    except Exception:
        try:
            article = wikia.search("lotr", arg0)
            await bot.say("Article not found, performing search instead, please search again using one of the possible relevant articles below:\n" + str(article))
        except Exception:
            await bot.say("Article not found, and search didn't return any result. Please try again with different terms.")

@bot.command(pass_context = True)
async def wiki(cont, arg0,*,arg1):
    logit(cont,"wiki")
    try:
        article = wikia.page(arg0, arg1)
        url = article.url.replace(" ","_")
        related ="- " + "\n- ".join(article.related_pages[:3])

        embed = discord.Embed(title="__**" + article.title + "**__", colour=discord.Colour(0x277b0), url=url, description=article.section(article.sections[0]))

        embed.set_thumbnail(url=article.images[0]+"?size=400")
        embed.set_author(name=article.sub_wikia.title() + " Wiki", url="http://"+ article.sub_wikia + ".wikia.com/", icon_url="https://vignette3.wikia.nocookie.net/"+ article.sub_wikia +"/images/6/64/Favicon.ico")
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

        embed.add_field(name="More Pages:", value=related)

        await bot.say(embed=embed)
    except Exception as e:
        try:
            article = wikia.search(arg0, arg1)
            await bot.say("Article not found, performing search instead, please search again using one of the possible relevant articles below:\n" + str(article))
        except Exception:
            await bot.say("Article not found or wiki not recognized, and search didn't return any result. Please try again with different terms.")

@bot.command(pass_context = True)
async def dadjoke(cont):
    logit(cont,"dadjoke")
    await bot.say(":speaking_head: | **" + dadJoke[random.randint(0,len(dadJoke)-1)] + "**")

@bot.command(pass_context = True)
async def play(cont, arg0):
    logit(cont,"play")
    vc = cont.message.author.voice_channel
    voice_client = await bot.join_voice_channel(vc)

    try:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(arg0) as r:
                filename = os.path.basename(arg0)
                with open(filename, 'wb') as f_handle:
                    while True:
                        chunk = await r.content.read(1024)
                        if not chunk:
                            break
                        f_handle.write(chunk)
                await r.release()

        print("File downloaded")

        player = voice_client.create_ffmpeg_player(filename, after=lambda:close_player(filename))
        
    except:
        player = await voice_client.create_ytdl_player(arg0, after=lambda:close_player(filename))
        await bot.say(":musical_note: | Playing `" + player.title)

    player.start()

@bot.command(pass_context = True)
async def cat(cont):
    logit(cont,"cat")
    async with aiohttp.ClientSession() as cs:
        async with cs.get('http://random.cat/meow') as r:
            res = await r.json()
            await bot.send_message(cont.message.channel, res['file'])

@bot.command(pass_context = True)
async def dog(cont):
    logit(cont,"dog")
    async with aiohttp.ClientSession() as cs:
        async with cs.get('http://random.dog/woof.json') as r:
            res = await r.json()
            await bot.send_message(cont.message.channel, res['url'])


#*****************************************************************************************************************
# Moderation Features
#*****************************************************************************************************************

@bot.event
async def on_message_delete(message):
    if selfDel:
        try:
            ChannelId = serverData[message.server.id]["automod"]
        except Exception:
            ChannelId = "318828760331845634"

        if message.author.id not in ignoreAutomodList and message.channel.id not in ignoreAutomodList:
            fmt = '**Auto Moderation: Deletion Detected!**\n{0.author} has deleted the message: ``` {0.content} ```'
            await bot.send_message(bot.get_channel(ChannelId), fmt.format(message))
    else:
        selfDel = True

@bot.event
async def on_message_edit(before, after):
    try:
        ChannelId = serverData[before.server.id]["automod"]
    except Exception:
        ChannelId = "318828760331845634"

    if before.author.id not in ignoreAutomodList and before.channel.id not in ignoreAutomodList:
        fmt = '**Auto Moderation: Edition Detected!**\n{0.author} edited their message: ``` {1.content}\n{0.content} ```'
        await bot.send_message(bot.get_channel(ChannelId), fmt.format(after, before))

@bot.event
async def on_member_join(member):
    if member.id in blacklistList:
        await bot.ban(member, delete_message_days=7)

    server = member.server
    fmt = 'Welcome {0.mention} to {1.name}!'
    await bot.change_nickname(member, str(member.name))
    await bot.send_message(bot.get_channel(server.default_channel.id), fmt.format(member, server))
    if member.id not in userData:
        userData[member.id] = {'money': 200, 'daily': '32','title':' ','exp':0,'perms':{},'warning':[],'lastMessage':'','lastMessageTime':0, 'locked':''}
    userData[member.id]["perms"][server.id] = 0

@bot.event
async def on_member_remove(member):
    await bot.send_message(bot.get_channel(server.default_channel.id),"Leaving us so soon, {0.mention}? We'll miss you...".format(member))

# @bot.event
# async def on_error(event, *args, **kwargs):
#     message = args[0]
#     await bot.send_message(message.channel, ":x: | **Missing some parameters check !h [command] to check all required parameters.**")

@bot.event
async def on_voice_state_update(before, after):
    if before.id in lockedList:
        await bot.move_member(before, bot.get_channel(userData[before.id]["locked"]))

@bot.event
async def on_message(message):
    userID = message.author.id
    channelID = message.channel.id

    if ((message.content == userData[userID]['lastMessage'] and userData[userID]['lastMessageTime'] > c.timegm(t.gmtime()) + 2) or userData[userID]['lastMessageTime'] > c.timegm(t.gmtime())) and (userID not in ignoreAutomodList and channelID not in ignoreAutomodList) and message.content.startswith("!") == False:
        try:
            ChannelId = serverData[message.server.id]["automod"]
        except Exception:
            ChannelId = "318828760331845634"

        selfDel = False
        await bot.send_message(bot.get_channel(ChannelId), "User: {0.author} spammed message: ``` {0.content} ```".format(message))
        await bot.delete_message(message)
        userData[userID]['lastMessage'] = message.content
        userData[userID]['lastMessageTime'] = int(c.timegm(t.gmtime()) + 1)
    else:
        userData[userID]['lastMessage'] = message.content
        userData[userID]['lastMessageTime'] = int(c.timegm(t.gmtime()) + 1)

        if len(message.content) != 0:
            if message.content[0] != "!":
                userData[userID]["exp"] += 2

        if message.content.startswith("<!@317619283377258497>"):
            await bot.send_message(message.channel, replyList[random.randint(0,len(replyList)-1)].format(message.author))

        if (channelID in ignoreCommandList or userID in ignoreCommandList) and message.content.startswith("!"):
            await bot.send_message(bot.get_channel("318828760331845634"), "User: **{0.author}** attempted to summon bot in channel **{0.channel.name}** with arguments: ``` {0.content} ```".format(message))
            await bot.delete_message(message)
        else:
            await bot.process_commands(message)

token = open("data/token.txt","r").read()
bot.run(token)
