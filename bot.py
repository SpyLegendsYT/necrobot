import discord
from discord.ext import commands

import csv
import random
import sys
import time as t
import calendar as c
import datetime as d
from var import *
import wikia
import asyncio
import json


bot = commands.Bot(command_prefix='!')
log = open("data/logfile.txt","a+")
userData = dict()
serverData = dict()



#*****************************************************************************************************************
# Initialize
#*****************************************************************************************************************

with open("data/userdata.csv","r") as f:
    reader = csv.reader(f)
    for row in reader:
        permsDict = json.loads(row[5].replace("'", "\""))
        userData[row[0]] = {"money":int(row[1]),"daily":row[2],"title":row[3],"exp":int(row[4]),"perms":permsDict,"warnings":row[6].split(","),"lastMessage":"","lastMessageTime":0}

with open("data/setting.csv","r") as f:
    reader = csv.reader(f)
    ignoreUserList = list(next(reader))
    ignoreChannelList = list(next(reader))
    blacklistList = list(next(reader))
    line = next(reader)
    for row in reader:
        serverData[row[1]] = {"mute":row[2],"automod":row[3]}

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    # print(userData)
    print(ignoreUserList)
    print(ignoreChannelList)
    print(blacklistList)
    print(serverData)
    print('------')
    await bot.change_presence(game=discord.Game(name='!h for help'))
    await bot.send_message(bot.get_channel("318465643420712962"), "**Bot Online**")
    # await bot.send_message(bot.get_channel("319640180241727490"), "**Bot Online**")
    # await bot.send_message(bot.get_channel("287420616930492416"), "**Bot Online**")


#*****************************************************************************************************************
# Internal Function
#*****************************************************************************************************************

def time():
    localtime = str("\n" + t.asctime(t.localtime(t.time())) + ": ")
    return localtime

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

@bot.command(pass_context = True)
async def kill(cont):
    if cont.message.author.id == "241942232867799040":
        log.write(time()+"Necro killed bot")
        log.close()
        with open("data/userdata.csv","w",newline="") as csvfile:
            Awriter = csv.writer(csvfile)
            for x in userData:
                warningList = ",".join(userData[x]["warnings"])
                Awriter.writerow([x,userData[x]["money"],userData[x]["daily"],userData[x]["title"],userData[x]["exp"],userData[x]["perms"],warningList])

        with open("data/setting.csv","w",newline="") as csvfile:
            Awriter = csv.writer(csvfile)
            Awriter.writerow(ignoreUserList)
            Awriter.writerow(ignoreChannelList)
            Awriter.writerow(blacklistList)
            Awriter.writerow(['Server Name','Server','Mute Role','Autmod Channel'])
            for x in serverData:
                Awriter.writerow([bot.get_server(x).name,x,serverData[x]["mute"],serverData[x]["automod"]])

        await bot.send_message(bot.get_channel("318465643420712962"), "**Bot Offline**")
        # await bot.send_message(bot.get_channel("319640180241727490"), "**Bot Offline**")
        # await bot.send_message(bot.get_channel("287420616930492416"), "**Bot Offline**")
        sys.exit()
    else:
        log.write(time()+ str(cont.message.author) + " tried to kill bot")
        await bot.say(":negative_squared_cross_mark: | You do not have permission to kill the bot. Your attempt has been logged.")

@bot.command(pass_context = True)
async def add(cont, arg0 : str, arg1 : int, arg2 : str):
    log.write(time()+str(cont.message.author)+" used add with arguments: "+arg0+" "+str(arg1)+" "+arg2)
    arg2 = arg2.replace("<@","").replace(">","").replace("!","")
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4:
        if arg0 == "+":
            userData[arg2]["money"] += arg1
            await bot.say(":atm: | New user balance is **"+str(userData[arg2]["money"])+ "** :euro:")
        elif arg0 == "-":
            userData[arg2]["money"] -= arg1
            await bot.say(":atm: | New user balance is **"+str(userData[arg2]["money"])+ "** :euro:")
        else:
            await bot.say(":negative_squared_cross_mark: | Operation no recognized.")
    else:
        await bot.say(":negative_squared_cross_mark: | You do not have the permission to use this command.")

