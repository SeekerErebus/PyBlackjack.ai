from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import List

from .hand import Hand


class HandOutcome(Enum):
    PLAYER_BLACKJACK = auto()
    PLAYER_WIN = auto()
    PUSH = auto()
    PLAYER_LOSS = auto()
    PLAYER_SURRENDER = auto()


@dataclass(frozen=True)
class RulesConfig:
    blackjack_payout: float = 1.5  # 3:2
    max_hands_from_splits: int = 4
    dealer_stands_on_soft_17: bool = True
    late_surrender: bool = True


@dataclass(frozen=True)
class HandResolution:
    outcome: HandOutcome
    payout: int  # net chip change to player for this hand (excluding insurance)


def allowed_player_actions(
    hand: Hand,
    rules: RulesConfig,
    current_hand_count: int,
    player_balance: int,
) -> List[str]:
    actions: List[str] = []

    # No actions possible once the hand is surrendered or bust.
    if hand.surrendered or hand.is_bust:
        return actions

    # Base actions depend on the current total.
    # - Hands below 21 may hit or stand.
    # - Hands at 21 (including blackjack) may only stand.
    if hand.best_value < 21:
        actions.extend(["hit", "stand"])
    else:
        actions.append("stand")

    # Splits are allowed only for valid pairs and when we are still under 21.
    if (
        hand.best_value < 21
        and hand.can_split
        and current_hand_count < rules.max_hands_from_splits
        and player_balance >= hand.bet
    ):
        actions.append("split")

    # Double-down is available on the initial two-card hand when below 21
    # and the player can afford to double the original bet.
    if (
        len(hand.cards) == 2
        and hand.best_value < 21
        and player_balance >= hand.bet
    ):
        actions.append("double")

    # Surrender is only available on the initial two-card hand and while below 21.
    if len(hand.cards) == 2 and hand.best_value < 21:
        actions.append("surrender")

    return actions


def resolve_hand_vs_dealer(
    player_hand: Hand,
    dealer_hand: Hand,
    rules: RulesConfig,
) -> HandResolution:
    bet = player_hand.bet

    if player_hand.surrendered:
        payout = -(bet // 2)
        return HandResolution(HandOutcome.PLAYER_SURRENDER, payout)

    if player_hand.is_bust:
        return HandResolution(HandOutcome.PLAYER_LOSS, -bet)

    if dealer_hand.is_bust:
        return HandResolution(HandOutcome.PLAYER_WIN, bet)

    player_blackjack = player_hand.is_blackjack
    dealer_blackjack = dealer_hand.is_blackjack

    if player_blackjack and not dealer_blackjack:
        win_amount = int(bet * rules.blackjack_payout)
        return HandResolution(HandOutcome.PLAYER_BLACKJACK, win_amount)

    if dealer_blackjack and not player_blackjack:
        return HandResolution(HandOutcome.PLAYER_LOSS, -bet)

    if player_hand.best_value > dealer_hand.best_value:
        return HandResolution(HandOutcome.PLAYER_WIN, bet)
    if player_hand.best_value < dealer_hand.best_value:
        return HandResolution(HandOutcome.PLAYER_LOSS, -bet)
    return HandResolution(HandOutcome.PUSH, 0)
