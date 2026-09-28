"""Shared definitions for the analyses: paths, the 25 models and their characteristics, the 38 games and the
eight categories.

The model characteristics (developer, product line, size tier, reasoning mode) are fixed here; release dates join
from summary_data/A7_release_dates.csv. Every analysis reads the trial-level data in summary_data/ and writes its
results there. The raw trial files are read from raw_data/ at the top of the repository, or from the folder named by
the environment variable RAW_DATA_DIR.
"""
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "summary_data")
PROFILES = os.path.join(OUT, "behavioral_profiles.csv")
RAW = os.environ.get("RAW_DATA_DIR") or os.path.join(ROOT, "raw_data")
os.makedirs(OUT, exist_ok=True)

NUMERIC = ["mean_guess", "k_level_estimate", "distance_to_equilibrium", "strategic_depth", "risk_taking_rate",
           "safe_rate", "mean_bid", "bid_ratio", "bid_std", "demand_level", "demand_ratio", "demand_std",
           "offer_amount", "offer_ratio", "offer_std", "rejection_rate", "amount_sent", "trust_index",
           "amount_returned", "cooperation_rate", "joint_cooperation", "forgiveness_rate", "retaliation_rate",
           "coordination_rate", "preferred_option_rate", "alternation_rate", "mean_take_node", "take_node_std",
           "backward_induction_compliance", "pass_rate", "player0_payoff", "player1_payoff"]

# model_key -> (display, developer, product_line, size_tier, reasoning)
MODELS = {
    "claude-haiku-4.5": ("Claude Haiku 4.5", "Anthropic", "Haiku", "small", False),
    "claude-haiku-4.5-thinking": ("Claude Haiku 4.5 (Thinking)", "Anthropic", "Haiku", "small", True),
    "claude-sonnet-4.5": ("Claude Sonnet 4.5", "Anthropic", "Sonnet", "medium", False),
    "claude-sonnet-4.6": ("Claude Sonnet 4.6", "Anthropic", "Sonnet", "medium", False),
    "claude-opus-4.5": ("Claude Opus 4.5", "Anthropic", "Opus", "frontier", False),
    "claude-opus-4.6": ("Claude Opus 4.6", "Anthropic", "Opus", "frontier", False),
    "gpt-4o-mini": ("GPT-4o Mini", "OpenAI", "GPT-4o", "small", False),
    "gpt-4.1": ("GPT-4.1", "OpenAI", "GPT-4.1", "frontier", False),
    "gpt-4.1-mini": ("GPT-4.1 Mini", "OpenAI", "GPT-4.1", "small", False),
    "gpt-4.1-nano": ("GPT-4.1 Nano", "OpenAI", "GPT-4.1", "small", False),
    "gpt-5-mini": ("GPT-5 Mini", "OpenAI", "GPT-5", "small", False),
    "gpt-5-nano": ("GPT-5 Nano", "OpenAI", "GPT-5", "small", False),
    "gpt-5.3": ("GPT-5.3", "OpenAI", "GPT-5", "frontier", False),
    "gpt-5.4": ("GPT-5.4", "OpenAI", "GPT-5", "frontier", False),
    "gemini-2.0-flash": ("Gemini 2.0 Flash", "Google", "Flash", "medium", False),
    "gemini-2.5-flash": ("Gemini 2.5 Flash", "Google", "Flash", "medium", False),
    "gemini-2.5-flash-thinking": ("Gemini 2.5 Flash (Thinking)", "Google", "Flash", "medium", True),
    "gemini-3-flash": ("Gemini 3 Flash", "Google", "Flash", "medium", False),
    # Gemini 3 Pro and 3.1 Pro reason by default (thinking is enabled for them in data_collection/models.py).
    "gemini-3-pro": ("Gemini 3 Pro", "Google", "Pro", "frontier", True),
    "gemini-3.1-pro": ("Gemini 3.1 Pro", "Google", "Pro", "frontier", True),
    "deepseek-v3": ("DeepSeek V3", "DeepSeek", "DeepSeek", "frontier",False),
    "deepseek-r1": ("DeepSeek R1", "DeepSeek", "DeepSeek", "frontier",True),
    "llama-3.3-70b": ("LLaMA 3.3 70B", "Meta", "LLaMA", "medium", False),
    "ministral-14b": ("Ministral 14B", "Mistral", "Ministral", "small", False),
    "qwen3.5-flash": ("Qwen 3.5 Flash", "Alibaba", "Qwen", "medium", False),
}
ORDER = list(MODELS.keys())
# The nine frontier models played fixed opponents and themselves, with one trial in most cells (labelled G in
# Supplementary Table S1); the other 16 models played all three matchup types, including full cross-play, with five
# trials in most cells (labelled F).
FRONTIER_MODELS = {"claude-sonnet-4.5", "claude-sonnet-4.6", "claude-opus-4.5", "claude-opus-4.6", "gpt-4.1", "gpt-5.3",
                   "gpt-5.4", "gemini-3-pro", "gemini-3.1-pro"}
