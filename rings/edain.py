import discord
from discord.ext import commands

from rings.utils.utils import has_perms

import re
import asyncio
import emoji_unicode

class Edain:
    """A cog for commands and events solely created for the unofficial Edain Community server. Commands 
    and functionalities provided by this cog will not work on any other server."""
    def __init__(self, bot):
        self.bot = bot

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
        votes = re.search(r'Votes: (\d*)', message.content)
        votes = int(votes.group(1)) if votes is not None else 1
        
        self.bot.polls[message.id] = {'votes': votes, 'voters':[]}
        await self.bot.query_executer("INSERT INTO necrobot.Polls VALUES($1, $2)", message.id, votes)

        for emoji in emojis:
            try:
                await message.add_reaction(emoji)
            except (discord.NotFound, discord.InvalidArgument, discord.HTTPException):
                pass

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

    async def on_message(self, message):
        if message.author.bot or message.author.id in self.bot.settings["blacklist"]:
            return
            
        if message.channel.id in [504389672945057799, 487306953253584936]:
            await self.poll_builder(message)

    async def on_raw_reaction_add(self, payload):
        to_remove = False
        if payload.message_id not in self.bot.polls:
            return

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
            await  self.bot._connection.http.remove_reaction(payload.message_id, payload.channel_id, emoji, payload.user_id)


    async def on_raw_reaction_remove(self, payload):
        if payload.message_id not in self.bot.polls:
            return

        if payload.user_id == self.bot.user.id:
            return

        if self.bot.polls[payload.message_id]["voters"].count(payload.user_id) > 0:
            self.bot.polls[payload.message_id]["voters"].remove(payload.user_id)
            await self.bot.query_executer("DELETE FROM necrobot.Votes WHERE message_id=$1 AND user_id=$2 AND reaction=$3", 
                payload.message_id, payload.user_id, payload.emoji.name)

    async def on_raw_message_delete(self, payload):
        if payload.message_id in self.bot.polls:
            del self.bot.polls[payload.message_id]
            await self.bot.query_executer("DELETE FROM necrobot.Polls WHERE message_id=$1", payload.message_id)

def setup(bot):
    bot.add_cog(Edain(bot))
