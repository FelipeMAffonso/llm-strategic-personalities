**Table S5.** Linear probability model of trial-level cooperation in the four prisoner's dilemma variants on strategy-play trials against the 16 common opponents, with opponent and game-variant fixed effects (not shown) and standard errors clustered by model. Reference categories: OpenAI, small tier, no reasoning traces. Coefficients are shares of rounds (0.261 = 26.1 percentage points). Meta, Mistral and Alibaba have one model each, so their contrasts are shown without a standard error or test.

| Term | coef | se | p |
|---|---|---|---|
| Intercept | 0.4626 | 0.1793 | 0.0099 |
| Developer: Alibaba | 0.1714 |  |  |
| Developer: Anthropic | 0.2607 | 0.1057 | 0.0137 |
| Developer: DeepSeek | -0.1708 | 0.1588 | 0.2821 |
| Developer: Google | -0.0662 | 0.1423 | 0.6416 |
| Developer: Meta | -0.2450 |  |  |
| Developer: Mistral | 0.2057 |  |  |
| Size tier: frontier | 0.2695 | 0.1162 | 0.0203 |
| Size tier: medium | 0.1777 | 0.0623 | 0.0044 |
| reasoning | -0.0097 | 0.0698 | 0.8890 |
| release_years | -0.1004 | 0.2006 | 0.6167 |
