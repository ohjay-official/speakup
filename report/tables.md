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
| Gemini 3.1 Flash Lite (preview id) | 0.55 | 77% | 1.00 | 30 |
| gpt-oss-120b (cerebras) | 0.55 | 77% | 1.00 | 30 |
| gpt-oss-120b (groq) | 0.55 | 77% | 1.00 | 30 |
| gpt-oss-120b (nebius) | 0.55 | 77% | 1.00 | 30 |

## Main arm: warning rates (grader gpt-oss-120b)

| Model | System | Fraud advice | Fraud task | Legit advice | Legit task | task d' [95% CI] | task c [95% CI] |
|---|---|---|---|---|---|---|---|
| Gemini 3.5 Flash Lite | default | 100% | 96% | 82% | 26% | 2.4 [1.78, 3.26] | -0.56 [-0.93, -0.18] |
| Gemini 3.5 Flash Lite | generic | 100% | 100% | 77% | 59% | 2.4 [1.71, 3.02] | -1.43 [-1.77, -1.13] |
| Gemini 3.5 Flash Lite | guardian | 100% | 100% | 32% | 33% | 3.05 [2.59, 3.6] | -1.1 [-1.34, -0.85] |
| Qwen3.8-27B | default | 100% | 71% | 100% | 23% | 1.28 [0.84, 1.77] | 0.1 [-0.13, 0.37] |
| Qwen3.8-27B | generic | 100% | 99% | 100% | 59% | 2.0 [1.44, 2.68] | -1.22 [-1.57, -0.95] |
| Qwen3.8-27B | guardian | 100% | 100% | 90% | 56% | 2.47 [1.75, 3.1] | -1.39 [-1.76, -1.09] |

### Fraud warning rate by mode (default system prompt)

| Model | A advice | T1 table | T2 invite | T3 borrow | McNemar A vs task (p) |
|---|---|---|---|---|---|
| Gemini 3.5 Flash Lite | 100% | 100% | 92% | 97% | 4 vs 0 (p=0.12) |
| Qwen3.8-27B | 100% | 95% | 58% | 61% | 33 vs 0 (p=2.3e-10) |

## AI grader panel on a 1-in-12 sample of main-arm replies

| Graders | kappa | n |
|---|---|---|

| Grader | Tested model | warned rate | n |
|---|---|---|---|

## Pushback (default arm, task replies that had warned)

| Model | Label | n | still warns | complies without warning | refuses |
|---|---|---|---|---|---|
| Gemini 3.5 Flash Lite | fraud | 33 | 100% | 0% | 97% |
| Qwen3.8-27B | fraud | 61 | 100% | 0% | 85% |
| Qwen3.8-27B | legit | 2 | 100% | 0% | 100% |

## Fresh-branch probe and knew-but-helped (default arm)

| Model | mean P(fraud) frauds | mean P(fraud) legit | fraud task replies with no warning | of those, probe >= 70% |
|---|---|---|---|---|
| Gemini 3.5 Flash Lite | 100 | 21 | 4 | 4 (100%) |
| Qwen3.8-27B | 97 | 22 | 33 | 33 (100%) |

## Anchor (false facts) and generality (jobs, rentals) arms

| Arm | Model | System | fake advice | fake task | real advice | real task | task d' |
|---|---|---|---|---|---|---|---|
| anchor | Gemini 3 Flash | default | n/a | 83% | n/a | n/a | n/a |
| anchor | Gemini 3.5 Flash Lite | default | n/a | 13% | n/a | n/a | n/a |
| anchor | Gemini 3.5 Flash Lite | guardian | n/a | 70% | n/a | n/a | n/a |
| anchor | Qwen3.8-27B | default | n/a | 23% | n/a | n/a | n/a |
| anchor | Qwen3.8-27B | guardian | n/a | 60% | n/a | n/a | n/a |
| anchor | gpt-oss-20b | default | n/a | 25% | n/a | n/a | n/a |
| anchor | gpt-oss-20b | guardian | n/a | 60% | n/a | n/a | n/a |
| general | Gemini 3.5 Flash Lite | default | 100% | 100% | 50% | 38% | 2.36 |
| general | Gemini 3.5 Flash Lite | guardian | 100% | 100% | 62% | 50% | 2.05 |
| general | Qwen3.8-27B | default | 100% | 83% | 100% | 9% | 2.17 |
| general | Qwen3.8-27B | guardian | 100% | 100% | 100% | 59% | 1.83 |
| general | gpt-oss-20b | default | 100% | 20% | 100% | 0% | 0.86 |
| general | gpt-oss-20b | guardian | n/a | 100% | 0% | 25% | 1.91 |

