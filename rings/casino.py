#!/usr/bin/python3.6
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from rings.botdata.data import Data
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

userData = Data.userData
serverData = Data.serverData

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

    def start(self):
        self.deck = self.create_deck()
        for player in self.players:
            self.hands[player] = self.create_hand()
            player.set_hand(self.create_hand())
        self.started = True

    def play(self, player):
        if not self.is_over():
            over = 0
            hand = self.hands[player]
            if not hand.busted:
                card = self.deck.draw()
                hand.add_card(card)
                player.add_card(card)
                return "draws a **{0}**".format(card)

            # if over == len(self.players):
            #     self.over = True

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

    def win(self, player, bank, bet, cont, msg):
        userData[cont.message.author.id]["money"] += bet
        return "{2} \nEnd of the game \n**{4}'s** hand: {0} \n**Dealer's** hand: {1} \nYour bet money is doubled, you win {3} :euro:".format(player.hand.value(), bank.hand.value(), msg, bet * 2, cont.message.author.display_name)
 

    def loose(self, player, bank, bet, cont, msg):
        userData[cont.message.author.id]["money"] -= bet
        return "{2} \nEnd of the game \n**{3}'s** hand: {0} \n**Dealer's** hand: {1}. \nYou lose the game and the bet money placed.".format(player.hand.value(), bank.hand.value(), msg, cont.message.author.display_name)
 

    @commands.command(pass_context = True, aliases=["bj"])
    async def blackjack(self, cont, bet : int = 10):
        """A simpe game of black jack against NecroBot's dealer. You can either draw a card by click on :black_joker: or you can pass your turn by clicking on :stop_button: . If you win you get double the amount of money you placed, if you lose you lose it all and if you tie everything is reset. Minimum bet 10 :euro:
         
        {usage}
        
        __Example__
        `n!blackjack 200` - bet 200 :euro: in the game of blackjack
        `n!blackjack` - bet the default 10 :euro:"""
        if userData[cont.message.author.id]["money"] >= bet and bet >= 10:
            await self.bot.say("Starting a game of Blackjack with **{0.display_name}** for {1} :euro:".format(cont.message.author, bet))
            name = cont.message.author.display_name
            player = Player(name, 0)
            bank = Player("Bank", 0)
            players = (player,bank)
            game = Game(players)
            game.start()
            for x in players:
                game.play(x)
                game.play(x)

            while not game.is_over():
                status = await self.bot.say("**You** have {0} Total: {1} \n**The Dealer** has {2} Total: {3}".format(player.hand, player.hand.value(), bank.hand, bank.hand.value()))
                if player.hand.value() == 21:
                    await self.bot.say(self.win(player, bank, bet, cont, "**BLACKJACK**"))
                    return
                
                msg = await self.bot.say("What would you like to do? \n :black_joker: - Draw a card \n :stop_button: - Pass your turn")
                await self.bot.add_reaction(msg, "\N{PLAYING CARD BLACK JOKER}")
                await self.bot.add_reaction(msg, "\N{BLACK SQUARE FOR STOP}")
                res = await self.bot.wait_for_reaction(["\N{PLAYING CARD BLACK JOKER}","\N{BLACK SQUARE FOR STOP}"], message=msg, user=cont.message.author, timeout=60)


                if res is not None:
                    await self.bot.delete_message(msg)
                    if res.reaction.emoji == '\N{PLAYING CARD BLACK JOKER}':
                        await self.bot.say("**" + name + "** " + game.play(player), delete_after=5)
                        if player.hand.busted:
                            await self.bot.say(self.loose(player, bank, bet, cont, "**You** go bust."))
                            return
                        elif player.hand.value() == 21:
                            await self.bot.say(self.win(player, bank, bet, cont, "**BLACKJACK**"))
                            return
                        else:
                            if bank.hand.is_passing():
                                await self.bot.say("**The Dealer** passes his turn", delete_after=5)
                            else:
                                await self.bot.say("**The Dealer** " + game.play(bank), delete_after=5)
                                if bank.hand.busted:
                                    await self.bot.say(self.win(player, bank, bet, cont, "**The Dealer** goes bust."))
                                    return
                    elif res.reaction.emoji == '\N{BLACK SQUARE FOR STOP}':
                        await self.bot.say("**You** pass your turn", delete_after=5)
                        if bank.hand.is_passing():
                            await self.bot.say("**The Dealer** passes his turn too", delete_after=5)
                            if bank.hand.beats(player.hand):
                                await self.bot.say(self.loose(player, bank, bet, cont, "**The Dealer's** hand beats **your** hand."))
                                return
                            elif player.hand.beats(bank.hand):
                                await self.bot.say(self.win(player, bank, bet, cont, "**Your** hand beats **the Dealer's** hand."))
                                return
                            else:
                                await self.bot.say("Tie, everything is reset.")
                                return
                        else:
                            await self.bot.say("**The Dealer** " + game.play(bank))
                            if bank.hand.busted:
                                await self.bot.say(self.win(player, bank, bet, cont, "**The Dealer** goes bust."))
                                return
                else:
                    await self.bot.say("Too slow, please decide within one minute next time.")
                    userData[cont.message.author.id]["money"] -= bet

                await self.bot.delete_message(status)
        else:
            await self.bot.say("You don't have enough money to do that, also, the minimum bet is 10 :euro:.")





def setup(bot):
    bot.add_cog(Casino(bot))
