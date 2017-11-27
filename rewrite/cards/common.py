#!/usr/bin/env python

import random


class Card(object):
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def value(self):
        return 0

    def is_joker(self):
        return False

    def is_ace(self):
        return False


class Deck(object):
    def __init__(self):
        self.cards = []

    def draw(self):
        return self.cards.pop()

    def shuffle(self):
        random.shuffle(self.cards)

    def add(self, card):
        self.cards.append(card)

    def is_empty(self):
        return not len(self.cards)


class Hand(object):
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def beats(self, hand):
        return self.value() > hand.value()

    def value(self):
        return 0

    def __str__(self):
        if len(self.cards):
            return '%s' % ', '.join([str(x) for x in self.cards])
        else:
            return 'EMPTY'


class Game(object):
    def __init__(self, players=[]):
        self.players = players
        self.hands = {}
        self.started = False
        self.over = False

    def start(self):
        self.deck = self.create_deck()
        for player in self.players:
            self.hands[player] = self.create_hand()
            player.set_hand(self.create_hand())
        self.started = True

    def is_over(self):
        return self.over

    def play(self):
        self.over = True


class Player(object):
    def print_msg(self, message):
        return '*' + message

    def set_hand(self, hand):
        self.hand = hand
        self.print_msg('%s received hand: %s' % (self, hand))

    def add_card(self, card):
        self.hand.add_card(card)
        self.print_msg('%s: received card: %s' % (self, card))

    def print_status(self):
        self.print_msg('%s: value: %s, hand: %s' % (
            self, self.hand.value(), self.hand))
