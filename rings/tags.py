#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from rings.botdata.data import Data
import datetime as d

userData = Data.userData
serverData = Data.serverData

class Tags():
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context = True, invoke_without_command = True, aliases=["t","tags"])
    @commands.cooldown(5, 10, BucketType.channel)
    async def tag(self, cont, tag : str, *, tag_args : str = ""):
        """The base of the tag system. Also used to summoned tags through the [tag] argument.
        
        {usage}
        
        __Example__
        `n!tag necro` - prints the content of the tag 'necro' given that it exists on this server"""
        argDict = dict()
        argList = tag_args.split(" ")
        tag = tag.lower()
        for x in argList:
            argDict["arg"+str(argList.index(x))] = x

        if tag in serverData[cont.message.server.id]["tags"]:
            tag_content = serverData[cont.message.server.id]["tags"][tag]["content"]
            serverData[cont.message.server.id]["tags"][tag]["counter"] += 1
            await self.bot.say(tag_content.format(server=cont.message.server, member=cont.message.author, channel=cont.message.channel, content=cont.message.content,**argDict))
        else:
            await self.bot.say(":negative_squared_cross_mark: | This tag doesn't exist on this server.")

    @tag.command(pass_context = True, name="create",aliases=["add"])
    async def tag_create(self, cont, tag, *, content):
        """Assigns the [text] passed through to the tag named [name]. A few reserved keywords can be used to render the tag dynamic.
        
        `{server.keyword}`
        Represents the server
        __Keywords__
        `name` - name of the server
        `id` - id of the server
        `created_at` - UTC tag of the creation time of the server
        `member_count` - returns the number of member
        
        `{member.keyword}`
        Represents the user that called the command
        __Keywords__
        `display_name` - the user nick if they have one, else the user's username
        `name` - the user's username
        `discriminator` - the user's discriminator (the 4 digits at the end)
        `joined_at` - specifies at what time the user joined the server
        `id` - user's id
        `mention` - mentions the user
        `created_at` - returns the creation time of the account
        
        `{channel.keyword}`
        Represents the channel the tag was summoned in
        __Keywords__
        `name` - channel name
        `id` - channel id
        `topic` - the channel's topic
        `mention` - returns a mention of the channel
        
        `{content}`
        Represents the content of the message
        
        `{argx}`
        Represents an argument you pass into the tag, replace x by the argument number starting from 0.
        E.g: `n!tag test [arg0] [arg1] [arg2]` 
        
        {usage}
        
        __Example__
        `n!tag add test1 {server.name} is cool` - creates a tag that will replace `{server.name}` by the name of the server it is summoned in
        `n!tag add test2 {arg0} {arg1}` - creates a tag that will replace arg0 and arg1 by the arguments passed
        """
        tag = tag.lower()
        if tag not in serverData[cont.message.server.id]["tags"]:
            serverData[cont.message.server.id]["tags"][tag] = {'content':content.replace("'", "\'").replace('"', '\"'),'owner':cont.message.author.id, 'created':d.datetime.today().strftime("%d - %B - %Y %H:%M"), 'counter':0}
            await self.bot.say(":white_check_mark: | Tag " + tag + " added")
        else:
            await self.bot.say(":negative_squared_cross_mark: | A tag with this name already exists")

    @tag.command(pass_context = True, name="del", aliases=["remove", "delete"])
    async def tag_del(self, cont, tag):
        """Deletes the tag [tag] if the users calling the command is its owner or a Server Admin (4+)
        
        {usage}
        
        __Example__
        `n!tag delete necro` - removes the tag 'necro' if you are the owner of if you have a permission level of 4+"""
        tag = tag.lower()
        if tag in serverData[cont.message.server.id]["tags"]:
            if cont.message.author.id == serverData[cont.message.server.id]["tags"][tag]["owner"] or userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4:
                del serverData[cont.message.server.id]["tags"][tag]
                await self.bot.say(":white_check_mark: | Tag " + tag + " removed")
            else:
                await self.bot.say(":negative_squared_cross_mark: | You can't delete someone else's tag.")
        else:
            await self.bot.say(":negative_squared_cross_mark: | This tag doesn't exist.")

    @tag.command(pass_context = True, name="edit", aliases=["modify"])
    async def tag_edit(self, cont, tag, *, text):
        """Replaces the content of [tag] with the [text] given. Basically works as a delete + create function but without the risk of losing the tag name ownership.
        
        {usage}
        
        __Example__
        `n!tag edit necro cool server` - replaces the content of the 'necro' tag with 'cool server'"""
        tag = tag.lower()
        if tag in serverData[cont.message.server.id]["tags"]:
            if cont.message.author.id == serverData[cont.message.server.id]["tags"][tag]["owner"] or userData[cont.message.author.id]["perms"][cont.message.server.id] >= 4:
                serverData[cont.message.server.id]["tags"][tag]["content"] = text.replace("'", "\'").replace('"', '\"')
                await self.bot.say(":white_check_mark: | Tag " + tag + " modified")
            else:
                await self.bot.say(":negative_squared_cross_mark: | You can't edit someone else's tag.")
        else:
            await self.bot.say(":negative_squared_cross_mark: | This tag doesn't exist.")

    @tag.command(pass_context = True, name="raw", aliases=["source"])
    async def tag_raw(self, cont, tag):
        """Returns the unformatted content of the tag [tag] so other users can see how it works.
        
        {usage}
        
        __Example__
        `n!raw necro` - prints the raw data of the 'necro' tag"""
        tag = tag.lower()
        if tag in serverData[cont.message.server.id]["tags"]:
            await self.bot.say(":notebook: | Source code for " + tag + ": ```" + serverData[cont.message.server.id]["tags"][tag]["content"] + "```")

    @tag.command(pass_context = True, name="list")
    async def tag_list(self, cont):
        """Returns the list of tags present on the server.
        
        {usage}"""
        await self.bot.say("Tags in " + cont.message.server.name + ": ```" + ", ".join(serverData[cont.message.server.id]["tags"].keys()) + "```")

    @tag.command(pass_context = True, name="info")
    async def tag_info(self, cont, tag):
        """Returns information on the tag given.
        
        {usage}
        
        __Example__
        `n!tag info necro` - prints info for the tag 'necro'"""
        tag = tag.lower()
        tag_dict = serverData[cont.message.server.id]["tags"][tag]
        embed = discord.Embed(title="__**" + tag + "**__", colour=discord.Colour(0x277b0), description="Created on " + tag_dict["created"])
        embed.add_field(name="Owner", value=cont.message.server.get_member(tag_dict["owner"]).mention)
        embed.add_field(name="Uses", value=tag_dict["counter"])
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

        await self.bot.say(embed=embed)



def setup(bot):
    bot.add_cog(Tags(bot))