#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from rings.botdata.data import Data

userData = Data.userData
serverData = Data.serverData

class Tags():
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context = True, invoke_without_command = True, aliases=["t","tags"])
    @commands.cooldown(5, 10, BucketType.channel)
    async def tag(self, cont, *, tag : str):
        """The base of the tag system. Also used to summoned tags through the [tag] argument."""
        if tag in serverData[cont.message.server.id]["tags"]:
            await self.bot.say(serverData[cont.message.server.id]["tags"][tag]["content"].format(server=cont.message.server, member=cont.message.author, channel=cont.message.channel, content=cont.message.content))
        else:
            await self.bot.say(":negative_squared_cross_mark: | This tag doesn't exist on this server.")

    @tag.command(pass_context = True, name="create",aliases=["add"])
    async def tag_create(self, cont, name, *, text):
        """Assigns the [text] passed through to the tag named [name]. A few reserved keywords can be used to render the tag dynamic.

        `{server.[keyword]}`
        Represents the server
        __Keywords__
        `name` - name of the server
        `id` - id of the server
        `created_at` - UTC tag of the creation time of the server
        `member_count` - returns the number of member

        `{member.[keyword]}`
        Represents the user that called the command
        __Keywords__
        `display_name` - the user nick if they have one, else the user's username
        `name` - the user's username
        `discriminator` - the user's discriminator (the 4 digits at the end)
        `joined_at` - specifies at what time the user joined the server
        `id` ` user's id
        `mention` - mentions the user
        `created_at` - returns the creation time of the account

        `{channel.[keyword]}`
        Represents the channel the tag was summoned in
        __Keywords__
        `name` - channel name
        `id` - channel id
        `topic` - the channel's topic
        `mention` - returns a mention of the channel

        `{content}`
        Represents the content of the message
        """
        if name not in serverData[cont.message.server.id]["tags"]:
            serverData[cont.message.server.id]["tags"][name] = {'content':text.replace("'", "\'").replace('"', '\"'),'owner':cont.message.author.id}
            await self.bot.say("Tag " + name + " added")
        else:
            await self.bot.say(":negative_squared_cross_mark: | A tag with this name already exists")

    @tag.command(pass_context = True, name="del", aliases=["remove"])
    async def tag_del(self, cont, tag):
        """Deletes the tag [tag] if the users calling the command is its owner or a Server Admin (4+)"""
        if tag in serverData[cont.message.server.id]["tags"]:
            if cont.message.author.id == serverData[cont.message.server.id]["tags"][tag]["owner"] or userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4:
                del serverData[cont.message.server.id]["tags"][tag]
                await self.bot.say("Tag " + tag + " removed")
            else:
                await self.bot.say(":negative_squared_cross_mark: | You can't delete someone else's tag.")
        else:
            await self.bot.say(":negative_squared_cross_mark: | This tag doesn't exist.")

    @tag.command(pass_context = True, name="edit", aliases=["modify"])
    async def tag_edit(self, cont, tag, *, text):
        """Replaces the content of [tag] with the [text] given. Basically works as a delete + create function but without the risk of losing the tag name ownership."""
        if tag in serverData[cont.message.server.id]["tags"]:
            if cont.message.author.id == serverData[cont.message.server.id]["tags"][tag]["owner"] or userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4:
                serverData[cont.message.server.id]["tags"][tag]["content"] = text.replace("'", "\'").replace('"', '\"')
                await self.bot.say("Tag " + tag + " modified")
            else:
                await self.bot.say(":negative_squared_cross_mark: | You can't edit someone else's tag.")
        else:
            await self.bot.say(":negative_squared_cross_mark: | This tag doesn't exist.")

    @tag.command(pass_context = True, name="raw", aliases=["source"])
    async def tag_raw(self, cont, tag):
        """Returns the unformatted content of the tag [tag] so other users can see how it works."""
        if tag in serverData[cont.message.server.id]["tags"]:
            await self.bot.say(":notebook: | Source code for " + tag + ": ```" + serverData[cont.message.server.id]["tags"][tag]["content"] + "```")

    @tag.command(pass_context = True, name="list")
    async def tag_list(self, cont):
        """Returns the list of tags present on the server"""
        await self.bot.say("Tags in " + cont.message.server.name + ": ```" + ", ".join(serverData[cont.message.server.id]["tags"].keys()) + "```")


def setup(bot):
    bot.add_cog(Tags(bot))