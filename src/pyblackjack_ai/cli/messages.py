from __future__ import annotations

"""
Centralised CLI message templates for the terminal UI.

Keeping messages in one place makes it easier to tweak tone and wording
without touching control-flow logic.
"""

WELCOME = "Welcome to PyBlackjack.ai!"

PROMPT_STARTING_PLAYER_BALANCE = "Enter starting player balance: "
PROMPT_DEALER_BALANCE = "Enter starting dealer (house) balance: "
PROMPT_NEW_HAND_OR_EXIT = "Start a new hand or exit"
PROMPT_BET = "Enter your bet: "
PROMPT_INSURANCE = "Dealer shows an Ace. Take insurance?"
PROMPT_INSURANCE_AMOUNT = "Enter insurance amount (max {max_insurance}): "
PROMPT_ACTION = "Choose action"

ERROR_POSITIVE_INT = "Please enter a positive integer."
ERROR_INVALID_NUMBER = "Invalid number, try again."
ERROR_INVALID_CHOICE = "Invalid choice, try again."
ERROR_BET_TOO_HIGH = "You cannot bet more than your current balance."
ERROR_INSURANCE_TOO_HIGH = "Insurance amount too high, skipping insurance."
ERROR_INSURANCE_FAILED = "Could not take insurance: {exc}"
ERROR_ACTION_FAILED = "Action failed: {exc}"

LABEL_PLAYER_DEALER_BALANCE = (
    "\nPlayer balance: {player_balance} | Dealer balance: {dealer_balance}"
)
LABEL_DEALER_SHOWS = "\nDealer shows: {card}"
LABEL_YOUR_HAND = "Your hand:"
LABEL_CARD_LINE = " - {card}"
LABEL_HAND_HEADER = "\nHand {index} of {total}"
LABEL_CARDS = "Cards:"
LABEL_CURRENT_VALUE = "Current value: {value}"
LABEL_AVAILABLE_ACTIONS = "Available actions: {actions}"
LABEL_DEALER_HIDDEN_CARD = "\nDealer's hidden card was: {card}"
LABEL_DEALER_DRAWS = "Dealer draws:"
LABEL_DEALER_FINAL_TOTAL = "Dealer final total: {total}"
LABEL_ROUND_COMPLETE = "\nRound complete."
LABEL_ROUND_BALANCES = (
    "Player balance: {player_balance} | Dealer balance: {dealer_balance}"
)
LABEL_SESSION_OVER = "Session Over"

HIT_BUST_MESSAGE = (
    "You bust with a hand value of {value} after drawing {card}."
)
HIT_REACH_21_MESSAGE = (
    "You reached 21 with a hand value of {value}. Standing automatically."
)
DOUBLE_MESSAGE = (
    "You double down and draw {card}, ending with a hand value of {value}."
)

SUMMARY_HEADER = "\nSession summary:"
SUMMARY_HANDS_LINE = "Hands played: {hands}"
SUMMARY_RESULTS_LINE = (
    "Wins: {wins} | Losses: {losses} | Pushes: {pushes}"
)
SUMMARY_NET_LINE = "Net result: {net} ({result})"

END_CONGRATS_BANKRUPT_DEALER = (
    "You bankrupted the dealer. Congratulations, you broke the house!"
)
END_PLAYER_BROKE = (
    "You're out of chips. Consider this a gentle reminder that the house "
    "usually wins—and maybe take a break from gambling."
)
END_EARLY_EXIT_POSITIVE = (
    "You left the table ahead. Nice work walking away a winner."
)
END_EARLY_EXIT_NEGATIVE = (
    "You chose to walk away while behind. Could be worse—at least you "
    "stopped feeding the house."
)
END_EARLY_EXIT_EVEN = (
    "You broke even and walked away. Not bad; many gamblers wish they did the same."
)


