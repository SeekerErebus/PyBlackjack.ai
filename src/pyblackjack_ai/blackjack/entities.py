from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .cards import Deck
from .exceptions import InsufficientBalanceError
from .hand import Hand


@dataclass
class Participant:
    balance: int
    hands: List[Hand] = field(default_factory=list)

    def clear_hands(self) -> None:
        self.hands.clear()


@dataclass
class Player(Participant):
    def place_bet(self, amount: int) -> Hand:
        if amount <= 0:
            raise ValueError("Bet amount must be positive")
        if amount > self.balance:
            raise InsufficientBalanceError("Player does not have enough balance for bet")
        self.balance -= amount
        hand = Hand(bet=amount)
        self.hands = [hand]
        return hand

    def ensure_can_wager(self, amount: int) -> None:
        if amount > self.balance:
            raise InsufficientBalanceError("Player does not have enough balance for wager")


@dataclass
class Dealer(Participant):
    def initial_hand(self) -> Hand:
        self.hands = [Hand()]
        return self.hands[0]

    @property
    def hand(self) -> Hand:
        if not self.hands:
            self.hands = [Hand()]
        return self.hands[0]

    def play_out(self, deck: Deck) -> None:
        while self.hand.best_value < 17:
            card = deck.draw(1)[0]
            self.hand.add_card(card)


