import discord
from discord.ext import commands
from moddb_reader import Reader
from moddb_reader.moddb_objects import Mod
import aiohttp
from bs4 import BeautifulSoup

class AsyncReader(Reader):
    async def _soup_page(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                soup = BeautifulSoup(await resp.text(), "html.parser")

            async with session.get(self.url.replace("www","rss") + "/articles/feed/rss.xml") as resp:
                rss = BeautifulSoup(await resp.text(), "xml")

        return soup, rss

    async def parse_mod(self, moddb_url):
        self.url = moddb_url
        self.soup, self.rss = await self._soup_page()

        return Mod(self.url, *self._general_parser(), *self._basic_mod_parser(), self._share_parser())

class Modding():
    """The modding commands that allow modders to showcase their work and users to interact with it. This is NecroBot's main purpose albeit one of his smallest feature now."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def moddb(self, ctx, url : str):
        """This command takes in a mod url from ModDB and returns a rich embed of it. Due to the high variety of mod formats, embed appearances will vary but it should always return one as long as it is given a proper url starting with `http://www.moddb.com/mods/`
        
        {usage}
        
        __Example__
        `{pre}moddb http://www.moddb.com/mods/edain-mod` - creates a rich embed of the Edain Mod ModDB page"""
    
        if not url.startswith("http://www.moddb.com/mods/"):
            await ctx.channel.send("URL was not valid, try again with a valid url. URL must be from an existing mod page. Acceptable examples: `http://www.moddb.com/mods/edain-mod`, `http://www.moddb.com/mods/rotwk-hd-edition`, ect...")
            return

        reader = AsyncReader()
        mod = await reader.parse_mod(url)

        embed = discord.Embed(title="__**{0}**__".format(mod.name), colour=discord.Colour(0x277b0), url=url, description=mod.desc)
        embed.set_author(name="ModDB", url="http://www.moddb.com", icon_url="http://i.imgur.com/aExydLm.png")
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

        #navbar
        sections = ["Articles","Reviews","Downloads","Videos","Images"]
        nav_bar = ["[{0}]({1}/{0})".format(x, url) for x in sections]
        embed.add_field(name="Navigation", value=" - ".join(nav_bar))

        for article in mod.articles[:3]:
            embed.add_field(name=article.title, value="{0}... [Link]({1})\nPublished {2}".format(article.desc, article.url, article.date))

        embed.add_field(name="\u200b", value=" ".join(["[#{0}]({1})".format(tag.name, tag.url) for tag in mod.tags]))
        embed.add_field(name="Misc: ", value="{0} \n{1}  -  {2}\n**[Comment]({3})**  -  **[Follow]({4})**".format(mod.rating, mod.publishers, mod.release_date, mod.comment, mod.follow))
        embed.add_field(name="Style", value= "\n".join([mod.style.genre, mod.style.theme, mod.style.players]), inline=True)
        embed.add_field(name="Stats", value= "\n".join(["Rank: " + mod.rank, "Visits: " + mod.count.visits, "Files: " + mod.count.files, "Articles: " + mod.count.articles, "Reviews: " + mod.count.reviews, "Last Update: " + mod.last_update]))

        suggestion_list = list()
        for suggestion in mod.suggestions:
            suggestion_list.append("[{0}]({1})".format(suggestion.name, suggestion.url))
        embed.add_field(name="You may also like",value=" - ".join(suggestion_list))
    
        await ctx.channel.send(embed=embed)
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(Modding(bot))