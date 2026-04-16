def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None or raw == "":
        return False, None, "Enter a guess."

    try:
        # Accept floats like "3.0" but truncate to int
        value = int(float(raw)) if "." in raw else int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret, low=1, high=100):
    """
    Compare guess to secret and return (outcome, message).

    Validates that guess falls within [low, high] before comparing.
    outcome: "Win", "Too High", "Too Low", or "Invalid"
    """
    try:
        secret = int(secret)
    except (ValueError, TypeError):
        return "Invalid", "❌ Could not read the secret number."

    if guess < low or guess > high:
        return "Invalid", f"❌ Guess must be between {low} and {high}!"

    if guess == secret:
        return "Win", "🎉 Correct!"
    if guess > secret:
        return "Too High", "📈 Go LOWER!"
    return "Too Low", "📉 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number.

    Win:     sliding bonus (100 pts minus 10 per attempt, floor 10)
    Wrong:   -5 penalty regardless of direction or attempt parity
    """
    if outcome == "Win":
        points = max(10, 100 - 10 * attempt_number)
        return current_score + points

    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    # "Invalid" or unknown — no change
    return current_score