@bot.command(pass_context = True)
async def setStats(cont, arg0):
    log.write(time()+str(cont.message.author)+" used setStats with args: "+str(arg0))
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 2:
        arg0 = arg0.replace("<@","").replace(">","").replace("!","")
        if arg0 not in userData:
            userData[arg0] = {'money': 2000, 'daily': '32','title':' ','exp':0,'perms':{},'warnings':[],'lastMessage':'','lastMessageTime':0}
            userData[arg0]["perms"][cont.message.server.id] = 0
        await bot.say("Stats set for user")
    else:
        await bot.say(":negative_squared_cross_mark: | You do not have sufficent permission to access this command.")

@bot.command(pass_context = True)
async def perms(cont, arg0 : str, arg1 : str,*, arg2 : str):
    log.write(time()+str(cont.message.author)+"used perms with args: "+arg0+", "+arg1+" and "+arg2)
    arg0Fixed = arg0.replace("<@","").replace(">","").replace("!","")
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4:
        userData[arg0Fixed]["perms"][cont.message.server.id] = int(arg1)
        userData[arg0Fixed]["title"] = arg2
        return await bot.say("All good to go, **"+ arg0 + "** is now **"+ arg2 + "** with permission level **"+ str(userData[arg0Fixed]["perms"][cont.message.server.id]) + "**")
    elif userData[cont.message.author.id]["perms"][cont.message.server.id] <= 3:
        return await bot.say(":negative_squared_cross_mark: | You do not have sufficient permissions to grant this title")

@bot.command(pass_context = True)
async def setAll(cont, *arg0):
    log.write(time()+str(cont.message.author)+" used setAll")
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 6:
        membersServer = bot.get_all_members()
        for x in membersServer:
            if x.id not in userData:
                # log.write(time()+" set stats for "+str(x.name))
                userData[x.id] = {'money': 2000, 'daily': '32','title':' ','exp':0,'perms':{},'warnings':[],'lastMessage':'','lastMessageTime':0}
            if cont.message.server.id not in userData[x.id]["perms"]:
                userData[x.id]["perms"][cont.message.server.id] = 0

            # print(userData[x.id])
                
        await bot.say("Stats sets for users")

@bot.command(pass_context = True)
async def ignored(cont, *arg0):
    log.write(time()+str(cont.message.author)+" used ignore")
    myList = []
    for x in ignoreChannelList:
        myList.append(bot.get_channel(x).name)
    
    await bot.say("Channels ignored by NecroBot:\n```\n"+str(myList)+"\n```")

    myList = []
    for x in ignoreUserList:
        myList.append(bot.get_server(cont.message.server.id).get_member(x).name)

    await bot.say("Users ignored by NecroBot:\n```\n"+str(myList)+"\n```")

@bot.command(pass_context = True)
async def mute(cont, arg0):
    log.write(time()+str(cont.message.author)+" used mute")
    role = discord.utils.get(cont.message.server.roles, name=userData[cont.message.server.id]["mute"])
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 2:
        for x in cont.message.mentions:
            if role in x.roles:
                await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** is already muted".format(x))
            else:
                await bot.add_roles(x, role)
                await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** has been muted".format(x))
    else:
        await bot.say("You don't have the neccessary permissions to mute a user.")

    try:
        await asyncio.sleep(float(arg0))
        for x in cont.message.mentions:
            if role in x.roles:
                await bot.remove_roles(x, role)
                await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** has been automatically unmuted".format(x))
    except Exception:
        pass

@bot.command(pass_context = True)
async def unmute(cont,*, arg0):
    log.write(time()+str(cont.message.author)+" used mute")
    role = discord.utils.get(cont.message.server.roles, name=userData[cont.message.server.id]["mute"])
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 1:
        for x in cont.message.mentions:
            if role in x.roles:
                await bot.remove_roles(x, role)
                await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** has been unmuted".format(x))
            else:
                await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** is not muted".format(x))
    else:
        await bot.say("You don't have the neccessary permissions to unmute a user.")


