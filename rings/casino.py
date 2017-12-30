#!/usr/bin/python3.6
import discord
from discord.ext import commands

import random
import asyncio

from cards import common
from cards.decks import standard52
from cards.decks.standard52 import JACK, QUEEN, KING

ACE_LOW = 1
ACE_HIGH = 11
JACK_VALUE = 10

WIN_MIN = 17
WIN_MAX = 21

class Card(standard52.Card):
    def value(self):
        if self.rank in (JACK, QUEEN, KING):
            return JACK_VALUE
        else:
            return self.rank

class Deck(standard52.Deck):
    def create_card(self, suit, rank):
        return Card(suit, rank)

class Hand(common.Hand):
    def __init__(self):
        super(Hand, self).__init__()
        self.busted = False
        self.passing = False

    def add_card(self, card):
        super(Hand, self).add_card(card)
        self.busted = self.is_bust()
        self.passing = self.is_passing()

    def value(self):
        total = 0
        aces = 0
        for card in self.cards:
            if card.is_ace():
                aces += 1
            else:
                total += card.value()
        for i in range(aces):
            if total + ACE_HIGH <= WIN_MAX:
                total += ACE_HIGH
            else:
                total += ACE_LOW
        return total

    def is_bust(self):
        return self.value() > WIN_MAX

    def is_passing(self):
        return not self.busted and self.value() >= WIN_MIN

    def beats(self, other):
        if not self.busted and other.busted:
            return True
        if self.busted:
            return False
        if self.value() == WIN_MAX:
            return True
        return self.value() >= WIN_MIN and self.value() > other.value()

class Game(common.Game):
    def create_deck(self):
        return Deck()

    def create_hand(self):
        return Hand()

    def play(self, player):
        if not self.is_over():
            over = 0
            hand = self.hands[player]
            if not hand.busted:
                card = self.deck.draw()
                hand.add_card(card)
                player.add_card(card)
                return "draws a **{0}**".format(card)

class Player(common.Player):
    def __init__(self, name, risk):
        self.name = name
        self.risk = risk
        self.stop = False

    def __str__(self):
        return self.name

    def add_card(self, card):
        super(Player, self).add_card(card)
        self.stop = self.should_stop()

    def should_stop(self):
        if self.hand.value() < WIN_MIN:
            return False
        if self.hand.value() == WIN_MAX:
            return True
        if self.risk == 0:
            return True
        if self.risk == 1:
            return False
        return not random.random() < self.risk

    def to_hit(self):
        return not self.stop


