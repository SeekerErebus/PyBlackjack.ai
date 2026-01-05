from __future__ import annotations

from typing import List

from ..blackjack import Game, RulesConfig
from . import messages as msg


def _prompt_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if value <= 0:
                print(msg.ERROR_POSITIVE_INT)
                continue
            return value
        except ValueError:
            print(msg.ERROR_INVALID_NUMBER)


def _prompt_choice(prompt: str, choices: List[str]) -> str:
    lowered = {c.lower(): c for c in choices}
    while True:
        raw = input(f"{prompt} ({'/'.join(choices)}): ").strip().lower()
        if raw in lowered:
            return lowered[raw]
        print(msg.ERROR_INVALID_CHOICE)


def run() -> None:
    print(msg.WELCOME)
    player_balance = _prompt_int(msg.PROMPT_STARTING_PLAYER_BALANCE)
    dealer_balance = _prompt_int(msg.PROMPT_DEALER_BALANCE)

    game = Game(rules=RulesConfig())
    game.start_new_session(player_balance=player_balance, dealer_balance=dealer_balance)

    reshuffle_threshold = 0.2

    first_round = True
    exited_early = False

    while not game.is_session_over():
        state = game.get_state()
        print(
            msg.LABEL_PLAYER_DEALER_BALANCE.format(
                player_balance=state.player_balance,
                dealer_balance=state.dealer_balance,
            )
        )

        if not first_round:
            choice = _prompt_choice(msg.PROMPT_NEW_HAND_OR_EXIT, ["hand", "exit"])
            if choice == "exit":
                exited_early = True
                break

        game.maybe_reshuffle(reshuffle_threshold)

        bet = _prompt_int(msg.PROMPT_BET)
        if bet > state.player_balance:
            print(msg.ERROR_BET_TOO_HIGH)
            continue

        game.start_hand(bet)
        first_round = False
        state = game.get_state()

        round_view = state.round_view
        assert round_view is not None

        dealer_up = round_view.dealer_hand.cards[0]
        print(msg.LABEL_DEALER_SHOWS.format(card=dealer_up))
        print(msg.LABEL_YOUR_HAND)
        for card in round_view.player_hands[0].cards:
            print(msg.LABEL_CARD_LINE.format(card=card))

        if round_view.insurance_offered:
            ins_choice = _prompt_choice(msg.PROMPT_INSURANCE, ["yes", "no"])
            if ins_choice == "yes":
                max_insurance = round_view.player_hands[0].bet // 2
                if max_insurance > 0:
                    amount = _prompt_int(
                        msg.PROMPT_INSURANCE_AMOUNT.format(
                            max_insurance=max_insurance
                        )
                    )
                    if amount > max_insurance:
                        print(msg.ERROR_INSURANCE_TOO_HIGH)
                    else:
                        try:
                            game.take_insurance(amount)
                        except Exception as exc:  # noqa: BLE001
                            print(msg.ERROR_INSURANCE_FAILED.format(exc=exc))

        while True:
            state = game.get_state()
            round_view = state.round_view
            assert round_view is not None

            if round_view.round_over:
                break

            hand = round_view.player_hands[round_view.active_hand_index]
            print(
                msg.LABEL_HAND_HEADER.format(
                    index=round_view.active_hand_index + 1,
                    total=len(round_view.player_hands),
                )
            )
            print(msg.LABEL_CARDS)
            for card in hand.cards:
                print(msg.LABEL_CARD_LINE.format(card=card))
            print(msg.LABEL_CURRENT_VALUE.format(value=hand.best_value))

            actions = game.available_actions()
            if not actions:
                break

            print(
                msg.LABEL_AVAILABLE_ACTIONS.format(actions=", ".join(actions))
            )
            action = _prompt_choice(msg.PROMPT_ACTION, actions)

            try:
                if action == "hit":
                    # Perform hit and report if the player busts or reaches 21.
                    game.player_hit()
                    # `hand` is a live object from the game state, so it now includes the drawn card.
                    if hand.is_bust:
                        bust_card = hand.cards[-1]
                        print(
                            msg.HIT_BUST_MESSAGE.format(
                                value=hand.best_value,
                                card=bust_card,
                            )
                        )
                    elif hand.best_value == 21:
                        print(
                            msg.HIT_REACH_21_MESSAGE.format(
                                value=hand.best_value,
                            )
                        )
                elif action == "stand":
                    game.player_stand()
                elif action == "split":
                    game.player_split()
                elif action == "surrender":
                    game.player_surrender()
                elif action == "double":
                    # On double-down, draw exactly one card, show it, and then
                    # automatically stand on the resulting total.
                    before_count = len(hand.cards)
                    game.player_double()
                    drawn_card = (
                        hand.cards[-1] if len(hand.cards) > before_count else None
                    )
                    if drawn_card is not None:
                        print(
                            msg.DOUBLE_MESSAGE.format(
                                card=drawn_card,
                                value=hand.best_value,
                            )
                        )
            except Exception as exc:  # noqa: BLE001
                print(msg.ERROR_ACTION_FAILED.format(exc=exc))

        # Show how the dealer finished the hand.
        state = game.get_state()
        round_view = state.round_view
        if round_view is not None:
            dealer_hand = round_view.dealer_hand
            dealer_cards = dealer_hand.cards

            if len(dealer_cards) >= 2:
                print(
                    msg.LABEL_DEALER_HIDDEN_CARD.format(card=dealer_cards[1])
                )

            if len(dealer_cards) > 2:
                print(msg.LABEL_DEALER_DRAWS)
                for card in dealer_cards[2:]:
                    print(msg.LABEL_CARD_LINE.format(card=card))

            print(
                msg.LABEL_DEALER_FINAL_TOTAL.format(
                    total=dealer_hand.best_value
                )
            )

        summary = game.get_summary()
        print(msg.LABEL_ROUND_COMPLETE)
        print(
            msg.LABEL_ROUND_BALANCES.format(
                player_balance=summary["final_player_balance"],
                dealer_balance=summary["final_dealer_balance"],
            )
        )

        if game.is_session_over():
            print(msg.LABEL_SESSION_OVER)
            break

    final = game.get_summary()
    print(msg.SUMMARY_HEADER)
    print(msg.SUMMARY_HANDS_LINE.format(hands=final["hands_played"]))
    print(
        msg.SUMMARY_RESULTS_LINE.format(
            wins=final["player_wins"],
            losses=final["player_losses"],
            pushes=final["pushes"],
        )
    )
    net = final["net_player_profit"]
    result = "profit" if net > 0 else "loss" if net < 0 else "break-even"
    print(msg.SUMMARY_NET_LINE.format(net=net, result=result))

    player_final = final["final_player_balance"]
    dealer_final = final["final_dealer_balance"]

    if not exited_early:
        if dealer_final <= 0 and player_final > 0:
            print(msg.END_CONGRATS_BANKRUPT_DEALER)
        elif player_final <= 0 and dealer_final > 0:
            print(msg.END_PLAYER_BROKE)
    else:
        if net > 0:
            print(msg.END_EARLY_EXIT_POSITIVE)
        elif net < 0:
            print(msg.END_EARLY_EXIT_NEGATIVE)
        else:
            print(msg.END_EARLY_EXIT_EVEN)


