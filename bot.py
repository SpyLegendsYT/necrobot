# NecroBot: The ultimate moderation bot with some fun commands to keep everybody entertained

# import statements for basic discord bot functionalities
import discord
from discord.ext import commands

# import statements for commands
import csv
import random
import sys
import os
import time as t
import calendar as c
import datetime as d
import asyncio
import json
import urllib.request
import aiohttp
import async_timeout
from bs4 import BeautifulSoup

bot = commands.Bot(command_prefix='!')
userData = dict()
serverData = dict()
lockedList = list()
extensions = ["animals","social"]

#Help Doc
helpVar=""":information_source: **NecroBot v1.0 Help Menu** :information_source: 
To access the help page pf the command simply us `!h [command]` and replace [command] with the command you seek to display, such as `!h edain` will display the help page of the edain command. NecroBot is still WIP so take it easy.

__User Commands__
1. **Economy** - `claim` | `balance`
2. **Wiki** - `edain` | `lotr` | `wiki`
3. **Fun** - `rr` | `tarot` | `calc` | `riddle` | `dadjoke`
4. **Utility** - `h` | `info` | `play`
5. **Animal** - `cat`| `dog`

__Moderation Commands__
1. **User Profile** - `add` | `setStats` | `perms` | `setAll` | `setRoles`
2. **User Moderation** - `mute`  | `unmute` | `warn` | `lock` | `nick`
3. **Feature Enable/Disable** - `automod` | `ignore` | `ignored`
4. **Broadcast** - `speak` | `pm`
5. **Others** - `kill` | `purge` | `blacklist` | `eval`

```Markdown
>>> The bot usually has a response system so if there is no answer to your command it is either broken, offline or you haven't written the right command
>>> Do not attempt to break the bot if possible
>>> More commands and features will come later...
```
**For more help:** https://discord.gg/sce7jmB"""

