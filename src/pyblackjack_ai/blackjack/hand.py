from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .cards import Card, Rank


@dataclass
class Hand:
    cards: List[Card] = field(default_factory=list)
    bet: int = 0
    insurance_bet: int = 0
    surrendered: bool = False

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    @property
    def is_empty(self) -> bool:
        return not self.cards

    @property
    def values(self) -> List[int]:
        """Return all possible hand totals accounting for aces."""
        total = 0
        aces = 0
        for card in self.cards:
            if card.rank == Rank.ACE:
                aces += 1
                total += 11
            else:
                total += card.rank.value

        totals = [total]
        while aces > 0 and totals[-1] > 21:
            totals.append(totals[-1] - 10)
            aces -= 1

        return sorted(set(totals))

    @property
    def best_value(self) -> int:
        """Highest valid total not exceeding 21, or lowest total if all bust."""
        valid_totals = [v for v in self.values if v <= 21]
        if valid_totals:
            return max(valid_totals)
        return min(self.values) if self.values else 0

    @property
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.best_value == 21

    @property
    def is_bust(self) -> bool:
        return self.best_value > 21

    @property
    def is_soft(self) -> bool:
        """True if the hand has an ace counted as 11 without busting."""
        return len(self.values) >= 2 and not self.is_bust

    @property
    def can_split(self) -> bool:
        if len(self.cards) != 2:
            return False
        first, second = self.cards
        return first.rank == second.rank


