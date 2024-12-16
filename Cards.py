import random

import enum


class CardSuites(enum.Enum):
    heart = 0x00,
    spades = 0x01,
    clubs = 0x02,
    diamonds = 0x03


class CardValues(enum.Enum):
    val_1 = 1,
    val_2 = 2,
    val_3 = 3,
    val_4 = 4,
    val_5 = 5,
    val_6 = 6,
    val_7 = 7,
    val_8 = 8,
    val_9 = 9,
    val_10 = 10,
    val_A = 11,
    val_K = 12,
    val_Q = 13,
    val_Kn = 14


class Card:

    def __init__(self, suite: CardSuites, value: CardValues):
        self.suite: CardSuites = suite
        self.value: CardValues = value

    def get_card_value(self) -> int:
        return self._internal_value_to_card_value()

    def _internal_value_to_card_value(self) -> int:
        if self.value == CardValues.val_10:
            return 10

        if self.value == CardValues.val_Q:
            return 12

        if self.value == CardValues.val_K:
            return 13

        if self.value == CardValues.val_Kn:
            return 11

        if self.value == CardValues.val_A:
            return 14

        return self.value.value[0]

    def __repr__(self):
        val = self._internal_value_to_card_value()
        return "{0} - {1}".format(val, self.suite)


class Deck:

    def __init__(self):
        self.cards = []
        for suite in CardSuites:
            for value in CardValues:
                if value == CardValues.val_1:
                    continue
                self.cards.append(Card(suite, value))

    def shuffle(self):
        shuffled_deck: list[Card] = self.cards.copy()
        random.shuffle(shuffled_deck)
        return shuffled_deck


class Player:

    def __init__(self, name: str, lower_hand: list[Card], hand: list[Card]):
        self.hand: hand = hand
        self.lower_hand: lower_hand = lower_hand
        self.name = name


class Stack:
    def __init__(self, cards: list[Card]):
        self.cards = cards

    def add_card(self, card: Card):
        self.cards.append(card)

    def stack_clearer(self):
        self.cards.clear()
        return self.cards

    def stack_checker(self):
        if self.cards[-1].get_card_value() == self.cards[-2].get_card_value() == self.cards[-3].get_card_value() == \
                self.cards[-4].get_card_value():
            self.stack_clearer()

class Pile:

    def __init__(self, cards: list[Card]):
        self.cards: list[Card] = cards
