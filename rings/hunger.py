#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import csv
import random
import asyncio

class Hunger():
    """The all inclusive commands for friends looking to share a good old battle to the death time."""
    def __init__(self, bot):
        self.bot = bot
        self.game_start_events = ["Bloodbath", self._event_parser("hunger_games/game_start_data.csv")]
        self.day_events = ["Day", self._event_parser("hunger_games/day_data.csv")]
        self.night_events = ["Night", self._event_parser("hunger_games/night_data.csv")]
        self.feast_events = ["Feast", self._event_parser("hunger_games/feast_data.csv")]

    def _event_parser(self, filename):
        event_list = list()
        with open(filename) as f:
            reader = csv.reader(f)
            for row in reader:
                event_list.append({"tributes" : int(row[0]), "killed" : list(row[1]), "string" : row[2]})
        return event_list

    @commands.command()
    async def fight(self, ctx, *, tributes):
        """Takes in a list of tributes separated by `,` and simulates a hunger games based on Bransteele's Hunger Game Simulator. More than 
        one tribute needs to be supplied.

        {usage}

        __Example__
        `{pre}fight john , bob , emilia the trap` - starts a battle between tributes john, bob and emilia the trap"""
        tributes_list = list(set([x.strip() for x in tributes.split(",")]))
        if len(tributes_list) <2:
            await ctx.send(":negative_squared_cross_mark: | Please provide at least two names separated by `,`")
            return

        if len(tributes_list) > 32:
            await ctx.send(":negative_squared_cross_mark: | Please provide no more than 32 characters separated by `,`.")

        dead_list = list()

        def _phase_parser(event_list):
            idle_tributes = tributes_list
            idle_events = event_list[1]
            embed = discord.Embed(title="__**Hunger Games Simulator**__", colour=discord.Colour(0x277b0), description="{}\nPress :arrow_forward: to proceed".format(" - ".join(tributes_list)))
            embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")

            done_list = list()
            while len(idle_tributes) > 0 and len(tributes_list) > 1:
                tributes = list()
                event = random.choice([event for event in idle_events if event["tributes"] <= len(idle_tributes) and len(event["killed"]) < len(tributes_list)])
                tributes = random.sample(idle_tributes, event["tributes"])
                idle_tributes = [x for x in idle_tributes if x not in tributes]
                if len(event["killed"]) > 0:
                    idle_events.remove(event)
                    for killed in event["killed"]:
                        tribute = tributes[int(killed)-1]
                        del tributes_list[tributes_list.index(tribute)]
                        dead_list.append(tribute)

                format_dict = dict()
                print(tributes)
                for tribute in tributes:
                    format_dict["p"+str(tributes.index(tribute)+1)] = tribute

                done_list.append(event["string"].format(**format_dict))

            embed.add_field(name=event_list[0] + " " + str(day), value="\n".join(done_list))
            return embed            
        
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == "\N{BLACK RIGHT-POINTING TRIANGLE}" and msg.id == reaction.message.id

        day = 0
        embed = _phase_parser(self.game_start_events)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("\N{BLACK RIGHT-POINTING TRIANGLE}")
        await self.bot.wait_for("reaction_add", check=check, timeout=600)

        while len(tributes_list) > 1:
            if day == 6:
                embed = _phase_parser(self.feast_events)
                msg = await ctx.send(embed=embed)
                await msg.add_reaction("\N{BLACK RIGHT-POINTING TRIANGLE}")
                try:
                    await self.bot.wait_for("reaction_add", check=check, timeout=600)
                except asyncio.TimeoutError:
                    await ctx.send(":negative_squared_cross_mark: | Please answer within 10 minutes next time")
                    return

            if len(tributes_list) >1: 
                embed = _phase_parser(self.day_events)
                msg = await ctx.send(embed=embed)
                await msg.add_reaction("\N{BLACK RIGHT-POINTING TRIANGLE}")
                try:
                    await self.bot.wait_for("reaction_add", check=check, timeout=600)
                except asyncio.TimeoutError:
                    await ctx.send(":negative_squared_cross_mark: | Please answer within 10 minutes next time")
                    return

            embed = discord.Embed(title="__**Dead Tributes**__", description="- " + "\n- ".join(dead_list) if len(dead_list) > 0 else "None")
            embed.set_footer(text="Generated by NecroBot", icon_url="https://cdn.discordapp.com/avatars/317619283377258497/a491c1fb5395e699148fcfed2ee755cf.jpg?size=128")
            msg = await ctx.send(embed=embed)
            await msg.add_reaction("\N{BLACK RIGHT-POINTING TRIANGLE}")
            try:
                await self.bot.wait_for("reaction_add", check=check, timeout=600)
            except asyncio.TimeoutError:
                    await ctx.send(":negative_squared_cross_mark: | Please answer within 10 minutes next time")
                    return
            del dead_list[:]

            if len(tributes_list) >1: 
                embed = _phase_parser(self.night_events)
                msg = await ctx.send(embed=embed)
                await msg.add_reaction("\N{BLACK RIGHT-POINTING TRIANGLE}")
                try:
                    await self.bot.wait_for("reaction_add", check=check, timeout=600)
                except asyncio.TimeoutError:
                    await ctx.send(":negative_squared_cross_mark: | Please answer within 10 minutes next time")
                    return

            day += 1

        await ctx.send(":tada:" + tributes_list[0] + " is the Winner! :tada:") 




def setup(bot):
    bot.add_cog(Hunger(bot))