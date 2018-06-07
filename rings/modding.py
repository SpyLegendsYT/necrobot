import discord
from discord.ext import commands
from moddb_reader import Reader
from moddb_reader.moddb_objects import Mod, Game
import aiohttp
import difflib
from bs4 import BeautifulSoup
from rings.utils.utils import react_menu

class AsyncReader(Reader):
    async def _soup_page(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                soup = BeautifulSoup(await resp.text(), "lxml")

            async with session.get(self.url.replace("www","rss") + "/articles/feed/rss.xml") as resp:
                rss = BeautifulSoup(await resp.text(), "xml")

        return soup, rss

    async def parse_mod(self, moddb_url):
        self.url = moddb_url
        self.soup, self.rss = await self._soup_page()

        return Mod(self.url, *self._general_parser(), *self._basic_mod_parser(), self._share_parser())

    async def parse_game(self, moddb_url):
        self.url = moddb_url
        self.soup, self.rss = await self._soup_page()

        return Game(self.url, *self._general_parser(), *self._basic_game_parser(), self._share_parser())

class Modding():
    """The modding commands that allow modders to showcase their work and users to interact with it. 
    This is NecroBot's main purpose albeit one of his smallest feature now."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mod(self, ctx, *, mod : str):
        """This command takes in a mod name from ModDB and returns a rich embed of it. Due to the high variety of 
        mod formats, embed appearances will vary but it should always return one as long as it is given the name of
        an existing mod`
        
        {usage}
        
        __Example__
        `{pre}mod edain mod` - creates a rich embed of the Edain Mod ModDB page"""
        async with self.bot.session.get("http://www.moddb.com/mods?filter=t&kw={}&released=&genre=&theme=&players=&timeframe=&game=&sort=visitstotal-desc".format(mod.replace(" ", "+"))) as resp:
            soup = BeautifulSoup(await resp.text(), "lxml")
            
        try:
            search_return = difflib.get_close_matches(mod, [x.string for x in soup.find("div", class_="table").findAll("h4")])[0]
        except IndexError:
            await ctx.send(":negative_squared_cross_mark: | No mod with that name found")
            return
            
        url = "http://www.moddb.com" + soup.find("div", class_="table").find("h4", string=search_return).a["href"]

        def _embed_generator(page):
            embed = discord.Embed(title="__**{0}**__".format(mod.name), colour=discord.Colour(0x277b0), url=url, description=mod.desc)
            embed.set_author(name="ModDB", url="http://www.moddb.com", icon_url="http://i.imgur.com/aExydLm.png")
            embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

            #navbar
            sections = ["Articles","Reviews","Downloads","Videos","Images"]
            nav_bar = ["[{0}]({1}/{0})".format(x, url) for x in sections]
            embed.add_field(name="Navigation", value=" - ".join(nav_bar))

            if page == 0:
                for article in mod.articles[:4]:
                    embed.add_field(name=article.title, value="{0}... [Link]({1})\nPublished {2}".format(article.desc, article.url, article.date))
            elif page == 1:
                embed.add_field(name="\u200b", value=" ".join(["[#{0}]({1})".format(tag.name, tag.url) for tag in mod.tags]))
                embed.add_field(name="Misc: ", value="{0} \n{1}\n{2}\n**[Comment]({3})**  -  **[Follow]({4})**".format(mod.rating, mod.publishers, mod.release_date, mod.comment, mod.follow))
                embed.add_field(name="Style", value= "\n".join([mod.style.genre, mod.style.theme, mod.style.players]), inline=True)
                embed.add_field(name="Stats", value= "\n".join(["Rank: " + mod.rank, "Visits: " + mod.count.visits, "Files: " + mod.count.files, "Articles: " + mod.count.articles, "Reviews: " + mod.count.reviews, "Last Update: " + mod.last_update]))
            elif page == 2:
                suggestion_list = list()
                for suggestion in mod.suggestions:
                    suggestion_list.append("[{0}]({1})".format(suggestion.name, suggestion.url))
                embed.add_field(name="You may also like",value=" - ".join(suggestion_list))

            return embed

        reader = AsyncReader()
        mod = await reader.parse_mod(url)
        page = 0
        await react_menu(self.bot, ctx, 2, _embed_generator)

    @commands.command()
    async def game(self, ctx, *, game : str):
        """This command takes in a game name from ModDB and returns a rich embed of it. Due to the high variety of 
        game formats, embed appearances will vary but it should always return one as long as it is given the name of
        an existing game
        
        {usage}
        
        __Example__
        `{pre}game battle for middle earth` - creates a rich embed of the BFME ModDB page"""
        async with self.bot.session.get("https://www.moddb.com/games?filter=t&kw={}&released=&genre=&theme=&indie=&players=&timeframe=".format(game.replace(" ", "+"))) as resp:
            soup = BeautifulSoup(await resp.text(), "lxml")
            
        try:
            search_return = difflib.get_close_matches(game, [x.string for x in soup.find("div", class_="table").findAll("h4")])[0]
        except IndexError:
            await ctx.send(":negative_squared_cross_mark: | No game with that name found")
            return
            
        url = "http://www.moddb.com" + soup.find("div", class_="table").find("h4", string=search_return).a["href"]

        def _embed_generator(page):
            embed = discord.Embed(title="__**{0}**__".format(game.name), colour=discord.Colour(0x277b0), url=url, description=game.desc)
            embed.set_author(name="ModDB", url="http://www.moddb.com", icon_url="http://i.imgur.com/aExydLm.png")
            embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

            #navbar
            sections = ["Articles","Reviews","Downloads","Videos","Images"]
            nav_bar = ["[{0}]({1}/{0})".format(x, url) for x in sections]
            embed.add_field(name="Navigation", value=" - ".join(nav_bar))

            if page == 0:
                for article in game.articles[:4]:
                    embed.add_field(name=article.title, value="{0}... [Link]({1})\nPublished {2}".format(article.desc, article.url, article.date))
            elif page == 1:
                embed.add_field(name="\u200b", value=" ".join(["[#{0}]({1})".format(tag.name, tag.url) for tag in game.tags]))
                embed.add_field(name="Misc: ", value="{0} \n{1}\n{2}\n{5}\n**[Comment]({3})**  -  **[Follow]({4})**".format(game.rating, game.publishers, game.release_date, game.comment, game.follow, game.engine))
                embed.add_field(name="Style", value= "\n".join([game.style.genre, game.style.theme, game.style.players]), inline=True)
                embed.add_field(name="Stats", value= "\n".join(["Rank: " + game.rank, "Visits: " + game.count.visits, "Files: " + game.count.files, "Articles: " + game.count.articles, "Reviews: " + game.count.reviews, "Last Update: " + game.last_update]))
            elif page == 2:
                suggestion_list = list()
                for suggestion in game.suggestions:
                    suggestion_list.append("[{0}]({1})".format(suggestion.name, suggestion.url))
                embed.add_field(name="You may also like",value=" - ".join(suggestion_list))

            return embed

        reader = AsyncReader()
        game = await reader.parse_game(url)
        page = 0
        await react_menu(self.bot, ctx, 2, _embed_generator)



def setup(bot):
    bot.add_cog(Modding(bot))