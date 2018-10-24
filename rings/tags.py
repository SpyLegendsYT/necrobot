import discord
from discord.ext import commands

import datetime as d

class Tag(commands.Converter):
    async def convert(self, ctx, argument):
        argument = argument.lower()
        if argument in ctx.bot.server_data[ctx.guild.id]["tags"]:
            return argument
        elif argument in ctx.bot.server_data[ctx.guild.id]["aliases"]:
            return ctx.bot.server_data[ctx.guild.id]["aliases"][argument]
        else:
            raise commands.BadArgument(f"Tag {argument} doesn't exist in server.")

class Tags():
    def __init__(self, bot):
        self.bot = bot
        self.restricted = ("list", "raw", "add", "edit", "info", "delete", "alias")

    def is_tag_owner(self, ctx, tag):
        if ctx.author.id == self.bot.server_data[ctx.guild.id]["tags"][tag]["owner"]:
            return True
        elif self.bot.user_data[ctx.author.id]["perms"][ctx.guild.id] >= 4:
            return True
        else:
            raise commands.CheckFailure("You don't have permissions to modify this tag")

    @commands.group(invoke_without_command = True, aliases=["t","tags"])
    @commands.guild_only()
    async def tag(self, ctx, tag : Tag, *tag_args):
        """The base of the tag system. Also used to summoned tags through the [tag] argument.
        
        {usage}
        
        __Example__
        `{pre}tag necro` - prints the content of the tag 'necro' given that it exists on this server"""
        arg_dict = dict()
        for arg in tag_args:
            arg_dict["arg"+str(tag_args.index(arg))] = arg

        tag_content = self.bot.server_data[ctx.guild.id]["tags"][tag]["content"]
        try:
            await ctx.send(tag_content.format(server=ctx.guild, member=ctx.author, channel=ctx.channel, content=ctx.message.content,**arg_dict))
            self.bot.server_data[ctx.guild.id]["tags"][tag]["counter"] += 1
            await self.bot.query_executer("UPDATE necrobot.Tags SET uses = uses + 1 WHERE guild_id = $1 AND name = $2", ctx.guild.id, tag)
        except KeyError as e:
            await ctx.send(f"Expecting the following argument: {e.args[0]}")

    @tag.command(name="add")
    @commands.guild_only()
    async def tag_add(self, ctx, tag, *, content):
        """Assigns the [text] passed through to the tag named [name]. A few reserved keywords can be used to render the 
        tag dynamic.
        
        `{server.keyword}`
        Represents the server
        __Keywords__
        `name` - name of the server
        `id` - id of the server
        `created_at` - UTC tag of the creation time of the server
        `member_count` - returns the number of member
        
        `{member.keyword}`
        Represents the user that called the tag
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
        if tag in self.restricted:
            await ctx.send(":negative_squared_cross_mark: | Tag not created, tag name is a reserved keyword")
        elif tag not in self.bot.server_data[ctx.guild.id]["tags"]:
            self.bot.server_data[ctx.guild.id]["tags"][tag] = {'content':content,'owner':ctx.author.id, 'created':d.datetime.today().strftime("%d - %B - %Y %H:%M"), 'counter':0}
            await self.bot.query_executer("INSERT INTO necrobot.Tags VALUES ($1, $2, $3, $4, 0, $5)", ctx.guild.id, tag, content, ctx.author.id, d.datetime.today().strftime("%d - %B - %Y %H:%M"))
            await ctx.send(f":white_check_mark: | Tag {tag} added")
        else:
            await ctx.send(":negative_squared_cross_mark: | A tag with this name already exists")

    @tag.group(name="delete")
    @commands.guild_only()
    async def tag_del(self, ctx, tag : Tag):
        """Deletes the tag [tag] if the users calling the command is its owner or a Server Admin (4+)
        
        {usage}
        
        __Example__
        `{pre}tag delete necro` - removes the tag 'necro' if you are the owner of if you have a permission level of 4+"""
        self.is_tag_owner(ctx, tag)

        del self.bot.server_data[ctx.guild.id]["tags"][tag]
        await self.bot.query_executer("DELETE FROM necrobot.Tags WHERE guild_id = $1 AND name = $2", ctx.guild.id, tag)
        for alias, tag_name in self.bot.server_data[ctx.guild.id]["aliases"].items():
            if tag_name == tag:
                del self.bot.server_data[ctx.guild.id]["aliases"][alias]
                await self.bot.query_executer("DELETE FROM necrobot.Aliases WHERE guild_id = $1 and original = $2", ctx.guild.id, tag_name)

        await ctx.send(f":white_check_mark: | Tag {tag} and its aliases removed")

    @tag_del.command(name="alias")
    @commands.guild_only()
    async def tag_del_alias(self, ctx, alias : str):
        """Remove the alias to a tag. Only Server Admins and the tag owner can remove aliases and they can remove any aliases.

        {usage}

        __Examples__
        `{pre}tag delete alias necro1` - remove the alias "necro1"

        """
        try:
            tag = await Tag().convert(ctx, alias)
        except commands.BadArgument:
            raise commands.BadArgument(f"Alias {alias} does not exist.")

        self.is_tag_owner(ctx, tag)

        del self.bot.server_data[ctx.guild.id]["aliases"][alias]
        await self.bot.query_executer("DELETE FROM necrobot.Aliases WHERE guild_id = $1 and original = $2", ctx.guild.id, tag_name)
        await ctx.send(f":white_check_mark: | Alias `{alias}` removed")

    @tag.command(name="edit")
    @commands.guild_only()
    async def tag_edit(self, ctx, tag : Tag, *, content):
        """Replaces the content of [tag] with the [text] given. Basically works as a delete + create function but without the risk of losing the tag name ownership.
        
        {usage}
        
        __Example__
        `{pre}tag edit necro cool server` - replaces the content of the 'necro' tag with 'cool server'"""
        self.is_tag_owner(ctx, tag)

        self.bot.server_data[ctx.guild.id]["tags"][tag]["content"] = content
        await self.bot.query_executer("UPDATE necrobot.Tags SET content = $1 WHERE guild_id = $2 AND name = $3", content, ctx.guild.id, tag)
        await ctx.send(f":white_check_mark: | Tag `{tag}` modified")

    @tag.command(name="raw")
    @commands.guild_only()
    async def tag_raw(self, ctx, tag : Tag):
        """Returns the unformatted content of the tag [tag] so other users can see how it works.
        
        {usage}
        
        __Example__
        `{pre}raw necro` - prints the raw data of the 'necro' tag"""
        await ctx.send(f":notebook: | Source code for {tag}: ```{self.bot.server_data[ctx.guild.id]['tags'][tag]['content']}```")

    @tag.command(name="list")
    @commands.guild_only()
    async def tag_list(self, ctx):
        """Returns the list of tags present on the guild.
        
        {usage}"""
        tag_list = list(self.bot.server_data[ctx.guild.id]["tags"].keys()) + list(self.bot.server_data[ctx.guild.id]["aliases"].keys())
        tag_str = ", ".join(tag_list) if len(tag_list) > 0 else "None"
        await ctx.send(f"Tags in **{ctx.guild.name}**: ```{tag_str}```")

    @tag.command(name="info")
    @commands.guild_only()
    async def tag_info(self, ctx, tag : Tag):
        """Returns information on the tag given.
        
        {usage}
        
        __Example__
        `{pre}tag info necro` - prints info for the tag 'necro'"""
        tag_dict = self.bot.server_data[ctx.guild.id]["tags"][tag]
        embed = discord.Embed(title=f"__**{tag}**__", colour=discord.Colour(0x277b0), description=f'Created on {tag_dict["created"]}')
        embed.add_field(name="Owner", value=ctx.guild.get_member(tag_dict["owner"]).mention)
        embed.add_field(name="Uses", value=tag_dict["counter"])
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

        await ctx.send(embed=embed)

    @tag.command(name="alias")
    @commands.guild_only()
    async def tag_alias(self, ctx, tag : Tag, new_name : str):
        """Allows to create an alias for a tag, allowing to call the content of the
        tag by another name without changing the name or editing the content. Alias are
        merely a link, therefore any content updates to the original tag will be reflected 
        in its aliases. You cannot alias an an alias and nor can you edit an alias. Trying
        to alias or edit an alias will simply edit or alias the original.

        {usage}

        __Example__
        `{pre}tag alias necro super_necro` - You can now call the tag necro using the name "super_necro"
        """
        if new_name in self.restricted:
            await ctx.send(":white_check_mark: | Alias name is a reserved keyword")
        elif new_name not in self.bot.server_data[ctx.guild.id]["tags"] and new_name not in self.bot.server_data[ctx.guild.id]["aliases"]:
            self.bot.server_data[ctx.guild.id]["aliases"][new_name] = tag
            await self.bot.query_executer("INSERT INTO necrobot.Aliases VALUES ($1, $2, $3)", new_name, tag, ctx.guild.id)
            await ctx.send(":white_check_mark: | Alias successfully created")
        else:
            await ctx.send(":white_check_mark: | Alias already exists.")


def setup(bot):
    bot.add_cog(Tags(bot))
