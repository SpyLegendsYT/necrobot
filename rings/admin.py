#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from rings.botdata.data import Data
from simpleeval import simple_eval
import inspect

userData = Data.userData
serverData = Data.serverData

class Admin():
    def __init__(self, bot):
        self.bot = bot

    def has_perms(perms_level):
        def predicate(cont):
            return userData[cont.message.author.id]["perms"][cont.message.server.id] >= perms_level and not cont.message.channel.is_private 
        return commands.check(predicate)

    def is_necro():
        def predicate(cont):
            return cont.message.author.id == "241942232867799040"
        return commands.check(predicate)

    def default_stats(self, member, server):
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

    @commands.command(pass_context = True)
    @has_perms(2)
    async def setstats(self, cont, user : discord.Member):
        """Allows server specific authorities to set the default stats for a user that might have slipped past the on_ready and on_member_join events (Permission level required: 2+ (Moderator))
         
        {usage}
        
        __Example__
        `{pre}setstats @NecroBot` - sets the default stats for NecroBot"""
        self.default_stats(user, cont.message.server)
        await self.bot.say("Stats set for user")

    @commands.command(hidden=True)
    @has_perms(6)
    async def add(self, user : discord.Member, *, equation : str):
        """Does the given pythonic equations on the given user's NecroBot balance. (Permission level required: 6+ (NecroBot Admin))
        `*` - for multiplication
        `+` - for additions
        `-` - for substractions
        `/` - for divisons
        `**` - for exponents
        `%` - for modulo
        More symbols can be used, simply research 'python math symbols'
        
        {usage}
        
        __Example__
        `{pre}add @NecroBot +400` - adds 400 to NecroBot's balance"""
        s = str(userData[user.id]["money"]) + equation
        try:
            operation = simple_eval(s)
            userData[user.id]["money"] = abs(int(operation))
            await self.bot.say(":atm: | **{}'s** balance is now **{:,}** :euro:".format(user.display_name, userData[user.id]["money"]))
        except (NameError,SyntaxError):
            await self.bot.say(":negative_squared_cross_mark: | Operation no recognized.")

    @commands.command(hidden=True)
    @has_perms(6)
    async def pm(self, ID : str, *, message : str):
        """Sends the given message to the user of the given id. It will then wait 5 minutes for an answer and print it to the channel it was called it. (Permission level required: 6+ (NecroBot Admin))
        
        {usage}
        
        __Example__
        `{pre}pm 34536534253Z6 Hello, user` - sends 'Hello, user' to the given user id and waits for a reply"""
        user = discord.utils.get(self.bot.get_all_members(), id=ID)
        if not user is None:
            send = await self.bot.send_message(user, message + "\n*You have 5 minutes to reply to the message*")
            to_edit = await self.bot.say(":white_check_mark: | **Message sent**")
            msg = await self.bot.wait_for_message(author=user, channel=send.channel, timeout=300)
            await self.bot.edit_message(to_edit, ":speech_left: | **User: {0.author}** said :**{0.content}**".format(msg))
        else:
            await self.bot.say(":negative_squared_cross_mark: | No such user.")

    @commands.command(hidden = True)
    @is_necro()
    async def test(self, ID : str):
        """Returns the name of the user or server based on the given id. Used to debug the auto-moderation feature
        
        {usage}
        
        __Example__
        `{pre}test 345345334235345` - returns the user or server name with that id"""
        user = discord.utils.get(self.bot.get_all_members(), id=ID)
        if not user is None:
            await self.bot.say("User: **{}#{}**".format(user.name, user.discriminator))
            return

        await self.bot.say("User with that ID not found.")

        server = discord.utils.get(self.bot.servers, id=ID)
        if not server is None:
            await self.bot.say("Server: **{}**".format(server.name))
            return

        await self.bot.say("Server with that ID not found")

        channel = discord.utils.get(self.bot.get_all_channels(), id=ID)
        if not channel is None:
            await self.bot.say("Channel: **{}** on **{}**".format(channel.name, channel.server.name))
            return

        await self.bot.say("Channel with that ID not found")

    @commands.command(pass_context = True, hidden=True)
    @is_necro()
    async def invites(self, cont):
        """Returns invites (if the bot has valid permissions) for each server the bot is on.
        
        {usage}"""
        for server in self.bot.servers:
            try:
                invite = await self.bot.create_invite(server)
                await self.bot.whisper("Server: " + server.name + " - " + invite.url)
            except:
                await self.bot.whisper("I don't have the necessary permissions on " + server.name + ". That server is owned by " + server.owner.name + "#" + str(server.owner.discriminator) + " (" + str(server.id) + ")")

    @commands.command(pass_context=True, hidden=True)
    @is_necro()
    async def debug(self, cont, *, code : str):
        """Evaluates code.
        
        {usage}
        
        __Example__
        `It's python code, either you know it or you shouldn't be using this command`"""
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        env = {
            'bot': self.bot,
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
            await self.bot.say(python.format(type(e).__name__ + ': ' + str(e)))
            return

def setup(bot):
    bot.add_cog(Admin(bot))