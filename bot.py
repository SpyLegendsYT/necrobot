import discord
from discord.ext import commands

import csv
import random
import sys
import time as t
import datetime as d

bot = commands.Bot(command_prefix='!')

log = open("data/logfile.txt","a+")
userData = dict()

helpVar=""" :information_source: The `NecroBot` Help Guide :information_source: 
The NecroBot is a new highly buggy bot which is currently WIP, use this guide to figure out what it can do but be warned: if the bot doesn't respond it's either offline or has crashed. Either way best to wait for Necro to come on in that case.

__Command List (may not always be up to date)__
`!claim` - claim your daily bonus
`!balance [@User]` - check your balance or the balance of another user
`!calc [equation]` - evaluates equation us `+` to add, `-` to minus, `*` to multiply, `/` to divide, `**` for exponents, `%` for modulo
`!h ` - for this help bar

Attempt to not break the bot please. And good day."""

permsDict = {"peasant": 0, "ally" : 1, "mod": 2, "lord": 3, "admin": 4, "smith": 5}

with open("data/userdata.csv","r") as f:
    reader = csv.reader(f)
    for row in reader:
        userData[row[0]] = {"money":int(row[1]),"perms":int(row[2]),"daily":row[3],"title":row[4]}

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print(userData)
    print('------')
    await bot.change_presence(game=discord.Game(name='shipping Necro x Elfu'))


def time():
    localtime = str("\n" + t.asctime(t.localtime(t.time())) + ": ")
    return localtime

# @bot.command(pass_context = True)
# async def add(cont, arg0 : int, arg1 : int):
#     await bot.say(arg0 + arg1)
#     action = str(time()+str(cont.message.author)+" used add with variables:"+str(arg1)+" "+str(arg0))
#     log.write(action)

@bot.command(pass_context = True)
async def calc(cont,*, arg : str):
    action = str(time() + str(cont.message.author) + " used calc with message:" + arg)
    log.write(action)
    try:
        final = eval(arg)
        await bot.say(final)
    except NameError:
        await bot.say(":negative_squared_cross_mark: | **Mathematical equation not recognized.**")

@bot.command(pass_context = True)
async def kill(cont):
    if cont.message.author.id == "241942232867799040":
        log.write(time()+"Necro killed bot")
        log.close()
        with open("data/userdata.csv","w",newline="") as csvfile:
            Awriter = csv.writer(csvfile)
            for x in userData:
                Awriter.writerow([x,userData[x]["money"],userData[x]["perms"],userData[x]["daily"],userData[x]["title"]])
        await bot.say("Ready to be killed.")
    else:
        log.write(time()+cont.message.author," tried to kill bot")
        await bot.say(":negative_squared_cross_mark: | You do not have permission to kill the bot. Your attempt has been logged.")

@bot.command(pass_context = True)
async def balance(cont,*arg0):
    log.write(time()+str(cont.message.author)+" used balance")
    if arg0:
        fixed = arg0.replace("<@","").replace(">","").replace("!","")
        await bot.say(":atm: | **"+ arg0 +"** has **"+ str(userData[fixed]["money"]) +"** :euro:")
    else:
        await bot.say(":atm: | **"+ str(cont.message.author.nick) +"** you have **"+ str(userData[cont.message.author.id]["money"])+"** :euro:")

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
async def setStats(cont, arg0):
    log.write(time()+str(cont.message.author)+" used setStats with args: "+str(arg0))
    if userData[cont.message.author.id]["perms"] > 3:
        arg0 = arg0.replace("<@","").replace(">","").replace("!","")
        userData[arg0] = {'money': 2000, 'perms': 0, 'daily': '26'}
        await bot.say("Stats set for user")
    else:
        await bot.say(":negative_squared_cross_mark: | You do not have sufficent permission to access this command.")

# @bot.command(pass_context = True)
# async def setAll():
#     print(cont.message.author.)

# @bot.command()
# async def test(arg0):
#     server = discord.Server()
#     fixed = arg0.replace("<@!","").replace(">","")
#     user = server.get_member(fixed)
#     print(user)
#     await bot.say(user)

@bot.command(pass_context = True)
async def h(cont, *arg0):
    log.write(time()+str(cont.message.author)+"used help")
    if arg0:
        pass
    else:
        await bot.say(helpVar)

# @bot.command(pass_context = True)
# async def transfer(cont, arg0 : int, arg1 : str):
#     log.write(time()+str(cont.message.author)+"used transfer with args: "+str(arg0)+" and "+arg1)

@bot.command(pass_context = True)
async def perms(cont, arg0 : str,*, arg1 : str):
    log.write(time()+str(cont.message.author)+"used perms with args: "+arg0+" and "+arg1)
    arg0Fixed = arg0.replace("<@","").replace(">","").replace("!","")
    for x in permsDict:
        if x in arg1.lower() and userData[cont.message.author.id]["perms"] > permsDict[x]:
            userData[arg0Fixed]["perms"] = permsDict[x]
            userData[arg0Fixed]["title"] = arg1
            return await bot.say("All good to go, **"+ arg0 + "** is now **"+ arg1 + "** with permission level **"+ str(userData[arg0Fixed]["perms"]) + "**")
        elif x in arg1.lower() and userData[cont.message.author.id]["perms"] <= permsDict[x]:
            return await bot.say(":negative_squared_cross_mark: | You do not have sufficient permissions to grant this title")


    return await bot.say(":negative_squared_cross_mark: | This title cannot be granted.")

@bot.command(pass_context = True)
async def info(cont, *arg0):
    log.write(time()+str(cont.message.author)+" used info")
    if arg0:
        userID = arg0.replace("<@","").replace(">","").replace("!","")
    else:
        userID = str(cont.message.author.id)

    await bot.say(""" :id: User Info :id:
        **User Title**: """ + userData[userID]["title"] + """
        **User Perms Level**: """ + str(userData[userID]["perms"]) + """
        **User Balance**: """ + str(userData[userID]["money"]) + """
        **User ID**: """ + str(userID))

bot.run('MzE3NjE5MjgzMzc3MjU4NDk3.DAo8eQ.dmwPhH-zuqm5XzBhPjk_0nmitks')