#Help Dict
helpDict = {"claim" : "The claim commands allows the user to claim their daily random income of money, money which can then later be used to buy various things and participate in various mini games. Daily can be claimed once a day at any time. As soon as the clock hits midnight GMT all cooldowns are refreshed. Use without any arguments:\n \n__Usage__ \n `!claim`","balance":"Used to check a user's euro balance, if no user is provided it will display your own balance.\n \n__Usage__ \n`!balance` \n`!balance [@User]` \n \n__Example__\n`!balance` \n`!balance @NecroBot`", "edain":"Command can be used to look up articles through the Edain Wiki. If the article is found it will return a rich embed version of the article, else it will return a series of world results similar to the search term.\n \n__Usage__\n`!edain [article]` \n \n__Example__ \n`!edain Sauron`\n`!edain Castellans`","lotr":"Command can be used to look up articles through the LOTR Wiki. If the article is found it will return a rich embed version of the article, else it will return a series of world results similar to the search term.\n \n__Usage__\n`!lotr [article]` \n \n__Example__ \n`!lotr Sauron`\n`!lotr Boromir`","wiki":"Command returns a short summary of the requested article from the requested wiki, else returns a number of different others error messages ranging for plain error messages to a series of articles related to the search result.\n \n__Usage__\n`!wiki [wiki] [article]` \n \n__Example__\n`!wiki disney Donald Duck`\n`!wiki transformers Optimus Prime`","rr":"The rr tag allows users to play a game of russian roulette by loading a number of bullets into a gun. The number can either be picked by adding it after the rr command or will default to 1. \n\n __Usage__\n`!rr`\n`!rr [1-6]`\n\n__Example__\n`!rr 5`\n`!rr`\n`!rr 3`","tarot":"The tarot command allows user to have their destiny read in tarot cards using our extremely *advanced* card reading system.\n\n__Usage__\n`!tarot`","calc":"The calc command will evaluate a simple mathematical equation according to its pythonic mathematical symbols and return the result.\n - `+` for additions\n - `-` for subtractions\n - `*` for multiplications \n - `/` for divisions\n - `**` for exponents\n\n__Usage__\n`!calc [equation]`\n \n__Example__\n`!calc 4 + 2 / 4`\n`!calc (4+2)*2`\n`!calc 4**2`","h":"The help tag will either display the help menu for the supplied command name  or will display the default help menu\n\n__Usage__\n`!h`\n`!h [command]`\n\n__Example__\n`!h`\n`!h wiki`","info":"The info command will display a user's NecroBot profile allowing users to see their warning history along with other misc data such as id, balance and permission level.\n\n__Usage__\n`!info`\n`!info [@User]`\n\n__Example__\n`!info`\n`!info @NecroBot`","add":"Does the given pythonic operation on the user's current balance (works the same way as `calc`) (Permission level of 6+ (NecroBot Admins))\n\n__Usage__\n`!add [@User] [operation]`\n\n__Example__\n`!add @Necro +300`\n`!add @Necro *2`\n`!add @Necro -200`\n`!add @Necro **3`","setStats":"Sets the default stats for all the users if not on the database already, used when a user's name gives the bot trouble. (Permission level of 2+ (Mod))\n\n__Usage__\n`!setStats [@User]`\n\n__Example__\n`!setStats @NecroBot`\n`!setStats @Necro @NecroBot @SilverElf","perms":"Sets the permission level for the user ranging from 0-6, user can only set permission levels that is less than their own. (Permission level of 4+ (Server Admin))\n\n__Hierachy Level__\n7: The Bot Smith - Bot Owners & Collaborators\n6: NecroBot Admin - Trusted Friends\n5: Server Owner - Given to owners of a server using NecroBot\n4: Admin - Trusted members of indivudal servers\n3: Semi-Admin - 'Trainee' admins\n2: Mods - active, helpful and mature members of individual servers\n1: Helpers - helpful members of individual servers\n0: Users - members of servers\n\n__Usage__\n`!perms [@User] [0-6]`\n\n__Example__\n`!perms @Necro 7`","mute":"Mutes a user (restrict their ability to type in channels) either permanently or temporarily.(Permission level of 2+ (Mod))\n\n__Usage__\n`!mute @User`\n`!mute [second] [@User]`\n\n__Example__\n`!mute @NecroBot`\n`!mute 15 @NecroBot`","unmute":"Unmutes a user, removing the mute role from their profiles.(Permission level of 2+ (Mod))\n\n__Usage__\n`!unmute [@User]`\n\n__Example__\n`!unmute @NecroBot`","warn":"Adds or removes a warning from the user's NecroBot profile.(Permission level of 1+ (Helper) to add warnings and 3+ (Semi Admin) to remove a warnings)\n\n__Usage__\n`!warn [add/del] [@User] [message/position]`\n\n__Example__\n`!warn add @Necro this is a test warning`\n`!warn del @Necro 1`","speak":"Sends the message to a specific channels. (Permission level of 4+ (Server Admin))\n\n__Usage__\n`!speak [channe id] [message]`\n\n__Example__\n`!speak 31846564420712962 Hello, this is a message`","pm":"Sends a user a message through the bot and awaits for a reply.(Permission level of 6+ (NecroBot Admin))\n\n__Usage__\n`!pm [user ID] [message]`\n\n__Example__\n`!pm 97846534420712962 This is another message`","automod":"Add/removes the channels/users from the necrobot automoderation, this means users/channels will no longer be affected by the spam filter, edition tracking and deletion tracking. (Permission leve of 5+ (Server Owner))\n\n__Usage__\n`!automod (add/del) [@Users/#channels]`\n\n__Example__\n`!automod add #necrobot-channel`\n`!automod add @NecroBot`\n`!automod del #necrobot-channel`\n`!automod del @Necrobot`","ignore":"Add/removes the channels/users from the necrobot , this means users/channels will no longer be able to use commands. (Permission leve of 5+ (Server Owner))\n\n__Usage__\n`!ignore (add/del) [@Users/#channels]`\n\n__Example__\n`!ignore add #necrobot-channel`\n`!ignore add @NecroBot`\n`!ignore del #necrobot-channel`\n`!ignore del @Necrobot`","ignored":"Displays the list of ignored channels and users.\n\n__Usage__\n`!ignored`","kill":"Kills the bot and saves all the data.(Permission level of 7+ (Bot Smith))\n\n__Usage__\n`!kill`","purge":"Looks over the given number of messages and removes all the one that fit the parameters.(Permission level of 5+ (Server Owner))\n\n__Usage__\n`!purge [number]`\n\n__Example__\n`!purge 45`","blacklist":"The ultimate moderation tool, the most powerful tool out there in terms of user moderation. This will ban the users in every server NecroBot is on and will keep them out for as long as they are on the NecroBot blacklist. This is especially good for hacking users that can unban themselves from the Discord system.(Permission level of 6+ (NecroBot Admin))\n\n__Usage__\n`!blacklist [@User]`\n\n__Example__`!blacklist @Invisible`","cat":"Post the picture of a random cat. \n\n__Usage__\n`!cat`","dog":"Post the picture of a random dog. \n\n__Usage__\n`!dog`","riddle":"Asks the user a riddle, the user must then answer the riddle by typing the solution in the channel the !riddle command was summoned in.\n\n__Usage__\n`!riddle`","dadjoke":"Replies with a random dad joke/pun.\n\n__Usage__\n`!dadjoke`","play":"A command that allows the user to play either an audio file using a link or a youtube video. The audio file link must finish with a valid audio file extension.\n\n__Usage__\n`!play [audio file url]`\n`!play [youtube link]`\n\n__Example__\n`!play https://vignette1.wikia.nocookie.net/edain-mod/images/2/20/Castellan2_select5.ogg`\n`!play https://www.youtube.com/watch?v=o6HDfqjlCAs`","setRoles":"Sets the NecroBot roles for the server and assigns them to users according to their permission level.(Permission leve of 5+ (Server Owner))\n\n__Usage__\n`!setRoles`","lock":"Locks the user in either the given channel or the channel they currently are in.(Permission level of 3+ (Semi-Admin))\n\n__Usage__\n`!lock`\n`!lock [voice_channel]`\n\n__Example__\n`!lock`\n`!lock #voice-channel`","eval":"Evaluates the code given and executes it.(Permission level of 7 (Bot Owner))\n\n__Usage__\n`!eval [code]`\n\n__Example__\n`!eval print(\"hello world\")`","nick":"Changes the nickname of the user (Permission level of 3+ (Moderator))\n\n__Usage__\n`!nick [@User] [nickname]`\n\n__Example__\n`!nick @NecroBot Lord of all Bots` "}


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
    await bot.change_presence(game=discord.Game(name='!h for help'))
    await bot.send_message(bot.get_channel("318465643420712962"), "**Bot Online**")




