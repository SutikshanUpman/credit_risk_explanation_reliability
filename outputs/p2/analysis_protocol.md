# P2 analysis protocol (frozen before any full-cohort explanation was computed)

Written 17 November 2026, before `run_p2.py` was run. P1 predictive results already existed when this was
written, so the *whole study* is not pre-registered; only the P2 explanation analysis is.
Before this file was written, only a smoke test was run (one model, 200 test rows: timing and additivity).
No stability, fidelity or rank result had been looked at.

## 1. Questions (from plan.md)
- H1: similar predictive performance does not necessarily imply similar borrower-level explanations.
- H2: explanation stability can change with modelling conditions (seed noise vs. positive-class weighting).
- H3: perturbing features that SHAP ranks high changes predictions more than perturbing low-ranked features.
Each is answered descriptively, with distributions; none is assumed to hold.

## 2. Inputs (read-only, from P1)
All ten models in `outputs/p1/runs/`, `processed/X_test.csv` (30,013 rows), `processed/X_train.csv`,
`feature_schema.json`. Nothing is re-imputed, rescaled, reordered or re-split.

## 3. Explanation setup
| Decision | Choice | Reason |
| --- | --- | --- |
| Library | `shap` 0.54.1, `shap.TreeExplainer` | Documented explicit reference modes |
| Mode | `feature_perturbation="interventional"` | Same reference for every model, so differences are not caused by model-specific references |
| Output scale | `model_output="raw"` (log-odds margin) | Additive; used for all runs. Probability-scale SHAP is never mixed in |
| Background | 100 rows sampled once from `X_train` with `DataFrame.sample(100, random_state=2026)`; IDs saved | Training data only; identical for all 10 models |
| Cohort | All 30,013 held-out rows in saved order | Primary analysis. No subsetting |
| Additivity check | `sum(SHAP)+expected_value` vs `Booster.predict(output_margin=True)`, tolerance 1e-4 | Float32 tree arithmetic gave ~6e-6 in P1 review |
| Sensitivity (secondary only) | Native `pred_contribs` (tree-path-dependent) for rank metrics only | Shows whether the reference choice matters. The primary mode is NOT changed by its result |

## 4. Metric definitions
Feature ranking: descending absolute SHAP over the 10 predictors (bias excluded); ties broken by feature-schema order (stable sort).

- **Spearman** (rank stability): Spearman correlation of the two 10-vectors of |SHAP| (average ranks for ties). If either vector is constant, the value is missing (NaN); the count is reported.
- **Top-k agreement**: |top-k(A) ∩ top-k(B)| / k, k in {3, 5}.
- **Near-zero threshold**: |SHAP| < 1e-3 log-odds. Reason: 100x above numerical additivity error (~1e-5), and below any change that matters for a lending-score explanation.
- **Signed SD**: per borrower/feature/condition, sample SD (ddof=1) of signed SHAP across the 5 seeds.
- **Sign frequencies**: fraction of the 5 seeds with SHAP > +1e-3, < -1e-3, or near-zero.
- **Sign consistency**: max(n_pos, n_neg) / (n_pos + n_neg), among non-near-zero seeds; missing if all five are near-zero (all-near-zero is NOT counted as consistent).
- **Magnitude CV**: SD(|SHAP|, ddof=1) / mean(|SHAP|) over the 5 seeds. Valid only if mean(|SHAP|) >= 1e-3; masked counts reported. This is a CV of magnitudes, not of signed values.
- **Weighting change**: per matched seed, borrower, feature: SHAP_weighted - SHAP_unweighted (signed) and |.| of it. Raw-margin SHAP scales can differ between a weighted and unweighted model, so signed differences are descriptive; rank/top-k metrics are scale-free and are the main between-condition evidence.

## 5. Comparison families (kept separate)
1. Within condition: 10 seed pairs x 2 conditions = 20 model pairs.
2. Between conditions: 5 same-seed pairs.
The 25 comparisons share models and borrowers, so they are not independent. Primary summary: per borrower, average over pairs of the family; then mean, median and quantiles across borrowers. Uncertainty: percentile bootstrap over borrowers (2,000 resamples, seed 7). It describes borrower sampling variation conditional on these ten fixed models; it says nothing about other seeds, splits or datasets.

## 6. Perturbation fidelity
- Replacement values: training medians from `feature_schema.json` (checked to equal medians of `X_train`).
- For each model and borrower, k in {3, 5}: replace the k highest-ranked features (high arm) or the k lowest-ranked features (low arm) jointly with the medians; recompute prediction with the same model.
- Outputs: absolute probability change, absolute raw-margin change, high-minus-low paired difference, number of features actually changed per arm, and a no-op flag (zero features changed).
- Primary: all borrowers (no-ops retained and counted). Secondary (labelled): borrowers where both arms changed at least one feature.
- H3 is read as supported for a model/k only if the borrower-averaged high-minus-low difference is positive with a bootstrap interval excluding 0, and I also report the share of borrowers with positive/negative/zero difference, so counterexamples remain visible.
- Perturbation measures model sensitivity, not causal effects; independent median replacement can create unrealistic borrowers. Cross-condition probability changes are not directly comparable because weighted models are differently calibrated.

## 7. H1 handling
No equivalence threshold is justified in advance, so no "similar/equivalent" claim is made. Predictive differences are analysed continuously: for each of the 25 model pairs, |ΔROC-AUC|, |Δlog loss|, |ΔBrier| next to mean Spearman and top-k agreement (descriptive only, no test).

## 8. Overlap sensitivity (separate, labelled)
Rank-stability and fidelity summaries are repeated excluding the 99 test rows in `outputs/p1_review_overlap_test_ids.csv`. The primary results keep them.

## 9. Borrower examples (recorded rule)
Using the unweighted within-condition mean Spearman per borrower: borrowers nearest to the 1st, 50th and 99th percentile (ties: lowest borrower_id). Plus: the borrower with the most negative mean high-minus-low (k=3) difference across models (counterexample), and the borrower with the lowest mean between-condition top-3 agreement. No hand-picking.
