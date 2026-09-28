import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

import figlib
from figlib import plt
from figS9_crossplay_matrix import SUMMARY, KEYS, MODELS, DEVELOPER_ORDER
from common import CATEGORIES

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


def build():
    figlib.style()
    profiles = pd.read_csv(SUMMARY / "behavioral_profiles.csv", usecols=["model_key", "game_id"])
    games = [game for entry in CATEGORIES for game in entry[2]]
    frontier = sorted(set(MODELS) - set(KEYS), key=lambda key: (DEVELOPER_ORDER.index(MODELS[key][1]), list(MODELS).index(key)))
    order = KEYS + frontier
    counts = profiles.groupby(["model_key", "game_id"]).size().unstack(fill_value=0).reindex(index=order, columns=games, fill_value=0)
    assert counts.shape == (25, 38) and len(frontier) == 9
    assert counts.to_numpy().sum() == profiles.loc[profiles.model_key.isin(MODELS)].shape[0]
    assert len(set(GAME_NAMES[game] for game in games)) == 38
    print("Trials:", counts.to_numpy().sum(), "cell count range:", counts.to_numpy().min(), counts.to_numpy().max())
    fig = plt.figure(figsize=(7.2, 9.5))
    cmap = LinearSegmentedColormap.from_list("coverage", ["white", figlib.color("Google"), figlib.color("Alibaba")])
    axes = []
    for keys, bottom, height in [(KEYS, 0.52, 0.352), (frontier, 0.277, 0.198)]:
        axis = fig.add_axes([0.275, bottom, 0.69, height])
        axes.append(axis)
        image = axis.imshow(counts.loc[keys], vmin=0, vmax=counts.to_numpy().max(), cmap=cmap, aspect="auto", interpolation="none")
        axis.set_yticks(range(len(keys)), [MODELS[key][0] for key in keys], fontsize=6)
        axis.set_xticks(range(38), [GAME_NAMES[game] for game in games] if keys == frontier else [""] * 38,
                       rotation=90, fontsize=5.5)
        axis.tick_params(length=0, pad=4)
        for tick, key in zip(axis.get_yticklabels(), keys):
            tick.set_color(figlib.color(MODELS[key][1]))
        for boundary in np.cumsum([len(entry[2]) for entry in CATEGORIES])[:-1]:
            axis.axvline(boundary - 0.5, color=figlib.PALETTE["separator"], linewidth=0.8)
        for boundary in range(len(keys) - 1):
            if MODELS[keys[boundary]][1] != MODELS[keys[boundary + 1]][1]:
                axis.axhline(boundary + 0.5, color=figlib.PALETTE["separator"], linewidth=0.6)
        for spine in axis.spines.values():
            spine.set_visible(False)
    start = 0
    for category in CATEGORIES:
        length = len(category[2])
        middle = (start + length / 2) / 38
        label = category[1].replace("Strategic depth", "Strategic\ndepth").replace("Risk taking", "Risk\ntaking")
        fig.text(0.275 + 0.69 * middle, 0.889, label, ha="center", va="bottom", fontsize=6)
        axes[0].plot([start - 0.4, start + length - 0.6], [1.012, 1.012], transform=axes[0].get_xaxis_transform(),
                     color=figlib.PALETTE["benchmark"], linewidth=0.6, clip_on=False)
        start += length
    fig.text(0.275, 0.95, "Five-trial protocol (16 models)", fontsize=7)
    fig.text(0.275, 0.495, "One-trial protocol (9 frontier models)", fontsize=7)
    color_axis = fig.add_axes([0.275, 0.065, 0.69, 0.016])
    colorbar = fig.colorbar(image, cax=color_axis, orientation="horizontal")
    colorbar.set_ticks(np.arange(0, counts.to_numpy().max() + 1, 50))
    colorbar.set_label("Trials", labelpad=5)
    colorbar.outline.set_visible(False)
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "figS10_coverage")
