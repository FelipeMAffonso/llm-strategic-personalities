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
