from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .cards import Card
from .hand import Hand


@dataclass
class SessionStats:
    initial_player_balance: int
    initial_dealer_balance: int
    hands_played: int = 0
    player_wins: int = 0
    player_losses: int = 0
    pushes: int = 0


@dataclass
class RoundView:
    player_hands: List[Hand] = field(default_factory=list)
    dealer_hand: Optional[Hand] = None
    active_hand_index: int = 0
    insurance_offered: bool = False
    awaiting_player_action: bool = False
    round_over: bool = False


@dataclass
class GameState:
    session_stats: SessionStats
    player_balance: int
    dealer_balance: int
    deck_remaining: int
    deck_total: int
    round_view: Optional[RoundView] = None


