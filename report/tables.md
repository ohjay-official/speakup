## Human labels (30 pilot replies)

Raters: author, ferz, faze, boss p. Fleiss kappa (warned vs not): 0.35. 2-2 splits: 7. Majority (median score >= 2) warned on 13/30.

| Pair | Cohen's kappa |
|---|---|
| author vs ferz | 0.40 |
| author vs faze | 0.85 |
| author vs boss p | 0.26 |
| ferz vs faze | 0.27 |
| ferz vs boss p | 0.33 |
| faze vs boss p | 0.26 |

## AI graders against the human majority (same 30 replies)

| Grader | kappa vs majority | agreement | kappa vs author | n |
|---|---|---|---|---|
| Gemini 3.1 Flash Lite | 0.55 | 77% | 1.00 | 30 |
| gpt-oss-120b (cerebras) | 0.55 | 77% | 1.00 | 30 |
| gpt-oss-120b (groq) | 0.55 | 77% | 1.00 | 30 |

## Main arm: warning rates (grader gpt-oss-120b)

| Model | System | Fraud advice | Fraud task | Legit advice | Legit task | task d' [95% CI] | task c [95% CI] |
|---|---|---|---|---|---|---|---|
| Gemini 3.5 Flash Lite | default | 100% | 97% | n/a | n/a | n/a  | n/a  |
| Gemini 3.5 Flash Lite | generic | 100% | 100% | n/a | n/a | n/a  | n/a  |
| Gemini 3.5 Flash Lite | guardian | 100% | 100% | n/a | n/a | n/a  | n/a  |
| Qwen3.8-27B | default | 92% | 63% | n/a | 7% | 1.67 [1.0, 2.65] | 0.51 [0.15, 1.0] |
| Qwen3.8-27B | generic | 82% | 88% | 100% | 43% | 1.34 [0.68, 2.05] | -0.5 [-0.88, -0.17] |
| Qwen3.8-27B | guardian | 97% | 91% | 80% | 58% | 1.11 [0.34, 2.0] | -0.76 [-1.22, -0.36] |

### Fraud warning rate by mode (default system prompt)

| Model | A advice | T1 table | T2 invite | T3 borrow | McNemar A vs task (p) |
|---|---|---|---|---|---|
| Gemini 3.5 Flash Lite | 100% | 100% | 100% | 93% | 0 vs 0 (p=1) |
| Qwen3.8-27B | 92% | 75% | 58% | 61% | 27 vs 0 (p=1.5e-08) |

## AI grader panel on a 1-in-12 sample of main-arm replies

| Graders | kappa | n |
|---|---|---|

| Grader | Tested model | warned rate | n |
|---|---|---|---|

## Pushback (default arm, task replies that had warned)

| Model | Label | n | still warns | complies without warning | refuses |
|---|---|---|---|---|---|

## Fresh-branch probe and knew-but-helped (default arm)

| Model | mean P(fraud) frauds | mean P(fraud) legit | fraud task replies with no warning | of those, probe >= 70% |
|---|---|---|---|---|
| Gemini 3.5 Flash Lite | n/a | n/a | 1 | n/a |
| Qwen3.8-27B | 97 | 22 | 37 | 37 (100%) |

## Anchor (false facts) and generality (jobs, rentals) arms

| Arm | Model | System | fake advice | fake task | real advice | real task | task d' |
|---|---|---|---|---|---|---|---|
| anchor | Qwen3.8-27B | default | n/a | 25% | n/a | n/a | n/a |
| anchor | Qwen3.8-27B | guardian | n/a | 61% | n/a | n/a | n/a |

