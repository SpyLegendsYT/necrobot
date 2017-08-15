#!/usr/bin/env python
# coding:utf-8

from cards import common


CLUBS = 1
DIAMONDS = 2
HEARTS = 3
SPADES = 4
SUITS = (CLUBS, DIAMONDS, HEARTS, SPADES)
SUITS_SYMBOLS = {
        CLUBS: "♣",
        DIAMONDS: "♦",
        HEARTS: "♥",
        SPADES: "♠",
        }

JACK = 11
QUEEN = 12
KING = 13
ACE = 14
RANKS = (JACK, QUEEN, KING, ACE)
RANKS_SYMBOLS = {
        JACK: 'J',
        QUEEN: 'Q',
        KING: 'K',
        ACE: 'A',
        }


class Deck(common.Deck):
    def __init__(self):
        super(Deck, self).__init__()
        for suit in SUITS:
            for rank in RANKS:
                self.add(self.create_card(suit, rank))
            for i in range(2, 10):
                self.add(self.create_card(suit, i))
        self.shuffle()

    def create_card(self, suit, rank):
        return Card(suit, rank)

    def spade(self, rank):
        return self.create_card(SPADES, rank)


class Card(common.Card):
    def value(self):
        return self.rank

    def is_ace(self):
        return self.rank == ACE

    def __str__(self):
        return '%s%s' % (
                SUITS_SYMBOLS[self.suit],
                RANKS_SYMBOLS.get(self.rank, self.rank))
