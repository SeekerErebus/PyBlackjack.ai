from pyblackjack_ai.blackjack.cards import Card, Rank, Suit
from pyblackjack_ai.blackjack.hand import Hand
from pyblackjack_ai.blackjack.rules import HandOutcome, RulesConfig, resolve_hand_vs_dealer


def _hand_from_cards(*cards: tuple[Rank, Suit]) -> Hand:
    h = Hand()
    for rank, suit in cards:
        h.add_card(Card(rank, suit))
    return h


def test_blackjack_payout() -> None:
    rules = RulesConfig()
    player = _hand_from_cards((Rank.ACE, Suit.SPADES), (Rank.TEN, Suit.HEARTS))
    dealer = _hand_from_cards((Rank.NINE, Suit.CLUBS), (Rank.SEVEN, Suit.DIAMONDS))
    player.bet = 10
    result = resolve_hand_vs_dealer(player, dealer, rules)
    assert result.outcome == HandOutcome.PLAYER_BLACKJACK
    assert result.payout == 15


def test_push() -> None:
    rules = RulesConfig()
    player = _hand_from_cards((Rank.TEN, Suit.SPADES), (Rank.SEVEN, Suit.HEARTS))
    dealer = _hand_from_cards((Rank.NINE, Suit.CLUBS), (Rank.EIGHT, Suit.DIAMONDS))
    player.bet = 10
    result = resolve_hand_vs_dealer(player, dealer, rules)
    assert result.outcome == HandOutcome.PUSH
    assert result.payout == 0


