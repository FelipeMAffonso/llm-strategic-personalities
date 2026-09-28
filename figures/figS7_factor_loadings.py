from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

import figlib
from figlib import plt

from common import CATEGORIES, MODELS


def principal_components():
    data = pd.read_csv(Path(figlib.CLUSTERING) / "behavioral_signatures.csv")
    data = data.loc[data.model_key.isin(MODELS)]
    assert len(data) == 25 and data.model_key.is_unique
    features = sorted(key for key in data if "__" in key and not key.startswith("lex_")
                      and any(metric in key for metric in ["entropy", "consistency", "first_round_rate", "endgame_shift", "dominant_rate"]))
    values = data[features].fillna(0).to_numpy()
    deviations = values.std(axis=0)
    deviations[deviations == 0] = 1
    standardized = (values - values.mean(axis=0)) / deviations
    left, singular, right = np.linalg.svd(standardized, full_matrices=False)
    loadings = right[:2].T * singular[:2] / np.sqrt(len(data) - 1)
    variance = singular**2 / (singular**2).sum()
    print(f"PCA: {len(data)} models, {len(features)} features, {data[features].isna().sum().sum()} missing entries filled with zero as in the original")
    print("Variance explained (%):", variance[:10] * 100)
    return features, loadings, variance


def build():
    figlib.style()
    features, loadings, variance = principal_components()
    shades = list(figlib.PALETTE["developer"].values()) + [figlib.PALETTE["benchmark"]]
    category_colors = {entry[0]: shade for entry, shade in zip(CATEGORIES, shades)}
    game_categories = {game: entry[0] for entry in CATEGORIES for game in entry[2]}
    names = {
        "auction_vickrey": "Vickrey auction", "chicken_high_stakes": "Chicken (high stakes)",
        "matching_pennies": "Matching pennies", "chicken": "Chicken",
        "stag_hunt_risky": "Stag hunt (risky)", "bos_standard": "Battle of the sexes",
        "auction_first_price": "First-price auction", "stag_hunt_standard": "Stag hunt",
        "cheap_talk": "Cheap talk",
    }
    fig = plt.figure(figsize=(7.2, 6.2))
    loading_axis = fig.add_axes([0.085, 0.14, 0.59, 0.68])
    variance_axis = fig.add_axes([0.785, 0.36, 0.185, 0.40])
    for category in CATEGORIES:
        selected = [index for index, feature in enumerate(features) if game_categories[feature.split("__")[0]] == category[0]]
        loading_axis.scatter(loadings[selected, 0], loadings[selected, 1], s=12, color=category_colors[category[0]],
                             edgecolor="white", linewidth=0.25, zorder=3)
    loading_axis.axhline(0, color=figlib.PALETTE["separator"], linewidth=0.6, zorder=0)
    loading_axis.axvline(0, color=figlib.PALETTE["separator"], linewidth=0.6, zorder=0)
    loading_axis.set(xlim=(-2.5, 1.2), ylim=(-1.4, 1.4), xlabel=f"Factor 1 ({variance[0] * 100:.1f}% variance)",
                     ylabel=f"Factor 2 ({variance[1] * 100:.1f}% variance)")
    loading_axis.set_xticks([-2, -1, 0, 1])
    loading_axis.set_yticks([-1, -0.5, 0, 0.5, 1])
    components = np.arange(1, 11)
    variance_axis.bar(components, variance[:10] * 100, color=figlib.color("Google"), alpha=0.7, edgecolor="white", linewidth=0.3)
    variance_axis.plot(components, np.cumsum(variance[:10]) * 100, "o-", color=figlib.color("Anthropic"), markersize=3, linewidth=0.8)
    variance_axis.set(xlim=(0.3, 10.7), ylim=(0, 80), xlabel="Component", ylabel="Variance explained (%)")
    variance_axis.set_xticks(components, components, fontsize=6)
    variance_axis.set_yticks([0, 20, 40, 60, 80])
    variance_axis.legend([Line2D([], [], color=figlib.color("Anthropic"), marker="o", markersize=3),
                          Line2D([], [], color=figlib.color("Google"), linewidth=5, alpha=0.7)],
                         ["Cumulative", "Per component"], loc="lower left", bbox_to_anchor=(-0.05, -0.43), frameon=False, fontsize=6)
    handles = [Line2D([], [], marker="o", linestyle="none", color=category_colors[entry[0]], markersize=4, label=entry[1]) for entry in CATEGORIES]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.51, 0.985), ncol=4, frameon=False, fontsize=7)
    fig.text(0.04, 0.845, "a", fontweight="bold", fontsize=8)
    fig.text(0.76, 0.845, "b", fontweight="bold", fontsize=8)
    top = np.argsort(np.linalg.norm(loadings, axis=1))[-10:][::-1]
    points = [(horizontal, vertical, "", "") for horizontal, vertical in loadings]
    for index in top:
        game, metric = features[index].split("__", 1)
        label = f"{names[game]}\n({metric.replace('_', ' ')})"
        points.append((*loadings[index], label, category_colors[game_categories[game]]))
    line_count = len(loading_axis.lines)
    figlib.label_points(loading_axis, points, fontsize=6, avoid_leader_crossings=True)
    for line in list(loading_axis.lines)[line_count:]:
        line.remove()
    ordered = sorted(zip(loading_axis.texts, top), key=lambda pair: loadings[pair[1], 1])
    for (text, index), label_height in zip(ordered, np.linspace(-1.05, 1.05, 10)):
        text.set_transform(loading_axis.transData)
        text.set_position((-1.25, label_height))
        text.set_ha("right")
        text.set_va("center")
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for text, index in zip(loading_axis.texts, top):
        horizontal, vertical = loadings[index]
        source = loading_axis.transData.transform((horizontal, vertical))
        box = text.get_window_extent(renderer).padded(1)
        target = loading_axis.transData.inverted().transform([np.clip(source[0], box.x0, box.x1), np.clip(source[1], box.y0, box.y1)])
        loading_axis.plot([horizontal, target[0]], [vertical, target[1]], color=text.get_color(), linewidth=0.5, zorder=2)
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "figS7_factor_loadings")
