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

bot = commands.Bot(command_prefix='!')
log = open("data/logfile.txt","a+")
userData = dict()


#*****************************************************************************************************************
# Initialize
#*****************************************************************************************************************

with open("data/userdata.csv","r") as f:
    reader = csv.reader(f)
    for row in reader:
        userData[row[0]] = {"money":int(row[1]),"perms":int(row[2]),"daily":row[3],"title":row[4],"exp":int(row[5]),"lastMessage":"","lastMessageTime":0}

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print(userData)
    print('------')
    await bot.change_presence(game=discord.Game(name='!h for help'))
    await bot.send_message(bot.get_channel("318465643420712962"), "**Bot Online**")


#*****************************************************************************************************************
# Internal Function
#*****************************************************************************************************************

def time():
    localtime = str("\n" + t.asctime(t.localtime(t.time())) + ": ")
    return localtime


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
                Awriter.writerow([x,userData[x]["money"],userData[x]["perms"],userData[x]["daily"],userData[x]["title"],userData[x]["exp"]])
        await bot.say("Bot Killed.")
        sys.exit()
    else:
        log.write(time()+ str(cont.message.author) + " tried to kill bot")
        await bot.say(":negative_squared_cross_mark: | You do not have permission to kill the bot. Your attempt has been logged.")

@bot.command(pass_context = True)
async def add(cont, arg0 : str, arg1 : int, arg2 : str):
    log.write(time()+str(cont.message.author)+" used add with arguments: "+arg0+" "+str(arg1)+" "+arg2)
    arg2 = arg2.replace("<@","").replace(">","").replace("!","")
    if userData[cont.message.author.id]["perms"] > 2:
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
    if userData[cont.message.author.id]["perms"] > 3:
        arg0 = arg0.replace("<@","").replace(">","").replace("!","")
        userData[arg0] = {'money': 2000, 'perms': 0, 'daily': '32','title':' ','exp':0,'lastMessage':'','lastMessageTime':0}
        await bot.say("Stats set for user")
    else:
        await bot.say(":negative_squared_cross_mark: | You do not have sufficent permission to access this command.")

@bot.command(pass_context = True)
async def perms(cont, arg0 : str, arg1 : str,*, arg2 : str):
    log.write(time()+str(cont.message.author)+"used perms with args: "+arg0+", "+arg1+" and "+arg2)
    arg0Fixed = arg0.replace("<@","").replace(">","").replace("!","")
    for x in permsDict:
        if x in arg1.lower() and userData[cont.message.author.id]["perms"] > permsDict[x]:
            userData[arg0Fixed]["perms"] = permsDict[x]
            userData[arg0Fixed]["title"] = arg2
            return await bot.say("All good to go, **"+ arg0 + "** is now **"+ arg2 + "** with permission level **"+ str(userData[arg0Fixed]["perms"]) + "**")
        elif x in arg1.lower() and userData[cont.message.author.id]["perms"] <= permsDict[x]:
            return await bot.say(":negative_squared_cross_mark: | You do not have sufficient permissions to grant this title")
    return await bot.say(":negative_squared_cross_mark: | This title cannot be granted.")

@bot.command(pass_context = True)
async def setAll(cont, *arg0):
    log.write(time()+str(cont.message.author)+" used setAll")
    if userData[cont.message.author.id]["perms"] > 3:
        membersServer = bot.get_all_members()
        for x in membersServer:
            if x.id not in userData:
                log.write(time()+" set stats for "+str(x.name))
                userData[x.id] = {'money': 2000, 'perms': 0, 'daily': '32','title':' ','exp':0,'lastMessage':'','lastMessageTime':0}
                
        await bot.say("Stats sets for users")

@bot.command(pass_context = True)
async def ignored(cont, *arg0):
    log.write(time()+str(cont.message.author)+" used ignore")
    myList = []
    for x in ignoreChannelList:
        myList.append(bot.get_channel(x).name)
    
    await bot.say("Channels ignored by NecroBot Automoderation:\n```\n"+str(myList)+"\n```")

    myList = []
    for x in ignoreUserList:
        myList.append(bot.get_server(cont.message.server.id).get_member(x).name)

    await bot.say("Users ignored by NecroBot Automoderation:\n```\n"+str(myList)+"\n```")

