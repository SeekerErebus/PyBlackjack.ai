class BlackjackError(Exception):
    """Base exception for blackjack engine errors."""


class InvalidActionError(BlackjackError):
    """Raised when an action is not allowed in the current state."""


class InsufficientBalanceError(BlackjackError):
    """Raised when a participant lacks funds for a bet or split."""


class GameStateError(BlackjackError):
    """Raised when the game state is inconsistent or an operation is out of order."""


