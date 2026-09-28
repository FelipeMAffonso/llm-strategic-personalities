# Language models are equally competitive but unequally cooperative

## Overview

This repository contains the code and data for the paper "Language models are equally competitive but unequally
cooperative" (Felipe M. Affonso, Spears School of Business, Oklahoma State University). Twenty-five language models from
seven developers (Anthropic, OpenAI, Google, DeepSeek, Meta, Mistral and Alibaba) played 38 repeated economic games in
eight categories (coordination, strategic depth, competition, cooperation, trust, fairness, negotiation and risk
taking) against programmed opponents (strategy-play), against copies of themselves (self-play) and against other
models (cross-play). The data hold 51,906 trials, 578,425 rounds and 813,950 model replies, collected between
28 February and 9 March 2026. (Counting one seat per model per round gives 826,990; the 13,040 recipient seats of
the dictator and third-party punishment games in self-play and cross-play hold no reply.)

The repository holds:
- **The games**: the game engine, the prompts, the programmed opponents and the 38 games (`games/`).
- **Data collection**: the code that ran the models through their APIs, with the two designs of the study
  (`data_collection/`).
- **Analyses**: the trial-level measures computed from the raw trial files, the analyses reported in the paper, the
  clustering of the models' reasoning texts and the re-parsing check (`analysis/`).
- **Summary data**: the trial-level data (one row per trial), every analysis result and the results of the
  re-parsing check (`summary_data/`).
- **Supplementary tables and figures**: Supplementary Tables 1 to 10 and the scripts that write them
  (`supplementary_tables/`), and Figs. 1 to 5 and Supplementary Figs. 1 to 16 with their scripts (`figures/`).
- **Sample data**: five raw trial files, so that the raw format can be read without the full corpus
  (`sample_data/`). The complete raw corpus (51,906 trial files; `raw_corpus_v1.tar.gz`, 768 MB) is in the Zenodo
  deposit https://doi.org/10.5281/zenodo.19896196.

This code is archived at https://doi.org/10.5281/zenodo.23021930.

## Repository Structure

```
├── README.md                          # This file
├── LICENSE                            # MIT licence for the code
├── requirements.txt                   # Python packages (the optional ones are listed in a comment)
├── reproduce.sh                       # Every analysis, table and figure from the raw trial files, in one command
├── games/                             # The game engine, the prompts, the programmed opponents and the 38 games
│   ├── engine.py                      # Rules, history and query blocks, option letters, reply parsing, payoffs
│   ├── prompts.py                     # The prompt structure and the framing presets
│   ├── strategies.py                  # The programmed opponents (always-cooperate, tit-for-tat, grim trigger, ...)
│   ├── definitions/                   # The 38 games, one module per category
│   └── example_match.py               # One match between two programmed strategies, with no API call
├── data_collection/                   # The code that ran the models
│   ├── run.py                         # Command line: list the games, models and designs, or run a design
│   ├── designs.py                     # The complete design (16 models) and the frontier design (9 models)
│   ├── models.py                      # The 25 models: provider, API model identifier, reasoning mode
│   ├── conditions.py                  # The prompt framing and temperature of each condition
│   ├── runner.py                      # Plays the trials in parallel and writes one JSON file per trial
│   └── api.py                         # Calls to Anthropic, OpenAI, OpenRouter and Google Vertex AI
├── analysis/
│   ├── behavioral_profiles.py         # The trial-level measures from the raw trial files
│   ├── common.py                      # Paths, the 25 models and their characteristics, the games and categories
│   ├── same_opponent.py               # A1: cooperation against the same opponents, weighted equally
│   ├── variance_decomposition.py      # A2: developer, size tier, reasoning mode and release date
│   ├── endgame_by_opponent.py         # A3: the last rounds by opponent class, with the benchmarks
│   ├── category_tables.py             # A4: one index per category and model, with its interval (Table 1)
│   ├── mechanism_profiles.py          # A6: preference, belief, risk and rule components
│   ├── reciprocity.py                 # Cooperation after the other player cooperated or defected
│   ├── reasoning_text_clustering.py   # Embedding and clustering of the reasoning texts
│   ├── reasoning_text_robustness.py   # The same statistics with a sentence-transformer embedding
│   ├── check_developer_labels.py      # Checks that both embeddings label every agent by its developer
│   └── reparse_check.py               # Every reply re-parsed with the rule-based parser alone, analyses repeated
├── summary_data/
│   ├── behavioral_profiles.csv        # One row per trial (51,906) with the measures of its game category
│   ├── A7_release_dates.csv           # Release date, API snapshot and source of each model's date
│   ├── A1_*, A2_*, A3_*, A4_*, A6_*   # The results of the analyses (CSV and JSON)
│   ├── reciprocity.csv                # P(C|C) and P(C|D) for each model
│   ├── reasoning_text_clustering/     # Distances, projections, silhouette scores and signatures of the reasoning
│   │                                  # texts, and the sentence-transformer results (robustness_st.json)
│   └── reparse_check/                 # The re-parsed trial-level data and the A1 to A6 results on it
├── supplementary_tables/
│   ├── build_tables.py                # Writes the tables from summary_data/
│   ├── TableS1.md ... TableS10.md     # Supplementary Tables 1 to 10
│   └── ALL-TABLES.md                  # The ten tables in one file
├── figures/
│   ├── fig1_design.py ... fig5_endgame.py
│   ├── figS1_category_heatmap.py ... figS16_thinking_comparison.py
│   ├── figlib.py                      # Style, paths, point labels and the text collision check
│   ├── compact_style.py               # The style of Supplementary Figs. 4, 8 and 11
│   ├── palette.json                   # Developer colors
│   └── out/                           # Every figure as PDF and PNG
└── sample_data/                       # Five raw trial files in the format of the Zenodo corpus
```

