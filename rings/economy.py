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

    def is_passing(self, other):
        return not self.busted and self.value() >= WIN_MIN and self.value() >= other.hand.value()

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
                return f"draws a **{card}**"

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


class Economy():
    """All the economy commands that NecroBot includes, careful, they all require you to pay with with your Necroins"""
    def __init__(self, bot):
        self.bot = bot
        self.IS_GAME = list()


    @commands.command(aliases=["bj"])
    async def blackjack(self, ctx, bet : int = 10):
        """A simpe game of black jack against NecroBot's dealer. You can either draw a card by click on :black_joker: 
        or you can pass your turn by clicking on :stop_button: . If you win you get double the amount of money you 
        placed, if you lose you lose it all and if you tie everything is reset. Minimum bet 10 :euro:
         
        {usage}
        
        __Example__
        `{pre}blackjack 200` - bet 200 :euro: in the game of blackjack
        `{pre}blackjack` - bet the default 10 :euro:"""
        if ctx.message.channel.id in self.IS_GAME:
            await ctx.send(":negative_squared_cross_mark: | There is already a game ongoing", delete_after = 5)
            return 
        
        if self.bot.user_data[ctx.author.id]["money"] < bet :
            await ctx.send(":negative_squared_cross_mark: | You don't have enough money", delete_after = 5)
            return

        if bet < 10:
            await ctx.send(":negative_squared_cross_mark: | Please bet at least 10 necroins.", delete_after=5)
            return


        self.IS_GAME.append(ctx.message.channel.id)
        await self.blackjack_game(ctx, bet)
        self.IS_GAME.remove(ctx.message.channel.id)


    async def blackjack_game(self, ctx, bet):
        async def win(msg):
            self.bot.user_data[ctx.author.id]["money"] += bet
            await self.bot.query_executer("UPDATE necrobot.Users SET necroins = $1 WHERE user_id = $2",self.bot.user_data[ctx.author.id]["money"], ctx.author.id)
            await ctx.send(f"{msg} \nEnd of the game \n**{ctx.author.display_name}'s** hand: {player.hand} : {player.hand.value()} \n**Dealer's** hand: {bank.hand} : {bank.hand.value()} \nYour bet money is doubled, you win {bet * 2} :euro:")
     

        async def lose(msg):
            self.bot.user_data[ctx.author.id]["money"] -= bet
            await self.bot.query_executer("UPDATE necrobot.Users SET necroins = $1 WHERE user_id = $2",self.bot.user_data[ctx.author.id]["money"], ctx.author.id)
            await ctx.send(f"{msg} \nEnd of the game \n**{ctx.author.display_name}'s** hand: {player.hand} : {player.hand.value()} \n**Dealer's** hand: {bank.hand} : {bank.hand.value()}. \nYou lose the game and the bet money placed.")

        async def game_end():
            if player.hand.value == 21:
                await win("**BLACKJACK**")
            elif bank.hand.value == 21:
                await lose("**BlackJack for the Dealer**")
            elif player.hand.value > 21:
                await lose("**You** go bust.")
            elif bank.hand.value > 21:
                await win("**The Dealer** goes bust.")
            elif bank.hand.beats(player.hand):
                await lose("**The Dealer's** hand beats **your** hand.")
            elif player.hand.beats(bank.hand):
                await win("**Your** hand beats **the Dealer's** hand.")
            else: #tie
                await ctx.send("Tie, everything is reset.")

            await status.delete()

        
        await ctx.send(f":white_check_mark: | Starting a game of Blackjack with **{ctx.author.display_name}** for {bet} :euro: \n :warning: **Wait till all three reactions have been added before choosing** :warning: ")
        reaction_list = ["\N{PLAYING CARD BLACK JOKER}","\N{BLACK SQUARE FOR STOP}", "\N{MONEY BAG}"]
        player = Player(ctx.author.display_name, 0)
        bank = Player("Bank", 0)
        game = Game((bank, player))
        game.start()
        for player in game.players:
            game.play(player)
            game.play(player)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in reaction_list and msg.id == reaction.message.id

        while not game.is_over():
            status = await ctx.send(f"**You** have {player.hand} Total: {player.hand.value()} \n**The Dealer** has {bank.hand} Total: {bank.hand.value()}")
            if player.hand.value() == 21:
                break
            elif bank.hand.value() == 21:
                break
            
            msg = await ctx.send(f"**Current bet** - {bet} \nWhat would you like to do? \n :black_joker: - Draw a card \n :stop_button: - Pass your turn \n :moneybag: - Double your bet and draw a card")
            for reaction in reaction_list:
                await msg.add_reaction(reaction)

            try :
                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=120)
            except asyncio.TimeoutError:
                await ctx.send("You took too long to reply, please reply within **two minutes** next time. You lose the game and the bet money placed.")
                self.bot.user_data[ctx.author.id]["money"] -= bet
                await self.bot.query_executer("UPDATE necrobot.Users SET necroins = $1 WHERE user_id = $2",self.bot.user_data[ctx.author.id]["money"], ctx.author.id)
                await msg.delete()
                return     

            await msg.delete()
            if reaction.emoji == '\N{PLAYING CARD BLACK JOKER}':
                await ctx.send(f"**You** {game.play(player)}", delete_after=5)
                if player.hand.busted:
                    break
                else:
                    if bank.hand.is_passing(player):
                        await ctx.send("**The Dealer** passes his turn", delete_after=5)
                    else:
                        await ctx.send(f"**The Dealer** {game.play(bank)}", delete_after=5)
                        if bank.hand.busted:
                            break
                        elif player.hand.value() == 21:
                            break

            elif reaction.emoji == "\N{MONEY BAG}":
                if self.bot.user_data[ctx.author.id]["money"] >= bet * 2:
                    await ctx.send(f"**You** double your bet and {game.play(player)}", delete_after=5)
                    bet *= 2
                    if player.hand.busted:
                        break
                    elif player.hand.value() == 21 and bank.hand.value() < 21:
                        break
                    else:
                        while not bank.hand.is_passing(player) and not bank.hand.busted:
                            await ctx.send(f"**The Dealer** {game.play(bank)}", delete_after=5)

                        break
                else:
                    await ctx.send(":negative_squared_cross_mark: | Not enough money to double bet", delete_after=5)

            elif reaction.emoji == "\N{BLACK SQUARE FOR STOP}":
                await ctx.send("**You** pass your turn", delete_after=5)
                if not bank.hand.is_passing(player):
                    await ctx.send(f"**The Dealer** {game.play(bank)}", delete_after=5)
                    if bank.hand.busted:
                        break
                else:
                    break                  

            await game_end()
            await status.delete()

    @commands.command(aliases=["slots"], enabled=False)
    async def slot(self, ctx):
        """Enter 50 Necroins and roll to see if you win more

        {usage}"""
        symbol_list = [":black_joker:", ":white_flower:", ":diamond_shape_with_a_dot_inside:", ":fleur_de_lis:", ":trident:", ":cherry_blossom:", "<:onering:351442796420399119>", ":squid:"]
        
        l1 = random.sample(symbol_list, len(symbol_list))
        l2 = random.sample(symbol_list, len(symbol_list))
        l3 = random.sample(symbol_list, len(symbol_list))

        msg = await ctx.send(f"{l1[0]}|{l2[0]}|{l3[0]}\n{l1[1]}|{l2[1]}|{l3[1]}\n{l1[2]}|{l2[2]}|{l3[2]}")

        for sym in range(len(symbol_list[2:-1])):
            await msg.edit(content=f"{l1[sym-1]}|{l2[sym-1]}|{l3[sym-1]}\n{l1[sym]}|{l2[sym]}|{l3[sym]}\n{l1[sym+1]}|{l2[sym+1]}|{l3[sym+1]}")
            final = [l1[sym], l2[sym], l3[sym]]
            await asyncio.sleep(1)

        if len(set(final)) == 1:
            final = final[0]
        else:
            await ctx.send(":negative_squared_cross_mark: | Better luck next time")
            return

        if final == "<:onering:351442796420399119>":
            await ctx.send(":white_check_mark: | **Jackpot!** You won **2500** Necroins!")
        else:
            await ctx.send(final)

    @commands.command()
    async def ttt(self, ctx, enemy : discord.Member):
        """Play a game of tic tac toe either against either a chosen enemy or against necrobot. 

        {usage}

        __Examples__
        `{pre}ttt @NecroBot` - play a game against NecroBot (AI)
        `{pre}ttt @ThatUser` - play a game against ThatUser, given that they agree"""
        def check_win(b):
            #horizontal check 2.0
            if any(len(set(row)) == 1 for row in b):
                return True

            #vertical check 2.0
            c = list(map(list, zip(*b))) #transpose
            if any(len(set(row)) == 1 for row in c):
                return True

            #diagonal check 2.0
            if len(set([b[x][x] for x in range(3)])) == 1 or len(set([b[2 - x][x] for x in range(3)])) == 1:
                return True

            return False

        def board_full(b):
            board_list = []
            for row in b:
                board_list += row

            return len(set(board_list)) == 2

        def print_board(b):
            msg = []
            for x in b:
                msg.append(f" {x[0]} | {x[1]} | {x[2]} \n")

            return "```\n"+ "------------\n".join(msg) + "\n```\nReply with the desired grid position. Won't work if not an intenger between 1 and 9 or from a place already taken."

        def comp_move(b):
            #check if any of our moves can win
            for row in b:
                for e in row:
                    if e not in ["O", "X"]:
                        num = int(e)
                        copy_b = [x.copy() for x in b]
                        copy_b[b.index(row)][row.index(e)] = "X"
                        if check_win(copy_b):
                            return num

            #check if any of the enemy moves can win
            for row in b:
                for e in row:
                    if e not in ["O", "X"]:
                        num = int(e)
                        copy_b = [x.copy() for x in b]
                        copy_b[b.index(row)][row.index(e)] = "O"
                        if check_win(copy_b):
                            return num

            #take the center
            if not b[1][1] in ["X", "O"]:
                return 5

            #take a random corner
            choices = []
            for corner in [1, 3, 7, 9]:
                if not b[int(corner//3.5)][(corner-1)%3] in ["X", "O"]:
                    choices.append(corner)

            if len(choices) > 0:
                return random.choice(choices)

            choice = []
            #take a random side
            for side in [2, 4, 6, 8]:
                if not b[int(side//3.5)][(side-1)%3] in ["X", "O"]:
                    choices.append(side)

            if len(choices) > 0:
                return random.choice(choices)


        async def two_players():
            while True:
                await msg.edit(content=print_board(board))

                def check(message):
                    if not message.content.isdigit():
                        return False

                    return message.author == ctx.author and int(message.content) > 0 and int(message.content) < 10 and message.channel == ctx.channel  and board[int(int(message.content)//3.5)][(int(message.content)-1)%3] not in ["X", "O"]
                
                try:
                    await current_msg.edit(content=f"Awaiting response from player: **{ctx.author.display_name}**")
                    user1 = await self.bot.wait_for("message", check=check, timeout=300)
                except asyncio.TimeoutError as e:
                    e.timer = 120
                    self.IS_GAME.remove(ctx.message.channel.id)
                    await msg.delete()
                    return self.bot.dispatch("command_error", ctx, e)

                await user1.delete()
                user1 = int(user1.content)

                board[int(user1//3.5)][(user1-1)%3] = "O"

                if check_win(board):
                    await ctx.send(f"{ctx.author.display_name} wins")
                    break

                if board_full(board):
                    await ctx.send("**Nobody wins**")
                    break

                await msg.edit(content=print_board(board))

                def check(message):
                    if not message.content.isdigit():
                        return False

                    return message.author == enemy and int(message.content) > 0 and int(message.content) < 10 and message.channel == ctx.channel  and board[int(int(message.content)//3.5)][(int(message.content)-1)%3] not in ["X", "O"]
                
                try:
                    await current_msg.edit(content=f"Awaiting response from player: **{enemy.display_name}**")
                    user2 = await self.bot.wait_for("message", check=check, timeout=300)
                except asyncio.TimeoutError as e:
                    e.timer = 120
                    self.IS_GAME.remove(ctx.message.channel.id)
                    await msg.delete()
                    return self.bot.dispatch("command_error", ctx, e)
                
                await user2.delete()
                user2 = int(user2.content)

                board[int(user2//3.5)][(user2-1)%3] = "X"

                if check_win(board):
                    await ctx.send(f"{enemy.display_name} wins")
                    break

            await msg.edit(content=print_board(board))

        async def against_ai():
            while True:
                await msg.edit(content=print_board(board))
                
                def check(message):
                    if not message.content.isdigit():
                        return False

                    return message.author == ctx.author and int(message.content) > 0 and int(message.content) < 10 and message.channel == ctx.channel  and board[int(int(message.content)//3.5)][(int(message.content)-1)%3] not in ["X", "O"]
                
                try:
                    user1 = await self.bot.wait_for("message", check=check, timeout=300)
                except asyncio.TimeoutError as e:
                    e.timer = 120
                    self.IS_GAME.remove(ctx.message.channel.id)
                    await msg.delete()
                    return self.bot.dispatch("command_error", ctx, e)

                await user1.delete()
                user1 = int(user1.content)

                board[int(user1//3.5)][(user1-1)%3] = "O"

                if check_win(board):
                    await ctx.send("**You win**")
                    break

                if board_full(board):
                    await ctx.send("**Nobody wins**")
                    break
                    
                await msg.edit(content=print_board(board))
                user2 = comp_move(board)
                await ai_msg.edit(content=f"AI picks: {user2}")
                board[int(user2//3.5)][(user2-1)%3] = "X"

                if check_win(board):
                    await ctx.send("**Necrobot wins**")
                    break

            await msg.edit(content=print_board(board))

        board = [
                ["1", "2", "3"],
                ["4", "5", "6"],
                ["7", "8", "9"]
                ]
                
        if enemy == ctx.author:
            await ctx.send(":negative_squared_cross_mark: | You cannot play against yourself, pick a player or fight Necrobot.")
            return

        if enemy == self.bot.user:
            msg = await ctx.send(":white_check_mark: | NecroBot has accepted your challenge, be prepared to face him")
            await asyncio.sleep(2)
            ai_msg = await ctx.send("AI picks: ")
            await against_ai()
        else:
            msg = await ctx.send(f":white_check_mark: | You have challenged **{enemy.display_name}**. {enemy.mention}, would you like to play? React with :white_check_mark: to play or with :negative_squared_cross_mark: to reject their challenge.")
            await msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
            await msg.add_reaction("\N{NEGATIVE SQUARED CROSS MARK}")

            def check(reaction, user):
                return user == enemy and str(reaction.emoji) in ["\N{WHITE HEAVY CHECK MARK}", "\N{NEGATIVE SQUARED CROSS MARK}"] and msg.id == reaction.message.id
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=300)
            except asyncio.TimeoutError as e:
                    e.timer = 120
                    self.IS_GAME.remove(ctx.message.channel.id)
                    await msg.delete()
                    return self.bot.dispatch("command_error", ctx, e)

            if reaction.emoji == "\N{NEGATIVE SQUARED CROSS MARK}":
                await ctx.send(":negative_squared_cross_mark: | Looks like they don't wanna play.")
                await msg.delete()
            elif reaction.emoji == "\N{WHITE HEAVY CHECK MARK}":
                await msg.clear_reactions()
                current_msg = await ctx.send("Awaiting response from player: ")
                await two_players()

def setup(bot):
    bot.add_cog(Economy(bot))
