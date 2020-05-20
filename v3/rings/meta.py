import discord
from discord.ext import commands

from rings.db import DatabaseError
from rings.utils.utils import time_converter

import io
import aiohttp
import asyncio
import datetime
from PIL import Image

class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot        
        self.hourly_task = self.bot.loop.create_task(self.hourly())
        
        self.tasks = [
            self.broadcast,
            self.clear_potential_star,
            self.rotate_status,
        ]
        
    def cog_unload(self):
        self.hourly_task.cancel()

    async def bmp_converter(self, message):
        attachment = message.attachments[0]
        f = io.BytesIO()
        await attachment.save(f)

        with Image.open(f) as im:
            output_buffer = io.BytesIO()
            im.save(output_buffer, "png")
            output_buffer.seek(0)
            ifile = discord.File(filename="converted.png", fp=output_buffer)
        
        await message.channel.send(file=ifile)
        
    async def new_guild(self, guild_id):
        if guild_id in self.bot.guild_data:
            return
        
        welcome_message = "Welcome {member} to {server}!"
        goodbye_message = "Leaving so soon? We\'ll miss you, {member}!"
    
        self.bot.guild_data[guild_id] = {
            "mute":"",
            "automod":"",
            "welcome-channel":"",
            "ignore-command":[],
            "ignore-automod":[],
            "welcome": welcome_message,
            "goodbye": goodbye_message,
            "prefix" :"",
            "broadcast-channel": "",
            "broadcast": "",
            "broadcast-time": 1,
            "disabled": [],
            "auto-role": "",
            "auto-role-timer": 0,
            "starboard-channel":"",
            "starboard-limit":5,
            "self-roles": [],
        }
        
        await self.bot.db.query_executer(
            "INSERT INTO necrobot.Guilds VALUES($1, 0, 0, 0, $2, $3, '', 0, '', 1, 0, 5, 0, 0);",
            guild_id, welcome_message, goodbye_message
        )
        
        await self.bot.db.insert_leaderboard(guild_id)
        
    async def delete_guild(self, guild_id):
        if guild_id not in self.bot.guild_data:
            return
            
        del self.bot.guild_data[guild_id]
        await self.bot.db.query_executer(
            "DELETE FROM necrobot.Guilds WHERE guild_id = $1",
            guild_id
        )    
        
    async def new_member(self, user, guild = None):
        await self.bot.db.query_executer(
                "INSERT INTO necrobot.Users VALUES ($1, 200, 0, $2, '', '', 'False') ON CONFLICT (user_id) DO NOTHING", 
                user.id, datetime.datetime.now()
            )
            
        if guild is None:
            return
        
        if isinstance(user, discord.User):
            user = guild.get_member(user.id)
            
        permissions = await self.bot.db.get_permission(user.id)
        
        if not any(x[0] == guild.id for x in permissions):
            if any(x[1] == 7 for x in permissions):
                level = 7
            elif any(x[1] == 6 for x in permissions):
                level = 6
            elif user.id == guild.owner.id:
                level = 5
            elif user.guild_permissions.administrator:
                level = 4
            else:
                level = 0
                
            await self.bot.db.insert_permission(user.id, guild.id, level)
            
        await self.bot.db.insert_leaderboard_member(guild.id, user.id)
        
    async def _star_message(self, message):
        if self.bot.blacklist_check(message.author.id):
            return

        embed = discord.Embed(colour=discord.Colour(0x277b0), description = message.content)
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url_as(format="png", size=128))
        embed.set_footer(text="Generated by Necrobot", icon_url=self.bot.user.avatar_url_as(format="png", size=128))
        if message.embeds:
            data = message.embeds[0]
            if data.type == 'image':
                embed.set_image(url=data.url)

        if message.attachments:
            file = message.attachments[0]
            if file.url.lower().endswith(('png', 'jpeg', 'jpg', 'gif', 'webp')):
                embed.set_image(url=file.url)
            else:
                embed.add_field(name='Attachment', value=f'[{file.filename}]({file.url})', inline=False)

        embed.add_field(name="Message", value=f'[Jump]({message.jump_url})', inline=False)

        msg = await self.bot.get_channel(self.bot.guild_data[message.guild.id]["starboard-channel"]).send(content=f"In {message.channel.mention}", embed=embed)
        
        if message.id not in self.bot.starred:
            self.bot.starred.append(message.id)
            await self.bot.db.add_star(message, msg)
            
    async def hourly(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            if self.bot.counter >= 24:
                self.bot.counter = 0

            now = datetime.datetime.now()
            time = 3600 - (now.second + (now.minute * 60))
            try:
                await asyncio.sleep(time) # task runs every hour
            except asyncio.CancelledError:
                return
            
            self.bot.counter += 1
            
            for task in self.tasks:
                await task()
                
                
    async def broadcast(self):
        def guild_check(guild):
            if self.bot.guild_data[guild]["broadcast-time"] < 1:
                return False

            if self.bot.get_guild(guild) is None:
                return False

            if self.bot.get_channel(self.bot.guild_data[guild]["broadcast-channel"]) is None:
                return False
                
            return self.bot.counter % self.bot.guild_data[guild]["broadcast-time"] == 0

        broadcast_guilds = [guild for guild in self.bot.guild_data if guild_check(guild)]

        for guild in broadcast_guilds:
            try:
                channel = self.bot.get_channel(self.bot.guild_data[guild]["broadcast-channel"])
                await channel.send(self.bot.guild_data[guild]["broadcast"])
            except Exception as e:
                await self.bot.get_error_channel().send(f"Broadcast error with guild {guild}\n{e}")
        
    async def clear_potential_star(self):
        if self.bot.counter != 24:
            return
        
        ids = list(self.bot.potential_stars.keys())
        ids.sort()
        
        for message_id in ids:
            limit = datetime.datetime.utcnow() - datetime.timedelta(days=3)
            timestamp = discord.utils.snowflake_time(message_id)
            
            if timestamp < limit:
                del self.bot.potential_stars[message_id]
            else:
                break
                
    async def rotate_status(self):
        status = self.bot.statuses.pop(0)
        self.bot.statuses.append(status)
        await self.bot.change_presence(
            activity=discord.CustomActivity(
                name=status.format(
                    guild=len(self.bot.guilds), 
                    members=len(self.bot.users)
                )
            )
        )
        
    async def load_cache(self):
        await self.bot.db.create_pool()
        self.bot.session = aiohttp.ClientSession(loop=self.bot.loop)
        
        msg = await self.bot.get_bot_channel().send("**Initiating Bot**")
        
        for guild in self.bot.guilds:
            if guild.id in self.bot.guild_data:
                await self.guild_checker(guild)
            else:
                await self.new_guild(guild.id) 
                
            for member in guild.members:
                await self.new_member(member, guild)
                
        await msg.edit(content="All servers checked")
        
        reminders = await self.bot.db.get_reminders()
        for reminder in reminders:
            timer = time_converter(reminder["timer"])
            sleep = timer - ((datetime.datetime.now() - reminder["start_date"]).total_seconds())
            if sleep <= 0:
                await self.bot.db.delete_reminder(reminder["id"])
            else:
                task = self.bot.loop.create_task(
                    self.bot.meta.reminder_task(
                        reminder["id"],
                        sleep, 
                        reminder["reminder"], 
                        reminder["channel_id"],
                        reminder["user_id"]
                    )
                )
                
                self.bot.reminders[reminder["id"]] = task
                
        await msg.edit(content="**Bot Online**")
        
    async def guild_checker(self, guild):
        channels = [channel.id for channel in guild.channels]
        roles = [role.id for role in guild.roles] 
        g = self.bot.guild_data[guild.id]

        if g["broadcast-channel"] not in channels:
            await self.bot.db.update_broadcast_channel(guild.id)

        if g["starboard-channel"] not in channels:
            await self.bot.db.update_starboard_channel(guild.id)
            
        if g["welcome-channel"] not in channels:
            await self.bot.db.update_greeting_channel(guild.id)
            
        if g["automod"] not in channels:
            await self.bot.db.update_automod_channel(guild.id)
            
        if g["mute"] not in roles:
            await self.bot.db.update_mute_role(guild.id)
            
        await self.bot.db.delete_self_roles(guild.id, [role for role in g["self-roles"] if role not in roles])
        await self.bot.db.update_invites(guild)
        
    async def reminder_task(self, reminder_id, time, message, channel_id, user_id):
        try:
            await asyncio.sleep(time)
        except asyncio.CancelledError:
            return

        channel = self.bot.get_channel(channel_id)
        user = self.bot.get_user(user_id)
        if channel is not None and user is not None:
            await channel.send(f":alarm_clock: | {user.mention} reminder: **{message}**")
        
        del self.bot.reminders[reminder_id]
        await self.bot.db.delete_reminder(reminder_id)
        
def setup(bot):
    bot.add_cog(Meta(bot))
