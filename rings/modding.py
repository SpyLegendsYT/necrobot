import discord
from discord.ext import commands

from rings.utils.utils import react_menu

import aiohttp
from bs4 import BeautifulSoup
from fuzzywuzzy import process
from moddb_reader import Reader
from moddb_reader.moddb_objects import Mod, Game

class AsyncReader(Reader):
    async def _soup_page(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                soup = BeautifulSoup(await resp.text(), "lxml")

            async with session.get(self.url.replace("www", "rss") + "/articles/feed/rss.xml") as resp:
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
        async with self.bot.session.get(f"http://www.moddb.com/mods?filter=t&kw={mod.replace(' ', '+')}&released=&genre=&theme=&players=&timeframe=&game=&sort=visitstotal-desc") as resp:
            soup = BeautifulSoup(await resp.text(), "lxml")
            
        try:
            search_return = process.extract(mod, [x.string for x in soup.find("div", class_="table").findAll("h4")])[0][0]
        except IndexError:
            await ctx.send(f":negative_squared_cross_mark: | {self.bot.t(ctx, 'no-mod')}")
            return
            
        url = "http://www.moddb.com" + soup.find("div", class_="table").find("h4", string=search_return).a["href"]

        def _embed_generator(page):
            embed = discord.Embed(title=f"__**{mod.name}**__", colour=discord.Colour(0x277b0), url=url, description=mod.desc)
            embed.set_author(name="ModDB", url="http://www.moddb.com", icon_url="http://i.imgur.com/aExydLm.png")
            embed.set_footer(text=self.bot.t(ctx, "generated-necrobot"), icon_url=self.bot.user.avatar_url_as(format="png", size=128))

            #navbar
            sections = ["Articles", "Reviews", "Downloads", "Videos", "Images"]
            nav_bar = [f"[{x}]({url}/{x})" for x in sections]
            embed.add_field(name="Navigation", value=" - ".join(nav_bar))

            if page == 0:
                for article in mod.articles[:4]:
                    embed.add_field(name=article.title, value=f"{article.desc}... [Link]({article.url})\nPublished {article.date}")
            elif page == 1:
                embed.add_field(name="\u200b", value=" ".join([f"[#{tag.name}]({tag.url})" for tag in mod.tags]))
                embed.add_field(name="Misc: ", value=f"{mod.rating} \n{mod.publishers}\n{mod.release_date}\n**[Comment]({mod.comment})**  -  **[Follow]({mod.follow})**")
                embed.add_field(name="Style", value="\n".join([mod.style.genre, mod.style.theme, mod.style.players]), inline=True)
                embed.add_field(name="Stats", value=f"Rank: {mod.rank}\nVisits: {mod.count.visits}\nFiles:  {mod.count.files}\nArticles: {mod.count.articles}\nReviews: {mod.count.reviews}\nLast Update: {mod.last_update}")
            elif page == 2:
                suggestion_list = [f"[{suggestion.name}]({suggestion.url})" for suggestion in mod.suggestions]
                embed.add_field(name=self.bot.t(ctx, "also-like"), value=" - ".join(suggestion_list))

            return embed

        reader = AsyncReader()
        mod = await reader.parse_mod(url)
        await react_menu(ctx, 2, _embed_generator)

    @commands.command()
    async def game(self, ctx, *, game : str):
        """This command takes in a game name from ModDB and returns a rich embed of it. Due to the high variety of 
        game formats, embed appearances will vary but it should always return one as long as it is given the name of
        an existing game
        
        {usage}
        
        __Example__
        `{pre}game battle for middle earth` - creates a rich embed of the BFME ModDB page"""
        async with self.bot.session.get(f"https://www.moddb.com/games?filter=t&kw={game.replace(' ', '+')}&released=&genre=&theme=&indie=&players=&timeframe=") as resp:
            soup = BeautifulSoup(await resp.text(), "lxml")
            
        try:
            search_return = process.extract(game, [x.string for x in soup.find("div", class_="table").findAll("h4")])[0][0]
        except IndexError:
            await ctx.send(f":negative_squared_cross_mark: | {self.bot.t(ctx, 'no-mod')}")
            return
            
        url = "http://www.moddb.com" + soup.find("div", class_="table").find("h4", string=search_return).a["href"]

        def _embed_generator(page):
            embed = discord.Embed(title=f"__**{game.name}**__", colour=discord.Colour(0x277b0), url=url, description=game.desc)
            embed.set_author(name="ModDB", url="http://www.moddb.com", icon_url="http://i.imgur.com/aExydLm.png")
            embed.set_footer(text=self.bot.t(ctx, "generated-necrobot"), icon_url=self.bot.user.avatar_url_as(format="png", size=128))

            #navbar
            sections = ["Articles", "Reviews", "Downloads", "Videos", "Images"]
            nav_bar = [f"[{x}]({url}/{x})" for x in sections]
            embed.add_field(name="Navigation", value=" - ".join(nav_bar))

            if page == 0:
                for article in game.articles[:4]:
                    embed.add_field(name=article.title, value=f"{article.desc}... [Link]({article.url})\nPublished {article.date}")
            elif page == 1:
                embed.add_field(name="\u200b", value=" ".join([f"[#{tag.name}]({tag.url})" for tag in game.tags]))
                embed.add_field(name="Misc: ", value=f"{game.rating} \n{game.publishers}\n{game.release_date}\n{game.engine}\n**[Comment]({game.comment})**  -  **[Follow]({game.follow})**")
                embed.add_field(name="Style", value="\n".join([game.style.genre, game.style.theme, game.style.players]), inline=True)
                embed.add_field(name="Stats", value=f"Rank: {game.rank}\nVisits: {game.count.visits}\nFiles:  {game.count.files}\nArticles: {game.count.articles}\nReviews: {game.count.reviews}\nLast Update: {game.last_update}")
            elif page == 2:
                suggestion_list = [f"[{suggestion.name}]({suggestion.url})" for suggestion in game.suggestions]
                embed.add_field(name=self.bot.t(ctx, "also-like"), value=" - ".join(suggestion_list))

            return embed

        reader = AsyncReader()
        game = await reader.parse_game(url)
        await react_menu(ctx, 2, _embed_generator)

def setup(bot):
    bot.add_cog(Modding(bot))