# *****************************************************************************************************************
#  Internal Function
# *****************************************************************************************************************

def close_player(filename):
    os.remove(filename)

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
async def setStats(cont,* arg0 : discord.Member):
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
async def setAll(cont):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 6:
        membList = cont.message.server.members
        for x in membList:
            if x.id not in userData:
                try: 
                    log.write(time()+" set stats for "+str(x.name))
                except Exception:
                    log.write(time()+" set stats for user id:"+str(x.id))

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

# list of users/channels ignored by the bot and by the autmoderation
@bot.command(pass_context = True)
async def ignored(cont):
    myList1 = []
    for x in ignoreAutomodList:
        try:
            myList1.append("C: "+bot.get_channel(x).name)
        except Exception:
            myList1.append("U: "+bot.get_server(cont.message.server.id).get_member(x).name)

    myList2 = []
    for x in ignoreCommandList:
        try:
            myList2.append("C: "+bot.get_channel(x).name)
        except Exception:
            myList2.append("U: "+bot.get_server(cont.message.server.id).get_member(x).name)

    await bot.say("Channels/Users ignored by auto moderation: ``` "+str(myList1)+" ```\nChannels/Users ignored by NecroBot: ``` "+str(myList2)+" ```")


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
        except Exception:
            pass
    else:
        await bot.say("You don't have the neccessary permissions to mute this user.")

# unmutes user
@bot.command(pass_context = True)
async def unmute(cont, arg0):
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

# disable/enable autmoderation for users and channels
@bot.command(pass_context = True)
async def automod(cont, arg0):
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

# enable/disable commands for users and channels
@bot.command(pass_context = True)   
async def ignore(cont, arg0):
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
            userData[cont.message.mentions[0].id]["warnings"].append(arg2)
        else:
            await bot.say("You don't have the permission to add warnings.")
    else:
        await bot.say("Argument not recognized, you can either add a warning with `!warn add [@User] [message]` or remove a warning with `!warn del [@User] [warning position]`")

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
async def blacklist(cont):
    if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 6:
        blacklistList.append(cont.message.mentions[0].id)
        await bot.ban(bot.get_server(cont.message.server.id).get_member(cont.message.mentions[0].id), delete_message_days=7)
# set roles
@bot.command(pass_context = True)
async def setRoles(cont):
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

