#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Music():
    """Everything related to the bot's voice chat capabilities. """
    def __init__(self, bot):
        self.bot = bot

    def close_player(filename):
        os.remove(filename)

    @commands.command(pass_context = True, enabled=False, hidden=True)
    @commands.cooldown(1, 10, BucketType.channel)
    async def play(self, cont, url):
        """Plays either a youtube link or a link ending with a valid audio file format extension: .mp4, .mkv, .ogg, ect... 
        
        {usage}
        
        __Example__
        `{pre}play Ring Verse Black Speech` - plays the first video from youtube that matches this name"""
        vc = cont.message.author.voice_channel
        voice_client = await self.bot.join_voice_channel(vc)

        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(url) as r:
                    filename = os.path.basename(url)
                    with open(filename, 'wb') as f_handle:
                        while True:
                            chunk = await r.content.read(1024)
                            if not chunk:
                                break
                            f_handle.write(chunk)
                    await r.release()
            player = voice_client.create_ffmpeg_player(filename, after=lambda:close_player(filename))
        except:
            player = await voice_client.create_ytdl_player(url, after=lambda:close_player(filename))

        await self.bot.say(":musical_note: | Playing `" + player.title)
        player.start()



def setup(bot):
    bot.add_cog(Music(bot))