import json
import requests
from logic_utils import check_guess

# ── AI reliability helpers ────────────────────────────────────────────────────

def ask_claude(guess: int, secret: int) -> str:
    """
    Ask Claude what outcome a guess should produce, and return the
    normalised outcome string: "Win", "Too High", or "Too Low".
    Returns "Error" if the API call fails or the response is unrecognisable.
    """
    prompt = (
        f"You are judging a number-guessing game. "
        f"The secret number is {secret}. The player guessed {guess}. "
        f'Reply with ONLY one of these exact words: "Win", "Too High", or "Too Low". '
        f"No explanation, no punctuation, just the outcome word."
    )
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=15,
        )
        resp.raise_for_status()
        raw = resp.json()["content"][0]["text"].strip().strip('"').strip("'")
        if raw in ("Win", "Too High", "Too Low"):
            return raw
        return "Error"
    except Exception:
        return "Error"


def run_ai_reliability_suite(cases: list[tuple[int, int]]) -> dict:
    """
    Run a list of (guess, secret) cases through both check_guess() and Claude.
    Returns a summary dict with pass count, fail count, and any mismatches.
    """
    results = {"passed": 0, "failed": 0, "mismatches": []}
    for guess, secret in cases:
        expected_outcome, _ = check_guess(guess, secret)
        ai_outcome = ask_claude(guess, secret)
        if ai_outcome == expected_outcome:
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["mismatches"].append(
                {"guess": guess, "secret": secret,
                 "expected": expected_outcome, "ai_said": ai_outcome}
            )
    return results


# ── Original unit tests ───────────────────────────────────────────────────────

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == ("Win", "🎉 Correct!")

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == ("Too High", "📈 Go LOWER!")

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == ("Too Low", "📉 Go HIGHER!")

def test_guess_out_of_range_low():
    # If guess is less than 1, it should return "Invalid"
    result = check_guess(0, 50)
    assert result == ("Invalid", "❌ Guess must be between 1 and 100!")

def test_guess_out_of_range_high():
    # If guess is greater than 100, it should return "Invalid"
    result = check_guess(101, 50)
    assert result == ("Invalid", "❌ Guess must be between 1 and 100!")


# ── AI reliability test (calls Claude API) ────────────────────────────────────

# A small fixed set of cases covering all three outcomes
AI_TEST_CASES = [
    (50, 50),   # Win
    (60, 50),   # Too High
    (40, 50),   # Too Low
    (1,  100),  # Too Low  (extreme)
    (99, 1),    # Too High (extreme)
    (7,  7),    # Win      (low value)
]
AI_PASS_THRESHOLD = 0.80   # require ≥ 80 % agreement to pass


def test_ai_outcome_reliability():
    """
    Claude should agree with check_guess() on at least 80 % of test cases.
    Prints a detailed report so you can see exactly where it diverges.
    """
    summary = run_ai_reliability_suite(AI_TEST_CASES)
    total = summary["passed"] + summary["failed"]
    rate  = summary["passed"] / total if total else 0

    print(f"\nAI reliability: {summary['passed']}/{total} passed ({rate:.0%})")
    if summary["mismatches"]:
        print("Mismatches:")
        for m in summary["mismatches"]:
            print(f"  guess={m['guess']} secret={m['secret']} "
                  f"expected={m['expected']} ai_said={m['ai_said']}")

    assert rate >= AI_PASS_THRESHOLD, (
        f"AI reliability {rate:.0%} is below the {AI_PASS_THRESHOLD:.0%} threshold. "
        f"Mismatches: {json.dumps(summary['mismatches'], indent=2)}"
    )


# ── Run as a standalone script ────────────────────────────────────────────────

if __name__ == "__main__":
    print("Running AI reliability suite...")
    summary = run_ai_reliability_suite(AI_TEST_CASES)
    total = summary["passed"] + summary["failed"]
    rate  = summary["passed"] / total if total else 0
    print(f"Result: {summary['passed']}/{total} passed ({rate:.0%})")
    if summary["mismatches"]:
        print("Mismatches:")
        for m in summary["mismatches"]:
            print(f"  guess={m['guess']} secret={m['secret']} "
                  f"expected={m['expected']} ai_said={m['ai_said']}")