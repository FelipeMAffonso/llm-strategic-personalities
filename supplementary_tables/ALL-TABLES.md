**Table S1.** The 25 models: developer, product line, size tier, whether internal reasoning traces were captured, public release date (verified on the developer's page), API snapshot, design and number of trials. Gemini 3 Pro and 3.1 Pro reason by default; the GPT-5 series reasons internally without exposing traces through the endpoint used.

| Model | Developer | Product line | Size tier | Reasoning traces captured | Release date | Snapshot | Design | Trials |
|---|---|---|---|---|---|---|---|---|
| Claude Haiku 4.5 | Anthropic | Haiku | small | no | 2025-10-15 | claude-haiku-4-5-20251001 | F (five trials per cell) | 3781 |
| Claude Haiku 4.5 (Thinking) | Anthropic | Haiku | small | yes | 2025-10-15 | claude-haiku-4-5-20251001 | F (five trials per cell) | 3588 |
| Claude Sonnet 4.5 | Anthropic | Sonnet | medium | no | 2025-09-29 | claude-sonnet-4-5-20250929 | G (one trial per cell) | 521 |
| Claude Sonnet 4.6 | Anthropic | Sonnet | medium | no | 2026-02-17 | claude-sonnet-4-6 | G (one trial per cell) | 513 |
| Claude Opus 4.5 | Anthropic | Opus | frontier | no | 2025-11-24 | claude-opus-4-5 | G (one trial per cell) | 440 |
| Claude Opus 4.6 | Anthropic | Opus | frontier | no | 2026-02-05 | claude-opus-4-6 | G (one trial per cell) | 449 |
| GPT-4o Mini | OpenAI | GPT-4o | small | no | 2024-07-18 | gpt-4o-mini-2024-07-18 | F (five trials per cell) | 2934 |
| GPT-4.1 | OpenAI | GPT-4.1 | frontier | no | 2025-04-14 | gpt-4.1-2025-04-14 | G (one trial per cell) | 400 |
| GPT-4.1 Mini | OpenAI | GPT-4.1 | small | no | 2025-04-14 | gpt-4.1-mini-2025-04-14 | F (five trials per cell) | 3006 |
| GPT-4.1 Nano | OpenAI | GPT-4.1 | small | no | 2025-04-14 | gpt-4.1-nano-2025-04-14 | F (five trials per cell) | 3274 |
| GPT-5 Mini | OpenAI | GPT-5 | small | no | 2025-08-07 | gpt-5-mini-2025-08-07 | F (five trials per cell) | 2739 |
| GPT-5 Nano | OpenAI | GPT-5 | small | no | 2025-08-07 | gpt-5-nano-2025-08-07 | F (five trials per cell) | 2507 |
| GPT-5.3 | OpenAI | GPT-5 | frontier | no | 2026-03-03 | gpt-5.3-chat-latest | G (one trial per cell) | 488 |
| GPT-5.4 | OpenAI | GPT-5 | frontier | no | 2026-03-05 | gpt-5.4 | G (one trial per cell) | 486 |
| Gemini 2.0 Flash | Google | Flash | medium | no | 2025-02-05 | gemini-2.0-flash-001 | F (five trials per cell) | 4532 |
| Gemini 2.5 Flash | Google | Flash | medium | no | 2025-06-17 | gemini-2.5-flash | F (five trials per cell) | 4345 |
| Gemini 2.5 Flash (Thinking) | Google | Flash | medium | yes | 2025-06-17 | gemini-2.5-flash | F (five trials per cell) | 4107 |
| Gemini 3 Flash | Google | Flash | medium | no | 2025-12-17 | gemini-3-flash-preview | F (five trials per cell) | 3982 |
| Gemini 3 Pro | Google | Pro | frontier | yes | 2025-11-18 | gemini-3-pro-preview | G (one trial per cell) | 304 |
| Gemini 3.1 Pro | Google | Pro | frontier | yes | 2026-02-19 | gemini-3.1-pro-preview | G (one trial per cell) | 336 |
| DeepSeek V3 | DeepSeek | DeepSeek | frontier | no | 2024-12-26 | deepseek-chat | F (five trials per cell) | 2016 |
| DeepSeek R1 | DeepSeek | DeepSeek | frontier | yes | 2025-01-20 | deepseek-reasoner | F (five trials per cell) | 1794 |
| LLaMA 3.3 70B | Meta | LLaMA | medium | no | 2024-12-06 | Llama-3.3-70B-Instruct | F (five trials per cell) | 2105 |
| Ministral 14B | Mistral | Ministral | small | no | 2025-12-02 | ministral-14b-2512 | F (five trials per cell) | 1730 |
| Qwen 3.5 Flash | Alibaba | Qwen | medium | no | 2026-02-23 | qwen3.5-flash-2026-02-23 | F (five trials per cell) | 1529 |


**Table S2.** Cooperation in the four prisoner's dilemma variants by model: against the 16 fixed opponents every model faced, weighted equally per opponent (the headline measure), and pooled across every matchup the model played, with the 95 percent t-distribution interval on the trial-level pooled values, clipped to the unit range. Sorted by the same-opponent rate.

| Model | Developer | Same opponents (%) | n | Pooled (%) | Pooled 95% CI | n pooled |
|---|---|---|---|---|---|---|
| GPT-5 Nano | OpenAI | 1.4 | 285 | 1.5 | [1.0, 1.9] | 378 |
| GPT-5 Mini | OpenAI | 6.7 | 305 | 6.3 | [5.3, 7.4] | 414 |
| Gemini 2.0 Flash | Google | 8.3 | 320 | 8.3 | [7.5, 9.1] | 616 |
| GPT-4.1 Nano | OpenAI | 17.3 | 300 | 15.1 | [13.0, 17.1] | 466 |
| LLaMA 3.3 70B | Meta | 19.7 | 270 | 19.9 | [18.8, 20.9] | 346 |
| GPT-5.3 | OpenAI | 23.8 | 84 | 23.0 | [16.9, 29.1] | 90 |
| Gemini 2.5 Flash (Thinking) | Google | 28.5 | 319 | 26.5 | [24.1, 28.9] | 564 |
| Gemini 2.5 Flash | Google | 29.2 | 319 | 28.5 | [26.0, 31.0] | 587 |
| Gemini 3.1 Pro | Google | 32.0 | 53 | 35.7 | [25.3, 46.1] | 56 |
| DeepSeek V3 | DeepSeek | 33.1 | 264 | 31.0 | [27.7, 34.3] | 328 |
| DeepSeek R1 | DeepSeek | 36.7 | 243 | 36.6 | [33.4, 39.8] | 283 |
| Ministral 14B | Mistral | 37.7 | 263 | 37.5 | [35.4, 39.7] | 293 |
| GPT-4.1 Mini | OpenAI | 41.9 | 283 | 38.5 | [34.9, 42.0] | 432 |
| Claude Haiku 4.5 | Anthropic | 42.2 | 320 | 39.8 | [36.5, 43.1] | 528 |
| Claude Haiku 4.5 (Thinking) | Anthropic | 42.5 | 320 | 39.3 | [36.0, 42.6] | 508 |
| GPT-5.4 | OpenAI | 46.8 | 75 | 48.4 | [39.6, 57.1] | 80 |
| Qwen 3.5 Flash | Alibaba | 49.6 | 247 | 49.4 | [45.1, 53.7] | 262 |
| GPT-4.1 | OpenAI | 52.5 | 64 | 53.7 | [45.0, 62.4] | 68 |
| GPT-4o Mini | OpenAI | 53.2 | 306 | 50.3 | [47.1, 53.4] | 439 |
| Gemini 3 Pro | Google | 55.7 | 59 | 56.2 | [47.2, 65.3] | 61 |
| Gemini 3 Flash | Google | 59.7 | 320 | 56.8 | [53.8, 59.7] | 549 |
| Claude Sonnet 4.6 | Anthropic | 65.9 | 83 | 70.9 | [63.6, 78.1] | 90 |
| Claude Sonnet 4.5 | Anthropic | 67.7 | 81 | 69.0 | [62.3, 75.6] | 87 |
| Claude Opus 4.5 | Anthropic | 68.3 | 67 | 70.4 | [62.1, 78.7] | 71 |
| Claude Opus 4.6 | Anthropic | 69.3 | 68 | 71.5 | [63.6, 79.4] | 72 |


**Table S3.** Cooperation (percent of rounds) in the four prisoner's dilemma variants against each of the 16 fixed opponents, by model.

Part (a), columns 1 to 8 of 16.

| Model | always_cooperate | always_defect | anti_mirror | defect_once | false_defector | grim_trigger | hard_tft | mirror |
|---|---|---|---|---|---|---|---|---|
| Claude Haiku 4.5 | 61.5 | 6.5 | 18.0 | 38.5 | 16.0 | 76.0 | 53.5 | 42.0 |
| Claude Haiku 4.5 (Thinking) | 67.5 | 7.0 | 24.0 | 33.0 | 20.0 | 76.0 | 73.0 | 33.0 |
| Claude Sonnet 4.5 | 96.0 | 16.0 | 38.3 | 87.5 | 33.3 | 94.0 | 96.0 | 66.0 |
| Claude Sonnet 4.6 | 100.0 | 10.0 | 38.3 | 87.5 | 26.0 | 100.0 | 100.0 | 54.0 |
| Claude Opus 4.5 | 100.0 | 10.0 | 47.5 | 87.5 | 30.0 | 100.0 | 100.0 | 97.5 |
| Claude Opus 4.6 | 100.0 | 10.0 | 37.5 | 90.0 | 32.5 | 100.0 | 100.0 | 80.0 |
| GPT-4o Mini | 73.7 | 22.6 | 22.6 | 25.6 | 30.5 | 87.5 | 86.1 | 48.5 |
| GPT-4.1 | 67.5 | 10.0 | 25.0 | 60.0 | 20.0 | 90.0 | 87.5 | 52.5 |
| GPT-4.1 Mini | 53.2 | 10.7 | 16.5 | 38.3 | 15.6 | 69.4 | 70.0 | 60.5 |
| GPT-4.1 Nano | 18.8 | 5.0 | 19.5 | 23.5 | 11.1 | 23.2 | 18.3 | 10.0 |
| GPT-5 Mini | 7.4 | 2.5 | 7.9 | 5.8 | 6.5 | 4.7 | 5.9 | 7.2 |
| GPT-5 Nano | 1.9 | 0.6 | 0.5 | 3.3 | 1.6 | 0.7 | 1.9 | 2.1 |
| GPT-5.3 | 25.0 | 8.6 | 3.3 | 6.2 | 10.0 | 33.3 | 64.0 | 65.0 |
| GPT-5.4 | 47.5 | 10.0 | 16.0 | 26.0 | 17.5 | 82.5 | 80.0 | 75.0 |
| Gemini 2.0 Flash | 10.0 | 5.5 | 7.5 | 8.0 | 11.0 | 8.5 | 10.0 | 7.0 |
| Gemini 2.5 Flash | 45.5 | 9.0 | 22.5 | 30.5 | 19.5 | 25.5 | 41.0 | 28.9 |
| Gemini 2.5 Flash (Thinking) | 42.0 | 4.5 | 26.0 | 27.5 | 16.5 | 27.5 | 47.0 | 32.0 |
| Gemini 3 Flash | 93.0 | 10.0 | 41.0 | 70.5 | 20.5 | 92.0 | 91.5 | 50.5 |
| Gemini 3 Pro | 90.0 | 7.5 | 33.3 | 50.0 | 20.0 | 67.5 | 90.0 | 90.0 |
| Gemini 3.1 Pro | 67.5 | 5.0 | 30.0 | 45.0 | 10.0 | 90.0 | 45.0 | 12.5 |
| DeepSeek V3 | 65.3 | 7.7 | 26.7 | 27.8 | 17.3 | 43.5 | 31.1 | 33.3 |
| DeepSeek R1 | 32.4 | 10.7 | 22.0 | 63.3 | 35.9 | 32.2 | 26.0 | 52.3 |
| LLaMA 3.3 70B | 9.3 | 25.9 | 20.0 | 14.7 | 23.5 | 23.8 | 20.6 | 20.0 |
| Ministral 14B | 44.0 | 19.4 | 33.8 | 41.7 | 30.7 | 51.6 | 39.4 | 36.0 |
| Qwen 3.5 Flash | 70.8 | 6.2 | 21.5 | 64.4 | 22.0 | 81.2 | 65.3 | 37.3 |

Part (b), columns 9 to 16 of 16.

| Model | noise_10 | noise_20 | pavlov | random | reverse_tft | suspicious_tft | tit_for_tat | tit_for_two_tats |
|---|---|---|---|---|---|---|---|---|
| Claude Haiku 4.5 | 60.5 | 41.0 | 58.0 | 26.5 | 17.0 | 12.5 | 67.0 | 81.5 |
| Claude Haiku 4.5 (Thinking) | 47.0 | 49.0 | 64.0 | 19.0 | 20.0 | 13.5 | 65.5 | 69.0 |
| Claude Sonnet 4.5 | 82.0 | 60.0 | 100.0 | 48.0 | 40.0 | 38.3 | 96.0 | 92.0 |
| Claude Sonnet 4.6 | 86.7 | 60.0 | 100.0 | 37.5 | 35.0 | 20.0 | 100.0 | 100.0 |
| Claude Opus 4.5 | 80.0 | 52.5 | 100.0 | 40.0 | 28.0 | 20.0 | 100.0 | 100.0 |
| Claude Opus 4.6 | 71.7 | 74.0 | 100.0 | 55.0 | 35.0 | 22.5 | 100.0 | 100.0 |
| GPT-4o Mini | 61.6 | 51.1 | 86.8 | 32.5 | 26.0 | 27.4 | 84.2 | 84.2 |
| GPT-4.1 | 67.5 | 40.0 | 67.5 | 47.5 | 15.0 | 10.0 | 90.0 | 90.0 |
| GPT-4.1 Mini | 71.7 | 44.4 | 74.4 | 22.4 | 13.9 | 14.4 | 32.2 | 63.3 |
| GPT-4.1 Nano | 9.4 | 22.5 | 17.2 | 22.2 | 26.0 | 8.4 | 16.3 | 25.5 |
| GPT-5 Mini | 18.4 | 5.3 | 6.5 | 5.3 | 3.5 | 5.8 | 2.8 | 12.0 |
| GPT-5 Nano | 0.6 | 0.0 | 0.5 | 2.5 | 1.1 | 2.1 | 2.4 | 0.5 |
| GPT-5.3 | 24.0 | 22.5 | 34.0 | 8.0 | 15.0 | 6.7 | 25.0 | 30.0 |
| GPT-5.4 | 77.5 | 58.3 | 73.3 | 40.0 | 22.0 | 12.5 | 62.5 | 48.3 |
| Gemini 2.0 Flash | 9.0 | 7.0 | 12.0 | 6.5 | 6.5 | 5.0 | 11.5 | 8.0 |
| Gemini 2.5 Flash | 31.5 | 28.0 | 44.5 | 26.5 | 19.0 | 21.5 | 38.5 | 34.8 |
| Gemini 2.5 Flash (Thinking) | 33.0 | 29.0 | 34.5 | 18.0 | 17.5 | 14.5 | 39.5 | 46.8 |
| Gemini 3 Flash | 71.0 | 58.0 | 91.5 | 33.0 | 27.0 | 24.0 | 91.0 | 91.0 |
| Gemini 3 Pro | 46.7 | 40.0 | 90.0 | 33.3 | 17.5 | 50.0 | 90.0 | 75.0 |
| Gemini 3.1 Pro | 40.0 | 17.5 | 45.0 | 10.0 | 20.0 | 30.0 | 45.0 | 0.0 |
| DeepSeek V3 | 43.5 | 26.7 | 67.7 | 27.6 | 22.5 | 7.4 | 37.2 | 44.7 |
| DeepSeek R1 | 49.3 | 38.8 | 45.7 | 24.0 | 22.7 | 39.3 | 62.0 | 31.2 |
| LLaMA 3.3 70B | 20.0 | 20.6 | 21.3 | 18.2 | 20.6 | 20.0 | 18.3 | 18.8 |
| Ministral 14B | 45.9 | 40.5 | 45.6 | 35.6 | 35.9 | 21.1 | 38.2 | 44.4 |
| Qwen 3.5 Flash | 59.3 | 52.5 | 82.7 | 32.4 | 23.1 | 31.9 | 66.9 | 76.0 |


**Table S4.** The four competition games separately: the measure, its cross-model range and coefficient of variation, and each model's value. The competition index in the main text is the first-price row.

Part (a), columns 1 to 8 of 30.

| game | measure | definition | min | max | cv | Claude Haiku 4.5 | Claude Haiku 4.5 (Thinking) | Claude Sonnet 4.5 |
|---|---|---|---|---|---|---|---|---|
| First-price auction | bid_ratio | mean bid over maximum bid | 0.249 | 0.426 | 0.164 | 0.367 | 0.368 | 0.348 |
| Vickrey auction | bid_ratio | mean bid over maximum bid (truthful bidding is 0.50 when values average 50) | 0.474 | 0.513 | 0.022 | 0.505 | 0.501 | 0.475 |
| All-pay auction | bid_ratio | mean bid over maximum bid | 0.012 | 0.297 | 0.370 | 0.273 | 0.267 | 0.229 |
| Colonel Blotto | bid_ratio | mean allocation over the maximum on the reported battlefield | 0.131 | 0.410 | 0.229 | 0.257 | 0.262 | 0.193 |

Part (b), columns 9 to 16 of 30.

| game | Claude Sonnet 4.6 | Claude Opus 4.5 | Claude Opus 4.6 | GPT-4o Mini | GPT-4.1 | GPT-4.1 Mini | GPT-4.1 Nano | GPT-5 Mini |
|---|---|---|---|---|---|---|---|---|
| First-price auction | 0.340 | 0.357 | 0.316 | 0.378 | 0.319 | 0.359 | 0.317 | 0.253 |
| Vickrey auction | 0.507 | 0.512 | 0.500 | 0.501 | 0.474 | 0.502 | 0.508 | 0.495 |
| All-pay auction | 0.284 | 0.195 | 0.246 | 0.183 | 0.096 | 0.273 | 0.255 | 0.222 |
| Colonel Blotto | 0.131 | 0.222 | 0.410 | 0.299 | 0.332 | 0.247 | 0.324 | 0.301 |

Part (c), columns 17 to 24 of 30.

| game | GPT-5 Nano | GPT-5.3 | GPT-5.4 | Gemini 2.0 Flash | Gemini 2.5 Flash | Gemini 2.5 Flash (Thinking) | Gemini 3 Flash | Gemini 3 Pro |
|---|---|---|---|---|---|---|---|---|
| First-price auction | 0.258 | 0.290 | 0.326 | 0.426 | 0.425 | 0.325 | 0.278 | 0.251 |
| Vickrey auction | 0.513 | 0.500 | 0.499 | 0.494 | 0.497 | 0.503 | 0.497 | 0.499 |
| All-pay auction | 0.146 | 0.249 | 0.012 | 0.234 | 0.297 | 0.279 | 0.247 | 0.161 |
| Colonel Blotto | 0.325 | 0.302 | 0.331 | 0.299 | 0.285 | 0.245 | 0.330 | 0.375 |

Part (d), columns 25 to 30 of 30.

| game | Gemini 3.1 Pro | DeepSeek V3 | DeepSeek R1 | LLaMA 3.3 70B | Ministral 14B | Qwen 3.5 Flash |
|---|---|---|---|---|---|---|
| First-price auction | 0.256 | 0.300 | 0.249 | 0.396 | 0.327 | 0.267 |
| Vickrey auction | 0.488 | 0.493 | 0.486 | 0.476 | 0.502 | 0.478 |
| All-pay auction | 0.023 | 0.192 | 0.164 | 0.270 | 0.284 | 0.161 |
| Colonel Blotto | 0.400 | 0.168 | 0.287 | 0.325 | 0.260 | 0.332 |


**Table S5.** Linear probability model of trial-level cooperation in the four prisoner's dilemma variants on strategy-play trials against the 16 common opponents, with opponent and game-variant fixed effects (not shown) and standard errors clustered by model. Reference categories: OpenAI, small tier, no reasoning traces. Coefficients are shares of rounds (0.257 = 25.7 percentage points).

| Term | coef | se | p |
|---|---|---|---|
| Intercept | 0.4610 | 0.1809 | 0.0108 |
| Developer: Alibaba | 0.1665 | 0.1588 | 0.2944 |
| Developer: Anthropic | 0.2572 | 0.1022 | 0.0119 |
| Developer: DeepSeek | -0.1849 | 0.1909 | 0.3329 |
| Developer: Google | -0.0712 | 0.1417 | 0.6153 |
| Developer: Meta | -0.2473 | 0.1309 | 0.0589 |
| Developer: Mistral | 0.2044 | 0.1365 | 0.1342 |
| Size tier: frontier | 0.2690 | 0.1191 | 0.0240 |
| Size tier: medium | 0.1808 | 0.0644 | 0.0050 |
| reasoning | -0.0043 | 0.0718 | 0.9521 |
| release_years | -0.0983 | 0.2034 | 0.6291 |


**Table S6.** Share of between-model variance (across the 25 model means) explained by each characteristic alone (eta squared or R squared), jointly, and by developer given the others, for prisoner's dilemma cooperation and for the trust index.

| outcome | developer | size_tier | reasoning | release_years | joint_r2 | developer_given_others |
|---|---|---|---|---|---|---|
| pd_cooperation | 0.390 | 0.119 | 0.000 | 0.126 | 0.571 | 0.368 |
| trust_index | 0.188 | 0.212 | 0.007 | 0.034 | 0.404 | 0.182 |


**Table S7.** Mechanism components by model, every measure on strategy-play trials against the fixed opponents every model faced with equal weight per opponent. Cooperation rates against three fixed opponents in the prisoner's dilemma (the best response is 0 against always-cooperate and always-defect, and 0.90 against tit-for-tat and grim trigger with a known last round), the dictator share, trust sent, the stag share in the risky stag hunt, the risky share in chicken, beauty-contest depth, and the four components (preference = mean of cooperation against always-cooperate and dictator share; belief = mean of cooperation against tit-for-tat and beauty depth; risk = mean of stag and chicken risky shares; rule = cooperation against always-defect).

Part (a), columns 1 to 8 of 14.

| Model | Developer | vs always-cooperate | vs always-defect | vs tit-for-tat | vs grim trigger | Dictator share | Trust sent | Stag (risky) |
|---|---|---|---|---|---|---|---|---|
| Claude Haiku 4.5 | Anthropic | 0.615 | 0.065 | 0.670 | 0.760 | 0.482 | 0.591 | 0.631 |
| Claude Haiku 4.5 (Thinking) | Anthropic | 0.675 | 0.070 | 0.655 | 0.760 | 0.469 | 0.588 | 0.620 |
| Claude Sonnet 4.5 | Anthropic | 0.960 | 0.160 | 0.960 | 0.940 | 0.500 | 0.652 | 0.694 |
| Claude Sonnet 4.6 | Anthropic | 1.000 | 0.100 | 1.000 | 1.000 | 0.500 | 0.767 | 0.694 |
| Claude Opus 4.5 | Anthropic | 1.000 | 0.100 | 1.000 | 1.000 | 0.500 | 0.913 | 0.644 |
| Claude Opus 4.6 | Anthropic | 1.000 | 0.100 | 1.000 | 1.000 | 0.500 | 0.902 | 0.667 |
| GPT-4o Mini | OpenAI | 0.737 | 0.226 | 0.842 | 0.875 | 0.500 | 0.816 | 0.571 |
| GPT-4.1 | OpenAI | 0.675 | 0.100 | 0.900 | 0.900 | 0.490 | 0.433 | 0.500 |
| GPT-4.1 Mini | OpenAI | 0.532 | 0.107 | 0.322 | 0.694 | 0.478 | 0.581 | 0.687 |
| GPT-4.1 Nano | OpenAI | 0.188 | 0.050 | 0.163 | 0.232 | 0.319 | 0.577 | 0.431 |
| GPT-5 Mini | OpenAI | 0.074 | 0.025 | 0.028 | 0.047 | 0.490 | 0.542 | 0.684 |
| GPT-5 Nano | OpenAI | 0.019 | 0.006 | 0.024 | 0.007 | 0.000 | 0.051 | 0.542 |
| GPT-5.3 | OpenAI | 0.250 | 0.086 | 0.250 | 0.333 | 0.255 | 0.808 | 0.667 |
| GPT-5.4 | OpenAI | 0.475 | 0.100 | 0.625 | 0.825 | 0.434 | 0.553 | 0.472 |
| Gemini 2.0 Flash | Google | 0.100 | 0.055 | 0.115 | 0.085 | 0.200 | 0.668 | 0.344 |
| Gemini 2.5 Flash | Google | 0.455 | 0.090 | 0.385 | 0.255 | 0.206 | 0.696 | 0.500 |
| Gemini 2.5 Flash (Thinking) | Google | 0.420 | 0.045 | 0.395 | 0.275 | 0.285 | 0.586 | 0.711 |
| Gemini 3 Flash | Google | 0.930 | 0.100 | 0.910 | 0.920 | 0.441 | 0.788 | 0.676 |
| Gemini 3 Pro | Google | 0.900 | 0.075 | 0.900 | 0.675 | 0.420 | 0.833 | 0.800 |
| Gemini 3.1 Pro | Google | 0.675 | 0.050 | 0.450 | 0.900 | 0.170 | 0.600 | 0.744 |
| DeepSeek V3 | DeepSeek | 0.653 | 0.077 | 0.372 | 0.435 | 0.367 | 0.577 | 0.300 |
| DeepSeek R1 | DeepSeek | 0.324 | 0.107 | 0.620 | 0.322 | 0.255 | 0.501 | 0.613 |
| LLaMA 3.3 70B | Meta | 0.093 | 0.259 | 0.183 | 0.237 | 0.436 | 0.637 | 0.351 |
| Ministral 14B | Mistral | 0.440 | 0.194 | 0.382 | 0.516 | 0.504 | 0.668 | 0.439 |
| Qwen 3.5 Flash | Alibaba | 0.708 | 0.062 | 0.669 | 0.812 | 0.490 | 0.634 | 0.680 |

Part (b), columns 9 to 14 of 14.

| Model | Chicken risky | Beauty depth | Preference | Belief | Risk | Rule |
|---|---|---|---|---|---|---|
| Claude Haiku 4.5 | 0.057 | 0.836 | 0.549 | 0.753 | 0.344 | 0.065 |
| Claude Haiku 4.5 (Thinking) | 0.046 | 0.866 | 0.572 | 0.761 | 0.333 | 0.070 |
| Claude Sonnet 4.5 | 0.142 | 0.961 | 0.730 | 0.961 | 0.418 | 0.160 |
| Claude Sonnet 4.6 | 0.142 | 0.704 | 0.750 | 0.852 | 0.418 | 0.100 |
| Claude Opus 4.5 | 0.115 | 0.765 | 0.750 | 0.883 | 0.380 | 0.100 |
| Claude Opus 4.6 | 0.115 | 0.857 | 0.750 | 0.928 | 0.391 | 0.100 |
| GPT-4o Mini | 0.165 | 0.633 | 0.618 | 0.738 | 0.368 | 0.226 |
| GPT-4.1 | 0.185 | 0.887 | 0.583 | 0.893 | 0.342 | 0.100 |
| GPT-4.1 Mini | 0.183 | 0.966 | 0.505 | 0.644 | 0.435 | 0.107 |
| GPT-4.1 Nano | 0.192 | 0.991 | 0.254 | 0.577 | 0.311 | 0.050 |
| GPT-5 Mini | 0.157 | 0.995 | 0.282 | 0.511 | 0.420 | 0.025 |
| GPT-5 Nano | 0.301 | 1.000 | 0.009 | 0.512 | 0.422 | 0.006 |
| GPT-5.3 | 0.088 | 0.965 | 0.252 | 0.608 | 0.378 | 0.086 |
| GPT-5.4 | 0.046 | 0.974 | 0.455 | 0.800 | 0.259 | 0.100 |
| Gemini 2.0 Flash | 0.352 | 0.760 | 0.150 | 0.438 | 0.348 | 0.055 |
| Gemini 2.5 Flash | 0.118 | 0.916 | 0.331 | 0.651 | 0.309 | 0.090 |
| Gemini 2.5 Flash (Thinking) | 0.121 | 0.974 | 0.352 | 0.684 | 0.416 | 0.045 |
| Gemini 3 Flash | 0.037 | 0.987 | 0.686 | 0.948 | 0.356 | 0.100 |
| Gemini 3 Pro | 0.069 | 1.000 | 0.660 | 0.950 | 0.435 | 0.075 |
| Gemini 3.1 Pro | 0.177 | 1.000 | 0.422 | 0.725 | 0.461 | 0.050 |
| DeepSeek V3 | 0.211 | 0.960 | 0.510 | 0.666 | 0.256 | 0.077 |
| DeepSeek R1 | 0.300 | 0.969 | 0.289 | 0.795 | 0.457 | 0.107 |
| LLaMA 3.3 70B | 0.492 | 0.884 | 0.265 | 0.533 | 0.421 | 0.259 |
| Ministral 14B | 0.458 | 0.386 | 0.472 | 0.384 | 0.449 | 0.194 |
| Qwen 3.5 Flash | 0.146 | 0.963 | 0.599 | 0.816 | 0.413 | 0.062 |


**Table S8.** Final-round cooperation (percent) in the four prisoner's dilemma variants by opponent class, with the round-9 rate against reactive opponents and the type assigned from reactive play (sustained cooperator: round 10 at or above 50 percent; horizon-conditioned: round 9 at or above 25 percent, round 10 below 10 percent, drop at least 25 points; unconditional defector: rounds 9 and 10 below 20 percent; the rest intermediate). Benchmarks: reactive opponents, cooperate through round 9 and defect in round 10; lenient reactive opponents (tit-for-two-tats, Pavlov, two noisy variants, false defector and defect-once), defect in round 10, although earlier defection can go unpunished; the fixed and model opponents, defect throughout. Self-play was run for every model; cross-play was run for the 16 models tested at five trials per cell, so cross-play cells for the nine frontier models rest on the few trials in which a frontier model appeared as another model's opponent, or are empty.

| Model | Reactive R9 | Reactive R10 | Lenient reactive R10 | Always-cooperate R10 | Always-defect R10 | Self-play R10 | Cross-play R10 | Type (reactive) |
|---|---|---|---|---|---|---|---|---|
| Claude Haiku 4.5 | 60.0 | 48.3 | 27.5 | 45.0 | 5.0 | 27.5 | 19.9 | intermediate |
| Claude Haiku 4.5 (Thinking) | 56.7 | 25.0 | 18.3 | 25.0 | 0.0 | 22.5 | 11.9 | intermediate |
| Claude Sonnet 4.5 | 86.7 | 40.0 | 32.5 | 60.0 | 0.0 | 80.0 | 100.0 | intermediate |
| Claude Sonnet 4.6 | 80.0 | 80.0 | 61.7 | 100.0 | 0.0 | 100.0 | 100.0 | sustained cooperator |
| Claude Opus 4.5 | 100.0 | 100.0 | 58.3 | 100.0 | 0.0 | 100.0 |  | sustained cooperator |
| Claude Opus 4.6 | 91.7 | 91.7 | 62.2 | 100.0 | 0.0 | 100.0 |  | sustained cooperator |
| GPT-4o Mini | 62.9 | 56.1 | 34.4 | 57.9 | 0.0 | 67.5 | 30.9 | sustained cooperator |
| GPT-4.1 | 83.3 | 8.3 | 0.0 | 0.0 | 0.0 | 0.0 |  | horizon-conditioned |
| GPT-4.1 Mini | 50.2 | 29.9 | 23.1 | 31.6 | 0.0 | 25.0 | 12.6 | intermediate |
| GPT-4.1 Nano | 12.7 | 10.7 | 16.3 | 17.6 | 0.0 | 2.8 | 5.3 | unconditional defector |
| GPT-5 Mini | 1.9 | 1.9 | 0.0 | 0.0 | 0.0 | 0.0 | 3.0 | unconditional defector |
| GPT-5 Nano | 4.1 | 1.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | unconditional defector |
| GPT-5.3 | 16.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | intermediate |
| GPT-5.4 | 58.3 | 58.3 | 21.4 | 25.0 | 0.0 | 50.0 | 50.0 | sustained cooperator |
| Gemini 2.0 Flash | 8.3 | 3.3 | 0.0 | 0.0 | 0.0 | 0.0 | 1.1 | unconditional defector |
| Gemini 2.5 Flash | 22.2 | 13.7 | 12.5 | 25.0 | 0.0 | 10.0 | 7.7 | intermediate |
| Gemini 2.5 Flash (Thinking) | 15.0 | 0.0 | 2.5 | 0.0 | 0.0 | 0.0 | 0.0 | intermediate |
| Gemini 3 Flash | 81.7 | 13.3 | 10.8 | 30.0 | 0.0 | 17.5 | 5.6 | intermediate |
| Gemini 3 Pro | 91.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | horizon-conditioned |
| Gemini 3.1 Pro | 50.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | horizon-conditioned |
| DeepSeek V3 | 26.1 | 12.0 | 18.2 | 35.3 | 0.0 | 2.5 | 10.5 | intermediate |
| DeepSeek R1 | 43.8 | 5.6 | 1.0 | 0.0 | 7.1 | 6.7 | 3.5 | horizon-conditioned |
| LLaMA 3.3 70B | 18.1 | 11.5 | 12.4 | 0.0 | 11.8 | 11.1 | 8.8 | intermediate |
| Ministral 14B | 30.3 | 22.5 | 20.6 | 13.3 | 18.8 | 10.7 | 17.9 | intermediate |
| Qwen 3.5 Flash | 55.4 | 2.0 | 1.0 | 0.0 | 0.0 | 3.3 | 0.8 | horizon-conditioned |


**Table S9.** Reciprocity statistics by model, pooled across all cooperation games and opponents: the probability of cooperating after the opponent cooperated, P(C|C), and after the opponent defected, P(C|D), in percent; their difference (the reciprocity index); the number of round pairs in each condition; and the archetype assigned by the thresholds in Note 10.

| Model | P(C\|C) | P(C\|D) | Reciprocity index | N after C | N after D | Archetype |
|---|---|---|---|---|---|---|
| Claude Opus 4.6 | 92.8 | 4.5 | 88.3 | 469 | 179 | Strict reciprocator |
| Claude Sonnet 4.6 | 91.7 | 4.1 | 87.6 | 588 | 222 | Strict reciprocator |
| Claude Opus 4.5 | 90.4 | 4.1 | 86.3 | 467 | 172 | Strict reciprocator |
| Claude Sonnet 4.5 | 88.7 | 8.8 | 79.9 | 556 | 227 | Strict reciprocator |
| Gemini 3 Flash | 83.6 | 0.3 | 83.3 | 3066 | 1875 | Grudge-holder |
| Gemini 3 Pro | 77.5 | 2.8 | 74.7 | 368 | 181 | Grudge-holder |
| GPT-4.1 | 72.2 | 1.5 | 70.7 | 417 | 195 | Grudge-holder |
| Qwen 3.5 Flash | 70.7 | 7.4 | 63.3 | 1464 | 894 | Strict reciprocator |
| Claude Haiku 4.5 | 68.5 | 5.1 | 63.4 | 2382 | 2370 | Strict reciprocator |
| Claude Haiku 4.5 (Thinking) | 67.9 | 3.7 | 64.2 | 2283 | 2289 | Strict reciprocator |
| GPT-4o Mini | 67.2 | 18.3 | 48.9 | 2225 | 1726 | Moderate reciprocator |
| GPT-5.4 | 64.8 | 4.8 | 60.0 | 472 | 248 | Strict reciprocator |
| GPT-4.1 Mini | 62.9 | 5.6 | 57.3 | 2007 | 1881 | Strict reciprocator |
| Gemini 3.1 Pro | 62.8 | 0.4 | 62.4 | 261 | 243 | Grudge-holder |
| DeepSeek V3 | 54.8 | 8.8 | 46.0 | 1345 | 1607 | Moderate reciprocator |
| Gemini 2.5 Flash | 54.0 | 11.1 | 42.9 | 2077 | 3206 | Moderate reciprocator |
| DeepSeek R1 | 50.7 | 22.8 | 27.9 | 1339 | 1208 | Moderate reciprocator |
| Gemini 2.5 Flash (Thinking) | 50.1 | 6.6 | 43.5 | 2133 | 2943 | Moderate reciprocator |
| Ministral 14B | 48.3 | 24.1 | 24.2 | 1245 | 1392 | Moderate reciprocator |
| GPT-4.1 Nano | 35.0 | 5.9 | 29.1 | 1339 | 2855 | Weak reciprocator |
| GPT-5.3 | 34.0 | 1.8 | 32.2 | 430 | 380 | Weak reciprocator |
| LLaMA 3.3 70B | 14.3 | 22.2 | -7.9 | 1157 | 1957 | Anti-reciprocator |
| Gemini 2.0 Flash | 12.5 | 6.1 | 6.4 | 1503 | 4041 | Unconditional defector |
| GPT-5 Mini | 10.5 | 2.8 | 7.7 | 1195 | 2531 | Unconditional defector |
| GPT-5 Nano | 2.1 | 1.0 | 1.1 | 1043 | 2359 | Unconditional defector |


**Table S10.** Reasoning-trace clustering by model: the silhouette score with developer as the label under the lexical embedding (TF-IDF reduced to 384 dimensions) and under the sentence-transformer embedding (all-MiniLM-L6-v2). Positive values mean a model's reasoning texts sit closer to its own developer's models than to another developer's.

| Model | Developer | Silhouette, lexical | Silhouette, sentence transformer |
|---|---|---|---|
| Claude Haiku 4.5 | Anthropic | 0.40 | 0.24 |
| Claude Haiku 4.5 (Thinking) | Anthropic | 0.20 | 0.11 |
| Claude Sonnet 4.5 | Anthropic | 0.62 | 0.44 |
| Claude Sonnet 4.6 | Anthropic | 0.49 | -0.01 |
| Claude Opus 4.5 | Anthropic | 0.61 | 0.52 |
| Claude Opus 4.6 | Anthropic | 0.58 | 0.47 |
| GPT-4o Mini | OpenAI | -0.68 | -0.75 |
| GPT-4.1 | OpenAI | -0.54 | -0.83 |
| GPT-4.1 Mini | OpenAI | -0.59 | -0.74 |
| GPT-4.1 Nano | OpenAI | -0.60 | -0.79 |
| GPT-5 Mini | OpenAI | 0.06 | -0.02 |
| GPT-5 Nano | OpenAI | 0.01 | 0.02 |
| GPT-5.3 | OpenAI | -0.13 | -0.48 |
| GPT-5.4 | OpenAI | 0.00 | -0.04 |
| Gemini 2.0 Flash | Google | -0.25 | -0.58 |
| Gemini 2.5 Flash | Google | 0.02 | -0.34 |
| Gemini 2.5 Flash (Thinking) | Google | -0.07 | -0.42 |
| Gemini 3 Flash | Google | -0.40 | -0.50 |
| Gemini 3 Pro | Google | -0.63 | -0.44 |
| Gemini 3.1 Pro | Google | -0.29 | -0.20 |
| DeepSeek V3 | DeepSeek | -0.35 | -0.58 |
| DeepSeek R1 | DeepSeek | 0.14 | 0.27 |
| LLaMA 3.3 70B | Meta | 0.00 | 0.00 |
| Ministral 14B | Mistral | -0.85 | 0.00 |
| Qwen 3.5 Flash | Alibaba | 0.00 | 0.00 |
