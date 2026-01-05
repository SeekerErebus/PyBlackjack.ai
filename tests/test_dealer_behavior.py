from pyblackjack_ai.blackjack.cards import Card, Deck, Rank, Suit
from pyblackjack_ai.blackjack.entities import Dealer


def test_dealer_hits_until_seventeen() -> None:
    deck = Deck()
    deck._cards = [  # type: ignore[attr-defined]
        Card(Rank.FIVE, Suit.SPADES),
        Card(Rank.SIX, Suit.HEARTS),
    ]
    dealer = Dealer(balance=0)
    hand = dealer.initial_hand()
    hand.add_card(Card(Rank.SIX, Suit.CLUBS))
    dealer.play_out(deck)
    assert dealer.hand.best_value >= 17


