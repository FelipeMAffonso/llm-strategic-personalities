#!/usr/bin/env bash
# Every analysis, table and figure of the paper from the trial data, in the order they depend on each other.
#
# Usage: bash reproduce.sh [--with-clustering]
#   The raw trial files are read from raw_data/ (download raw_corpus_v1.tar.gz from Zenodo,
#   https://doi.org/10.5281/zenodo.19896196, and unpack it there), or from the folder named by RAW_DATA_DIR.
#   --with-clustering also reruns the reasoning-text clustering and its robustness check (scikit-learn, umap-learn and
#   sentence-transformers; the robustness check takes about an hour on a CPU). Without it, the clustering results
#   shipped in summary_data/reasoning_text_clustering/ are used.
# Results are written to summary_data/, supplementary_tables/ and figures/out/.
set -e
cd "$(dirname "$0")"
RAW=${RAW_DATA_DIR:-raw_data}
if ! ls "$RAW"/pd_canonical_*.json > /dev/null 2>&1; then
  echo "No raw trial files in $RAW. Download raw_corpus_v1.tar.gz from https://doi.org/10.5281/zenodo.19896196 and run:"
  echo "  mkdir -p raw_data && tar -xzf raw_corpus_v1.tar.gz -C raw_data --strip-components=1"
  echo "or set RAW_DATA_DIR to the folder that holds the trial files."
  exit 1
fi
export SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH:-0}  # a fixed creation date in the PDFs, so that a rerun writes identical files
step() { echo "== $*"; }

step "the trial-level data from the raw trial files"
python analysis/behavioral_profiles.py > /dev/null

if [ "$1" = "--with-clustering" ]; then
  step "reasoning-text clustering and its sentence-transformer robustness check"
  python analysis/reasoning_text_clustering.py
  python analysis/reasoning_text_robustness.py
fi

step "A1, cooperation against the same opponents"
python analysis/same_opponent.py > /dev/null
step "A2, what explains cooperation"
python analysis/variance_decomposition.py > /dev/null
step "A3, the last rounds by opponent class (raw trial files)"
python analysis/endgame_by_opponent.py > /dev/null
step "A4, the category indices"
python analysis/category_tables.py > /dev/null
step "A6, the mechanism components"
python analysis/mechanism_profiles.py > /dev/null
step "reciprocity (raw trial files)"
python analysis/reciprocity.py > /dev/null

step "Supplementary Tables S1 to S10"
python supplementary_tables/build_tables.py

step "Figs. 1 to 5"
for f in fig1_design fig2_categories fig3_explains_and_drift fig4_mechanism fig5_endgame; do
  python figures/$f.py > /dev/null
done
step "Supplementary Figs. 1 to 16"
for f in figS1_category_heatmap figS2_radar figS3_behavioral_space figS4_dendrogram figS5_jsd_matrices \
         figS6_reactive_rounds figS7_factor_loadings figS8_lexical_features figS9_crossplay_matrix figS10_coverage \
         figS11_reciprocity_profiles figS12_developer_clustering figS13_cooperation_distributions \
         figS14_strategy_response figS15_crossplay_effects figS16_thinking_comparison; do
  python figures/$f.py > /dev/null
done
echo "done: results in summary_data/, supplementary_tables/ and figures/out/"
