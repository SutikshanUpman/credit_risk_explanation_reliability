# P2 handover to P3: SHAP stability and fidelity

Completed 17 November 2026. All numbers below come from files in `outputs/p2/` and were re-checked by `verify_p2.py` (all checks passed, see `verification_p2.txt`). `outputs/p1/` is unchanged (its hashes are re-verified).

## 1. What was done
All ten saved P1 XGBoost models were explained on all 30,013 held-out borrowers with one fixed TreeSHAP setup, and the three reliability dimensions were measured: rank stability, attribution stability, perturbation fidelity. Definitions are frozen in `analysis_protocol.md`, written before the full explanations were computed. (Only a 200-row timing/additivity smoke test preceded it; no stability or fidelity result had been seen. P1 predictive results already existed, so the whole study is not pre-registered.)

## 2. Setup actually used
| Item | Value |
| --- | --- |
| Library | `shap` 0.54.1, `TreeExplainer`, interventional, raw log-odds output |
| Background | 100 training rows, `X_train.sample(100, random_state=2026)`, IDs in `background_ids.csv`, same for all models |
| Cohort | all 30,013 held-out rows, saved order (`cohort_ids.csv`) |
| Additivity | sum of SHAP + base value equals raw margin; max error 3.0e-6 to 7.4e-6 (tolerance 1e-4) |
| Ranking | descending absolute SHAP, ties by feature-schema order; bias excluded |
| Near-zero cutoff | 1e-3 log-odds |
| Perturbation | k = 3 and 5 highest- or lowest-ranked features jointly replaced by training medians (from `feature_schema.json`, verified equal to `X_train` medians) |
| Uncertainty | percentile bootstrap over borrowers (2,000 resamples, seed 7). It covers borrower sampling only, for these ten fixed models |
| Environment | Python 3.12.3, Linux, 1 thread; P1 pins plus shap (`requirements_p2.txt`, `environment_versions_p2.txt`) |

## 3. Results (borrower-averaged; CI = bootstrap over borrowers)
**Rank stability** (`rank_stability_summary.csv`). No undefined Spearman values occurred.

| Comparison | Spearman | Top-3 agreement | Top-5 agreement |
| --- | --- | --- | --- |
| Within unweighted (10 pairs) | 0.959 (0.959-0.960) | 0.950 | 0.947 |
| Within weighted (10 pairs) | 0.949 (0.949-0.949) | 0.932 | 0.941 |
| Between conditions, same seed (5 pairs) | 0.925 (0.924-0.925) | 0.898 | 0.915 |

Medians for top-3 are 1.0 within condition and 0.933 between conditions; the 5th percentile of borrowers is 0.80 / 0.77 / 0.67 for top-3.

**Attribution stability** (`attribution_stability_summary.csv`). Signs are very consistent: mean sign consistency is 0.94 to 1.00 for every feature and condition. Signed SD across seeds is small (feature medians 0.001 to 0.031 log-odds). Magnitude CV is lowest for the delinquency counts (median about 0.02) and highest for DebtRatio and MonthlyIncome (median 0.21 to 0.27). Only 1 of 600,260 borrower-feature-condition CV values was masked (mean magnitude below 1e-3). Weighted models give slightly larger mean absolute SHAP for most features (`fig2`). Same-seed weighting changes (`weighting_change_summary.csv`) average 0.006 to 0.058 in absolute log-odds per feature, largest for DebtRatio and RevolvingUtilization. Raw-margin scales differ between weighted and unweighted models, so treat signed differences as descriptive.

**Fidelity** (`fidelity_summary.csv`; absolute raw-margin change, high-ranked minus low-ranked arm):

| Condition | k | Mean difference (95% CI) | Borrower-model rows: high > low / high < low |
| --- | --- | --- | --- |
| Unweighted | 3 | 0.956 (0.946-0.966) | 93.8% / 6.1% |
| Unweighted | 5 | 0.931 (0.920-0.941) | 89.5% / 10.5% |
| Weighted | 3 | 1.013 (1.002-1.022) | 92.8% / 7.1% |
| Weighted | 5 | 0.982 (0.970-0.993) | 87.7% / 12.3% |

All ten individual models have an interval above 0 for both k. In probability terms the mean high-minus-low difference is 0.049/0.047 (unweighted, k=3/5) and 0.176/0.172 (weighted); the weighted models are differently calibrated, so do not compare those across conditions.
No-op perturbations (replacement changes nothing): low-ranked arm 11.2% (unweighted) and 12.7% (weighted) of cases at k=3, under 1.5% at k=5; high-ranked arm under 0.1%. The secondary analysis restricted to cases where both arms changed at least one feature gives nearly the same differences (e.g. 0.961 unweighted k=3). The high arm still changes slightly more features on average (2.07 vs 1.37 at k=3), so part of the gap is mechanical.

**Predictive performance vs explanations** (`performance_vs_reliability.csv`, `fig4`). Between conditions ROC-AUC differs by at most 0.0006 while log loss differs by about 0.256. Descriptive only: across the 25 pairs the Spearman correlation between log-loss gap and explanation similarity is -0.75, but this is driven by the between-condition pairs; for within-condition pairs the ROC-AUC gap vs similarity correlation is -0.32. These pairs are dependent, so no test is reported.

