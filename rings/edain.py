import discord
from discord.ext import commands

from rings.utils.utils import has_perms, react_menu
from rings.utils.config import cookies

import re
import asyncio
import itertools
import emoji_unicode
from robobrowser import RoboBrowser
from collections import defaultdict

class Edain:
    """A cog for commands and events solely created for the unofficial Edain Community server. Commands 
    and functionalities provided by this cog will not work on any other server."""
    def __init__(self, bot):
        self.bot = bot
        self.browser = RoboBrowser(history=True, parser="html.parser")
        self.browser.session.cookies.update(cookies)
        self.in_process = []
        self.edain_mu = 0000000000

    def __local__check(self, ctx):
        if not ctx.guild:
            raise commands.CheckFailure("This command cannot be used in DMs")

        if not ctx.guild.id in (327175434754326539, 311630847969198082):
            raise commands.CheckFailure("This command cannot be used in this server")

        return True

    async def poll_builder(self, message):
        CUSTOM_EMOJI = r'<:[^\s]+:([0-9]*)>'
        UNICODE_EMOJI = emoji_unicode.RE_PATTERN_TEMPLATE

        custom_emojis = [self.bot.get_emoji(int(emoji)) for emoji in re.findall(CUSTOM_EMOJI, message.content)]
        unicode_emojis = re.findall(UNICODE_EMOJI, message.content)

        emojis = [*custom_emojis, *unicode_emojis]
        votes = re.search(r'votes: (\d*)', message.content.lower())
        votes = int(votes.group(1)) if votes is not None else 1
        
        self.bot.polls[message.id] = {'votes': votes, 'voters':[]}
        await self.bot.query_executer("INSERT INTO necrobot.Polls VALUES($1, $2)", message.id, votes)

        for emoji in emojis:
            try:
                await message.add_reaction(emoji)
            except (discord.NotFound, discord.InvalidArgument, discord.HTTPException):
                pass
                
    async def mu_poster(self, message_id):
        result = (await self.bot.query_executer("SELECT * FROM necrobot.MU WHERE id=$1", message_id))[0]
        self.browser.open(result[2])
        form = self.browser.get_form("postmodify")
        
        user = await self.bot.query_executer("SELECT * FROM necrobot.MU_Users WHERE id=$1", result[1])
        final_message = f"{result[3]}\n[hr]\n{user[0][1]} ({result[1]})"
        form["message"].value = final_message

        del form.fields["attachment[]"]
        del form.fields["preview"]
        
        # self.browser.submit_form(form) #actual sbumit 
        await self.bot.get_channel(671747329350565912).send(f"Payload sent. {form.serialize().data}") #dud debug test

        await self.bot.query_executer("DELETE FROM necrobot.MU WHERE id=$1", message_id)
        
    async def mu_parser(self, message):
        lines = message.content.splitlines()
        thread = lines[0]
        regex = r"https:\/\/modding-union\.com\/index\.php\/topic,([0-9]*)"
        try:
            match = re.findall(regex, thread)[0]
        except IndexError:
            await message.delete()
            await message.channel.send(f"{message.author.mention} | Could not find a valid thread url", delete_after=10)
            return
            
        url_template = "https://modding-union.com/index.php?action=post;topic={}"   
        thread = url_template.format(match)

        text = "\n".join(lines[1:])
        
        await self.bot.query_executer("INSERT INTO necrobot.MU VALUES ($1, $2, $3, $4, $5)", 
            message.id, message.author.id, thread, text, message.guild.id)
        
        await message.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        await message.add_reaction("\N{NEGATIVE SQUARED CROSS MARK}")

    @commands.command()
    @has_perms(3)
    async def poll(self, ctx):
        """This adds the necessary reactions to a reaction poll created, simply react to the poll with
        :white_check_mark:

        {usage}"""

        d = await ctx.send("Waiting for :white_check_mark: reaction")

        def check(reaction, user):
            return str(reaction.emoji) == "\N{WHITE HEAVY CHECK MARK}" and user == ctx.author

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", check=check, timeout=300)
        except asyncio.TimeoutError:
            return
            
        await d.delete()
        await reaction.message.clear_reactions()

        await self.poll_builder(reaction.message)

    @commands.command()
    async def results(self, ctx, index = 0):
        """Get the results of a poll

        {usage}"""
        sql = 'SELECT * FROM necrobot.Votes'
        results = await self.bot.query_executer(sql)
        final_results = defaultdict(dict)
        for result in results:
            if result[2] in final_results[result[0]]:
                final_results[result[0]][result[2]] += 1
            else:
                final_results[result[0]][result[2]] = 1

        final_results = list(final_results.items())
        final_results.reverse()

        def _embed_maker(index):
            def emojify(emoji):
                if re.match(emoji_unicode.RE_PATTERN_TEMPLATE, emoji):
                    return emoji

                return discord.utils.get(ctx.guild.emojis, name=emoji) or emoji

            results = sorted(final_results[index][1].items(), key=lambda x: x[1], reverse=True)
            string = "\n".join([f'{emojify(key)} - {value}' for key, value in results])
            url = f'https://discordapp.com/channels/327175434754326539/504389672945057799/{final_results[index][0]}'
            embed = discord.Embed(title="Results", description=f'[**Link**]({url})\n\n{string}')
            embed.set_footer(text="Generated by Necrobot", icon_url=self.bot.user.avatar_url_as(format="png", size=128))
            return embed

        await react_menu(ctx, len(final_results)-1, _embed_maker, index)
        
    @commands.group(invoke_without_command=True)
    async def register(self, ctx, username : str):
        """Register yourself to use the bot's modding-union capabilities. This forces you to pick a name and keep it, once
        you've registered your name you won't be able to change it without admin assistance so pick it with care. Names are
        on a first come first served basis, if you want a specific username get it before someone else does
        
        {usage}
        
        __Examples__
        `{pre}register Necro` - register yourself as user Necro
        """
        if username.lower() in self.in_process:
            return await ctx.send(":negative_squared_cross_mark: | A registration for that nickname is currently in progress. Please wait for it to complete, if the registration successfully completed please pick another nickname.")
            
        self.in_process.append(username.lower())
        msg = await ctx.send(f"By registering to use the bot's MU-Discord communication service you agree to the following forum rules: <https://modding-union.com/index.php/topic,30385.0.html>. If you break these rules, access to the channel may be restricted or taken away. React with :white_check_mark: if you agree or with :negative_squared_cross_mark: if you do not agree.")
        await msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        await msg.add_reaction("\N{NEGATIVE SQUARED CROSS MARK}")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["\N{WHITE HEAVY CHECK MARK}", "\N{NEGATIVE SQUARED CROSS MARK}"] and msg.id == reaction.message.id

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", check=check, timeout=300)
        except asyncio.TimeoutError:
            await msg.edit(content=":negative_squared_cross_mark: | User was too slow, please react within 5 minutes next time.")
            await msg.clear_reactions()
            self.in_process.remove(username.lower())
            return

        if reaction.emoji == "\N{NEGATIVE SQUARED CROSS MARK}":
            await msg.edit(content=":negative_squared_cross_mark: | User did not agree to forum rules.")
            await msg.clear_reactions()
            self.in_process.remove(username.lower())
            return
        elif reaction.emoji == "\N{WHITE HEAVY CHECK MARK}":
            try:
                await msg.delete()
                self.in_process.remove(username.lower())
                await self.bot.query_executer("INSERT INTO necrobot.MU_Users VALUES($1, $2, $3)", ctx.author.id, username, username.lower(), silent=True)
                await ctx.send(":white_check_mark: | You have now succesfully registered to the bot's modding union channel. You may now post in it.")
            except:
                await ctx.send(":negative_squared_cross_mark: | You are already registered or that username is taken.")
            
    @has_perms(6)
    @register.command(name="rename")
    async def register_rename(self, ctx, user : discord.Member, new_username : str):
        """Rename users, use sparingly.
        
        {usage}
        
        __Examples__
        `{pre}register rename @Necro NotNecro` - rename user Necro to NotNecro on their MU profile
        """
        try:
            await self.bot.query_executer("UPDATE FROM necrobot.MU_Users SET username=$1, username_lower=$2 WHERE id=$3", new_username, new_username.lower(), user.id, silent=True)
            await ctx.send(":white_check_mark: | MU username successfully changed.")
        except:
            await ctx.send(":negative_squared_cross_mark: | That username is already taken.")


    async def on_message(self, message):
        if message.author.bot or message.author.id in self.bot.settings["blacklist"]:
            return
            
        if message.channel.id in [504389672945057799, 487306953253584936]:
            await self.poll_builder(message)
            
        if message.channel.id in (671747329350565912,self.edain_mu):
            registered = await self.bot.query_executer("SELECT * FROM necrobot.MU_Users WHERE id=$1", message.author.id)
            if not registered:
                await message.channel.send(f'{message.author.mention} | You are not registered, please register with the `register` command first.', delete_after=10)
                await message.delete()
                return
                
            if len(message.content) > 20000:
                await message.channel.send(f'{message.author.mention} | Message too long, please keep messages under 20k characters.', delete_after=10)
                await message.delete()
                return
                
            await self.mu_parser(message)

    async def on_raw_reaction_add(self, payload):
        if payload.message_id in self.bot.polls:
            to_remove = False    
            if payload.user_id == self.bot.user.id:
                return

            counter = self.bot.polls[payload.message_id]["voters"].count(payload.user_id) + 1
            if counter > self.bot.polls[payload.message_id]["votes"]:
                to_remove = True

                channel = self.bot.get_channel(336820934117818368) or self.bot.get_channel(321305756999745547)
                user = self.bot.get_user(payload.user_id)

                await channel.send(f":warning:| User {user.mention} tried adding multiple reactions to the poll")

            await self.bot.query_executer("INSERT INTO necrobot.Votes VALUES($1, $2, $3)", payload.message_id, payload.user_id, payload.emoji.name)
            self.bot.polls[payload.message_id]["voters"].append(payload.user_id)

            if to_remove:
                emoji = payload.emoji._as_reaction()
                await self.bot._connection.http.remove_reaction(payload.message_id, payload.channel_id, emoji, payload.user_id)
        
        if payload.channel_id in (671747329350565912, self.edain_mu):
            if str(payload.emoji) == "\N{WHITE HEAVY CHECK MARK}":
                if payload.user_id == 241942232867799040:
                    await self.mu_poster(payload.message_id)
                    await self.bot._connection.http.delete_message(payload.channel_id, payload.message_id)  
            
            if str(payload.emoji) == "\N{NEGATIVE SQUARED CROSS MARK}":
                message = await self.bot.query_executer("SELECT * FROM necrobot.MU WHERE id=$1", payload.message_id)
                ids = [241942232867799040, message[0][1]]
                    
                if payload.user_id in ids:
                    await self.bot._connection.http.delete_message(payload.channel_id, payload.message_id)              

    async def on_raw_reaction_remove(self, payload):
        if payload.message_id in self.bot.polls:
            if payload.user_id == self.bot.user.id:
                return

            if self.bot.polls[payload.message_id]["voters"].count(payload.user_id) > 0:
                self.bot.polls[payload.message_id]["voters"].remove(payload.user_id)
                await self.bot.query_executer("DELETE FROM necrobot.Votes WHERE message_id=$1 AND user_id=$2 AND reaction=$3", 
                    payload.message_id, payload.user_id, payload.emoji.name) 
                    
    async def on_member_leave(self, member):
        if member.guild.id in (327175434754326539, 311630847969198082):
            results = await self.bot.query_executer("DELETE FROM necrobot.MU WHERE user_id=$1 AND guild_id=$2 RETURNING id", member.id, member.guild.id, fetchval=True) 
            for result in results:
                 await self.bot._connection.http.delete_message(channel, result[0])                     

def setup(bot):
    bot.add_cog(Edain(bot))