@bot.command(pass_context = True)
async def mute(cont, arg0):
    log.write(time()+str(cont.message.author)+" used mute")
    role = discord.utils.get(cont.message.server.roles, name="TimeOut")
    if userData[cont.message.author.id]["perms"] > 1:
        for x in cont.message.mentions:
            await bot.add_roles(x, role)
            await bot.send_message(bot.get_channel(cont.message.channel.id),"User: **{0}** has been muted".format(x))
    else:
        await bot.say("You don't have the neccessary permissions to mute a user.")



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
    log.write(time()+str(cont.message.author)+" used info")
    if arg0:
        arg0 = arg0[0]
        userID = arg0.replace("<@","").replace(">","").replace("!","")
    else:
        userID = str(cont.message.author.id)

    await bot.say(":id: User Info :id:\n**User Title**: " + userData[userID]["title"] + "\n**User Perms Level**: " + str(userData[userID]["perms"]) + "\n**User Balance**: " + str(userData[userID]["money"]) + "\n**User ID**: " + str(userID) + "\n**User XP**: " + str(userData[userID]["exp"]))

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

@bot.command(pass_context = True)


#*****************************************************************************************************************
# Moderation Features
#*****************************************************************************************************************

@bot.event
async def on_message_delete(message):
    try:
        ChannelId = automodChannel[message.server.id]
    except Exception as e:
        ChannelId = "318828760331845634"

    if message.author.id not in ignoreUserList:
        fmt = '**Auto Moderation: Deletion Detected!**\n{0.author} has deleted the message:```{0.content}```'
        await bot.send_message(bot.get_channel(ChannelId), fmt.format(message))

@bot.event
async def on_message_edit(before, after):
    try:
        ChannelId = automodChannel[message.server.id]
    except Exception as e:
        ChannelId = "318828760331845634"

    if before.author.id not in ignoreUserList:
        fmt = '**Auto Moderation: Edition Detected!**\n{0.author} edited their message:```{1.content}\n{0.content}```'
        await bot.send_message(bot.get_channel(ChannelId), fmt.format(after, before))

@bot.event
async def on_member_join(member):
    server = member.server
    fmt = 'Welcome {0.mention} to {1.name}!'
    await bot.send_message(bot.get_channel(bot.server.default_channel.id), fmt.format(member, server))
    if member.id not in userData:
        userData[member.id] = {'money': 2000, 'perms': 0, 'daily': '32','title':' ','exp':0}

@bot.event
async def on_message(message):
    if ((message.content == userData[message.author.id]['lastMessage'] and userData[message.author.id]['lastMessageTime'] > c.timegm(t.gmtime()) + 4) or userData[message.author.id]['lastMessageTime'] > c.timegm(t.gmtime())) and message.author.id not in ignoreUserList and message.content[0] != "!":
        try:
            ChannelId = automodChannel[message.server.id]
        except Exception as e:
            ChannelId = "318828760331845634"

        await bot.send_message(bot.get_channel(ChannelId), "User: {0.author} spammed message:```{0.content}```\n".format(message))
        await bot.delete_message(message)
    else:
        userData[message.author.id]['lastMessage'] = message.content
        userData[message.author.id]['lastMessageTime'] = int(c.timegm(t.gmtime()) + 2)

        if len(message.content) != 0:
            if message.content[0] != "!":
                userData[message.author.id]["exp"] += 2

        if "317619283377258497" in message.raw_mentions:
            if message.content != True:
                message.content = "..."

            await bot.send_message(message.channel, replyList[random.randint(0,len(replyList)-1)].format(message.author))

        if message.channel.id in ignoreChannelList and message.content[0] == "!" and userData[message.author.id]["perms"] < 4:
            await bot.send_message(bot.get_channel("318828760331845634"), "User: **{0.author}** attempted to summon bot in channel **{0.channel.name}** with arguments:```{0.content}```".format(message))
            await bot.delete_message(message)
        else:
            await bot.process_commands(message)

bot.run('MzE3NjE5MjgzMzc3MjU4NDk3.DAo8eQ.dmwPhH-zuqm5XzBhPjk_0nmitks')