@bot.command(pass_context = True)
async def ignore(cont, *arg0):
    log.write(time()+str(cont.message.author)+" used ignore")
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 3:
        if arg0:
            if arg0.mentions.id in ignoreUserList:
                ignoreUserList.remove(arg0.mentions.id)
                await bot.say(":white_check_mark: | User **{0.name}** is now no longer ignored by the bot autmoderation".format(arg0.mentions))
            else:
                ignoreUserList.append(arg0.mentions.id)
                await bot.say(":no_entry: | User **{0.name}** will now be ignored by the bot autmoderation".format(arg0.mentions))
        else:
            if cont.message.channel.id in ignoreChannelList:
                ignoreChannelList.remove(cont.message.channel.id)
                await bot.say(":white_check_mark: | Channel **{0.name}** is now no longer ignored by NecroBot".format(cont.message.channel))
            else:
                ignoreChannelList.append(cont.message.channel.id)
                await bot.say(":no_entry: | Channel **{0.name}** will now be ignored by NecroBot".format(cont.message.channel))
    else:
        await bot.say("You don't have the neccessary permissions to ignore a channel/user.")

@bot.command(pass_context = True)
async def speak(cont, arg0,*, arg1,):
    log.write(time()+str(cont.message.author)+" used speak with args: "+ str(arg1))
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4:
        await bot.send_message(bot.get_channel(arg0), arg1)

@bot.command(pass_context = True)
async def warn(cont, arg0, arg1,*, arg2):
    log.write(time()+str(cont.message.author)+" used warn with arg: " + str(arg0)+ " " + str(arg1) + " " +str(arg2))
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 1:
        if arg0 == "del":
            await bot.say("Warning position: **\"" + userData[cont.message.mentions.id]["warnings"][int(arg2)] + "\"** removed from warning list of user " + str(cont.message.mentions[0].name))
            userData[cont.message.mentions[0].id]["warnings"].pop(int(arg2) - 1)
        elif arg0 == "add":
            if '' in userData[cont.message.mentions[0].id]["warnings"]:
                userData[cont.message.mentions[0].id]["warnings"].remove('')
            await bot.say("Warning: **\"" + str(arg2) + "\"** added from warning list of user " + str(cont.message.mentions[0].name))
            userData[cont.message.mentions[0].id]["warnings"].append(arg2)
        else:
            await bot.say("Argument not recognized, you can either add a warning with `!warn add [@User] [message]` or remove a warning with `!warn del [@User] [warning position]`")
    else:
        await bot.say("You don't have the neccessary permissions to warn a user.")

@bot.command(pass_context = True)
async def purge(cont, arg0 : int):
    log.write(time()+str(cont.message.author)+" used purge with args: "+ str(arg0))

    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4:
        await bot.purge_from(bot.get_channel(cont.message.channel.id), limit=arg0+1)

        await bot.say("**" + str(arg0) + "** messages purged.")
        await asyncio.sleep(5)
        await bot.purge_from(bot.get_channel(cont.message.channel.id), limit=10, check=is_bot)
    else:
        await bot.say("You don't have the neccessary permissions to purge messages  .")

@bot.command(pass_context = True)
async def blacklist(cont):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 5:
        blacklistList.append(cont.message.mentions[0].id)
        await bot.ban(bot.get_server(cont.message.server.id).get_member(cont.message.mentions[0].id), delete_message_days=7)


#*****************************************************************************************************************
# Regular Commands
#*****************************************************************************************************************

@bot.command(pass_context = True)
async def calc(cont,*, arg : str):
    log.write(time() + str(cont.message.author.name) + " used calc with message:" + arg)
    try:
        final = eval(arg)
        await bot.say(final)
    except NameError:
        await bot.say(":negative_squared_cross_mark: | **Mathematical equation not recognized.**")

