"""Write Supplementary Tables S1 to S10 as markdown from the analysis results in summary_data/.

Writes supplementary_tables/TableS1.md to TableS10.md and supplementary_tables/ALL-TABLES.md, each table with its
caption. Run the analyses first (reproduce.sh runs everything in order):

    python supplementary_tables/build_tables.py
"""
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "summary_data")
CLUSTERING = os.path.join(OUT, "reasoning_text_clustering")
SI = HERE
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, ROOT)
from common import FRONTIER_MODELS, MODELS, ORDER  # noqa: E402
from data_collection.models import ALL_MODELS  # noqa: E402

# the endpoint behind each provider value in data_collection/models.py
ROUTES = {"anthropic": "Anthropic API", "openai": "OpenAI API", "openrouter": "OpenRouter", "google_vertex": "Vertex AI",
          "google": "Google AI Studio"}


def requested_identifier(key):
    """The model identifier the code sends for this model, with its route, as data_collection/models.py sets them
    (Table S1 reports what the code requested; the release date comes from A7_release_dates.csv)."""
    cfg = ALL_MODELS[key]
    return f"{cfg['model_id']} ({ROUTES[cfg['provider']]})"


MAX_COLS = 9  # a portrait page holds about nine columns at the Supplement's type size


def _one_table(df, floatfmt):
    cols = list(df.columns)
    # a pipe inside a cell ("P(C|C)") would split the cell, so it is escaped for the markdown table
    L = ["| " + " | ".join(str(c).replace("|", "\\|") for c in cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                cells.append("" if pd.isna(v) else f"{v:.{floatfmt}f}")
            else:
                cells.append(str(v))
        L.append("| " + " | ".join(str(c).replace("|", "\\|") for c in cells) + " |")
    return "\n".join(L)


def md_table(df, floatfmt=3):
    """Wide tables are split into parts that each repeat the first (model) column, so every part fits a page."""
    cols = list(df.columns)
    if len(cols) <= MAX_COLS:
        return _one_table(df, floatfmt)
    first, rest = cols[0], cols[1:]
    per = MAX_COLS - 1
    parts = []
    for i in range(0, len(rest), per):
        chunk = [first] + rest[i:i + per]
        letter = chr(ord("a") + i // per)
        parts.append(f"Part ({letter}), columns {i + 1} to {min(i + per, len(rest))} of {len(rest)}.\n\n" + _one_table(df[chunk], floatfmt))
    return "\n\n".join(parts)


def write(name, caption, body):
    text = f"**{name}.** {caption}\n\n{body}\n"
    with open(os.path.join(SI, name.replace(" ", "") + ".md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return text


def main():
    parts = []
    # S1 model catalog
    a7 = pd.read_csv(os.path.join(OUT, "A7_release_dates.csv"))
    prof = pd.read_csv(os.path.join(OUT, "behavioral_profiles.csv"), low_memory=False)
    n_tr = prof.groupby("model_key").size()
    rows = []
    for k in ORDER:
        r = a7[a7.model_key == k].iloc[0]
        rows.append({"Model": MODELS[k][0], "Developer": MODELS[k][1], "Product line": MODELS[k][2], "Size tier": MODELS[k][3],
                     "Reasoning traces captured": "yes" if MODELS[k][4] else "no", "Release date": r.release_date, "Requested identifier": requested_identifier(k),
                     "Design": "G (one trial in most cells)" if k in FRONTIER_MODELS else "F (five trials in most cells)",
                     "Trials": int(n_tr.get(k, 0))})
    parts.append(write("Table S1", "The 25 models: developer, product line, size tier, whether internal reasoning traces were captured, public release date (verified on the developer's page), the model identifier and route in the released configuration, design and number of trials. The Gemini Flash models may have used Google's own API (Supplementary Note 4). Gemini 3 Pro and 3.1 Pro reason by default; the GPT-5 series reasons internally without exposing traces through the endpoint used.", md_table(pd.DataFrame(rows))))
    # S2 same-opponent and pooled cooperation
    a1 = pd.read_csv(os.path.join(OUT, "A1_same_opponent.csv"), index_col=0)
    rows = [{"Model": MODELS[k][0], "Developer": MODELS[k][1], "Same opponents (%)": a1.loc[k, "same_opponent_rate"], "n": int(a1.loc[k, "n_trials_same_opponent"]), "Pooled (%)": a1.loc[k, "pooled_rate"], "Pooled 95% CI": f"[{a1.loc[k, 'pooled_ci_lo']:.1f}, {a1.loc[k, 'pooled_ci_hi']:.1f}]", "n pooled": int(a1.loc[k, "n_trials_pooled"])} for k in a1.index]
    parts.append(write("Table S2", "Cooperation in the four prisoner's dilemma variants by model: against the 16 fixed opponents every model faced, weighted equally per opponent (the headline measure), and pooled across every matchup the model played, with the 95 percent t-distribution interval on the trial-level pooled values, clipped to the unit range. Sorted by the same-opponent rate.", md_table(pd.DataFrame(rows), 1)))
    # S3 by opponent
    by = pd.read_csv(os.path.join(OUT, "A1_by_opponent.csv"), index_col=0).reindex(ORDER)
    by.index = [MODELS[k][0] for k in by.index]
    by.insert(0, "Model", by.index)
    parts.append(write("Table S3", "Cooperation (percent of rounds) in the four prisoner's dilemma variants against each of the 16 fixed opponents, by model.", md_table(by.reset_index(drop=True), 1)))
    # S4 competition games. Colonel Blotto is left out: each answer needed three numbers and the parser kept one, so
    # its allocation measure does not describe the models' play (analysis/category_tables.py keeps an empty row for it).
    comp = pd.read_csv(os.path.join(OUT, "A4_competition_games.csv"))
    assert (comp.game == "Colonel Blotto").sum() == 1
    comp = comp[comp.game != "Colonel Blotto"].reset_index(drop=True)
    assert list(comp.game) == ["First-price auction", "Vickrey auction", "All-pay auction"]
    parts.append(write("Table S4", "The three scored competition games separately: the measure, its cross-model range and coefficient of variation, and each model's value. The competition index in the main text pools the three auctions, using the fixed opponents every model faced with each opponent weighted equally (Table 1); the values here are each game's mean over all of a model's trials. Colonel Blotto was played but is not scored, because the parser kept only one of the several numbers each answer required.", md_table(comp, 3)))
    # S5 regression
    reg = pd.read_csv(os.path.join(OUT, "A2_regression.csv"), index_col=0)
    reg = reg[~reg.index.str.contains("opponent|game_id")]
    reg.index = [i.replace("C(developer, Treatment(reference='OpenAI'))[T.", "Developer: ").replace("C(size_tier, Treatment(reference='small'))[T.", "Size tier: ").replace("]", "") for i in reg.index]
    reg.insert(0, "Term", reg.index)
    # Meta, Mistral and Alibaba have one model each, so with standard errors clustered by model their contrasts rest on
    # one cluster and are reported without a test, as the Results say.
    one_model = reg.Term.isin(["Developer: Meta", "Developer: Mistral", "Developer: Alibaba"])
    assert one_model.sum() == 3, reg.Term.tolist()
    reg["se"] = reg["se"].astype(object); reg["p"] = reg["p"].astype(object)
    reg.loc[one_model, ["se", "p"]] = ""
    anth = float(reg.loc[reg.Term.eq("Developer: Anthropic"), "coef"].iloc[0])
    parts.append(write("Table S5", "Linear probability model of trial-level cooperation in the four prisoner's dilemma variants on strategy-play trials against the 16 common opponents, with opponent and game-variant fixed effects (not shown) and standard errors clustered by model. Reference categories: OpenAI, small tier, no reasoning traces. Coefficients are shares of rounds " + f"({anth:.3f} = {anth * 100:.1f} percentage points). " + "Meta, Mistral and Alibaba have one model each, so their contrasts are shown without a standard error or test.", md_table(reg.reset_index(drop=True), 4)))
    # S6 shares
    sh = pd.read_csv(os.path.join(OUT, "A2_variance_shares.csv"))
    parts.append(write("Table S6", "Share of between-model variance (across the 25 model means) explained by each characteristic alone (eta squared or R squared), jointly, and by developer given the others, for prisoner's dilemma cooperation and for the trust index.", md_table(sh, 3)))
    # S7 mechanism
    mech = pd.read_csv(os.path.join(OUT, "A6_mechanism.csv"), index_col=0).reindex(ORDER)
    cols = {"display": "Model", "developer": "Developer", "coop_vs_always_cooperate": "vs always-cooperate", "coop_vs_always_defect": "vs always-defect", "coop_vs_tit_for_tat": "vs tit-for-tat", "coop_vs_grim_trigger": "vs grim trigger", "dictator_share": "Dictator share", "trust_sent_share": "Trust sent", "stag_share_risky": "Stag (risky)", "chicken_risky_share": "Chicken risky", "beauty_depth": "Beauty depth", "preference_component": "Preference", "belief_component": "Belief", "risk_component": "Risk", "rule_component": "Rule"}
    m7 = mech[list(cols)].rename(columns=cols)
    parts.append(write("Table S7", "Mechanism components by model, every measure on strategy-play trials against the fixed opponents every model faced with equal weight per opponent. Cooperation rates against three fixed opponents in the prisoner's dilemma (the best response is 0 against always-cooperate and always-defect, and 0.90 against tit-for-tat and grim trigger with a known last round), the dictator share, trust sent, the stag share in the risky stag hunt, the risky share in chicken, beauty-contest depth, and the four components (preference = mean of cooperation against always-cooperate and dictator share; belief = mean of cooperation against tit-for-tat and beauty depth; risk = mean of stag and chicken risky shares; rule = cooperation against always-defect).", md_table(m7.reset_index(drop=True), 3)))
    # S8 endgame
    r10 = pd.read_csv(os.path.join(OUT, "A3_round10.csv"))
    # the lenient reactive class is reported beside the others (Supplementary Notes 3 and 9)
    r10 = r10[r10.opponent_class.isin(["reactive", "reactive_lenient", "fixed_cooperate", "fixed_defect", "self_play", "cross_play"])]
    piv9 = r10.pivot(index="model_key", columns="opponent_class", values="round9").reindex(ORDER)
    piv10 = r10.pivot(index="model_key", columns="opponent_class", values="round10").reindex(ORDER)
    a3 = json.load(open(os.path.join(OUT, "A3_summary.json")))
    rows = []
    for k in ORDER:
        # no Developer column: the model names carry it, and nine columns keep the table in one piece on the page
        rows.append({"Model": MODELS[k][0],
                     "Reactive R9": piv9.loc[k, "reactive"] * 100 if "reactive" in piv9 else float("nan"), "Reactive R10": piv10.loc[k, "reactive"] * 100,
                     "Lenient reactive R10": piv10.loc[k, "reactive_lenient"] * 100 if "reactive_lenient" in piv10 else float("nan"),
                     "Always-cooperate R10": piv10.loc[k, "fixed_cooperate"] * 100 if "fixed_cooperate" in piv10 else float("nan"),
                     "Always-defect R10": piv10.loc[k, "fixed_defect"] * 100 if "fixed_defect" in piv10 else float("nan"),
                     "Self-play R10": piv10.loc[k, "self_play"] * 100 if "self_play" in piv10 else float("nan"),
                     "Cross-play R10": piv10.loc[k, "cross_play"] * 100 if "cross_play" in piv10 else float("nan"),
                     "Type (reactive)": a3["types_vs_reactive"].get(k, {}).get("type", "")})
    parts.append(write("Table S8", "Final-round cooperation (percent) in the four prisoner's dilemma variants by opponent class, with the round-9 rate against reactive opponents and the type assigned from play against the reactive opponents, weighted equally, with the rules applied in this order (sustained cooperator: round 10 at or above 50 percent; horizon-conditioned: round 9 at or above 25 percent, round 10 below 10 percent, and a drop from round 9 to round 10 of at least 25 percentage points; unconditional defector: mean cooperation over rounds 1 to 9 below 20 percent and round 10 below 20 percent; the rest intermediate). Benchmarks: reactive opponents, cooperate through round 9 and defect in round 10; lenient reactive opponents (tit-for-two-tats, Pavlov, two noisy variants, false defector and defect-once), defect in round 10, although earlier defection can go unpunished; the fixed and model opponents, defect throughout. Self-play was run for every model; cross-play was run for the 16 models of the complete design, so cross-play cells for the nine frontier models rest on the few trials in which a frontier model appeared as another model's opponent, or are empty.", md_table(pd.DataFrame(rows), 1)))
    # S9 reciprocity: the values of summary_data/reciprocity.csv (analysis/reciprocity.py) in percent, rounded half
    # up to one decimal, with the archetype given by the thresholds of Supplementary Note 10
    s9 = [("Claude Opus 4.6", 92.8, 4.5, 88.3, 469, 179, "Strict reciprocator"), ("Claude Sonnet 4.6", 91.7, 4.1, 87.6, 588, 222, "Strict reciprocator"), ("Claude Opus 4.5", 90.4, 4.1, 86.3, 467, 172, "Strict reciprocator"), ("Claude Sonnet 4.5", 88.7, 8.8, 79.9, 556, 227, "Strict reciprocator"), ("Gemini 3 Flash", 83.6, 0.3, 83.3, 3066, 1875, "Grudge-holder"), ("Gemini 3 Pro", 77.5, 2.8, 74.7, 368, 181, "Grudge-holder"), ("GPT-4.1", 72.2, 1.5, 70.7, 417, 195, "Grudge-holder"), ("Qwen 3.5 Flash", 70.7, 7.4, 63.3, 1464, 894, "Strict reciprocator"), ("Claude Haiku 4.5", 68.5, 5.1, 63.4, 2382, 2370, "Strict reciprocator"), ("Claude Haiku 4.5 (Thinking)", 67.9, 3.7, 64.2, 2283, 2289, "Strict reciprocator"), ("GPT-4o Mini", 67.2, 18.3, 48.9, 2225, 1726, "Moderate reciprocator"), ("GPT-5.4", 64.8, 4.8, 60.0, 472, 248, "Strict reciprocator"), ("GPT-4.1 Mini", 62.9, 5.6, 57.3, 2007, 1881, "Strict reciprocator"), ("Gemini 3.1 Pro", 62.8, 0.4, 62.4, 261, 243, "Grudge-holder"), ("DeepSeek V3", 54.8, 8.8, 46.0, 1345, 1607, "Moderate reciprocator"), ("Gemini 2.5 Flash", 54.0, 11.1, 42.9, 2077, 3206, "Moderate reciprocator"), ("DeepSeek R1", 50.7, 22.8, 27.9, 1339, 1208, "Moderate reciprocator"), ("Gemini 2.5 Flash (Thinking)", 50.1, 6.6, 43.5, 2133, 2943, "Moderate reciprocator"), ("Ministral 14B", 48.3, 24.1, 24.2, 1245, 1392, "Moderate reciprocator"), ("GPT-4.1 Nano", 35.0, 5.9, 29.1, 1339, 2855, "Weak reciprocator"), ("GPT-5.3", 34.0, 1.8, 32.2, 430, 380, "Weak reciprocator"), ("LLaMA 3.3 70B", 14.3, 22.2, -7.9, 1157, 1957, "Anti-reciprocator"), ("Gemini 2.0 Flash", 12.5, 6.1, 6.4, 1503, 4041, "Unconditional defector"), ("GPT-5 Mini", 10.5, 2.8, 7.7, 1195, 2531, "Unconditional defector"), ("GPT-5 Nano", 2.1, 1.0, 1.1, 1043, 2359, "Unconditional defector")]
    parts.append(write("Table S9", "Reciprocity statistics by model, pooled across all cooperation games and opponents: the probability of cooperating after the opponent cooperated, P(C|C), and after the opponent defected, P(C|D), in percent; their difference (the reciprocity index); the number of round pairs in each condition; and the archetype assigned by the thresholds in Note 10.", md_table(pd.DataFrame(s9, columns=["Model", "P(C|C)", "P(C|D)", "Reciprocity index", "N after C", "N after D", "Archetype"]), 1)))
    # S10 reasoning-text clustering
    H = json.load(open(os.path.join(CLUSTERING, "hodoscope_summary.json")))
    R = json.load(open(os.path.join(CLUSTERING, "robustness_st.json")))
    pm = H["provider_separation"]["per_model_silhouette"]
    pst = R["sentence_transformer_robustness"].get("per_model_silhouette", {}) if isinstance(R["sentence_transformer_robustness"].get("per_model_silhouette"), dict) else {}
    rows = [{"Model": MODELS[k][0], "Developer": MODELS[k][1], "Silhouette, lexical": pm.get(k, float("nan")), "Silhouette, sentence transformer": pst.get(k, float("nan"))} for k in ORDER]
    n_texts = R["sentence_transformer_robustness"]["n_traces_subsampled"]
    assert n_texts == H["n_traces"], "the two embeddings must read the same subsample"
    parts.append(write("Table S10", "Reasoning-trace clustering by model: the silhouette score with developer as the label under the lexical embedding (TF-IDF reduced to 384 dimensions) and under the sentence-transformer embedding (all-MiniLM-L6-v2). Positive values mean a model's reasoning texts sit closer to its own developer's models than to another developer's. " f"Both embeddings read the same {n_texts:,} texts and use the same labels: the nine fixed strategies form a group of their own, and a developer's only model (LLaMA 3.3 70B, Ministral 14B, Qwen 3.5 Flash) scores 0 by definition.", md_table(pd.DataFrame(rows), 2)))
    with open(os.path.join(SI, "ALL-TABLES.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n\n".join(parts))
    print(f"wrote {len(parts)} tables to {SI}")


if __name__ == "__main__":
    main()