# ****************** USER DEPENDENT COMMANDS ******************# 

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
    warningList = []
    if arg0:
        userID = arg0[0].id
        user = arg0[0]
    else:
        userID = str(cont.message.author.id)
        user = cont.message.author

    await bot.say(":id: User Info :id:\n**User Title**: " + userData[userID]["title"] + "\n**User Perms Level**: " + str(userData[userID]["perms"]) + "\n**User Balance**: " + str(userData[userID]["money"]) + "\n**User ID**: " + str(userID) + "\n**User XP**: " + str(userData[userID]["exp"]) + "\n**User Warnings**:" + str(userData[userID]["warnings"]) + "\n**User Nick**: "+ str(user.nick))

# ****************** STANDALONE COMMANDS *******************

# general help command (can be outdated)
@bot.command(pass_context = True)
async def h(cont, *arg0 : str):
    if arg0:
        helpRequest = arg0[0]
        await bot.say(":information_source: **The `" + helpRequest + "` command** :information_source:\n \n" + helpDict[helpRequest] + "\n ```Markdown \n>>> The bot usually has a response system so if there is no answer to your command it is either broken, offline or you haven't written the right command \n>>> Do not attempt to break the bot if possible \n>>> More commands and features will come later... \n```")
    else:
        await bot.say(helpVar)