@bot.command(pass_context = True)
async def balance(cont,*arg0):
    log.write(time()+str(cont.message.author)+" used balance")
    if arg0:
        arg0 = arg0[0]
        fixed = arg0.replace("<@","").replace(">","").replace("!","")
        await bot.say(":atm: | **"+ arg0 +"** has **"+ str(userData[fixed]["money"]) +"** :euro:")
    else:
        await bot.say(":atm: | **"+ str(cont.message.author.name) +"** you have **"+ str(userData[cont.message.author.id]["money"])+"** :euro:")

@bot.command(pass_context = True)
async def claim(cont):
    log.write(time()+str(cont.message.author)+" used claim")
    aDay = str(d.datetime.today().day)
    if aDay != userData[cont.message.author.id]["daily"]:
        await bot.say(":m: | You have received your daily **200** :euro:")
        userData[cont.message.author.id]["money"] += 200
        userData[cont.message.author.id]["daily"] = aDay
    else:
        await bot.say(":negative_squared_cross_mark: | You have already claimed your daily today, come back tomorrow.")

@bot.command(pass_context = True)
async def h(cont, *arg0):
    log.write(time()+str(cont.message.author)+" used help")
    if arg0:
        pass
    else:
        await bot.say(helpVar)

@bot.command(pass_context = True)
async def info(cont, *arg0):
    warningList = []
    log.write(time()+str(cont.message.author)+" used info")
    if arg0:
        arg0 = arg0[0]
        userID = arg0.replace("<@","").replace(">","").replace("!","")
    else:
        userID = str(cont.message.author.id)

    await bot.say(":id: User Info :id:\n**User Title**: " + userData[userID]["title"] + "\n**User Perms Level**: " + str(userData[userID]["perms"]) + "\n**User Balance**: " + str(userData[userID]["money"]) + "\n**User ID**: " + str(userID) + "\n**User XP**: " + str(userData[userID]["exp"]) + "\n**User Warnings**:" + str(userData[userID]["warnings"]))

@bot.command(pass_context = True)
async def tarot(cont, *arg0):
    log.write(time()+str(cont.message.author)+" used tarot")
    myList = []
    count = 0
    while count != 3:
        num = random.randint(0,43)
        if num not in myList:
            myList.append(num)
            count += 1

    await bot.say(":white_flower: | Settle down now and let Necro see your future my dear "+ cont.message.author.name + "...\n**Card #1:** " + tarotList[myList[0]] +"\n**Card #2:** " + tarotList[myList[1]] +"\n**Card #3:** " + tarotList[myList[2]] +"\n__*That is your fate, none can change it for better or worst.*__\n(**Not to be taken seriously**) ")

@bot.command(pass_context = True)
async def rr(cont, *arg0 : int):
    log.write(time()+str(cont.message.author)+" used rr")
    num1 = 7
    try:
        num1 = int(arg0[0]) 
    except Exception:
        pass

    if num1 > 0 and num1 <= 6:
        bullets = num1
    else:
        bullets = 5

    await bot.say(":gun: | You insert "+ str(bullets) + " bullets give the barrel a good spin and put the gun against your temple... \n:persevere: | You take a deep breath... and pull the trigger!")

    if random.randint(1,6) <= bullets:
        await bot.say(":boom: | You weren't so lucky this time. Rest in peace my friend.")
    else:
        await bot.say(":ok: | Looks like you'll last the night, hopefully your friends do too.")

@bot.command(pass_context = True)
async def lotrfact(cont, *agr0):
    log.write(time()+str(cont.message.author)+" used lotrfact")
    num1 = random.randint(0,59)
    await bot.say(":trident: | **Fact #"+str(num1)+"**: "+lotrList[num1])

@bot.command(pass_context = True)
async def edain(cont,*,arg0 : str):
    log.write(time()+str(cont.message.author)+" used edain with args: "+arg0)
    try:
        article = wikia.page("Edain", arg0)
        url = article.url.replace(" ","_")
        await bot.say(" **"+article.title+"** on Edain Wiki \n" + article.summary + " \nMore at: "+ url)
    except Exception:
        try:
            article = wikia.search("Edain", arg0)
            await bot.say("Article not found, performing search instead, please search again using one of the possible relevant articles below:\n" + str(article))
        except Exception:
            await bot.say("Article not found, and search didn't return any result. Please try again with different terms.")

