**Table S10.** Reasoning-trace clustering by model: the silhouette score with developer as the label under the lexical embedding (TF-IDF reduced to 384 dimensions) and under the sentence-transformer embedding (all-MiniLM-L6-v2). Positive values mean a model's reasoning texts sit closer to its own developer's models than to another developer's. Both embeddings read the same 41,520 texts and use the same labels: the nine fixed strategies form a group of their own, and a developer's only model (LLaMA 3.3 70B, Ministral 14B, Qwen 3.5 Flash) scores 0 by definition.

| Model | Developer | Silhouette, lexical | Silhouette, sentence transformer |
|---|---|---|---|
| Claude Haiku 4.5 | Anthropic | 0.19 | 0.24 |
| Claude Haiku 4.5 (Thinking) | Anthropic | 0.12 | 0.11 |
| Claude Sonnet 4.5 | Anthropic | 0.45 | 0.44 |
| Claude Sonnet 4.6 | Anthropic | 0.49 | -0.01 |
| Claude Opus 4.5 | Anthropic | 0.54 | 0.52 |
| Claude Opus 4.6 | Anthropic | 0.55 | 0.47 |
| GPT-4o Mini | OpenAI | -0.68 | -0.75 |
| GPT-4.1 | OpenAI | -0.54 | -0.83 |
| GPT-4.1 Mini | OpenAI | -0.59 | -0.74 |
| GPT-4.1 Nano | OpenAI | -0.60 | -0.79 |
| GPT-5 Mini | OpenAI | 0.06 | -0.02 |
| GPT-5 Nano | OpenAI | -0.02 | 0.02 |
| GPT-5.3 | OpenAI | -0.13 | -0.48 |
| GPT-5.4 | OpenAI | 0.00 | -0.04 |
| Gemini 2.0 Flash | Google | -0.25 | -0.58 |
| Gemini 2.5 Flash | Google | 0.02 | -0.34 |
| Gemini 2.5 Flash (Thinking) | Google | -0.07 | -0.42 |
| Gemini 3 Flash | Google | -0.40 | -0.50 |
| Gemini 3 Pro | Google | -0.63 | -0.44 |
| Gemini 3.1 Pro | Google | -0.29 | -0.20 |
| DeepSeek V3 | DeepSeek | -0.43 | -0.58 |
| DeepSeek R1 | DeepSeek | -0.14 | 0.27 |
| LLaMA 3.3 70B | Meta | 0.00 | 0.00 |
| Ministral 14B | Mistral | 0.00 | 0.00 |
| Qwen 3.5 Flash | Alibaba | 0.00 | 0.00 |
