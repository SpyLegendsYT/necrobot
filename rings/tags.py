#!/usr/bin/python3.6
import discord
from discord.ext import commands
import datetime as d


class Tags():
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command = True, aliases=["t","tags"])
    @commands.guild_only()
    async def tag(self, ctx, tag : str, *tag_args):
        """The base of the tag system. Also used to summoned tags through the [tag] argument.
        
        {usage}
        
        __Example__
        `{pre}tag necro` - prints the content of the tag 'necro' given that it exists on this server"""
        tag = tag.lower()
        arg_dict = dict()
        for arg in tag_args:
            arg_dict["arg"+str(tag_args.index(arg))] = arg

        if tag in self.bot.server_data[ctx.message.guild.id]["tags"]:
            tag_content = self.bot.server_data[ctx.message.guild.id]["tags"][tag]["content"]
            try:
                await ctx.channel.send(tag_content.format(server=ctx.message.guild, member=ctx.message.author, channel=ctx.message.channel, content=ctx.message.content,**arg_dict))
                self.bot.server_data[ctx.message.guild.id]["tags"][tag]["counter"] += 1
                await self.bot.query_executer("UPDATE necrobot.Tags SET uses = uses + 1 WHERE guild_id = $1 AND name = $2", ctx.guild.id, tag)
            except KeyError as e:
                await ctx.channel.send("Expecting the following argument: {}".format(e.args[0]))
        else:
            await ctx.channel.send(":negative_squared_cross_mark: | This tag doesn't exist on this guild.")

    @tag.command(pass_context = True, name="create",aliases=["add"])
    @commands.guild_only()
    async def tag_create(self, ctx, tag, *, content):
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
        E.g: `{pre}tag test [arg0] [arg1] [arg2]` 
        
        {usage}
        
        __Example__
        `{pre}tag add test1 {guild.name} is cool` - creates a tag that will replace `{guild.name}` by the name of the server it is summoned in
        `{pre}tag add test2 {arg0} {arg1}` - creates a tag that will replace arg0 and arg1 by the arguments passed
        """
        tag = tag.lower()
        if tag not in self.bot.server_data[ctx.message.guild.id]["tags"]:
            self.bot.server_data[ctx.message.guild.id]["tags"][tag] = {'content':content.replace("'", "\'").replace('"', '\"'),'owner':ctx.message.author.id, 'created':d.datetime.today().strftime("%d - %B - %Y %H:%M"), 'counter':0}
            await self.bot.query_executer("INSERT INTO necrobot.Tags VALUES ($1, $2, $3, $4, 0, $5);", ctx.guild.id, tag, content, ctx.author.id, d.datetime.today().strftime("%d - %B - %Y %H:%M"))
            await ctx.channel.send(":white_check_mark: | Tag " + tag + " added")
        else:
            await ctx.channel.send(":negative_squared_cross_mark: | A tag with this name already exists")

    @tag.command(name="del", aliases=["remove", "delete"])
    @commands.guild_only()
    async def tag_del(self, ctx, tag):
        """Deletes the tag [tag] if the users calling the command is its owner or a Server Admin (4+)
        
        {usage}
        
        __Example__
        `{pre}tag delete necro` - removes the tag 'necro' if you are the owner of if you have a permission level of 4+"""
        tag = tag.lower()
        if tag in self.bot.server_data[ctx.message.guild.id]["tags"]:
            if ctx.message.author.id == self.bot.server_data[ctx.message.guild.id]["tags"][tag]["owner"] or self.bot.user_data[ctx.message.author.id]["perms"][ctx.message.guild.id] >= 4:
                del self.bot.server_data[ctx.message.guild.id]["tags"][tag]
                await self.bot.query_executer("DELETE FROM necrobot.Tags WHERE guild_id = $1 AND name = $2;", ctx.guild.id, tag)
                await ctx.channel.send(":white_check_mark: | Tag " + tag + " removed")
            else:
                await ctx.channel.send(":negative_squared_cross_mark: | You can't delete someone else's tag.")
        else:
            await ctx.channel.send(":negative_squared_cross_mark: | This tag doesn't exist.")

    @tag.command(name="edit", aliases=["modify"])
    @commands.guild_only()
    async def tag_edit(self, ctx, tag, *, text):
        """Replaces the content of [tag] with the [text] given. Basically works as a delete + create function but without the risk of losing the tag name ownership.
        
        {usage}
        
        __Example__
        `{pre}tag edit necro cool server` - replaces the content of the 'necro' tag with 'cool server'"""
        tag = tag.lower()
        if tag in self.bot.server_data[ctx.message.guild.id]["tags"]:
            if ctx.message.author.id == self.bot.server_data[ctx.message.guild.id]["tags"][tag]["owner"] or self.bot.user_data[ctx.message.author.id]["perms"][ctx.message.guild.id] >= 4:
                self.bot.server_data[ctx.message.guild.id]["tags"][tag]["content"] = text.replace("'", "\'").replace('"', '\"')
                await self.bot.query_executer("UPDATE necrobot.Tags SET content = $1 WHERE guild_id = $2 AND name = $3", text, ctx.guild.id, tag)
                await ctx.channel.send(":white_check_mark: | Tag " + tag + " modified")
            else:
                await ctx.channel.send(":negative_squared_cross_mark: | You can't edit someone else's tag.")
        else:
            await ctx.channel.send(":negative_squared_cross_mark: | This tag doesn't exist.")

    @tag.command(name="raw", aliases=["source"])
    @commands.guild_only()
    async def tag_raw(self, ctx, tag):
        """Returns the unformatted content of the tag [tag] so other users can see how it works.
        
        {usage}
        
        __Example__
        `{pre}raw necro` - prints the raw data of the 'necro' tag"""
        tag = tag.lower()
        if tag in self.bot.server_data[ctx.message.guild.id]["tags"]:
            await ctx.channel.send(":notebook: | Source code for " + tag + ": ```" + self.bot.server_data[ctx.message.guild.id]["tags"][tag]["content"] + "```")

    @tag.command(name="list")
    @commands.guild_only()
    async def tag_list(self, ctx):
        """Returns the list of tags present on the guild.
        
        {usage}"""
        tag_list = ", ".join(self.bot.server_data[ctx.message.guild.id]["tags"].keys()) if len(self.bot.server_data[ctx.message.guild.id]["tags"].keys()) > 0 else "None"
        await ctx.channel.send("Tags in " + ctx.message.guild.name + ": ```" + tag_list + "```")

    @tag.command(name="info")
    @commands.guild_only()
    async def tag_info(self, ctx, tag):
        """Returns information on the tag given.
        
        {usage}
        
        __Example__
        `{pre}tag info necro` - prints info for the tag 'necro'"""
        tag = tag.lower()
        tag_dict = self.bot.server_data[ctx.message.guild.id]["tags"][tag]
        embed = discord.Embed(title="__**" + tag + "**__", colour=discord.Colour(0x277b0), description="Created on " + tag_dict["created"])
        embed.add_field(name="Owner", value=ctx.message.guild.get_member(tag_dict["owner"]).mention)
        embed.add_field(name="Uses", value=tag_dict["counter"])
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

        await ctx.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Tags(bot))