## 4. How the hypotheses fare (descriptive reading, not tests)
- **H1 (similar performance does not imply identical explanations): partly supported.** Same-seed unweighted/weighted models have almost identical ROC-AUC but lower explanation agreement than same-condition seed pairs (Spearman 0.925 vs 0.949-0.959, top-3 0.898 vs 0.93-0.95). But all agreement is still high and the weighted models are not predictively equivalent (log loss, Brier). No equivalence threshold was justified, so no "similar performance" claim is made.
- **H2 (stability depends on conditions): supported for the between-condition gap; mixed for within-condition.** Weighted models are slightly less stable than unweighted ones (Spearman 0.949 vs 0.959; top-3 0.932 vs 0.950; top-5 0.941 vs 0.947). In the path-dependent sensitivity (`sensitivity_path_dependent_rank_summary.csv`) the within-condition Spearman gap disappears (0.963 vs 0.964) and the top-5 order reverses, while the between-condition gap remains (0.935). So the within-condition weighted-vs-unweighted difference is small and depends on the SHAP reference mode; the between-condition gap is the robust finding.
- **H3 (high-ranked features change predictions more): supported on average**, but not for every borrower: 6-12% of borrower-model cases go the other way. Per-borrower examples are in `examples.md`.

## 5. Sensitivity analyses (secondary, labelled)
Excluding the 99 test rows whose processed profile also appears in training changes no rank or fidelity summary materially (e.g. Spearman 0.9594 vs 0.9594; weighted k=3 fidelity difference 1.011 vs 1.013). The path-dependent comparison is covered under H2.

## 6. Artifact map (`outputs/p2/`)
- `analysis_protocol.md`: frozen definitions.
- `explanations/<run>.npz`: per run `shap` (30,013 x 10), `expected_value`, `raw_margin`, `probability`, `borrower_id`, `native_shap`/`native_bias` (path-dependent sensitivity). Feature order = `outputs/p1/feature_schema.json`.
- `rank_stability.csv.gz`, `attribution_stability.csv.gz`, `weighting_change.csv.gz`, `fidelity.csv.gz`: per-borrower tables with the columns requested in `handover_p2.md`, plus `*_summary.csv`.
- `performance_vs_reliability.csv`, `figures/fig1-fig4`, `examples.md/csv`, `sensitivity_*.csv`.
- `cohort_ids.csv`, `background_ids.csv`, `manifest_p2.json` (file hashes, versions), `verification_p2.txt`, `analyze_log.txt`.
- Code: `run_p2.py` (stages `explain`, `analyze`), `verify_p2.py`, `requirements_p2.txt` in the project root.

## 7. How to reproduce and verify
Add `shap==0.54.1` to the P1 environment (`pip install -r requirements_p2.txt`), then from the project root:
```
python run_p2.py --stage explain    # about 19 minutes on one CPU; skips arrays that already exist
python run_p2.py --stage analyze    # about 4 minutes
python verify_p2.py                 # about 4 minutes; add --write-manifest to refresh hashes
```
To start fresh, move `outputs/p2/explanations/` aside first. `verify_p2.py` checks: P1 hashes unchanged; cohort and background IDs (background regenerated from the seed); additivity for all ten models; saved probabilities equal P1's; SHAP recomputed for 300 random rows per model; 3,000 rank rows recomputed with `scipy.stats.spearmanr` and plain loops; 1,500 attribution rows; fidelity recomputed with a one-borrower-at-a-time loop for 200 borrowers x 10 runs x 2 k x 2 arms (max difference 2.9e-8); table sizes and flags; protocol older than results.

## 8. Limitations and caveats
- One dataset, one split, five seeds per condition, loss weighting only (no SMOTE/bootstrap). Intervals describe borrower sampling for these ten models, not new seeds or splits.
- With only ten predictors, top features are dominated by a few strong variables (utilization, delinquency counts), so rank agreement is naturally high; Spearman over ten values is not a fine-grained measure.
- Mean results hide a tail: the least stable 5% of borrowers have top-3 agreement of 0.80 or lower (0.67 between conditions).
- Perturbation measures model sensitivity, not causal effects; replacing features independently with medians can create unrealistic borrowers. High and low arms do not change the same number of features (see no-op rates).
- Interventional vs path-dependent SHAP give somewhat different within-condition results (H2). Interventional was fixed in advance as primary; it was not chosen after comparing.
- 55 processed profiles overlap train/test (99 held-out rows); they are retained in all primary results.
- The least-stable example borrower (2157) still has identical top-3 features across all ten models; low Spearman there reflects reordering of lower-ranked features. See `examples.md`.

## 9. Environment differences from P1 (not defects)
P1 ran on Windows/Python 3.13/4 threads; P2 ran here on Linux/Python 3.12/1 thread. Consequences: (1) one held-out probability in `weighted_seed55` differs from P1's saved value by 1.2e-7 (about two float32 steps), so `verify_p2.py` uses a 2e-7 tolerance instead of P1's 1e-7; (2) `verify_p1.py` fails on this platform at a log-loss value differing from the saved one by 2e-12 (its tolerance is 1e-12), after passing its hash checks. P3 may want to re-run `verify_p1.py` on the original Windows setup. Fidelity columns are float32-derived, so values carry about 1e-7 precision.

## 10. Plain-language summary for a viva
We took ten credit models that differ only by random seed and by whether defaulters were given extra weight in the loss. For the same 30,013 borrowers we asked which features each model says drove the score. Models in the same group mostly agree on the top features; models from different groups agree a bit less even though their ability to rank borrowers (ROC-AUC) is almost identical. Swapping the most important features for typical values moves the prediction clearly more than swapping the least important ones, for roughly nine borrowers in ten, so the explanations point to features the model really uses. This shows explanation agreement and model sensitivity on this dataset only; it does not show causal effects, and it does not show the pattern holds for other data, seeds or methods.