DEVELOPER_ORDER = ["Anthropic", "OpenAI", "Google", "DeepSeek", "Meta", "Mistral", "Alibaba"]

PD = ["pd_canonical", "pd_harsh", "pd_medium", "pd_mild"]

# Readable game names (the coverage figure's mapping, shared here so Table 1 prints names, not identifiers).
GAME_NAMES = {
    "bos_standard": "Battle of the sexes (standard)", "bos_transposed": "Battle of the sexes (transposed)",
    "stag_hunt_standard": "Stag hunt (standard)", "stag_hunt_risky": "Stag hunt (risky)",
    "matching_pennies": "Matching pennies", "focal_point": "Focal point",
    "beauty_contest_23": "Beauty contest 2/3", "beauty_contest_12": "Beauty contest 1/2",
    "centipede_6": "Centipede (6 nodes)", "centipede_10": "Centipede (10 nodes)", "eleven_twenty": "11 to 20 game",
    "auction_first_price": "First-price auction", "auction_vickrey": "Vickrey auction",
    "auction_all_pay": "All-pay auction", "colonel_blotto": "Colonel Blotto",
    "pd_canonical": "Prisoner's dilemma (canonical)", "pd_harsh": "Prisoner's dilemma (harsh)",
    "pd_medium": "Prisoner's dilemma (medium)", "pd_mild": "Prisoner's dilemma (mild)",
    "pg_low_mpcr": "Public goods (low MPCR)", "pg_med_mpcr": "Public goods (medium MPCR)",
    "pg_high_mpcr": "Public goods (high MPCR)", "commons_dilemma": "Commons dilemma",
    "diners_dilemma": "Diner's dilemma", "el_farol_bar": "El Farol bar",
    "trust_berg": "Berg trust game", "gift_exchange": "Gift exchange", "repeated_trust": "Repeated trust",
    "ultimatum": "Ultimatum", "dictator": "Dictator", "third_party_punishment": "Third-party punishment",
    "nash_demand": "Nash demand", "alternating_offers": "Alternating offers", "multi_issue": "Multi-issue negotiation",
    "chicken": "Chicken", "chicken_high_stakes": "Chicken (high stakes)", "signaling": "Signaling", "cheap_talk": "Cheap talk",
}

