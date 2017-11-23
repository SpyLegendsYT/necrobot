from rings.botdata.data import Data
from discord.ext import commands
import re
from rings.help import NecroBotHelpFormatter
import discord

userData = Data.userData
serverData = Data.serverData

#prefix command
prefixes = ["n!","N!", "<@317619283377258497> "]
async def get_pre(bot, message):
    if not message.channel.is_private:
        if serverData[message.server.id]["prefix"] != "":
            return serverData[message.server.id]["prefix"]
    return prefixes

description = "The ultimate moderation bot which is also the first bot for video game modders and provides a simple economy simple, some utility commands and some fun commands."
bot = commands.Bot(command_prefix=get_pre, description=description, formatter=NecroBotHelpFormatter())

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

def has_perms(perms_level):
    def predicate(cont): 
        if cont.message.channel.is_private:
            return False

        return userData[cont.message.author.id]["perms"][cont.message.server.id] >= perms_level
          
    return commands.check(predicate)

def is_necro():
    def predicate(cont):
        return cont.message.author.id == "241942232867799040"
    return commands.check(predicate)