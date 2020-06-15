import discord
from discord.ext import commands

from rings.utils.utils import BotError, has_perms, react_menu
from rings.utils.config import cookies

import re
from robobrowser import RoboBrowser

def guild_only(guild_id):
    def predicate(ctx):
        if ctx.guild is None:
            raise commands.CheckFailure("This command cannot be executed in DMs")
            
        if ctx.guild.id not in (guild_id, 311630847969198082):
            raise commands.CheckFailure("This command cannot be executed in this server")
            
        return True
        
    return commands.check(predicate)

class Special(commands.Cog):
    """A cog for all commands specific to certain servers."""
    def __init__(self, bot):
        self.bot = bot
        self.mu_channels = (722040731946057789,)
        self.browser = RoboBrowser(history=True, parser="html.parser")
        self.browser.session.cookies.update(cookies)
        self.in_process = []
    
    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        if payload.message_id in self.bot.pending_posts:
            self.bot.pending_posts[payload.message_id]._update(payload.data)
            
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        if payload.message_id in self.bot.pending_posts:
            del self.bot.pending_posts[payload.message_id]
            
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id not in self.mu_channels:
            return
        
        registered = await self.bot.db.query_executer(
            "SELECT active FROM necrobot.MU_Users WHERE user_id=$1", 
            message.author.id, fetchval=True
        )
        if registered is None:
            await message.channel.send(f'{message.author.mention} | You are not registered, please register with the `register` command first.', delete_after=10)
            await message.delete()
            return
            
        if not registered:
            await message.channel.send(f'{message.author.mention} | Your account is banned from using the system, you may appeal with admins to have it unbanned', delete_after=10)
            await message.delete()
            return
            
        await self.mu_parser(message)
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.channel_id in self.mu_channels:
            return
            
        if not payload.message_id in self.bot.pending_posts:
            return
            
        ids = [241942232867799040]
        for role in ["Edain Team", "Edain Community Moderator"]:
            obj = discord.utils.get(self.bot.get_guild(payload.guild_id).roles, name=role)
            if not obj is None:
                ids.extend([x.id for x in obj.members])
        
        if str(payload.emoji) == "\N{WHITE HEAVY CHECK MARK}":
            if payload.user_id in ids:
                await self.mu_poster(payload.message_id, payload.user_id)
                await self.bot._connection.http.delete_message(payload.channel_id, payload.message_id)  
        elif str(payload.emoji) == "\N{NEGATIVE SQUARED CROSS MARK}":
            ids.append(self.bot.pending_posts[payload.message_id]["message"].author.id)
            if payload.user_id in ids:
                await self.bot._connection.http.delete_message(payload.channel_id, payload.message_id)  
        
    async def mu_poster(self, message_id, approver_id):
        pending = self.bot.pending_posts[message_id]
        self.browser.open(pending["url"])
        form = self.browser.get_form("postmodify")
        
        username = await self.bot.db.query_executer(
            "SELECT username FROM necrobot.MU_Users WHERE user_id=$1", 
            pending["message"].author.id, fetchval=True
        )
        final_message = f"{pending['text']}\n[hr]\n{username} ({pending['message'].author.id})"
        form["message"].value = final_message

        del form.fields["attachment[]"]
        del form.fields["preview"]
        
        # self.browser.submit_form(form) #actual sbumit 
        await self.bot.get_bot_channel().send(f"Payload sent. {form.serialize().data}") #dud debug test

        await self.bot.db.query_executer(
            "INSERT INTO necrobot.MU(user_id, url, guild_id, approver_id) VALUES ($1, $2, $3, $4)",
            pending["message"].author.id, self.browser.url, pending["message"].guild.id, approver_id
        )
        
        del self.bot.pending_posts[message_id]
        
    async def mu_parser(self, message):
        lines = message.content.splitlines()
        thread = lines[0]
        regex = r"https:\/\/modding-union\.com\/index\.php(?:\/|\?)topic(?:=|,)([0-9]*)"
        try:
            match = re.findall(regex, thread)[0]
        except IndexError:
            await message.delete()
            await message.channel.send(f"{message.author.mention} | Could not find a valid thread url", delete_after=10)
            return
            
        url_template = "https://modding-union.com/index.php?action=post;topic={}"   
        thread = url_template.format(match)

        text = "\n".join(lines[1:])
        
        await message.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        await message.add_reaction("\N{NEGATIVE SQUARED CROSS MARK}")
        
        self.bot.pending_posts[message.id] = {
            "message": message,
            "url": thread,
            "text": text
        }
        
    @commands.group(invoke_without_command=True)
    @guild_only(327175434754326539)
    async def register(self, ctx, username : str):
        """Register yourself to use the bot's modding-union capabilities. This forces you to pick a name and keep it, once
        you've registered your name you won't be able to change it without admin assistance so pick it with care. Names are
        on a first come first served basis, if you want a specific username get it before someone else does
        
        {usage}
        
        __Examples__
        `{pre}register Necro` - register yourself as user Necro
        """
        if len(username) > 200:
            raise BotError("Username too long, please keep the username below 200 characters")
        
        if username.lower() in self.in_process:
            raise BotError("A registration for that nickname is currently in progress. Please wait for it to complete, if the registration successfully completed please pick another nickname.")
            
        already_registered = await self.bot.db.query_executer(
            "SELECT * FROM necrobot.MU_Users WHERE user_id = $1 OR username_lower = $2",
            ctx.author.id, username.lower()    
        )
        
        if already_registered:
            raise BotError("You are already registered or that username is taken.")
        
        self.in_process.append(username.lower())
        msg = await ctx.send(f"By registering to use the bot's MU-Discord communication service you agree to the following forum rules: <https://modding-union.com/index.php/topic,30385.0.html>. If you break these rules, access to the channel may be restricted or taken away. React with :white_check_mark: if you agree or with :negative_squared_cross_mark: if you do not agree.")
        await msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        await msg.add_reaction("\N{NEGATIVE SQUARED CROSS MARK}")

        def check(reaction, user):
            return user.id == ctx.author.id and str(reaction.emoji) in ["\N{WHITE HEAVY CHECK MARK}", "\N{NEGATIVE SQUARED CROSS MARK}"] and msg.id == reaction.message.id

        async def cleanup():
            await msg.edit(content=":negative_squared_cross_mark: | User was too slow, please react within 5 minutes next time.")
            await msg.clear_reactions()
            self.in_process.remove(username.lower())
            
        reaction, _ = await self.bot.wait_for(
            "reaction_add", 
            check=check, 
            timeout=600, 
            handler=cleanup, 
            propogate=False
        )

        if reaction.emoji == "\N{NEGATIVE SQUARED CROSS MARK}":
            await msg.edit(content=":negative_squared_cross_mark: | User did not agree to forum rules.")
            await msg.clear_reactions()
            self.in_process.remove(username.lower())
        elif reaction.emoji == "\N{WHITE HEAVY CHECK MARK}":
            await msg.clear_reactions()
            self.in_process.remove(username.lower())
            await self.bot.db.query_executer(
                "INSERT INTO necrobot.MU_Users VALUES($1, $2, $3)", 
                ctx.author.id, username, username.lower(), 
            )
            await msg.edit(content=":white_check_mark: | You have now succesfully registered to the bot's modding union channel. You may now post in it.")
            
    @register.command(name="rename")
    @guild_only(327175434754326539)
    @has_perms(4)
    async def register_rename(self, ctx, user : discord.Member, new_username : str):
        """Rename users, use sparingly.
        
        {usage}
        
        __Examples__
        `{pre}register rename @Necro NotNecro` - rename user Necro to NotNecro on their MU profile
        """
        try:
            await self.bot.db.query_executer(
                "UPDATE FROM necrobot.MU_Users SET username=$1, username_lower=$2 WHERE id=$3", 
                new_username, new_username.lower(), user.id
            )
            await ctx.send(":white_check_mark: | MU username successfully changed.")
        except:
            raise BotError("That username is already taken.")
            
    @register.command(name="ban")
    @guild_only(327175434754326539)
    @has_perms(4)
    async def register_ban(self, ctx, *users : discord.Member):
        """Ban users from using the system, they will still be registered but unable to use the system.
        
        {usage}
        
        __Examples__
        `{pre}register ban @Necro @Necrobot` - ban both users
        """
        await self.bot.db.query_executer(
            "UPDATE necrobot.MU_Users SET active=False WHERE user_id = any($1)",
            [user.id for user in users]    
        )
        
        await ctx.send(":white_check_mark: | All users banned")
        
    @register.command(name="unban")
    @guild_only(327175434754326539)
    @has_perms(4)
    async def register_unban(self, ctx, *users : discord.Member):
        """Unban users from the system, they will be able to once again use their accounts and create posts
        
        {usage}
        
        __Examples__
        `{pre}register unban @Necro @Necrobot` - unban both users
        """
        await self.bot.db.query_executer(
            "UPDATE necrobot.MU_Users SET active=True WHERE user_id = any($1)",
            [user.id for user in users]    
        )
        
        await ctx.send(":white_check_mark: | All users unbanned")
            
    @register.command(name="info")
    @guild_only(327175434754326539)
    async def register_info(self, ctx, user : discord.Member = None):
        """Get info about the number of posts a user has made and their username.
        
        {usage}
        
        __Examples__
        `{pre}register info` - get info about your own MU account
        `{pre}register info @NecroBot` - get info about necrobot's MU account
        """
        if user is None:
            user = ctx.author
            
        username = await self.bot.db.query_executer(
            "SELECT (username, active) FROM necrobot.MU_Users WHERE user_id = $1",
            user.id, fetchval=True
        )
        
        if not username:
            raise BotError("This user is not currently registered to use the MU-Discord system.")
            
        posts = await self.bot.db.query_executer(
            """SELECT post_date, ARRAY_AGG((url, approver_id)) FROM necrobot.MU WHERE user_id = $1 AND guild_id = $2 
            GROUP BY post_date""",
            user.id, ctx.guild.id    
        )
        
        total = await self.bot.db.query_executer(
            "SELECT COUNT(url) FROM necrobot.MU WHERE user_id = $1 AND guild_id = $2",
            user.id, ctx.guild.id, fetchval=True    
        )
        
        def embed_maker(index, entries):
            embed = discord.Embed(title=f"{user.display_name} ({index[0]}/{index[1]})", description=f"Username:{username[0]}\nStatus: {'Active' if username[1] else 'Banned'}\nTotal Posts: {total}")
            embed.set_footer(text="Generated by Necrobot", icon_url=self.bot.user.avatar_url_as(format="png", size=128))
            
            for entry in entries:
                threads = []
                for url, approver in entry[1]:
                    approver_obj = ctx.guild.get_member(approver)
                    threads.append(f"{url} - {approver_obj.mention if approver_obj is not None else 'User has left'}")
                
                embed.add_field(name=str(entry[0]), value="\n".join(threads))
                
            return embed
        
        await react_menu(ctx, posts, 10, embed_maker)

        
def setup(bot):
    bot.add_cog(Special(bot))
