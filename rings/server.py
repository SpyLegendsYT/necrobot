#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from rings.botdata.data import Data
import re

userData = Data.userData
serverData = Data.serverData
roleList = [["Helper",discord.Colour.teal()],["Moderator",discord.Colour.orange()],["Semi-Admin",discord.Colour.darker_grey()],["Admin",discord.Colour.blue()],["Server Owner",discord.Colour.magenta()],["NecroBot Admin",discord.Colour.dark_green()],["The Bot Smith",discord.Colour.dark_red()]]

class Server():
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

    def allmentions(self, cont, msg):
        myList = []
        mentions = msg.split(" ")
        for x in mentions:
            ID = re.sub('[<>!#@]', '', x)
            if not self.bot.get_channel(ID) is None:
                channel = self.bot.get_channel(ID)
                myList.append(channel)
            elif not cont.message.server.get_member(ID) is None:
                member = cont.message.server.get_member(ID)
                myList.append(member)

        return myList

    @commands.command(pass_context = True)
    async def perms(self, cont, user : discord.Member, level : int):
        """Sets the NecroBot permission level of the given user, you can only set permission levels lower than your own. Permissions reset if you leave the server(Permission level required: 4+ (Server Admin))
         
        {usage}
        
        __Example__
        `{pre}perms @NecroBot 5` - set the NecroBot permission level to 5"""
        if userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4 and userData[cont.message.author.id]["perms"][cont.message.server.id] > level:
            userData[user.id]["perms"][cont.message.server.id] = level
            await self.bot.say(":white_check_mark: | All good to go, **"+ user.name + "** now has permission level **"+ str(level) + "**")
        elif userData[cont.message.author.id]["perms"][cont.message.server.id] <= level:
            await self.bot.say(":negative_squared_cross_mark: | You do not have the required NecroBot permission to grant this permission level")
        else:
            await self.bot.say("::negative_squared_cross_mark: | You do not have the required NecroBot permissions to use this command.")

    @commands.group(pass_context = True, invoke_without_command = True)
    @has_perms(4)
    async def automod(self, cont):
        """Used to manage the list of channels and user ignored by the bot's automoderation system. If no subcommand is called it will print out the list of ignored Users (**U**) and the list of ignored Channels (**C**). The automoderation feature tracks the edits made by users to their own messages and the deleted messages, printing them in the server's automod channel. Set the automod channel using `{pre}settings automod` (Permission level required: 4+ (Server Admin))
         
        {usage}"""
        myList = []
        for x in serverData[cont.message.server.id]["ignoreAutomod"]:
            try:
                myList.append("C: "+self.bot.get_channel(x).name)
            except AttributeError:
                try:
                    myList.append("U: "+cont.message.server.get_member(x).name)
                except AttributeError:
                    pass

        await self.bot.say("Channels(**C**) and Users(**U**) ignored by auto moderation: ``` "+str(myList)+" ```")

    @automod.command(pass_context = True, name="add")
    async def automod_add(self, cont, *, mentions : str):
        """Adds a user or channel to the list ignored by the bot's automoderation feature. Add users or channels by mentioning them in the [mentions] argument. (Permission level required: 4+ (Server Admin))
         
        {usage}
        
        __Example__
        `{pre}automod add #channel #channel2 @NecroBot` - have NecroBot ignore moderation from user 'NecroBot' and channels 'channel' and 'channel2'"""
        myList = self.allmentions(cont, mentions)
        for x in myList:
            if x.id not in serverData[cont.message.server.id]["ignoreAutomod"]:
                serverData[cont.message.server.id]["ignoreAutomod"].append(x.id)
                await self.bot.say(":white_check_mark: | **"+ x.name +"** will be ignored by the bot's automoderation.")
            else:
                await self.bot.say(":negative_squared_cross_mark: | **"+ x.name +"** is already ignored.")

    @automod.command(pass_context = True, name="del")
    async def automod_del(self, cont, *, mentions : str):
        """Removes a user or channel from the list ignored by the bot's automoderation feature. Remove users and channels by mentioning them in the [mentions] argument. (Permission level required: 4+ (Server Admin))
         
        {usage}
        
        __Example__
        `{pre}automod del #channel #channel2 @NecroBot` - have NecroBot no longer ignore moderation from user 'NecroBot' and channels 'channel' and 'channel2'"""
        myList = self.allmentions(cont, mentions)
        for x in myList:
            if x.id in serverData[cont.message.server.id]["ignoreAutomod"]:
                serverData[cont.message.server.id]["ignoreAutomod"].remove(x.id)
                await self.bot.say(":white_check_mark: | **"+ x.name +"** will no longer be ignored by the bot's automoderation.")
            else:
                await self.bot.say(":negative_squared_cross_mark: | **"+ x.name +"** is not ignored.")

    @commands.group(pass_context=True, invoke_without_command = True)
    @has_perms(4)
    async def ignore(self, cont):
        """Used to manage the list of channels and user ignored by the bot's command system. If no subcommand is called it will print out the list of ignored Users (**U**) and the list of ignored Channels (**C**). User and channels in the list will not be able to use commands. (Permission level required: 4+ (Server Admin))
         
        {usage}"""
        myList = []
        for x in serverData[cont.message.server.id]["ignoreCommand"]:
            try:
                myList.append("C: "+self.bot.get_channel(x).name)
            except AttributeError:
                try:
                    myList.append("U: "+cont.message.server.get_member(x).name)
                except AttributeError:
                    pass

        await self.bot.say("Channels(**C**) and Users(**U**) ignored by NecroBot: ``` "+str(myList)+" ```")

    @ignore.command(pass_context = True, name="add")
    async def ignore_add(self, cont, *, mentions : str):
        """Adds a user or channel to the list ignored by the bot's command system. Add users or channels by mentioning them in the [mentions] argument. (Permission level required: 4+ (Server Admin))
         
        {usage}
        
        __Example__
        `{pre}ignore add #channel #channel2 @NecroBot` - have NecroBot ignore commands from user 'NecroBot' and channels 'channel' and 'channel2'"""
        myList = self.allmentions(cont, mentions)
        for x in myList:
            if x.id not in serverData[cont.message.server.id]["ignoreCommand"]:
                serverData[cont.message.server.id]["ignoreCommand"].append(x.id)
                await self.bot.say(":white_check_mark: | **"+ x.name +"** will be ignored by the bot.")
            else:
                await self.bot.say(":negative_squared_cross_mark: | **"+ x.name +"** is already ignored.")

    @ignore.command(pass_context = True, name="del")
    async def ignore_del(self, cont, *, mentions : str):
        """Removes a user or channel from the list ignored by the bot's command system. Remove users and channels by mentioning them in the [mentions] argument. (Permission level required: 4+ (Server Admin))
         
        {usage}
        
        __Example__
        `{pre}ignore add #channel #channel2 @NecroBot` - have NecroBot ignore commands from user 'NecroBot' and channels 'channel' and 'channel2'"""
        myList = self.allmentions(cont, mentions)
        for x in myList:
            if x.id in serverData[cont.message.server.id]["ignoreCommand"]:
                serverData[cont.message.server.id]["ignoreCommand"].remove(x.id)
                await self.bot.say(":white_check_mark: | **"+ x.name +"** will no longer be ignored by the bot.")
            else:
                await self.bot.say(":negative_squared_cross_mark: | **"+ x.name +"** is not ignored.")

    @commands.group(invoke_without_command = True, aliases=["setting"])
    @has_perms(5)
    async def settings(self):
        """Used to decide of the NecroBot settings for the server. Useless without a subcommand. (Permission level required: 5+ (Server Owner))
         
        {usage}"""
        await self.bot.say(":negative_squared_cross_mark: | Please pass in a valid subcommand. (welcome, welcome-channel, goodbye, mute, automod)")

    @settings.command(pass_context = True, name="mute")
    async def settings_mute(self, cont, *, role=""):
        """Sets the mute role for this server to [role], this is used for the `mute` command, it is the role assigned by the command to the user. Make sure to spell the role correctly, the role name is case sensitive. It is up to the server authorities to set up the proper permissions for the chosen mute role. (Permission level required: 5+ (Server Owner))
         
        {usage}
        
        __Example__
        `{pre}settings mute Token Mute Role` - set the mute role to be the role named 'Token Mute Role'
        `{pre}settings mute` - resets the mute role and disables the `mute` command."""
        if role == "":
            serverData[cont.message.server.id]["mute"] = ""
            await self.bot.say(":white_check_mark: | Reset mute role")
            return

        if not discord.utils.get(cont.message.server.roles, name=role) is None:
            await self.bot.say(":white_check_mark: | Okay, the mute role for your server will be " + role)
            serverData[cont.message.server.id]["mute"] = role
        else:
            await self.bot.say(":negative_squared_cross_mark: | No such role, make sure the role is spelled correctly, the role name is case-sensitive")

    @settings.command(pass_context = True, name="welcome-channel")
    async def settings_welcome_channel(self, cont, channel : discord.Channel = ""):
        """Sets the welcome channel to [channel], the [channel] argument should be a channel mention. The welcome message for users will be sent there. (Permission level required: 5+ (Server Owner))
         
        {usage}
        
        __Example__
        `{pre}settings welcome-channel #channel` - set the welcome messages to be sent to 'channel'
        `{pre}settings welcome-channel` - disables welcome messages"""
        if channel == "":
            serverData[cont.message.server.id]["welcome-channel"] = ""
            await self.bot.say(":white_check_mark: | Welcome messages **disabled**")
        else:
            await self.bot.say(":white_check_mark: | Okay, users will get their welcome message in " + channel.mention + " from now on.")
            serverData[cont.message.server.id]["welcome-channel"] = channel.id

    @settings.command(pass_context = True, name="automod-channel")
    async def settings_automod_channel(self, cont, channel : discord.Channel = ""):
        """Sets the automoderation channel to [channel], [channel] argument should be a channel mention. All the auto-moderation related messages will be sent there. (Permission level required: 5+ (Server Owner))
         
        {usage}
        
        __Example__
        `{pre}settings automod-channel #channel` - set the automoderation messages to be sent to channel 'channel'
        `{pre}settings automod-channel` - disables automoderation for the entire server"""
        if channel == "":
            serverData[cont.message.server.id]["automod"] = ""
            await self.bot.say(":white_check_mark: | Auto-moderation **disabled**")
        else:
            await self.bot.say(":white_check_mark: | Okay, all automoderation messages will be posted in " + channel.mention + " from now on.")
            serverData[cont.message.server.id]["automod"] = channel.id

    @settings.command(pass_context = True, name="welcome")
    async def settings_welcome(self, cont, *, message=""):
        r"""Sets the welcome message (aka the message sent to the welcome channel when a new user joins), you can format the message to mention the user and server. `{member}` will be replaced by a mention of the member and `{server}` will be replaced by the server name. To add emojis you need to add a backslash `\` before every semi-colon `:` (e.g `\:smiley_face\:`) (Permission level required: 5+ (Server Owner))
         
        {usage}
        
        __Example__
        `{pre}settings welcome Hello {member} \:wave\:` - sets the welcome message to be 'Hello {member} :wave:' with `{member}` being replaced by the new member's name"""
        if message == "":
            await self.bot.say(":white_check_mark: | Welcome message reset and disabled")
        else:
            message = message.replace("\\","")
            await self.bot.say(":white_check_mark: | Your server's welcome message will be: " + message)

        serverData[cont.message.server.id]["welcome"] = message

    @settings.command(pass_context = True, name="goodbye")
    async def settings_goodbye(self, cont, *, message):
        r"""Sets the goodbye message (aka the message sent to the welcome channel when a user leaves), you can format the message to mention the user and server. `{member}` will be replaced by a mention of the member and `{server}` will be replaced by the server name. To add emojis you need to add a backslash `\` before every semi-colon `:` (e.g `\:smiley_face\:`) (Permission level required: 5+ (Server Owner))
         
        {usage}
        
        __Example__
        `{pre}settings goodbye Goodbye {member} \:wave\:` - sets the goodbye message to be 'Goodbye {member} :wave:' with `{member}` being replaced by the new member's name"""
        
        if message == "":
            await self.bot.say(":white_check_mark: | Goodbye message reset and disabled")
        else:
            message = message.replace("\\","")
            await self.bot.say(":white_check_mark: | Your server's goodbye message will be: \n" + message)

        serverData[cont.message.server.id]["goodbye"] = message

    @settings.command(pass_context = True, name="prefix")
    async def settings_prefix(self, cont, *, prefix=""):
        """Sets the bot to only respond to the given prefix. If no prefix is given it will reset it to NecroBot's deafult list of prefixes: `{pre}`, `N!` or `@NecroBot `

        {usage}

        __Example__
        `{pre}settings prefix bob! potato` - sets the prefix to be `bob! potato ` so a command like `{pre}cat` will now be summoned like this `bob! potato cat`
        `{pre}settings prefix` - resets the prefix to NecroBot's default list"""
        if prefix == "":
            serverData[cont.message.server.id]["prefix"] = ""
            await self.bot.say(":white_check_mark: | Custom prefix reset")
        else:
            serverData[cont.message.server.id]["prefix"] = prefix
            await self.bot.say(":white_check_mark: | Server prefix is now **{}**".format(prefix))

    @settings.command(pass_context = True, name="info")
    async def settings_info(self, cont):
        """Creates a rich embed of the server settings

        {usage}"""
        server = serverData[cont.message.server.id]
        embed = discord.Embed(title="__**Server Settings**__", colour=discord.Colour(0x277b0), description="Info on the NecroBot settings for this server")
        embed.add_field(name="Automod Channel", value=self.bot.get_channel(server["automod"]) if server["automod"] != "" else "Disabled")
        embed.add_field(name="Welcome Channel", value=self.bot.get_channel(server["welcome-channel"]) if server["welcome-channel"] != "" else "Disabled")
        embed.add_field(name="Welcome Message", value=server["welcome"] if server["welcome"] != "" else "None", inline=False)
        embed.add_field(name="Goodbye Message", value=server["goodbye"] if server["goodbye"] != "" else "None", inline=False)
        embed.add_field(name="Mute Role", value=server["mute"] if server["mute"] != "" else "Disabled")
        embed.add_field(name="Prefix", value=server["prefix"] if server["prefix"] != "" else "`n!`")

        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

        await self.bot.say(embed=embed)

    @commands.group(pass_context=True, invoke_without_command = True)
    async def giveme(self, cont, *, role):
        """Gives the user the role if it is part of this Server's list of self assignable roles. If the user already has the role it will remove it. **Roles names are case sensitive**
         
        {usage}
        
        __Example__
        `{pre}giveme Good` - gives or remove the role 'Good' to the user if it is in the list of self assignable roles"""
        if role in serverData[cont.message.server.id]["selfRoles"]:
            role_obj = discord.utils.get(cont.message.server.roles, name=role)
            if discord.utils.get(cont.message.author.roles, name=role) is None:
                await self.bot.add_roles(cont.message.author, role_obj)
                await self.bot.say(":white_check_mark: | Role " + role_obj.name + " added.")
            else:
                await self.bot.remove_roles(cont.message.author, role_obj)
                await self.bot.say(":white_check_mark: | Role " + role_obj.name + " removed.")

        else:
            await self.bot.say(":negative_squared_cross_mark: | Role not self assignable")

    @giveme.command(pass_context=True, name="add")
    @has_perms(4)
    async def giveme_add(self, cont, *, role):
        """Adds [role] to the list of the server's self assignable roles. (Permission level required: 4+ (Server Admin))
         
        {usage}
        
        __Example__
        `{pre}giveme add Good` - adds the role 'Good' to the list of self assignable roles"""
        if not discord.utils.get(cont.message.server.roles, name=role) is None:
            serverData[cont.message.server.id]["selfRoles"].append(role)
            await self.bot.say(":white_check_mark: | Added role " + role + " to list of self assignable roles.")
        else:
            await self.bot.say(":negative_squared_cross_mark: | No such role exists")

    @giveme.command(pass_context = True, name="del")
    @has_perms(4)
    async def giveme_del(self, cont, *, role):
        """Removes [role] from the list of the server's self assignable roles. (Permission level required: 4+ (Server Admin)
        
        {usage}
        
        __Example__
        `{pre}giveme del Good` - removes the role 'Good' from the list of self assignable roles"""
        if role in serverData[cont.message.server.id]["selfRoles"]:
            serverData[cont.message.server.id]["selfRoles"].remove(role)
            await self.bot.say(":white_check_mark: | Role " + role + " removed from self assignable roles")
        else:
            await self.bot.say(":negative_squared_cross_mark: | Role not in self assignable list")

    @giveme.command(pass_context = True, name="info")
    async def giveme_info(self, cont):
        """List the server's self assignable roles. 
        
        {usage}"""
        await self.bot.say("List of Self Assignable Roles:" + "\n- ".join(serverData[cont.message.server.id]["selfRoles"]))

    @commands.command(pass_context = True, enabled=False)
    @has_perms(5)
    async def setroles(self, cont):
        """Sets the NecroBot roles for this server and assigns them to user based on their NecroBot permission level. Permission level required: 5+ (Server Owner))
         
        {usage}"""
        for x in roleList:
            if discord.utils.get(cont.message.server.roles, name=x[0]) is None:
                new_role = await self.bot.create_role(cont.message.server, name=x[0], colour=x[1], mentionable=True)
                await self.bot.say(":white_check_mark: | Role " + x[0] + " created")
            else:
                await self.bot.say(":negative_squared_cross_mark: | A role with the name " + x[0] + " already exists.")
        await asyncio.sleep(5)
        await self.bot.purge_from(bot.get_channel(cont.message.channel.id), limit=8)
        await self.bot.say(":white_check_mark: | **Roles created**")

        for x in cont.message.server.members:
            role = userData[x.id]["perms"][cont.message.server.id]-1
            await self.bot.add_roles(x, discord.utils.get(cont.message.server.roles, name=roleList[role][0]))
        await self.bot.say(":white_check_mark: | **Roles assigned based on users' NecroBot permission level.**")

def setup(bot):
    bot.add_cog(Server(bot))