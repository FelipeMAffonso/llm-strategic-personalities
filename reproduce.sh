#!/usr/bin/env bash
# Every analysis, table and figure of the paper from the trial data, in the order they depend on each other.
#
# Usage: bash reproduce.sh [--with-clustering] [--with-reparse-check]
#   The raw trial files are read from raw_data/ (download raw_corpus_v1.tar.gz from Zenodo,
#   https://doi.org/10.5281/zenodo.19896196, and unpack it there), or from the folder named by RAW_DATA_DIR.
#   --with-clustering also reruns the reasoning-text clustering (scikit-learn) and its sentence-transformer robustness
#   check (sentence-transformers; about an hour on a CPU). The released results were computed without umap-learn, so
#   the files named umap hold principal components. Without the option, the clustering results shipped in
#   summary_data/reasoning_text_clustering/ are used.
#   --with-reparse-check also reruns the re-parsing check (analysis/reparse_check.py, about ten minutes), which
#   re-parses every reply with the rule-based parser alone and repeats the analyses. Without it, the results shipped
#   in summary_data/reparse_check/ are used.
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
WITH_CLUSTERING=0
WITH_REPARSE_CHECK=0
for option in "$@"; do
  case "$option" in
    --with-clustering) WITH_CLUSTERING=1 ;;
    --with-reparse-check) WITH_REPARSE_CHECK=1 ;;
    *) echo "unknown option: $option (use --with-clustering and/or --with-reparse-check)"; exit 1 ;;
  esac
done
export SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH:-0}  # a fixed creation date in the PDFs, so that a rerun writes identical files
step() { echo "== $*"; }

step "the trial-level data from the raw trial files"
python analysis/behavioral_profiles.py > /dev/null

if [ "$WITH_CLUSTERING" = 1 ]; then
  step "reasoning-text clustering and its sentence-transformer robustness check"
  if python -c "import umap" > /dev/null 2>&1; then
    echo "   note: umap-learn is installed, so centroid_umap.csv and trace_umap.csv will hold UMAP coordinates;"
    echo "   the released files hold the principal components computed without it"
  fi
  python analysis/reasoning_text_clustering.py
  python analysis/reasoning_text_robustness.py
fi
step "the developer labels of the reasoning-text clustering"
python analysis/check_developer_labels.py

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
if [ "$WITH_REPARSE_CHECK" = 1 ]; then
  step "the re-parsing check: every reply re-parsed with the rule-based parser alone, analyses repeated"
  python analysis/reparse_check.py > /dev/null
fi

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
