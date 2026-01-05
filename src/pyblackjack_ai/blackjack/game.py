from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .cards import Card, Deck
from .entities import Dealer, Player
from .exceptions import GameStateError, InvalidActionError
from .game_state import GameState, RoundView, SessionStats
from .hand import Hand
from .rules import HandResolution, RulesConfig, allowed_player_actions, resolve_hand_vs_dealer


@dataclass
class Game:
    rules: RulesConfig
    deck: Deck = Deck()
    player: Optional[Player] = None
    dealer: Optional[Dealer] = None
    session_stats: Optional[SessionStats] = None
    active_hand_index: int = 0
    insurance_offered: bool = False
    insurance_resolved: bool = False
    round_over: bool = False

    def start_new_session(self, player_balance: int, dealer_balance: int) -> None:
        self.player = Player(balance=player_balance)
        self.dealer = Dealer(balance=dealer_balance)
        self.session_stats = SessionStats(
            initial_player_balance=player_balance,
            initial_dealer_balance=dealer_balance,
        )
        self.deck.reset()
        self.active_hand_index = 0
        self.insurance_offered = False
        self.insurance_resolved = False
        self.round_over = False

    def _ensure_ready(self) -> None:
        if self.player is None or self.dealer is None or self.session_stats is None:
            raise GameStateError("Session has not been started")

    def is_session_over(self) -> bool:
        self._ensure_ready()
        assert self.player is not None and self.dealer is not None
        return self.player.balance <= 0 or self.dealer.balance <= 0

    def maybe_reshuffle(self, threshold: float) -> None:
        if self.deck.needs_reshuffle(threshold):
            self.deck.reset()

    def start_hand(self, bet: int) -> None:
        self._ensure_ready()
        if self.round_over is False and self.player and self.player.hands:
            raise GameStateError("Current round not finished")

        assert self.player is not None and self.dealer is not None

        self.player.clear_hands()
        self.dealer.clear_hands()
        self.active_hand_index = 0
        self.insurance_offered = False
        self.insurance_resolved = False
        self.round_over = False

        player_hand = self.player.place_bet(bet)
        dealer_hand = self.dealer.initial_hand()

        for _ in range(2):
            player_hand.add_card(self.deck.draw(1)[0])
            dealer_hand.add_card(self.deck.draw(1)[0])

        if dealer_hand.cards[0].rank.value == 11:
            self.insurance_offered = True

    def get_state(self) -> GameState:
        self._ensure_ready()
        assert self.player is not None and self.dealer is not None and self.session_stats is not None

        round_view: Optional[RoundView] = None
        if self.player.hands:
            round_view = RoundView(
                player_hands=self.player.hands.copy(),
                dealer_hand=self.dealer.hand,
                active_hand_index=self.active_hand_index,
                insurance_offered=self.insurance_offered and not self.insurance_resolved,
                awaiting_player_action=not self.round_over,
                round_over=self.round_over,
            )

        return GameState(
            session_stats=self.session_stats,
            player_balance=self.player.balance,
            dealer_balance=self.dealer.balance,
            deck_remaining=self.deck.remaining,
            deck_total=self.deck.total,
            round_view=round_view,
        )

    def _current_hand(self) -> Hand:
        assert self.player is not None
        try:
            return self.player.hands[self.active_hand_index]
        except IndexError as exc:
            raise GameStateError("No active hand") from exc

    def available_actions(self) -> List[str]:
        self._ensure_ready()
        assert self.player is not None
        if self.round_over:
            return []
        return allowed_player_actions(
            self._current_hand(),
            self.rules,
            current_hand_count=len(self.player.hands),
            player_balance=self.player.balance,
        )

    def player_hit(self) -> None:
        if "hit" not in self.available_actions():
            raise InvalidActionError("Hit is not allowed now")
        hand = self._current_hand()
        hand.add_card(self.deck.draw(1)[0])
        if hand.is_bust or hand.best_value == 21:
            self._advance_to_next_hand_or_dealer()

    def player_stand(self) -> None:
        if "stand" not in self.available_actions():
            raise InvalidActionError("Stand is not allowed now")
        self._advance_to_next_hand_or_dealer()

    def player_double(self) -> None:
        if "double" not in self.available_actions():
            raise InvalidActionError("Double is not allowed now")
        assert self.player is not None
        hand = self._current_hand()
        self.player.ensure_can_wager(hand.bet)
        self.player.balance -= hand.bet
        hand.bet *= 2
        hand.add_card(self.deck.draw(1)[0])
        self._advance_to_next_hand_or_dealer()

    def player_split(self) -> None:
        if "split" not in self.available_actions():
            raise InvalidActionError("Split is not allowed now")
        assert self.player is not None
        hand = self._current_hand()
        second_card = hand.cards.pop()
        self.player.ensure_can_wager(hand.bet)
        self.player.balance -= hand.bet
        new_hand = Hand(bet=hand.bet)
        new_hand.add_card(second_card)
        hand.add_card(self.deck.draw(1)[0])
        new_hand.add_card(self.deck.draw(1)[0])
        self.player.hands.insert(self.active_hand_index + 1, new_hand)

    def player_surrender(self) -> None:
        if "surrender" not in self.available_actions():
            raise InvalidActionError("Surrender is not allowed now")
        hand = self._current_hand()
        hand.surrendered = True
        self._advance_to_next_hand_or_dealer()

    def take_insurance(self, amount: int) -> None:
        self._ensure_ready()
        assert self.player is not None
        if not self.insurance_offered or self.insurance_resolved:
            raise InvalidActionError("Insurance is not available")
        if amount < 0 or amount > self.player.balance:
            raise InvalidActionError("Invalid insurance amount")
        hand = self._current_hand()
        if amount > hand.bet // 2:
            raise InvalidActionError("Insurance cannot exceed half the original bet")
        self.player.balance -= amount
        hand.insurance_bet = amount
        self.insurance_resolved = True

    def _advance_to_next_hand_or_dealer(self) -> None:
        assert self.player is not None and self.dealer is not None
        self.active_hand_index += 1
        if self.active_hand_index >= len(self.player.hands):
            self._dealer_play_and_settle()

    def _dealer_play_and_settle(self) -> None:
        assert self.player is not None and self.dealer is not None and self.session_stats is not None

        self.dealer.play_out(self.deck)

        dealer_has_blackjack = self.dealer.hand.is_blackjack

        for hand in self.player.hands:
            if hand.insurance_bet > 0:
                if dealer_has_blackjack:
                    self.player.balance += hand.insurance_bet * 3
                hand.insurance_bet = 0

        totals: List[HandResolution] = []
        for hand in self.player.hands:
            resolution = resolve_hand_vs_dealer(hand, self.dealer.hand, self.rules)
            totals.append(resolution)
            if resolution.payout > 0:
                self.player.balance += hand.bet + resolution.payout
                self.dealer.balance -= resolution.payout
            elif resolution.payout < 0:
                self.dealer.balance += -resolution.payout

        self.session_stats.hands_played += 1
        for res in totals:
            if res.payout > 0:
                self.session_stats.player_wins += 1
            elif res.payout < 0 and res.outcome != res.outcome.PLAYER_SURRENDER:
                self.session_stats.player_losses += 1
            elif res.payout == 0:
                self.session_stats.pushes += 1

        self.round_over = True

    def get_summary(self) -> dict:
        self._ensure_ready()
        assert self.player is not None and self.dealer is not None and self.session_stats is not None
        return {
            "initial_player_balance": self.session_stats.initial_player_balance,
            "final_player_balance": self.player.balance,
            "initial_dealer_balance": self.session_stats.initial_dealer_balance,
            "final_dealer_balance": self.dealer.balance,
            "hands_played": self.session_stats.hands_played,
            "player_wins": self.session_stats.player_wins,
            "player_losses": self.session_stats.player_losses,
            "pushes": self.session_stats.pushes,
            "net_player_profit": self.player.balance - self.session_stats.initial_player_balance,
        }


