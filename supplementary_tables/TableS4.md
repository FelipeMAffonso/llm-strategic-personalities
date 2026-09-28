**Table S4.** The three scored competition games separately: the measure, its cross-model range and coefficient of variation, and each model's value. The competition index in the main text pools the three auctions, using the fixed opponents every model faced with each opponent weighted equally (Table 1); the values here are each game's mean over all of a model's trials. Colonel Blotto was played but is not scored, because the parser kept only one of the several numbers each answer required.

Part (a), columns 1 to 8 of 30.

| game | measure | definition | min | max | cv | Claude Haiku 4.5 | Claude Haiku 4.5 (Thinking) | Claude Sonnet 4.5 |
|---|---|---|---|---|---|---|---|---|
| First-price auction | bid_ratio | mean bid over maximum bid | 0.249 | 0.426 | 0.164 | 0.367 | 0.368 | 0.348 |
| Vickrey auction | bid_ratio | mean bid over maximum bid (truthful bidding is 0.50 when values average 50) | 0.474 | 0.513 | 0.022 | 0.505 | 0.501 | 0.475 |
| All-pay auction | bid_ratio | mean bid over maximum bid | 0.012 | 0.297 | 0.370 | 0.273 | 0.267 | 0.229 |

Part (b), columns 9 to 16 of 30.

| game | Claude Sonnet 4.6 | Claude Opus 4.5 | Claude Opus 4.6 | GPT-4o Mini | GPT-4.1 | GPT-4.1 Mini | GPT-4.1 Nano | GPT-5 Mini |
|---|---|---|---|---|---|---|---|---|
| First-price auction | 0.340 | 0.357 | 0.316 | 0.378 | 0.319 | 0.359 | 0.317 | 0.253 |
| Vickrey auction | 0.507 | 0.512 | 0.500 | 0.501 | 0.474 | 0.502 | 0.508 | 0.495 |
| All-pay auction | 0.284 | 0.195 | 0.246 | 0.183 | 0.096 | 0.273 | 0.255 | 0.222 |

Part (c), columns 17 to 24 of 30.

| game | GPT-5 Nano | GPT-5.3 | GPT-5.4 | Gemini 2.0 Flash | Gemini 2.5 Flash | Gemini 2.5 Flash (Thinking) | Gemini 3 Flash | Gemini 3 Pro |
|---|---|---|---|---|---|---|---|---|
| First-price auction | 0.258 | 0.290 | 0.326 | 0.426 | 0.425 | 0.325 | 0.278 | 0.251 |
| Vickrey auction | 0.513 | 0.500 | 0.499 | 0.494 | 0.497 | 0.503 | 0.497 | 0.499 |
| All-pay auction | 0.146 | 0.249 | 0.012 | 0.234 | 0.297 | 0.279 | 0.247 | 0.161 |

Part (d), columns 25 to 30 of 30.

| game | Gemini 3.1 Pro | DeepSeek V3 | DeepSeek R1 | LLaMA 3.3 70B | Ministral 14B | Qwen 3.5 Flash |
|---|---|---|---|---|---|---|
| First-price auction | 0.256 | 0.300 | 0.249 | 0.396 | 0.327 | 0.267 |
| Vickrey auction | 0.488 | 0.493 | 0.486 | 0.476 | 0.502 | 0.478 |
| All-pay auction | 0.023 | 0.192 | 0.164 | 0.270 | 0.284 | 0.161 |