@bot.command(pass_context = True)
async def play(cont, arg0):
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
async def moddb(cont, url):
    if cont.message.content[7:].startswith("http://www.moddb.com/mods/"):
        #obtain xml and html pages
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                soup = BeautifulSoup(await resp.text(), "html.parser")

            async with session.get(url.replace("www","rss")+ "/articles/feed/rss.xml") as resp:
                rss = BeautifulSoup(await resp.text(), "xml")

        modName = str(soup.title.string[:len(soup.title.string)-9])

        try:
            modDesc = str(soup.find(itemprop="description")["content"])
        except KeyError:
            modDesc = str(soup.find(itemprop="description").string)

        embed = discord.Embed(title="__**" + modName + "**__", colour=discord.Colour(0x277b0), url=url, description=modDesc)
        embed.set_author(name="ModDB", url="http://www.moddb.com", icon_url="http://i.imgur.com/aExydLm.png")
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")
        
        #navbar
        sections = ["Articles","Reviews","Downloads","Videos","Images"]
        navBar = list()
        for x in sections:
            navBar.append("["+ str(x) +"]("+url+"/"+str(x)+")")

        embed.add_field(name="Navigation", value=" - ".join(navBar))

        #recent articles
        articles = rss.find_all("item")[:3]
        for article in articles:
            title = str(article.title.string)
            desc = str(article.find_all(type="plain")[1].string)
            link = str(article.link.string)
            date = str(article.pubDate.string[:len(article.pubDate.string)-14])
            embed.add_field(name=title, value=desc + "... [Link](" + link + ")\n" + "Published "+ date)

        #tags
        tags = soup.find(id="tagsform")
        tagList = list()
        for x in tags.descendants:
            if str(type(x)) == "<class 'bs4.element.NavigableString'>":
                if len(x) > 0 and x != "\n" and x != " ":
                    tagList.append(str(x))

        embed.add_field(name="Tags", value="#" + " #".join(tagList[:len(tagList)-1]))

        #misc stuff
        misc = soup.find_all("h5")
        try:
            follow = ["[Follow the mod](" + x.parent.a["href"] + ")" for x in misc if x.string == "Mod watch"][0]
        except IndexError:
            follow = "Cannot follow"
        try: 
            publishers = "Creator: " + [x.parent.a.string for x in misc if x.string in ["Developer", "Creator"]][0]
        except IndexError:
            follow = "No Creator"

        #comment
        comment = "[Leave a comment](" + url + "#commentform)"

        #release date
        release_date = "Release: " + str(soup.time.string)

        #rating
        try:
            score = str("Average Rating: " + soup.find(itemprop="ratingValue")["content"])
        except TypeError:
            score = "Average Rating: Not rated"
        
        embed.add_field(name="Misc: ", value=score + " \n" + publishers + "  -  " + release_date + "\n**" + comment + "**  -  **" + follow + "**")

        #style
        try:
            genre = "**Genre**: " + [x.parent.a.string for x in misc if x.string == "Genre"][0]
        except IndexError:
            genre = "**Genre**: None"
        try:
            theme = "**Theme**: " + [x.parent.a.string for x in misc if x.string == "Theme"][0]
        except IndexError:
            theme = "**Theme**: None"
        try:
            players = "**Players**: " + [x.parent.a.string for x in misc if x.string == "Players"][0]
        except IndexError:
            players = "**Players**: None"

        embed.add_field(name="Style", value= genre + "\n" + theme + "\n" + players, inline=True)

        #stats
        try:
            rank = "__Rank__: " + [x.parent.a.string for x in misc if x.string == "Rank"][0]
        except IndexError:
            rank = "__Rank__: Unclassed"
        try:
            visits = "__Visits__: " + [x.parent.a.string for x in misc if x.string == "Visits"][0]
        except IndexError:
            visits = "__Visits__: Not tracked"
        try:
            last_update = "__Last Update__: " + [x.parent.time.string for x in misc if x.string == "Last Update"][0]
        except IndexError:
            last_update = "__Last Update__: None"
        try:
            files = "__Files__: " + [x.parent.a.string for x in misc if x.string == "Files"][0]
        except IndexError:
            files = "__Files__: 0"
        try:
            articles_posted = "__Articles__: " + [x.parent.a.string for x in misc if x.string == "Articles"][0]
        except IndexError:
            articles_posted = "__Articles__: 0"
        try:
            reviews = "__Reviews__: " + [x.parent.a.string for x in misc if x.string == "Reviews"][0]
        except IndexError:
            reviews = "__Reviews__: 0"

        embed.add_field(name="Stats", value=rank + "\n" + visits + "\n" + last_update + "\n" + files + "\n" + articles_posted + "\n" + reviews)

        #you may also like
        suggestionList = list()
        suggestions = soup.find(string="You may also like").parent.parent.parent.parent.find_all(class_="row clear")
        for x in suggestions:
            link = x.find("a",class_="heading")
            suggestionList.append("[" + link.string + "](" + link["href"] + ")")

        embed.add_field(name="You may also like",value=" - ".join(suggestionList))

        await bot.say(embed=embed)
        await bot.delete_message(cont.message)

    else:
        await bot.say("URL was not valid, try again with a valid url. URL must be from an existing mod page. Accepted examples: `http://www.moddb.com/mods/edain-mod`, `http://www.moddb.com/mods/rotwk-hd-edition`, ect...")

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
    except Exception:
        ChannelId = "318828760331845634"

    if message.author.id not in ignoreAutomodList and message.channel.id not in ignoreAutomodList:
        fmt = '**Auto Moderation: Deletion Detected!**\n Message by **{0.author}** was deleted, it contained: ``` {0.content} ```'
        await bot.send_message(bot.get_channel(ChannelId), fmt.format(message))

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
        await bot.ban(member, delete_message_days=0)

    try:
        channel = bot.get_channel(serverData[member.server.id]["welcome"])
    except:
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
    except:
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

    if ((message.content == userData[userID]['lastMessage'] and userData[userID]['lastMessageTime'] > c.timegm(t.gmtime()) + 2) or userData[userID]['lastMessageTime'] > c.timegm(t.gmtime())) and (userID not in ignoreAutomodList and channelID not in ignoreAutomodList) and message.content.startswith("!") == False:
        try:
            ChannelId = serverData[message.server.id]["automod"]
        except Exception:
            ChannelId = "318828760331845634"

        await bot.send_message(bot.get_channel(ChannelId), "User: {0.author} spammed message: ``` {0.content} ```".format(message))
        await bot.delete_message(message)
        userData[userID]['lastMessage'] = message.content
        userData[userID]['lastMessageTime'] = int(c.timegm(t.gmtime()) + 1)
    else:
        userData[userID]['lastMessage'] = message.content
        userData[userID]['lastMessageTime'] = int(c.timegm(t.gmtime()) + 1)

        if len(message.content) > 0:
            if message.content[0] != "!":
                userData[userID]["exp"] += random.randint(1,5)

        if message.content.startswith("<!@317619283377258497>"):
            await bot.send_message(message.channel, replyList[random.randint(0,len(replyList)-1)].format(message.author))

        if (channelID in ignoreCommandList or userID in ignoreCommandList) and message.content.startswith("!"):
            await bot.send_message(bot.get_channel("318828760331845634"), "User: **{0.author}** attempted to summon bot in channel **{0.channel.name}** with arguments: ``` {0.content} ```".format(message))
            await bot.delete_message(message)
        elif message.content.startswith("!"):
            logit(message)
            await bot.process_commands(message)

if __name__ == "__main__":
    for extension in extensions:
        try:
            bot.load_extension("cogs."+extension)
        except Exception as e:
            exc = '{} : {}'.format(type(e).__name__, e)
            print("Failed to load extension {}\n{}".format(extension.exc))

token = open("data/token.txt", "r").read()
bot.run(token)
