import discord
from discord.ext import commands

from rings.utils.var import var

import random
import asyncio
from bs4 import BeautifulSoup

class Social():
    """All of NecroBot's fun commands to keep a user active and entertained"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["sean","joke","dad"])
    async def dadjoke(self, ctx):
        """Send a random dadjoke from a long list. 
        
        {usage}"""
        dad_joke = var[self.bot.server_data[ctx.guild.id]["language"]].dad_joke
        await ctx.send(f":speaking_head: | **{random.choice(dad_joke)}**")

    @commands.command()
    async def riddle(self, ctx):
        """Ask a riddle to the user from a long list and waits 30 seconds for the answer. If the 
        user fails to answer they go feed Gollum's fishies. To answer the riddle simply type out 
        the answer, no need to prefix it with anything. 
        
        {usage}"""
        riddle_list = var[self.bot.server_data[ctx.guild.id]["language"]].riddle_list
        riddle = random.choice(riddle_list)
        await ctx.send(f"{self.bot.t(ctx, 'riddle-message')} {ctx.author.name}: \n{riddle[0]}")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and riddle[1] in m.content

        try:
            await self.bot.wait_for("message", check=check, timeout=30)
            await ctx.send(self.bot.t(ctx, "riddle-correct"))
        except asyncio.TimeoutError:
            await ctx.send(self.bot.t(ctx, "riddle-wrong"))            

    @commands.command()
    async def tarot(self, ctx):
        """Using the mystical art of tarology, NecroBot reads the user's fate in the card and 
        returns the explanation for each card. Not to be taken seriously. 
        
        {usage}"""
        tarot_list = var[self.bot.server_data[ctx.guild.id]["language"]].tarot_list
        card_list = random.sample(tarot_list, 3)
        await ctx.send(f":white_flower: | {self.bot.t(ctx, 'riddle-wrong').format(ctx.author.name, card_list[0], card_list[1], card_list[2])}")

    @commands.command()
    async def rr(self, ctx, bullets : int = 1):
        """Plays a game of russian roulette with the user. If no number of bullets is entered it will default to one. 
        
        {usage}
        
        __Example__
        `{pre}rr 3` - game of russian roulette with 3 bullets
        `{pre}rr` - game of russian roulette with 1 bullet"""
        if bullets not in range(0,7):
            bullets = 1
            
        msg = f":gun: | {self.bot.t(ctx, 'rr-message').format(bullets)}"
        if random.randint(1,7) <= bullets:
            msg += f"\n:boom: | {self.bot.t(ctx, 'rr-lose')}"
        else:
            msg += f"\n:ok: | {self.bot.t(ctx, 'rr-win')}"

        await ctx.send(msg)

    @commands.command()
    async def lotrfact(self, ctx):
        """Prints a random Lord of the Rings fact. 
        
        {usage}"""
        lotr_list = var[self.bot.server_data[ctx.guild.id]["language"]].lotr_list
        choice = random.choice(lotr_list)
        await ctx.send(f"<:onering:351442796420399119> | **{self.bot.t(ctx, 'fact')} #{lotr_list.index(choice) + 1}**: {choice}")

    @commands.command()
    async def pokefusion(self, ctx, pokemon1 = None, pokemon2 = None):
        """Generates a rich embed containing a pokefusion from Gen 1, this can either be a two random pokemons, 
        one random pokemon and one chosen pokemon or two chosen pokemons.
        
        {usage}

        __Examples__
        `{pre}pokefusion` - random pokefusion
        `{pre}pokefusion raichu` - pokefusion of random pokemon and raichu
        `{pre}pokefusion raichu arceus` - pokefusion of raichu and arceus"""
        dex = var[self.bot.server_data[ctx.guild.id]["language"]].dex
        pokemon1 = pokemon1 or random.choice(dex)
        pokemon2 = pokemon2 or random.choice(dex)
         
        try:
            dex_1 = dex.index(pokemon1.lower()) + 1
            dex_2 = dex.index(pokemon2.lower()) + 1
        except ValueError:
            if dex_1:
                await ctx.send(f":negative_squared_cross_mark: | {self.bot.t(ctx, 'pokemone-two-not-exist')}")
            else:
                await ctx.send(f":negative_squared_cross_mark: | {self.bot.t(ctx, 'pokemone-one-not-exist')}")
            return

        async with self.bot.session.get(f"http://pokemon.alexonsager.net/{dex_1}/{dex_2}") as resp:
            soup = BeautifulSoup(await resp.text(), "html.parser")

        image = soup.find(id="pk_img")["src"]
        name = soup.find(id="pk_name").string
        fusion1 = soup.find(id="select1").find(selected="selected").string
        fusion2 = soup.find(id="select2").find(selected="selected").string
        url = soup.find(id="permalink")["value"]
        
        embed = discord.Embed(title=f"<:pokeball:351444031949111297> __**{name}**__", colour=discord.Colour(0x277b0), url=url, description=f"{fusion1} + {fusion2}")
        embed.set_footer(text=self.bot.t(ctx, 'generated-necrobot'), icon_url=self.bot.user.avatar_url_as(format="png", size=128))
        embed.set_image(url=image)

        await ctx.send(embed=embed)

    @commands.command()
    async def got(self, ctx, character=None):
        """Posts a random Game of Thrones quote.
    
        {usage}

        __Examples__
        `{pre}got` - posts a random quotes
        `{pre}got Tyrion` - posts a random quote from Tyrion
        """
        got_quotes = var[self.bot.server_data[ctx.guild.id]["language"]].got_quotes

        if character:
            quotes = [quote for quote in got_quotes if character.lower() in quote["character"].lower()]
            if quote:
                quote = random.choice(quotes)
            else:
                await ctx.send(f":negative_squared_cross_mark: | {self.bot.t(ctx, 'got-not-exist')}")
                return
        else:
            quote = random.choice(got_quotes)

        embed = discord.Embed(title=quote["character"], colour=discord.Colour(0x277b0), description=quote["quote"])
        embed.set_author(name=self.bot.t(ctx, 'got-title'))
        embed.set_footer(text=self.bot.t(ctx, 'generated-necrobot'), icon_url=self.bot.user.avatar_url_as(format="png", size=128))

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Social(bot))