class Casino():
    """All the cards games that NecroBot includes, careful, they all require you to pay with with your NecroBot currency"""
    def __init__(self, bot):
        self.bot = bot
        self.IS_GAME = list()

    @commands.command(aliases=["bj"])
    async def blackjack(self, ctx, bet : int = 10):
        """A simpe game of black jack against NecroBot's dealer. You can either draw a card by click on :black_joker: or you can pass your turn by clicking on :stop_button: . If you win you get double the amount of money you placed, if you lose you lose it all and if you tie everything is reset. Minimum bet 10 :euro:
         
        {usage}
        
        __Example__
        `{pre}blackjack 200` - bet 200 :euro: in the game of blackjack
        `{pre}blackjack` - bet the default 10 :euro:"""

        def win(msg):
            self.IS_GAME.remove(ctx.message.channel.id)
            self.bot.user_data[ctx.message.author.id]["money"] += bet * 2
            return "{2} \nEnd of the game \n**{4}'s** hand: {0} \n**Dealer's** hand: {1} \nYour bet money is doubled, you win {3} :euro:".format(player.hand.value(), bank.hand.value(), msg, bet * 2, ctx.message.author.display_name)
     

        def lose(msg):
            self.IS_GAME.remove(ctx.message.channel.id)
            return "{2} \nEnd of the game \n**{3}'s** hand: {0} \n**Dealer's** hand: {1}. \nYou lose the game and the bet money placed.".format(player.hand.value(), bank.hand.value(), msg, ctx.message.author.display_name)

        async def game_end():
            await ctx.message.channel.send("**The Dealer** passes his turn too", delete_after=5)
            if bank.hand.beats(player.hand):
                await ctx.message.channel.send(lose("**The Dealer's** hand beats **your** hand."))
            elif player.hand.beats(bank.hand):
                await ctx.message.channel.send(win("**Your** hand beats **the Dealer's** hand."))
            else:
                await ctx.message.channel.send("Tie, everything is reset.")
                self.IS_GAME.remove(ctx.message.channel.id)
                self.bot.user_data[ctx.message.author.id]["money"] += bet
            await status.delete()
            

        if ctx.message.channel.id in self.IS_GAME:
            await ctx.message.channel.send(":negative_squared_cross_mark: | There is already a game ongoing", delete_after = 5)
            return 
        else:
            self.IS_GAME.append(ctx.message.channel.id)

        if self.bot.user_data[ctx.message.author.id]["money"] >= bet and bet >= 10:
            await ctx.message.channel.send(":white_check_mark: | Starting a game of Blackjack with **{0.display_name}** for {1} :euro:".format(ctx.message.author, bet))
            self.bot.user_data[ctx.message.author.id]["money"] -= bet
            name = ctx.message.author.display_name
            player = Player(name, 0)
            bank = Player("Bank", 0)
            players = (player,bank)
            game = Game(players)
            game.start()
            for x in players:
                game.play(x)
                game.play(x)

            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) in ["\N{PLAYING CARD BLACK JOKER}","\N{BLACK SQUARE FOR STOP}", "\N{MONEY BAG}"] and msg.id == reaction.message.id


            while not game.is_over():
                status = await ctx.message.channel.send("**You** have {0} Total: {1} \n**The Dealer** has {2} Total: {3}".format(player.hand, player.hand.value(), bank.hand, bank.hand.value()))
                if player.hand.value() == 21:
                    await ctx.message.channel.send(win("**BLACKJACK**"))
                    await status.delete()
                    return
                
                msg = await ctx.message.channel.send("**Current bet** - {} \nWhat would you like to do? \n :black_joker: - Draw a card \n :stop_button: - Pass your turn \n :moneybag: - Double your bet and draw a card".format(bet))
                await msg.add_reaction("\N{PLAYING CARD BLACK JOKER}")
                await msg.add_reaction("\N{BLACK SQUARE FOR STOP}")
                await msg.add_reaction("\N{MONEY BAG}")
                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=60)

                if reaction is not None:
                    await msg.delete()
                    if reaction.emoji == '\N{PLAYING CARD BLACK JOKER}':
                        await ctx.message.channel.send("**You** " + game.play(player), delete_after=5)
                        if player.hand.busted:
                            await ctx.message.channel.send(lose("**You** go bust."))
                            await status.delete()
                            return
                        else:
                            if bank.hand.is_passing():
                                await ctx.message.channel.send("**The Dealer** passes his turn", delete_after=5)
                            else:
                                await ctx.message.channel.send("**The Dealer** " + game.play(bank), delete_after=5)
                                if bank.hand.busted:
                                    await ctx.message.channel.send(win("**The Dealer** goes bust."))
                                    return
                                elif player.hand.value() == 21:
                                    await ctx.message.channel.send(win("**BLACKJACK**"))
                                    await status.delete()
                                    return
                    elif reaction.emoji == "\N{MONEY BAG}":
                        if self.bot.user_data[ctx.message.author.id]["money"] >= bet * 2:
                            await ctx.message.channel.send("**You double your bet and ** " + game.play(player), delete_after=5)
                            self.bot.user_data[ctx.message.author.id]["money"] -= bet
                            bet *= 2
                            if player.hand.busted:
                                await ctx.message.channel.send(lose("**You** go bust."))
                                await status.delete()
                                return
                            elif player.hand.value() == 21 and bank.hand.value() < 21:
                                await ctx.message.channel.send(win("**BLACKJACK**"))
                                await status.delete()
                                return
                            else:
                                while not bank.hand.is_passing():
                                    await ctx.message.channel.send("**The Dealer** " + game.play(bank), delete_after=5)
                                    if bank.hand.busted:
                                        await ctx.message.channel.send(win("**The Dealer** goes bust."))
                                        return

                                return await game_end()
                        else:
                            await ctx.message.channel.send(":negative_squared_cross_mark: | Not enough money to double bet", delete_after=5)

                    elif reaction.emoji == "\N{BLACK SQUARE FOR STOP}":
                        await ctx.message.channel.send("**You** pass your turn", delete_after=5)
                        if not bank.hand.is_passing():
                            await ctx.message.channel.send("**The Dealer** " + game.play(bank), delete_after=5)
                            if bank.hand.busted:
                                await ctx.message.channel.send(win("**The Dealer** goes bust."))
                                await status.delete()
                                return
                        else:
                            return await game_end()
                else:
                    await ctx.message.channel.send("Too slow, please decide within one minute next time.")
                    self.IS_GAME.remove(ctx.message.channel.id)
                    return

                await status.delete()
        else:
            self.IS_GAME.remove(ctx.message.channel.id)
            await ctx.message.channel.send("You don't have enough money to do that, also, the minimum bet is 10 :euro:.")





def setup(bot):
    bot.add_cog(Casino(bot))
