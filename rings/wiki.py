#!/usr/bin/python3.6
import discord
from discord.ext import commands

import re
import wikia
import unwiki
import difflib
from mwclient import Site

class Wiki():
    """A series of wikia-related commands. Used to search the biggest fan-made database of 
    information."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def edain(self, ctx, *, article : str):
        """Performs a search on the Edain Mod Wiki for the give article name. If an article is found then it will 
        return a rich embed of it, else it will return a list of a related articles and an embed of the first related article. 
        
        {usage}
        
        __Example__
        `{pre}edain Castellans` - print a rich embed of the Castellans page
        `{pre}edain Battering Ram` - prints a rich embed of the Battering Ram disambiguation page"""
        msg = None
        try:
            article = wikia.page("edain", article)
        except wikia.wikia.WikiaError:
            try:
                search_list = wikia.search("edain", article)
                msg = f"Article: **{article}** not found, returning first search result and the following search list: {search_list[1:]}"
                article = wikia.page("Edain", search_list[0])
            except ValueError:
                await ctx.send(":negative_squared_cross_mark: | Article not found, and search didn't return any results. Please try again with different terms.")
                return

        url = article.url.replace(" ","_")
        embed = discord.Embed(title=article.title, colour=discord.Colour(0x277b0), url=url, description=article.section(article.sections[0]))

        try:
            embed.set_thumbnail(url=article.images[0]+"?size=400")
        except (IndexError, AttributeError, KeyError):
            pass

        embed.set_author(name="Edain Wiki", url="http://edain.wikia.com/", icon_url="http://i.imgur.com/lPPQzRg.png")
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

        if "Abilities" in article.sections:
            if len(article.section("Abilities")) < 1024  and len(article.section("Abilities")) > 0:
                embed.add_field(name="Abilities", value=article.section("Abilities"))
            else:
                for x in article.sections[1:]:
                    if len(article.section(x)) < 1024 and len(article.section(x)) > 0:
                        embed.add_field(name=x, value=article.section(x))
                        break
        else:
            for x in article.sections[1:]:
                if len(article.section(x)) < 1024 and len(article.section(x)) > 0:
                    embed.add_field(name=x, value=article.section(x))
                    break

        if len(article.related_pages) > 0:
            related ="- " + "\n- ".join(article.related_pages[:3])
            embed.add_field(name="More Pages:", value=related)

        embed.add_field(name="Quotes", value="Get all the sound quotes for units/heroes [here](http://edain.wikia.com/wiki/Edain_Mod_Soundsets)")

        await ctx.send(msg, embed=embed)

    @commands.command()
    async def lotr(self, ctx, *, article_name : str):
        """Performs a search on the Tolkien Gateway for the give article name. If an article is found then it 
        will return a rich embed of it, else it will return a list of a related articles and an embed of the first related article. 

        {usage}

        __Example__
        `{pre}lotr Finrod` - creates an embed of Finrod Felagund
        `{pre}lotr Fellowship` - searches for 'Fellowship' and returns the first result"""
        msg = ""
        site = Site(("http", "tolkiengateway.net"))
        if site.pages[article_name].text() != "":
            article = site.pages[article_name]
        else:
            search_list = [x for x in site.raw_api("opensearch", search=article_name)[1]]
            if len(search_list) == 1:
                article = site.pages[search_list[0]]
            elif len(search_list) > 0:
                msg = f"Article: **{article_name}** not found, returning first search result and the following search list: {search_list[1:]}"
                article = site.pages[difflib.get_close_matches(article_name, search_list, 1, 0.5)[0]]
            else:
                await ctx.send(":negative_squared_cross_mark: | Article not found, and search didn't return any result. Please try again with different terms.")
                return           

        url = "http://tolkiengateway.net/wiki/" + article.name.replace(" ","_")
        raw_desc = re.sub('<[^<]+?>', '', article.text(section=0))
        
        description = unwiki.UnWiki(raw_desc).__str__()
        embed = discord.Embed(title=article.name, colour=discord.Colour(0x277b0), url=url, description=description[:2047])

        try:
            embed.set_thumbnail(url= list(article.images())[0].imageinfo["url"]+ "?size=400")
        except (IndexError, AttributeError, KeyError):
            pass

        embed.set_author(name="Tolkien Gateway", url="http://tolkiengateway.net/", icon_url="http://i.imgur.com/I9Kx0kz.png")
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")
        await ctx.send(msg, embed=embed)

    @commands.command()
    async def wiki(self, ctx, wiki : str, *, article_name : str):
        """Performs a search on the given wiki (if valid) for the given article name. If an article is found then it 
        will return a rich embed of it, else it will return a list of a related articles and an embed of the first related article. 

        {usage}

        __Example__
        `{pre}wiki disney Donald Duck` - creates a rich embed of the Donald Duck page
        `{pre}wiki transformers Optimus` - searches for the 'Optimus Page' and returns a list of search results and a
         rich embed of the first one."""
        msg = ""
        if wiki.lower() == "edain":
            await ctx.send(":negative_squared_cross_mark: | No. Use the `edain` command")
            return
        elif wiki.lower() == "lotr":
            await ctx.send(":negative_squared_cross_mark: | No. Use the `lotr` command")
            return
            
        try:
            article = wikia.page(wiki, article_name)
        except wikia.wikia.WikiaError:
            try:
                search_list = wikia.search(wiki, article_name)
                msg = f"Article: **{article.name}** not found, returning first search result and the following search list: {search_list[1:]}"
                article = wikia.page(wiki, search_list[0])
            except ValueError:
                await ctx.send(":negative_squared_cross_mark: | Article not found or wiki not recognized, and search didn't return any result. Please try again with different terms.")
                return

        url = article.url.replace(" ","_")

        embed = discord.Embed(title=article.title, colour=discord.Colour(0x277b0), url=url, description=article.section(article.sections[0]))

        try:
            embed.set_thumbnail(url=article.images[0]+"?size=400")
        except (IndexError, AttributeError, KeyError):
            pass
        embed.set_author(name=article.sub_wikia.title() + " Wiki", url="http://"+ article.sub_wikia + ".wikia.com/")
        embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

        try:
            if len(article.related_pages) > 0:
                related ="- " + "\n- ".join(article.related_pages[:5])
                embed.add_field(name="More Pages:", value=related)
        except ValueError:
            pass
            
        await ctx.send(msg, embed=embed)

def setup(bot):
    bot.add_cog(Wiki(bot))