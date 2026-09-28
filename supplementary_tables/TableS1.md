**Table S1.** The 25 models: developer, product line, size tier, whether internal reasoning traces were captured, public release date (verified on the developer's page), the model identifier and route in the released configuration, design and number of trials. The Gemini Flash models may have used Google's own API (Supplementary Note 4). Gemini 3 Pro and 3.1 Pro reason by default; the GPT-5 series reasons internally without exposing traces through the endpoint used.

| Model | Developer | Product line | Size tier | Reasoning traces captured | Release date | Requested identifier | Design | Trials |
|---|---|---|---|---|---|---|---|---|
| Claude Haiku 4.5 | Anthropic | Haiku | small | no | 2025-10-15 | claude-haiku-4-5-20251001 (Anthropic API) | F (five trials in most cells) | 3781 |
| Claude Haiku 4.5 (Thinking) | Anthropic | Haiku | small | yes | 2025-10-15 | claude-haiku-4-5-20251001 (Anthropic API) | F (five trials in most cells) | 3588 |
| Claude Sonnet 4.5 | Anthropic | Sonnet | medium | no | 2025-09-29 | claude-sonnet-4-5-20250929 (Anthropic API) | G (one trial in most cells) | 521 |
| Claude Sonnet 4.6 | Anthropic | Sonnet | medium | no | 2026-02-17 | claude-sonnet-4-6 (Anthropic API) | G (one trial in most cells) | 513 |
| Claude Opus 4.5 | Anthropic | Opus | frontier | no | 2025-11-24 | claude-opus-4-5 (Anthropic API) | G (one trial in most cells) | 440 |
| Claude Opus 4.6 | Anthropic | Opus | frontier | no | 2026-02-05 | claude-opus-4-6 (Anthropic API) | G (one trial in most cells) | 449 |
| GPT-4o Mini | OpenAI | GPT-4o | small | no | 2024-07-18 | gpt-4o-mini (OpenAI API) | F (five trials in most cells) | 2934 |
| GPT-4.1 | OpenAI | GPT-4.1 | frontier | no | 2025-04-14 | gpt-4.1 (OpenAI API) | G (one trial in most cells) | 400 |
| GPT-4.1 Mini | OpenAI | GPT-4.1 | small | no | 2025-04-14 | gpt-4.1-mini (OpenAI API) | F (five trials in most cells) | 3006 |
| GPT-4.1 Nano | OpenAI | GPT-4.1 | small | no | 2025-04-14 | gpt-4.1-nano (OpenAI API) | F (five trials in most cells) | 3274 |
| GPT-5 Mini | OpenAI | GPT-5 | small | no | 2025-08-07 | gpt-5-mini (OpenAI API) | F (five trials in most cells) | 2739 |
| GPT-5 Nano | OpenAI | GPT-5 | small | no | 2025-08-07 | gpt-5-nano (OpenAI API) | F (five trials in most cells) | 2507 |
| GPT-5.3 | OpenAI | GPT-5 | frontier | no | 2026-03-03 | gpt-5.3-chat-latest (OpenAI API) | G (one trial in most cells) | 488 |
| GPT-5.4 | OpenAI | GPT-5 | frontier | no | 2026-03-05 | gpt-5.4 (OpenAI API) | G (one trial in most cells) | 486 |
| Gemini 2.0 Flash | Google | Flash | medium | no | 2025-02-05 | google/gemini-2.0-flash-001 (OpenRouter) | F (five trials in most cells) | 4532 |
| Gemini 2.5 Flash | Google | Flash | medium | no | 2025-06-17 | google/gemini-2.5-flash (OpenRouter) | F (five trials in most cells) | 4345 |
| Gemini 2.5 Flash (Thinking) | Google | Flash | medium | yes | 2025-06-17 | google/gemini-2.5-flash (OpenRouter) | F (five trials in most cells) | 4107 |
| Gemini 3 Flash | Google | Flash | medium | no | 2025-12-17 | google/gemini-3-flash-preview (OpenRouter) | F (five trials in most cells) | 3982 |
| Gemini 3 Pro | Google | Pro | frontier | yes | 2025-11-18 | gemini-3-pro-preview (Vertex AI) | G (one trial in most cells) | 304 |
| Gemini 3.1 Pro | Google | Pro | frontier | yes | 2026-02-19 | gemini-3.1-pro-preview (Vertex AI) | G (one trial in most cells) | 336 |
| DeepSeek V3 | DeepSeek | DeepSeek | frontier | no | 2025-03-24 | deepseek/deepseek-chat-v3-0324 (OpenRouter) | F (five trials in most cells) | 2016 |
| DeepSeek R1 | DeepSeek | DeepSeek | frontier | yes | 2025-01-20 | deepseek/deepseek-r1 (OpenRouter) | F (five trials in most cells) | 1794 |
| LLaMA 3.3 70B | Meta | LLaMA | medium | no | 2024-12-06 | meta-llama/llama-3.3-70b-instruct (OpenRouter) | F (five trials in most cells) | 2105 |
| Ministral 14B | Mistral | Ministral | small | no | 2025-12-02 | mistralai/ministral-14b-2512 (OpenRouter) | F (five trials in most cells) | 1730 |
| Qwen 3.5 Flash | Alibaba | Qwen | medium | no | 2026-02-23 | qwen/qwen3.5-flash-02-23 (OpenRouter) | F (five trials in most cells) | 1529 |
