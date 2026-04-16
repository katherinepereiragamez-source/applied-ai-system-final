# Glitchy Guesser — AI-Reliability Edition

> A number-guessing game rebuilt with clean architecture, bug-free logic, and an AI reliability testing layer powered by Claude.

---

## 🎮 Original Project (Modules 1–3)

**Project name:** Glitchy Guesser

Glitchy Guesser is a Streamlit-based number-guessing game where the player tries to identify a randomly generated secret number within a limited number of attempts. The original project supported three difficulty levels (Easy, Normal, Hard) with different number ranges and attempt limits, and tracked a running score that rewarded faster correct guesses. However, the original codebase contained several intentional and unintentional bugs — including a type-coercion bug that made winning impossible on every even-numbered attempt — making it a useful starting point for a debugging and refactoring exercise.

---

## 📌 Title and Summary

**Glitchy Guesser — AI-Reliability Edition** extends the original game in two ways:

1. **Refactored architecture** — all game logic was extracted from `app.py` into a dedicated `logic_utils.py` module, making the code testable, reusable, and easy to reason about.
2. **AI reliability layer** — a Claude-powered test suite (`test_game_logic.py`) sends game scenarios to the Claude API and verifies that the AI's judgment matches the deterministic ground truth produced by `check_guess()`. This demonstrates a real-world pattern used in AI quality assurance: comparing a language model's outputs against a trusted reference implementation.

**Why it matters:** As AI systems are used to interpret or judge game state, decisions, or user input, it's critical to measure how reliably they perform. This project shows how to build that measurement loop directly into a test suite.

---

## 🗺 Architecture Overview

```
Human player
     │  raw text input
     ▼
parse_guess()        ← validates and coerces input to int
     │ ok / error
     ▼
check_guess()        ← compares guess to secret; returns outcome + message
     │ outcome, message
     ▼
update_score()       ← awards or deducts points based on outcome
     │ new score
     ▼
Streamlit UI         ← renders hint, score, attempts remaining
     │
     ├── Win / Lose ──► Game over screen
     └── Continue ────► loops back to player

── Automated tests (test_game_logic.py) ──────────────────────
  • 5 unit tests target check_guess() directly (no UI needed)
  • test_ai_outcome_reliability() sends 6 scenarios to Claude
    and asserts ≥ 80% agreement with check_guess() ground truth

── Developer review ──────────────────────────────────────────
  • Debug expander in Streamlit sidebar shows secret, attempts,
    score, and full guess history at runtime
```

The system diagram is also available as an image in `/assets/system_diagram.png`.

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.11+
- An Anthropic API key (for the AI reliability test only)

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/glitchy-guesser.git
cd glitchy-guesser
```

### 2. Install dependencies
```bash
pip install streamlit requests
```

### 3. Set your API key (for AI tests only)
```bash
export ANTHROPIC_API_KEY=your_key_here
```

### 4. Run the game
```bash
streamlit run app.py
```

### 5. Run the test suite
```bash
# Unit tests only (no API key needed)
pytest test_game_logic.py -k "not ai"

# Full suite including AI reliability test
pytest test_game_logic.py -v

# AI reliability check as a standalone script
python test_game_logic.py
```

---

## 💬 Sample Interactions

### Example 1 — Correct guess (Win)
```
Secret number: 42
Player guesses: 42

check_guess(42, 42) → ("Win", "🎉 Correct!")
Claude asked:       → "Win"
Result: PASS ✅
```

### Example 2 — Guess too high
```
Secret number: 50
Player guesses: 99

check_guess(99, 50) → ("Too High", "📈 Go LOWER!")
Claude asked:        → "Too High"
Result: PASS ✅
```

### Example 3 — Out-of-range guess
```
Secret number: 50
Player guesses: 0

check_guess(0, 50) → ("Invalid", "❌ Guess must be between 1 and 100!")
UI displays error banner; attempt counter does not increment.
```

### Example 4 — AI reliability report (terminal output)
```
AI reliability: 6/6 passed (100%)
```

---

## 🏗 Design Decisions

**Separating logic from UI (`logic_utils.py`)**
The biggest structural decision was moving all game logic out of `app.py` into `logic_utils.py`. This makes every function independently testable without launching Streamlit, and follows the single-responsibility principle. The trade-off is a small amount of extra wiring — `app.py` now imports from `logic_utils` — but the testability gain is worth it.

**Range validation as a parameter, not a hard-coded constant**
The original `check_guess()` hard-coded the range as 1–100, which contradicted the Easy (1–20) and Hard (1–50) difficulty settings. The fix makes `low` and `high` optional parameters with sensible defaults, so the function works correctly for any difficulty without breaking existing calls.

**80% agreement threshold for AI tests**
Rather than requiring 100% agreement — which would make the test brittle to occasional API variance — the threshold is set at 80%. This is realistic for a production reliability check: you want to catch systematic failures, not fluke responses.

**`check_guess()` returns a tuple, not a bare string**
Returning `(outcome, message)` keeps the outcome machine-readable (for scoring logic and tests) while also carrying a human-readable message (for the UI), without needing two separate function calls.

---

## 🧪 Testing Summary

| Test | Status |
|---|---|
| `test_winning_guess` | ✅ Pass |
| `test_guess_too_high` | ✅ Pass |
| `test_guess_too_low` | ✅ Pass |
| `test_guess_out_of_range_low` | ✅ Pass |
| `test_guess_out_of_range_high` | ✅ Pass |
| `test_ai_outcome_reliability` (6 cases) | ✅ 6/6 Pass (100%) |

**What worked well:** Claude consistently produced the correct single-word outcome for straightforward numeric comparisons. The prompt engineering was simple — constraining the model to reply with only one of three exact words eliminated parsing ambiguity entirely.

**What was tricky:** The original tests assumed `check_guess()` returned a bare string (`"Win"`), but the refactored version returns a tuple (`("Win", "🎉 Correct!")`). The tests had to be updated to match the new return format.

**What I learned:** Deterministic unit tests and AI reliability tests serve different purposes. Unit tests verify exact correctness; AI reliability tests verify *consistency* — that the model behaves predictably across a range of inputs. Both are necessary in a system where AI is used to interpret or judge something.



## 🔗 Repository Structure

```
glitchy-guesser/
├── app.py                  # Streamlit UI and game loop
├── logic_utils.py          # All game logic (pure functions)
├── test_game_logic.py      # Unit tests + AI reliability suite
├── model_card.md           # Reflection and ethics documentation
├── README.md               # This file
└── assets/
    └── system_diagram.png  # Architecture diagram
```

---
