# Model Card — Glitchy Guesser AI Reliability Layer

This document covers the reflection, ethics, and AI collaboration notes required for the capstone submission.

---

## 🤖 Model Details

- **Model used:** Claude (claude-sonnet-4-20250514) via the Anthropic Messages API
- **Task:** Outcome classification — given a guess and a secret number, classify the result as "Win", "Too High", or "Too Low"
- **Input format:** Natural language prompt describing the game state
- **Output format:** A single constrained word from a fixed vocabulary of three options
- **Max tokens:** 10 (deliberately minimal to prevent verbose responses)

---

## 🎯 Intended Use

The AI layer is used exclusively as a **reliability evaluator**, not as a player or game engine. It answers the question: *"Does Claude agree with our deterministic game logic?"* This pattern — comparing an AI's judgment to a trusted reference — is common in production AI quality assurance pipelines.

The game logic itself (`check_guess()`, `update_score()`, etc.) remains fully deterministic and does not depend on the AI at any point during gameplay.

---

## ⚠️ Limitations and Biases

**Limitations:**
- The AI is tested on a narrow, well-defined task (three-way numeric comparison). This does not reflect how it would perform on ambiguous or open-ended game scenarios.
- The test suite uses only 6 fixed cases. A more robust evaluation would use hundreds of randomly generated cases across all difficulty ranges.
- The 80% pass threshold is somewhat arbitrary. In a production system, the threshold and case count would be determined through empirical baseline testing.

**Biases:**
- The prompt is written in English only. A non-English-speaking player's input is never passed to the AI, so there is no language bias risk in the current design.
- The test cases are not exhaustive — they do not cover boundary values like guess=1, secret=1 or guess=100, secret=100, which could theoretically behave differently.

---

## 🚨 Misuse Considerations

**Could this AI be misused?**
In its current form, the AI only ever receives a guess integer and a secret integer, and returns one of three words. There is no user-generated free text passed to the model, so prompt injection or adversarial input is not a realistic attack surface here.

If the system were extended to accept free-text player input and pass it directly to the API (e.g., "what should I guess next?"), that would introduce risk. Mitigations would include: input sanitization, a system prompt that constrains the model's role, and output validation before displaying results to the player.

---

## 😮 Surprises During Testing

The most surprising finding was how reliably Claude handled the task even with a minimal prompt. The initial assumption was that constraining the model to a single word would require careful prompt engineering — but a straightforward instruction ("Reply with ONLY one of these exact words") was sufficient for 100% accuracy across all test cases.

The trickier issue was not AI behavior but a code bug: the original `check_guess()` returned a bare string, while the refactored version returned a tuple. This caused all five original tests to fail until the assertions were updated — a reminder that test failures are not always caused by the thing you changed most recently.

---

## 🤝 AI Collaboration Notes

This project was built in collaboration with Claude (via claude.ai).

### One instance where the AI gave a helpful suggestion

When refactoring `check_guess()`, the AI proactively identified that the original range validation (`guess > 100`) was hard-coded and would silently be wrong for Easy and Hard difficulty levels. It suggested making `low` and `high` optional parameters instead, which was the right architectural call and something I had not specifically asked for. This saved a bug that would have been subtle and hard to catch in testing.

### One instance where the AI's suggestion was flawed

The AI initially removed the range validation from `check_guess()` entirely when doing the refactor, arguing that "range enforcement belongs in the UI, not in the function." While that argument has some merit architecturally, it caused the two out-of-range tests (`test_guess_out_of_range_low`, `test_guess_out_of_range_high`) to fail. The correct fix — adding `low` and `high` as parameters — preserved testability while keeping the validation in the logic layer where it could be verified independently of Streamlit. This was a case where the AI's reasoning was internally consistent but wrong in the context of the existing test requirements.

---

## 📊 Testing Results Summary

| Category | Result |
|---|---|
| Unit tests (5 cases) | 5/5 passed ✅ |
| AI reliability test (6 cases) | 6/6 passed (100%) ✅ |
| Pass threshold | 80% required, 100% achieved |
| Mismatches | 0 |

The AI performed at ceiling on this narrow task. Future work would expand the test case count and introduce edge cases (boundary values, extreme difficulty ranges, multi-round consistency checks) to stress-test reliability more rigorously.

---

## 💡 Reflection: What This Project Taught Me About AI and Problem-Solving

Building the reliability layer made concrete something that is easy to say but hard to internalize: **AI outputs need to be measured, not assumed.** It is tempting to run a model on a few examples, see correct answers, and call it reliable. The test suite forces a more rigorous standard — the model has to pass a defined threshold across a fixed set of cases, and that threshold is checked automatically every time the code runs.

The refactoring exercise also highlighted how much easier AI integration becomes when the underlying logic is clean and deterministic. Because `check_guess()` always returns the same output for the same input, it was trivial to use as a ground-truth reference. In messier systems, establishing that reference is often the hardest part of building a reliability evaluation layer.

Finally, working with an AI coding assistant revealed a pattern worth remembering: the AI is most useful when you know enough to evaluate its suggestions critically. The range-validation decision above was only catchable because the test suite made the failure visible immediately. Without tests, that architectural choice would have looked reasonable and shipped.