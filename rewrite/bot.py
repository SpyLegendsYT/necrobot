import discord
from discord.ext import commands
from rings.utils.help import NecroBotHelpFormatter
from rings.utils.utils import is_necro
import time


class NecroBot(commands.Bot):
    def __init__(self, user_data, server_data, settings, ERROR_LOG):
        self.command_prefix = get_pre
        self.description = ["A bot for moderation and LOTR"]
        self.formatter = NecroBotHelpFormatter()
        self.uptime_start = time.time()
        self.user_data = user_data
        self.sever_data = server_data
        self.settings = settings
        self.ERROR_LOG = ERROR_LOG

extensions = [
    "hunger",
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
    "admin",
    "decisions"
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
    server_id = message.server.id

    if message.content.startswith(tuple(prefixes)):
        return True
    if server_data[server_id]["prefix"] != "" and message.content.startswith(server_data[server_id]["prefix"]):
        return True

    return False

def is_spam(message):
    user_id = message.author.id
    channel_id = message.channel.id
    server_id = message.server.id

    if server_data[server_id]["automod"] == "" or startswith_prefix(message):
        return False
    if user_id in server_data[server_id]["ignoreAutomod"] or channel_id in server_data[server_id]["ignoreAutomod"]:
        return False
    if message.content.lower() == user_data[user_id]['lastMessage'].lower() and user_data[user_id]['lastMessageTime'] > c.timegm(t.gmtime()) + 2:
        return True
    if user_data[user_id]['lastMessageTime'] > c.timegm(t.gmtime()) + 1:
        return False

    return False

def is_allowed_summon(message):
    user_id = message.author.id
    channel_id = message.channel.id
    server_id = message.server.id

    if user_data[user_id]["perms"][server_id] >= 4:
        return True
    if user_id in server_data[server_id]["ignoreCommand"] or channel_id in server_data[server_id]["ignoreCommand"]:
        return False

    return True

async def save():
    with open(default_path + "rings/botdata/userdata.csv","w",newline="") as csvfile:
        Awriter = csv.writer(csvfile)
        for x in user_data:
            warningList = ",".join(user_data[x]["warnings"])
            Awriter.writerow([x,user_data[x]["money"],user_data[x]["daily"],user_data[x]["title"],user_data[x]["exp"],user_data[x]["perms"],warningList])

    with open(default_path + "rings/botdata/setting.csv","w",newline="") as csvfile:
        Awriter = csv.writer(csvfile)
        Awriter.writerow([starboard_messages])
        for x in server_data:
            try:
                selfRolesList = ",".join(server_data[x]["selfRoles"])
                automodList = ",".join(server_data[x]["ignoreAutomod"])
                commandList = ",".join(server_data[x]["ignoreCommand"])
                Awriter.writerow([x,server_data[x]["mute"],server_data[x]["automod"],server_data[x]["welcome-channel"],selfRolesList,commandList,automodList,server_data[x]["welcome"],server_data[x]["goodbye"],server_data[x]["tags"], server_data[x]["prefix"], server_data[x]["broadcast"], server_data[x]["broadcast-channel"], server_data[x]["starboard"], server_data[x]["starboard-count"]])
            except KeyError:
                print(x)
                Awriter.writerow([x,"","","","","","","Welcome {member} to {server}!","Leaving so soon? We'll miss you, {member}!","{}","","","","",""])

    await bot.send_message(bot.get_channel(bot.ERROR_LOG), "Saved at " + str(t.asctime(t.localtime(t.time()))))

async def broadcast():
    for x in server_data:
        if server_data[x]["broadcast"] != "" and server_data[x]["broadcast-channel"] != "":
            await bot.send_message(bot.get_channel(server_data[x]["broadcast-channel"]), server_data[x]["broadcast"])

# *****************************************************************************************************************
#  Background Tasks
# *****************************************************************************************************************
async def hourly_task():
    await bot.wait_until_ready()
    while not bot.is_closed:
        await asyncio.sleep(3600) # task runs every hour
        await save()
        await broadcast()

# *****************************************************************************************************************
#  Cogs Commands
# *****************************************************************************************************************
@bot.command(hidden=True)
@is_necro()
async def load(ctx, extension_name : str):
    """Loads the extension name if in NecroBot's list of rings.
    
    {usage}"""
    try:
        bot.load_extension("rings." + extension_name)
    except (AttributeError,ImportError) as e:
        await ctx.channel.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await ctx.channel.send("{} loaded.".format(extension_name))

@bot.command(hidden=True)
@is_necro()
async def unload(ctx, extension_name : str):
    """Unloads the extension name if in NecroBot's list of rings.
     
    {usage}"""
    bot.unload_extension("rings." + extension_name)
    await ctx.channel.send("{} unloaded.".format(extension_name))

@bot.command(hidden=True)
@is_necro()
async def reload(ctx, extension_name : str):
    """Unload and loads the extension name if in NecroBot's list of rings.
     
    {usage}"""
    bot.unload_extension("rings." + extension_name)
    try:
        bot.load_extension("rings." + extension_name)
    except (AttributeError,ImportError) as e:
        await ctx.channel.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await ctx.channel.send("{} reloaded.".format(extension_name))

# *****************************************************************************************************************
# Bot Smith Commands
# *****************************************************************************************************************
@bot.command()
@is_necro()
async def off(ctx):
    """Saves all the data and terminate the bot. (Permission level required: 7+ (The Bot Smith))
     
    {usage}"""
    await save()
    await bot.get_channel("318465643420712962").send("**Bot Offline**")
    await bot.logout()

@bot.command(name="save")
@is_necro()
async def command_save(ctx):
    """Saves all the data. (Permission level required: 7+ (The Bot Smith))
     
    {usage}"""
    msg = await ctx.channel.send("**Saving Data...**")
    try:
        await save()
        await msg.edit_message("**Data saved**")
    except KeyError:
        await msg.edit_message("**Failed to save Data**")