## Robustness checks (default system prompt unless noted)

### Gemini 3.5 Flash Lite

- advice: H 100%, F 82%, d' 1.37, c -1.54 (n 38/22); task: H 96%, F 26%, d' 2.4, c -0.56
- threshold >= 1: fraud advice 100%, fraud task 96%, legit advice 86%, legit task 35%
- threshold >= 2: fraud advice 100%, fraud task 96%, legit advice 82%, legit task 26%
- threshold >= 3: fraud advice 100%, fraud task 94%, legit advice 18%, legit task 6%
- McNemar, one pair per case x framing (advice warned vs all 3 task replies warned): {'advice_only': 4, 'task_only': 0, 'p': np.float64(0.125), 'pairs': 38}
- McNemar by request type: {'T1': {'advice_only': 0, 'task_only': 0, 'p': 1.0, 'pairs': 38}, 'T2': {'advice_only': 3, 'task_only': 0, 'p': np.float64(0.25), 'pairs': 38}, 'T3': {'advice_only': 1, 'task_only': 0, 'p': np.float64(1.0), 'pairs': 38}}
- suppression 0.04, 95% CI clustered by scheme [0.01, 0.07]; task d' CI by scheme [1.77, 3.39]
- framing McNemar (sceptic-only vs enthusiast-only warned): {'scep_only': 4, 'enth_only': 0, 'p': np.float64(0.125), 'pairs': 57}
- task d' fix minus default, CI by scheme: {'generic': {'diff': -0.0, 'ci': [-0.92, 0.5]}, 'guardian': {'diff': 0.65, 'ci': [-0.26, 1.21]}}

### Qwen3.8-27B

- advice: H 100%, F 100%, d' 0.29, c -2.08 (n 38/18); task: H 71%, F 23%, d' 1.28, c 0.1
- threshold >= 1: fraud advice 100%, fraud task 91%, legit advice 100%, legit task 37%
- threshold >= 2: fraud advice 100%, fraud task 71%, legit advice 100%, legit task 23%
- threshold >= 3: fraud advice 100%, fraud task 46%, legit advice 56%, legit task 16%
- McNemar, one pair per case x framing (advice warned vs all 3 task replies warned): {'advice_only': 21, 'task_only': 0, 'p': np.float64(9.5367431640625e-07), 'pairs': 38}
- McNemar by request type: {'T1': {'advice_only': 2, 'task_only': 0, 'p': np.float64(0.5), 'pairs': 37}, 'T2': {'advice_only': 16, 'task_only': 0, 'p': np.float64(3.0517578125e-05), 'pairs': 38}, 'T3': {'advice_only': 15, 'task_only': 0, 'p': np.float64(6.103515625e-05), 'pairs': 38}}
- suppression 0.29, 95% CI clustered by scheme [0.18, 0.4]; task d' CI by scheme [0.79, 1.84]
- framing McNemar (sceptic-only vs enthusiast-only warned): {'scep_only': 19, 'enth_only': 2, 'p': np.float64(0.00022125244140625), 'pairs': 56}
- task d' fix minus default, CI by scheme: {'generic': {'diff': 0.72, 'ci': [0.02, 1.51]}, 'guardian': {'diff': 1.19, 'ci': [0.36, 1.9]}}

