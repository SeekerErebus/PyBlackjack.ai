from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from random import shuffle
from typing import List


class Suit(Enum):
    CLUBS = auto()
    DIAMONDS = auto()
    HEARTS = auto()
    SPADES = auto()


class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 10
    QUEEN = 10
    KING = 10
    ACE = 11


@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit

    def __str__(self) -> str:
        rank_name = self.rank.name.title()
        suit_name = self.suit.name.title()
        return f"{rank_name} of {suit_name}"


class Deck:
    """Single 52-card deck with shuffle and penetration tracking."""

    def __init__(self) -> None:
        self._cards: List[Card] = []
        self.reset()

    @property
    def remaining(self) -> int:
        return len(self._cards)

    @property
    def total(self) -> int:
        return 52

    def reset(self) -> None:
        self._cards = [
            Card(rank=rank, suit=suit)
            for suit in Suit
            for rank in Rank
        ]
        shuffle(self._cards)

    def needs_reshuffle(self, threshold: float) -> bool:
        if threshold <= 0 or threshold >= 1:
            raise ValueError("threshold must be between 0 and 1 (exclusive)")
        return self.remaining < int(self.total * threshold)

    def draw(self, count: int = 1) -> List[Card]:
        if count < 1:
            raise ValueError("count must be at least 1")
        if count > self.remaining:
            raise ValueError("Not enough cards remaining in deck")
        drawn: List[Card] = []
        for _ in range(count):
            drawn.append(self._cards.pop())
        return drawn


