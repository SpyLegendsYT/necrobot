import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Music():
    def __init__(self, bot):
        self.bot = bot

    def close_player(filename):
        os.remove(filename)

    @commands.command(pass_context = True, enabled=False)
    @commands.cooldown(1, 10, BucketType.channel)
    async def play(self,cont, arg0):
        vc = cont.message.author.voice_channel
        voice_client = await self.bot.join_voice_channel(vc)

        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(arg0) as r:
                    filename = os.path.basename(arg0)
                    with open(filename, 'wb') as f_handle:
                        while True:
                            chunk = await r.content.read(1024)
                            if not chunk:
                                break
                            f_handle.write(chunk)
                    await r.release()

            print("File downloaded")

            player = voice_client.create_ffmpeg_player(filename, after=lambda:close_player(filename))

            
        except:
            player = await voice_client.create_ytdl_player(arg0, after=lambda:close_player(filename))

        await self.bot.say(":musical_note: | Playing `" + player.title)
        player.start()



def setup(bot):
    bot.add_cog(Music(bot))