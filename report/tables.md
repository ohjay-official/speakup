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
| Gemini 3.5 Flash Lite | default | 100% | 98% | n/a | n/a | n/a  | n/a  |
| Gemini 3.5 Flash Lite | generic | 100% | 100% | n/a | n/a | n/a  | n/a  |
| Gemini 3.5 Flash Lite | guardian | 100% | 100% | n/a | n/a | n/a  | n/a  |
| Qwen3.8-27B | default | 100% | 67% | n/a | 5% | 2.03 [1.35, 2.97] | 0.57 [0.22, 1.04] |
| Qwen3.8-27B | generic | 100% | 99% | 100% | 43% | 2.34 [1.66, 3.18] | -1.0 [-1.4, -0.66] |
| Qwen3.8-27B | guardian | 100% | 100% | 88% | 59% | 2.36 [1.63, 3.0] | -1.39 [-1.76, -1.1] |

### Fraud warning rate by mode (default system prompt)

| Model | A advice | T1 table | T2 invite | T3 borrow | McNemar A vs task (p) |
|---|---|---|---|---|---|
| Gemini 3.5 Flash Lite | 100% | 100% | 100% | 94% | 0 vs 0 (p=1) |
| Qwen3.8-27B | 100% | 92% | 58% | 61% | 25 vs 0 (p=6e-08) |

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
| Qwen3.8-27B | 97 | 22 | 33 | 33 (100%) |

## Anchor (false facts) and generality (jobs, rentals) arms

| Arm | Model | System | fake advice | fake task | real advice | real task | task d' |
|---|---|---|---|---|---|---|---|
| anchor | Gemini 3 Flash | default | n/a | 100% | n/a | n/a | n/a |
| anchor | Qwen3.8-27B | default | n/a | 23% | n/a | n/a | n/a |
| anchor | Qwen3.8-27B | guardian | n/a | 59% | n/a | n/a | n/a |
| anchor | gpt-oss-20b | default | n/a | 11% | n/a | n/a | n/a |
| anchor | gpt-oss-20b | guardian | n/a | 60% | n/a | n/a | n/a |
| general | Qwen3.8-27B | default | 100% | 73% | 100% | 0% | 2.47 |
| general | Qwen3.8-27B | guardian | 100% | 100% | 100% | 53% | 1.88 |
| general | gpt-oss-20b | default | 100% | 50% | 100% | 0% | 0.97 |
| general | gpt-oss-20b | guardian | n/a | 100% | 0% | 0% | 1.96 |