@bot.command(pass_context = True)
async def lotr(cont,*,arg0 : str):
    log.write(time()+str(cont.message.author)+" used lotr with args: "+arg0)
    try:
        article = wikia.page("lotr", arg0)
        url = article.url.replace(" ","_")
        await bot.say(" **"+article.title+"** on LOTR Wiki \n" + article.summary + " \nMore at: "+ url)
    except Exception:
        try:
            article = wikia.search("lotr", arg0)
            await bot.say("Article not found, performing search instead, please search again using one of the possible relevant articles below:\n" + str(article))
        except Exception:
            await bot.say("Article not found, and search didn't return any result. Please try again with different terms.")

@bot.command(pass_context = True)
async def music(cont, *arg0):
    await bot.join_voice_channel(bot.get_channel("319612586171826197"))


#*****************************************************************************************************************
# Moderation Features
#*****************************************************************************************************************

@bot.event
async def on_message_delete(message):
    try:
        ChannelId = serverData[message.server.id]["automod"]
    except Exception:
        ChannelId = "318828760331845634"

    if message.author.id not in ignoreUserList:
        fmt = '**Auto Moderation: Deletion Detected!**\n{0.author} has deleted the message:```{0.content}```'
        await bot.send_message(bot.get_channel(ChannelId), fmt.format(message))

@bot.event
async def on_message_edit(before, after):
    try:
        ChannelId = serverData[before.server.id]["automod"]
    except Exception:
        ChannelId = "318828760331845634"

    if before.author.id not in ignoreUserList:
        fmt = '**Auto Moderation: Edition Detected!**\n{0.author} edited their message:```{1.content}\n{0.content}```'
        await bot.send_message(bot.get_channel(ChannelId), fmt.format(after, before))

@bot.event
async def on_member_join(member):
    if member.id in blacklistList:
        await bot.ban(member, delete_message_days=7)

    server = member.server
    fmt = 'Welcome {0.mention} to {1.name}!'
    await bot.send_message(bot.get_channel(bot.server.default_channel.id), fmt.format(member, server))
    if member.id not in userData:
        userData[member.id] = {'money': 2000, 'daily': '32','title':' ','exp':0,'perms':{},'warning':[],'lastMessage':'','lastMessageTime':0}
    userData[member.id][permsDict][server.id] = 0

@bot.event
async def on_message(message):
    userID = message.author.id
    if ((message.content == userData[userID]['lastMessage'] and userData[userID]['lastMessageTime'] > c.timegm(t.gmtime()) + 4) or userData[userID]['lastMessageTime'] > c.timegm(t.gmtime())) and userID not in ignoreUserList and message.content[0] != "!":
        try:
            ChannelId = serverData[message.server.id]["automod"]
        except Exception:
            ChannelId = "318828760331845634"

        await bot.send_message(bot.get_channel(ChannelId), "User: {0.author} spammed message:```{0.content}```\n".format(message))
        await bot.delete_message(message)
        userData[userID]['lastMessage'] = message.content
        userData[userID]['lastMessageTime'] = int(c.timegm(t.gmtime()) + 2)
    else:
        userData[userID]['lastMessage'] = message.content
        userData[userID]['lastMessageTime'] = int(c.timegm(t.gmtime()) + 2)

        if len(message.content) != 0:
            if message.content[0] != "!":
                userData[userID]["exp"] += 2

        # if "317619283377258497" in message.raw_mentions:
        #     await bot.send_message(message.channel, replyList[random.randint(0,len(replyList)-1)].format(message.author))

        if message.channel.id in ignoreChannelList and message.content[0] == "!" and userData[userID]["perms"][message.server.id] < 4:
            await bot.send_message(bot.get_channel("318828760331845634"), "User: **{0.author}** attempted to summon bot in channel **{0.channel.name}** with arguments:```{0.content}```".format(message))
            await bot.delete_message(message)
        else:
            await bot.process_commands(message)

bot.run('MzE3NjE5MjgzMzc3MjU4NDk3.DAo8eQ.dmwPhH-zuqm5XzBhPjk_0nmitks')