# The eight categories: the games, the one reported measure (as computed in behavioral_profiles.csv), its
# definition in words, and the benchmark. This is Table 1's source.
CATEGORIES = [
    ("coordination", "Coordination", ["bos_standard", "bos_transposed", "stag_hunt_standard", "stag_hunt_risky", "matching_pennies", "focal_point"],
     "coordination_rate", "Share of rounds in which the two players chose matching actions",
     "A pure-strategy equilibrium requires matching; human pairs miscoordinate in a substantial share of rounds in battle-of-the-sexes experiments"),
    ("depth", "Strategic depth", ["beauty_contest_23", "beauty_contest_12", "centipede_6", "centipede_10", "eleven_twenty"],
     "strategic_depth", "One minus the mean beauty-contest guess divided by 50, so that guessing 50 scores 0 and guessing the equilibrium 0 scores 1",
     "Nash equilibrium guess 0; first-round human guesses average about 37 in the two-thirds game"),
    ("competition", "Competition", ["auction_first_price", "auction_vickrey", "auction_all_pay", "colonel_blotto"],
     "bid_ratio", "Mean bid divided by the maximum possible bid in the first-price sealed-bid auction",
     "Risk-neutral equilibrium shades below value in first-price; the dominant strategy in the Vickrey auction is to bid true value"),
    ("cooperation", "Cooperation", PD + ["pg_low_mpcr", "pg_med_mpcr", "pg_high_mpcr", "commons_dilemma", "diners_dilemma", "el_farol_bar"],
     "cooperation_rate", "Share of rounds in which the model chose the cooperative action, reported for the four prisoner's dilemma variants",
     "Stage-game equilibrium is mutual defection; one-shot human cooperation averages about 37 percent"),
    ("trust", "Trust", ["trust_berg", "gift_exchange", "repeated_trust"],
     "trust_index", "Share of the endowment sent in the trust game (sent amount divided by 10)",
     "Subgame-perfect prediction is to send nothing; human senders transfer about half"),
    ("fairness", "Fairness", ["ultimatum", "dictator", "third_party_punishment"],
     "offer_ratio", "Share of the endowment offered to the other player in the ultimatum game",
     "Subgame-perfect offer is the smallest positive amount; human offers average 40 percent"),
    ("negotiation", "Negotiation", ["nash_demand", "alternating_offers", "multi_issue"],
     "demand_ratio", "Share of the surplus demanded in the Nash demand game",
     "Any pair of demands summing to the surplus is an equilibrium; the equal split is the focal outcome"),
    ("risk", "Risk taking", ["chicken", "chicken_high_stakes", "signaling", "cheap_talk"],
     "risk_taking_rate", "Share of rounds in which the model chose the risky action (going straight) in the chicken game",
     "Mixed equilibrium of the standard chicken game is 2/13 straight"),
]

GAME_MEASURES = {
    # per-game measures shown beside the category index (name, column, definition)
    "auction_first_price": ("First-price auction", "bid_ratio", "mean bid over maximum bid"),
    "auction_vickrey": ("Vickrey auction", "bid_ratio", "mean bid over maximum bid (truthful bidding is 0.50 when values average 50)"),
    "auction_all_pay": ("All-pay auction", "bid_ratio", "mean bid over maximum bid"),
    "colonel_blotto": ("Colonel Blotto", "bid_ratio", "mean allocation over the maximum on the reported battlefield"),
}


def load_profiles():
    df = pd.read_csv(PROFILES, low_memory=False)
    for c in NUMERIC:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["developer"] = df.model_key.map(lambda k: MODELS[k][1] if k in MODELS else None)
    df["display"] = df.model_key.map(lambda k: MODELS[k][0] if k in MODELS else k)
    df["product_line"] = df.model_key.map(lambda k: MODELS[k][2] if k in MODELS else None)
    df["size_tier"] = df.model_key.map(lambda k: MODELS[k][3] if k in MODELS else None)
    df["reasoning"] = df.model_key.map(lambda k: MODELS[k][4] if k in MODELS else None)
    df["design"] = df.model_key.map(lambda k: "G" if k in FRONTIER_MODELS else "F")
    return df[df.model_key.isin(MODELS)]


def release_dates():
    p = os.path.join(OUT, "A7_release_dates.csv")
    if not os.path.exists(p):
        return None
    r = pd.read_csv(p)
    r["release_date"] = pd.to_datetime(r["release_date"], errors="coerce")
    return r.set_index("model_key")["release_date"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (c - h, c + h)
