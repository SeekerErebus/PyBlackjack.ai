from pyblackjack_ai.blackjack.cards import Card, Rank, Suit
from pyblackjack_ai.blackjack.hand import Hand


def test_blackjack_detection() -> None:
    hand = Hand()
    hand.add_card(Card(Rank.ACE, Suit.SPADES))
    hand.add_card(Card(Rank.TEN, Suit.HEARTS))
    assert hand.is_blackjack
    assert hand.best_value == 21


def test_soft_and_hard_totals() -> None:
    hand = Hand()
    hand.add_card(Card(Rank.ACE, Suit.SPADES))
    hand.add_card(Card(Rank.SIX, Suit.HEARTS))
    assert hand.best_value == 17
    assert hand.is_soft

    hand.add_card(Card(Rank.TEN, Suit.CLUBS))
    assert hand.best_value == 17
    assert not hand.is_soft