The file prefixes A1 to A7 number the analyses as in the study (there is no A5 in the paper); A7 is the table of
release dates, compiled from the developers' release notes and model pages, with the source of each date.

## Setup

The analyses need Python 3.12 and the packages in `requirements.txt`. If you use conda, create a new environment and
install the required dependencies:

```bash
conda create -n llm-games python=3.12
conda activate llm-games
git clone https://github.com/FelipeMAffonso/llm-strategic-personalities.git
cd llm-strategic-personalities
pip install -r requirements.txt
```

Similarly, if you use virtualenv:

```bash
python -m venv llm-games
source llm-games/bin/activate
git clone https://github.com/FelipeMAffonso/llm-strategic-personalities.git
cd llm-strategic-personalities
pip install -r requirements.txt
```

The setup should only take a few moments. The figures use the Arial font. Rerunning the reasoning-text clustering also
needs scikit-learn. sentence-transformers is optional: the clustering uses it only for its robustness step
(`analysis/reasoning_text_robustness.py`). The released clustering files were computed without umap-learn, and with it
installed the files named umap would hold UMAP coordinates instead of principal components (see "The reasoning-text
clustering" below). Data collection needs the provider libraries (anthropic, openai, google-genai and google-auth).
These optional packages are listed in the comment of `requirements.txt`.

## Usage

### Data configuration

Download `raw_corpus_v1.tar.gz` from the Zenodo deposit (https://doi.org/10.5281/zenodo.19896196) and unpack it into
`raw_data/` at the top of this repository:

```bash
mkdir -p raw_data
tar -xzf raw_corpus_v1.tar.gz -C raw_data --strip-components=1
```

The scripts read `raw_data/` by default; the environment variable `RAW_DATA_DIR` points them to any other folder that
holds the trial files (for example `export RAW_DATA_DIR=/data/llm-games/raw`). `sample_data/` has five trial files in
the same format.

### Reproducing every analysis, table and figure

```bash
bash reproduce.sh
```

The command rebuilds `summary_data/behavioral_profiles.csv` from the raw trial files, runs the analyses, writes the
Supplementary tables and draws every figure. It takes about five minutes on a desktop computer and rewrites
`summary_data/`, `supplementary_tables/` and `figures/out/`. With the package versions of `requirements.txt`, the
trial-level data, the analysis results and the tables it writes are identical to the released files, byte for byte;
the figures can differ by a few pixels with another version of matplotlib or of the Arial font. Every run also checks
the developer labels of the reasoning-text clustering (`analysis/check_developer_labels.py`) and stops if they are
wrong. `bash reproduce.sh --with-clustering` also reruns the reasoning-text clustering and its robustness check (the
sentence-transformer embedding takes about an hour on a CPU); without it, the clustering results in
`summary_data/reasoning_text_clustering/` are used.
`bash reproduce.sh --with-reparse-check` also reruns the re-parsing check described below (about ten minutes); without
it, the results in `summary_data/reparse_check/` are used. The two options can be given together. Each step can also
be run on its own, from the top of the repository:

```bash
python analysis/behavioral_profiles.py        # summary_data/behavioral_profiles.csv (reads the raw trial files)
python analysis/same_opponent.py              # A1
python analysis/variance_decomposition.py     # A2
python analysis/endgame_by_opponent.py        # A3 (reads the raw trial files)
python analysis/category_tables.py            # A4
python analysis/mechanism_profiles.py         # A6
python analysis/reciprocity.py                # reciprocity.csv (reads the raw trial files)
python analysis/check_developer_labels.py     # the developer labels of the reasoning-text clustering
python analysis/reparse_check.py              # summary_data/reparse_check/ (reads the raw trial files; after A1 to A6)
python supplementary_tables/build_tables.py
python figures/fig2_categories.py
```

What each analysis does:

- **A1** (`same_opponent.py`) restricts every model to the 16 programmed opponents that all 25 models faced in the four
  prisoner's dilemma variants, weights each opponent equally, and compares the result with the pooled rate over every
  matchup the model played, with a 95% t-distribution interval.
- **A2** (`variance_decomposition.py`) fits a linear probability model of trial-level cooperation against the 16 common
  opponents on developer, size tier, reasoning mode and release date, with opponent and game-variant fixed effects and
  standard errors clustered by model, and reports the share of between-model variance each characteristic explains
  (eta squared on the 25 model means, with a bootstrap over models for their order), for cooperation and for the
  trust index.
- **A3** (`endgame_by_opponent.py`) reads the round-by-round choices of the prisoner's dilemma trials and reports
  cooperation in each round by opponent class (always-defect, always-cooperate, reactive opponents, lenient reactive
  opponents, self-play and cross-play), with the benchmark of each class, and assigns each model a type from its play
  against reactive opponents.
- **A4** (`category_tables.py`) gives one index per model and category (the measures of Table 1, listed below).
  For each model it pools the trials of the category's index games against each programmed opponent that every
  model faced, then averages the opponents with equal weight, with a 95% percentile bootstrap interval (2,000
  resamples of the trials within each opponent). Per category it reports the cross-model range, the coefficient of
  variation and a Kruskal-Wallis test across the three developers with six or more models. Colonel Blotto and
  multi-issue negotiation are removed before anything is computed, and the script stops if the games that enter an
  index differ from the ones Table 1 names. It also writes the three scored competition games separately
  (`A4_competition_games.csv`, Supplementary Table 4).
- **A6** (`mechanism_profiles.py`) compares cooperation against always-cooperate, always-defect, tit-for-tat and grim
  trigger with the best response to each, and combines these rates with the dictator share, the trust game transfer,
  the stag hunt choice, the chicken choice and the beauty-contest depth into preference, belief, risk and rule
  components.
- **Reciprocity** (`reciprocity.py`) gives the probability of cooperating after the other player cooperated, P(C|C),
  and after it defected, P(C|D), in the prisoner's dilemma.

### The category indices (Table 1)

Each index is one column of `summary_data/behavioral_profiles.csv`, pooled over the index games of its category as
described for A4. `summary_data/A4_table1.csv` holds the full definitions and benchmarks, and lists every game played
in a category, marking the ones outside the index.

| category | index games | index |
|---|---|---|
| Coordination | both battle-of-the-sexes games, both stag hunts, matching pennies, focal point | share of rounds in which the two players chose matching actions (`coordination_rate`) |
| Strategic depth | both beauty contests, the 11 to 20 game | one minus the mean number chosen divided by 50 (`strategic_depth`) |
| Competition | first-price, Vickrey and all-pay auctions | mean bid divided by the maximum allowed bid of 100 (`bid_ratio`) |
| Cooperation | the four prisoner's dilemma variants | share of rounds with the cooperative action (`cooperation_rate`) |
| Trust | Berg trust game, gift exchange | share of the largest possible transfer sent as first mover (`trust_index`) |
| Fairness | ultimatum, dictator, third-party punishment | share of the 100-point endowment given to the other player (`offer_ratio`) |
| Negotiation | Nash demand, alternating offers | share of the 100-point surplus demanded (`demand_ratio`) |
| Risk taking | standard and high-stakes chicken | share of rounds with the risky action, going straight (`risk_taking_rate`) |

The centipede games, the public goods, commons, diner's dilemma and El Farol games, repeated trust, and the
signaling and cheap-talk games were played but do not enter an index. Colonel Blotto and multi-issue negotiation were
played but are not scored: each answer needed several numbers (an allocation over three battlefields, or demands on
two issues) and the parser kept one, so their measures do not describe the models' play. Their rows in
`behavioral_profiles.csv` still carry `bid_ratio` and `demand_ratio`, which no analysis uses. The risk index uses the
two chicken games only, because the paper defines risk taking as going straight in chicken; in cheap talk the measure
is 0 in every round (it compares a numeric message with an action label), and the signaling measure is not a risk
measure.

### How the replies were parsed, and the re-parsing check

A rule-based parser first read each reply, taking an answer tag that held an option label, an action name or a
number, or a short reply. The 71,934 replies it could not resolve (8.8 percent of 813,950) went to Claude Haiku 4.5 at
a temperature of 0, which extracted the answer from their first 800 characters. When that model returned nothing
usable, a pattern parser took the last option, action name or number in the reply. For 6,767 replies (0.83 percent),
the stored value differs from the rule-based reading or has no rule-based counterpart. The 1,037 replies (0.13
percent) that no rule could read carry that model's answer, a random option or zero; no reply was excluded. The code of
every step is in `games/engine.py` (`_parse_choice_pipeline` and `_parse_numeric_pipeline`).

`analysis/reparse_check.py` re-parses every reply with the rule-based parser alone (the engine with the language
model step switched off), drops the replies that no rule can read instead of storing a random option or zero, and
repeats analyses A1 to A6 on the result. It first checks that the stored values rebuild
`summary_data/behavioral_profiles.csv` byte for byte and that its copies of the analyses reproduce the released A1 to
A6 results, and it stops if either check fails. The re-parse changed 83 of the 245 numbers checked from the Abstract
and Results at their printed precision, mostly in the third decimal; no reported test crossed P = 0.05, no coefficient
of variation crossed 0.150, and the cooperation range and every endgame type were unchanged. Run it with
`bash reproduce.sh --with-reparse-check`, or on its own after the main analyses:

```bash
python analysis/reparse_check.py --workers 4   # about ten minutes; --selftest runs only its fixtures
```

It writes `summary_data/reparse_check/`: the re-parsed trial-level data (`behavioral_profiles.csv`, without Colonel
Blotto and multi-issue negotiation), the A1 to A6 results on it (named as in `summary_data/`), `parse_summary.json`
(for every game, how many replies the re-parse keeps, changes or drops) and `printed_numbers.csv`, which sets every
number printed in the Abstract and Results beside its value with the stored parse (`stored_full`), with the stored
parse without the two unscored games (`stored_excl`) and with the re-parse (`judge_free`), and marks the numbers that
change at the precision printed.

### The reasoning-text clustering

`analysis/reasoning_text_clustering.py` reads the visible reply text of every player in every round of the raw trial
files (the `reasoning` field of each round, not the `thinking` field): 645,190 texts of at least 30 characters, 636,759
from the models and 8,431 from fixed strategies. It subsamples 41,520 of them uniformly across the 34 agents (25 models
and nine fixed strategies), embeds them (TF-IDF with 5,000 features reduced to 384 dimensions by truncated SVD), and
computes each model's centroid, the cosine distances between centroids, UMAP, t-SNE and PCA projections, an
average-linkage clustering, silhouette scores with developer as the label (the fixed strategies form a group of their
own), the Jensen-Shannon distances between the models' choice distributions, and per-model behavioral signatures
(including the frequency of strategy terms). The released files were computed without umap-learn, so the UMAP step
fell back to PCA: `centroid_umap.csv` equals `centroid_pca.csv`, `trace_umap.csv` holds the first two principal
components of 10,000 individual texts, and Supplementary Figs. 3 and 12 label their axes as principal components.

`analysis/reasoning_text_robustness.py` repeats the developer-separation statistics with the sentence-transformer
embedding all-MiniLM-L6-v2, on the same 41,520 texts and with the same developer labels. It stops unless
`analysis/check_developer_labels.py` passes and unless the lexical statistics recomputed on its subsample reproduce
`hodoscope_summary.json`. Across the 25 models, the ratio of the mean between-developer to the mean within-developer
centroid distance is 1.14 with the lexical embedding and 1.07 with the sentence-transformer embedding, and 0.94 and
0.84 without Anthropic's models (`models_only` in `robustness_st.json`). Counting the nine fixed strategies as a group
as well, as `hodoscope_summary.json` does for all 34 agents, gives 1.51 and 2.17. Under both embeddings only
Anthropic's models group together (mean silhouette 0.39 lexical and 0.30 semantic). `st_centroid_distances.csv` holds
the cosine distances between the sentence-transformer centroids, as `centroid_distances.csv` does for the lexical
embedding. Both scripts write to `summary_data/reasoning_text_clustering/`; several of its file names begin with
"hodoscope", the name the code gives this analysis.

### Generating the tables and figures

`supplementary_tables/build_tables.py` writes Supplementary Tables 1 to 10 from `summary_data/`. Every figure script
reads `summary_data/` (and, for Supplementary Figs. 9 and 15, the raw prisoner's dilemma trials) and writes a PDF and a
PNG to `figures/out/`; `figlib.save` checks every figure for overlapping or clipped text before it writes it.

| Paper | Script | Data |
|---|---|---|
| Table 1 | `analysis/category_tables.py` | `A4_table1.csv` |
| Fig. 1 | `figures/fig1_design.py` | `A4_category_summary.csv`, `behavioral_profiles.csv`, a trial in `sample_data/` with the prompt built by `games/engine.py` |
| Fig. 2 | `figures/fig2_categories.py` | `A4_category_index.csv` |
| Fig. 3 | `figures/fig3_explains_and_drift.py` | `A2_variance_shares.csv`, `A7_release_dates.csv`, `A1_same_opponent.csv` |
| Fig. 4 | `figures/fig4_mechanism.py` | `A6_mechanism.csv` |
| Fig. 5 | `figures/fig5_endgame.py` | `A3_rounds_by_class.csv`, `A3_round10.csv`, `A3_summary.json` |
| Supplementary Figs. 1 and 2 | `figS1_category_heatmap.py`, `figS2_radar.py` | `A4_category_index.csv` |
| Supplementary Fig. 3 | `figS3_behavioral_space.py` | `trace_umap.csv`, `centroid_umap.csv` |
| Supplementary Fig. 4 | `figS4_dendrogram.py` | `centroid_distances.csv` |
| Supplementary Fig. 5 | `figS5_jsd_matrices.py` | `aggregate_jsd.csv`, `jsd_per_game/` |
| Supplementary Fig. 6 | `figS6_reactive_rounds.py` | `A3_rounds_by_class.csv` |
| Supplementary Figs. 7 and 8 | `figS7_factor_loadings.py`, `figS8_lexical_features.py` | `behavioral_signatures.csv` |
| Supplementary Fig. 9 | `figS9_crossplay_matrix.py` | the raw prisoner's dilemma trials |
| Supplementary Fig. 10 | `figS10_coverage.py` | `behavioral_profiles.csv` |
| Supplementary Fig. 11 | `figS11_reciprocity_profiles.py` | `reciprocity.csv` |
| Supplementary Fig. 12 | `figS12_developer_clustering.py` | `centroid_pca.csv`, `hodoscope_summary.json` |
| Supplementary Fig. 13 | `figS13_cooperation_distributions.py` | `behavioral_profiles.csv` |
| Supplementary Fig. 14 | `figS14_strategy_response.py` | `A1_by_opponent.csv` |
| Supplementary Fig. 15 | `figS15_crossplay_effects.py` | the raw prisoner's dilemma trials |
| Supplementary Fig. 16 | `figS16_thinking_comparison.py` | `A4_category_index.csv` |
| Supplementary Tables 1 to 10 | `supplementary_tables/build_tables.py` | `A7_release_dates.csv`, the requested identifiers in `data_collection/models.py`, A1 to A6, `reciprocity.csv`, `hodoscope_summary.json`, `robustness_st.json` |
| Re-parsing check (Methods; Supplementary Note 12) | `analysis/reparse_check.py` | the raw trial files, `behavioral_profiles.csv`, A1 to A6 |

### Running the study from the start

The games run without any API: `python games/example_match.py` plays tit-for-tat against suspicious tit-for-tat in the
prisoner's dilemma and prints the rounds, and `--show-prompt` prints the prompt a model would receive. To collect data,
set the API keys in the environment (or in a file `data_collection/.env` with `KEY=value` lines):
`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, and for Gemini 3 Pro and 3.1 Pro a Vertex AI service
account key file in `GOOGLE_APPLICATION_CREDENTIALS` with the project in `GOOGLE_CLOUD_PROJECT`. Then:

```bash
python data_collection/run.py --list-designs                # the two designs and their trial counts
python data_collection/run.py --design complete --dry-run   # the matchups of a design, without running it
python data_collection/run.py --design complete             # 16 models, five trials per cell, full cross-play
python data_collection/run.py --design frontier             # 9 frontier models, one trial per cell
python analysis/behavioral_profiles.py                      # the trial-level data from the new trial files
```

A cell is one model, one game and one opponent. The complete design runs 16 models on the 38 games against every
programmed opponent of each game, against themselves and against each of the other 15 models (120 pairs), and asks for
five trials per cell. The frontier design runs nine frontier models against the programmed opponents and against
themselves, with one trial per cell. Supplementary Table 1 labels them F and G. Every model received the same prompts
for each game at temperature 1.0 (apart from seven early trials at temperature 0), with the option letters randomized in
each trial; the rules of the game went as the system message, and the history and the question as the user message.

In the released corpus, the 16 models played all three matchup types with five trials in most cells: the corpus holds
47,962 of a possible 54,560 trials. Every one of the 10,912 cells has one to six trials, and 6,422 of them have at least
five. The nine frontier models have one trial in most cells: seven of them have every cell, Gemini 3 Pro and Gemini 3.1
Pro lack 132 and 95 of their 397 cells, and 496 cells hold two to four trials from earlier runs. A partial run added 43 cross-play trials among six frontier models; they enter the pooled rates and the
cross-play columns of Supplementary Tables 8 and 9, but no cross-play matrix or same-opponent analysis.

Each trial is written to `raw_data/` (or `RAW_DATA_DIR`) as one JSON file; a trial whose file exists is not run again,
so an interrupted run continues where it stopped. When the rule-based parser cannot read a reply, Claude Haiku 4.5 at
temperature 0 extracts the answer from it, as described above (`ENABLE_JUDGE=0` turns this off).

### Data format

Each raw trial file (`<game>_<model>_vs_<opponent>_<condition>_t<trial>_<hash>.json`) holds:

| field | values |
|---|---|
| `game_id`, `game_name`, `game_category`, `game_type` | the game, its category, and how moves are made: `simultaneous`, `sequential`, `auction` or `allocation` |
| `model_key`, `opponent`, `matchup_type` | the model in the first position, its opponent (a programmed strategy or a model), and `model_vs_strategy`, `self_play` or `cross_play` |
| `condition` | `baseline` in 51,889 trials; 17 trials ran under `goal_maximise`, `goal_win`, `goal_fair`, `scot` or `temp_0` (`data_collection/conditions.py`) |
| `trial_num`, `num_rounds` | the trial number within its cell and the number of rounds (5, 10, 15 or 20, by game) |
| `player0_id`, `player1_id`, `player0_total_payoff`, `player1_total_payoff` | the two players and their total payoffs |
| `label_map` | the option letters shown to the players and the actions they stand for |
| `input_tokens`, `output_tokens`, `cost_usd` | the tokens of the trial and the API charge computed from them |
| `cache_hit`, `timestamp` | whether the trial was read back from an existing file (false throughout) and when it finished |
| `cooperation_rate`, `joint_cooperation_rate`, `mean_choice_p0`, `mean_choice_p1` | in two-option simultaneous games: the share of cooperative choices averaged over both players, the share of rounds in which both cooperated, and each player's majority choice |
| `match_detail` | the match: `players`, `num_rounds`, `total_payoffs`, `label_map` and `rounds`, where each round holds `round_num`, `choices` (each player's reply), `parsed_choices` (the action read from the reply), `payoffs`, `reasoning` (the reply, kept for the reasoning-text analysis) and `thinking` (the reasoning text returned by the provider, where there is one) |

`summary_data/behavioral_profiles.csv` has one row per trial. The measures are those of the player in the first
position (the model in `model_key`), computed by `analysis/behavioral_profiles.py`; the measures of other categories
are empty:

| columns | values |
|---|---|
| `model_key`, `game_id`, `game_name`, `game_category`, `condition`, `opponent`, `matchup_type`, `trial_num`, `num_rounds` | as in the trial file |
| `player0_payoff`, `player1_payoff`, `input_tokens`, `output_tokens`, `cost_usd` | as in the trial file |
| `cooperation_rate`, `joint_cooperation`, `forgiveness_rate`, `retaliation_rate` | cooperation: the share of rounds in which the model chose the cooperative option, the share with mutual cooperation, and after the opponent defected, the share of next rounds in which the model cooperated (forgiveness) or not (retaliation) |
| `coordination_rate`, `preferred_option_rate`, `alternation_rate` | coordination: the share of rounds with matching choices, the share in which the model chose the first option, and the share of rounds in which it changed its choice |
| `mean_guess`, `guess_std`, `k_level_estimate`, `strategic_depth` | strategic depth, beauty contests and the 11 to 20 game: the mean and standard deviation of the guesses, the level k whose guess is closest to the mean guess, and one minus the mean guess divided by 50 (clamped to 0 to 1) |
| `mean_take_node`, `take_node_std`, `backward_induction_compliance`, `pass_rate` | strategic depth, centipede games: the mean and standard deviation of the node at which the model took (one past the last node when it passed throughout), the share of rounds in which it took at the first node (the subgame-perfect choice), and the share in which it passed at every node |
| `distance_to_equilibrium` | the distance of the mean choice from the equilibrium (cooperation, beauty contests and centipede games) |
| `mean_bid`, `bid_ratio`, `bid_std` | competition: the mean bid, the mean bid divided by the maximum bid, and its standard deviation (in Colonel Blotto, one number of each allocation; not scored) |
| `amount_sent`, `trust_index`, `amount_returned` | trust: the mean amount sent, the amount sent divided by the endowment, and the mean amount the other player returned |
| `offer_amount`, `offer_ratio`, `offer_std`, `rejection_rate` | fairness: the mean offer, the offer divided by the endowment, its standard deviation, and the share of rounds in which the offer was rejected |
| `demand_level`, `demand_ratio`, `demand_std` | negotiation: the mean demand, the demand divided by the surplus, and its standard deviation (in multi-issue negotiation, one of the two demands; not scored) |
| `risk_taking_rate`, `safe_rate` | risk taking: the share of rounds with the risky option (going straight in chicken) and with the safe option |

The eight category indices of the paper (Table 1) are `coordination_rate`, `strategic_depth`, `bid_ratio`,
`cooperation_rate`, `trust_index`, `offer_ratio`, `demand_ratio` and `risk_taking_rate`, each pooled over the index
games listed under "The category indices (Table 1)" above and averaged as described for A4.

### Models, games and opponents

| developer | models |
|---|---|
| Anthropic | Claude Haiku 4.5, Claude Haiku 4.5 (Thinking), Claude Sonnet 4.5, Claude Sonnet 4.6, Claude Opus 4.5, Claude Opus 4.6 |
| OpenAI | GPT-4o Mini, GPT-4.1, GPT-4.1 Mini, GPT-4.1 Nano, GPT-5 Mini, GPT-5 Nano, GPT-5.3, GPT-5.4 |
| Google | Gemini 2.0 Flash, Gemini 2.5 Flash, Gemini 2.5 Flash (Thinking), Gemini 3 Flash, Gemini 3 Pro, Gemini 3.1 Pro |
| DeepSeek, Meta, Mistral, Alibaba | DeepSeek V3, DeepSeek R1, LLaMA 3.3 70B, Ministral 14B, Qwen 3.5 Flash |

The nine frontier models are Claude Sonnet 4.5 and 4.6, Claude Opus 4.5 and 4.6, GPT-4.1, GPT-5.3, GPT-5.4, Gemini 3
Pro and Gemini 3.1 Pro. The API identifier of each model is in `data_collection/models.py`, and its release date and
snapshot in `summary_data/A7_release_dates.csv`; Supplementary Table 1 lists the identifier and route the configuration
requests for each model. `python data_collection/run.py --list-games` lists the 38 games with their number of rounds,
and `games/strategies.py` maps each game to its programmed opponents (three to twenty per game; the four prisoner's
dilemma variants have sixteen).

The Anthropic and OpenAI models were called through the developers' own APIs, Gemini 3 Pro and Gemini 3.1 Pro through
Google Vertex AI, and the DeepSeek, Meta, Mistral and Alibaba models through OpenRouter. The configuration sends the
four Gemini Flash models through OpenRouter as well, but the stored costs of their trials match Google's own model
identifiers, so they may have used Google's API; the trial files do not name the route. Most models could return up to
4,096 output tokens (`data_collection/runner.py`). GPT-5 Mini, GPT-5 Nano, GPT-5.3 and GPT-5.4 could return up to
8,192, Claude Haiku 4.5 (Thinking) up to 8,192 with a thinking budget of 4,096, and Gemini 3 Pro and Gemini 3.1 Pro up
to 16,384 (`data_collection/api.py`). The released settings of Gemini 2.5 Flash (Thinking) match those of Gemini 2.5
Flash, although only its trials carry reasoning text, so its thinking setting at collection is not recorded. Calls that
failed with a rate-limit or capacity error were retried up to four times, after waits of 2, 4, 8 and 16 seconds.

## Licence

The code is released under the MIT licence (`LICENSE`). The data in `summary_data/`, `sample_data/` and
`supplementary_tables/`, and the figures, are released under the Creative Commons Attribution 4.0 licence
(CC BY 4.0), as is the raw corpus on Zenodo.
