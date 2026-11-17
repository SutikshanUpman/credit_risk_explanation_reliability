# P2 outputs: what each file means, and which plots matter

Project: SHAP explanation reliability for credit-default XGBoost models (10 models, 30,013 held-out borrowers).
Hypotheses: **H1** similar performance does not imply identical explanations; **H2** stability changes with modelling conditions; **H3** high-ranked SHAP features change predictions more than low-ranked ones.

Importance key: **A** = goes into the paper's Results; **B** = supports a claim, cite or put in appendix; **C** = reproducibility/audit only.

---
## Part 1. Significance of every output file (`outputs/p2/`)

### Documentation
| File | What it is | Why it matters | Use |
| --- | --- | --- | --- |
| `handover.md` | Full P2 results, hypotheses reading, limitations, viva summary | Single source P3 writes Results/Limitations from | A |
| `analysis_protocol.md` | Metric definitions and choices frozen before the full run | Proves definitions were set before results were seen; copy into Methods | A |
| `examples.md` / `examples.csv` | 5 rule-selected borrowers with SHAP in all 10 runs | Shows what "unstable" looks like for a real person; the plan asks for "a few borrower-level examples" | A |
| `verification_p2.txt`, `manifest_p2.json`, `analyze_log.txt`, `environment_versions_p2.txt` | Check results, file hashes, run log, library versions | Evidence of reproducibility; cite in a reproducibility statement | C |

### Raw explanations (the foundation)
| File | What it is | Why it matters | Use |
| --- | --- | --- | --- |
| `explanations/<run>.npz` (10 files) | SHAP value of every feature for every borrower, per model; plus base value, margin, probability, additivity error, path-dependent SHAP | Everything else is computed from these. Any new analysis P3 wants starts here. Additivity error at most 7.4e-6 shows the SHAP values are correct | B |
| `cohort_ids.csv` | The 30,013 borrower IDs in order | Proves the same borrowers were explained in every run (the plan's central requirement) | B |
| `background_ids.csv` | 100 training rows used as SHAP reference | Needed to reproduce SHAP exactly | C |

### Per-borrower result tables (large, `.csv.gz`)
| File | One row is | What it answers | Use |
| --- | --- | --- | --- |
| `rank_stability.csv.gz` | borrower x model pair (25 pairs) | Do two models rank features the same for this person? (Spearman, top-3, top-5) | B (source of the tail analysis) |
| `attribution_stability.csv.gz` | borrower x feature x condition | Do SHAP sign and size stay similar across 5 seeds? (signed SD, sign consistency, magnitude CV) | B |
| `weighting_change.csv.gz` | borrower x seed x feature | How much does adding class weighting move each SHAP value? | B |
| `fidelity.csv.gz` | borrower x model x k | Prediction change when top-ranked vs low-ranked features are replaced by medians | B (source of the H3 counterexample share) |

### Summary tables (small; these are what the paper quotes)
| File | Key finding it holds | Use |
| --- | --- | --- |
| `rank_stability_summary.csv` | Spearman 0.959 / 0.949 / 0.925 (within-unweighted / within-weighted / between); top-3 0.950 / 0.932 / 0.898; 5th-percentile borrower is far worse (top-3 0.80 / 0.77 / 0.67) | **A** (core table, rank dimension) |
| `attribution_stability_summary.csv` | Signs consistent (0.94 to 1.00); delinquency counts most stable (CV about 0.02), DebtRatio and MonthlyIncome least (CV 0.21 to 0.27) | **A** (core table, attribution dimension) |
| `fidelity_summary.csv` | Replacing high-ranked features moves the margin about 0.93 to 1.01 more than low-ranked; high > low for 88 to 94% of cases | **A** (core table, fidelity dimension; H3) |
| `weighting_change_summary.csv` | Weighting shifts each feature by 0.006 to 0.058 log-odds; weighted models give slightly larger mean |SHAP| | B (H2) |
| `performance_vs_reliability.csv` | 25 model pairs: accuracy gap next to explanation similarity | **A** (H1 evidence; source of fig4) |
| `sensitivity_path_dependent_rank_summary.csv` | Same rank metrics with a different SHAP reference | B (robustness; changes how H2 is worded) |
| `sensitivity_overlap_excluded_*_summary.csv` | Same results after dropping 99 test rows also seen in training | B (shows leakage does not matter) |
| `p3_extras/key_results.csv`, `global_importance_by_feature.csv` | All headline numbers in one place; per-feature importance and rank | B (quick lookup for P3) |

---
## Part 2. Plots: which ones matter

### Existing figures, ranked for the project
| Rank | Figure | What it shows | Supports | Verdict |
| --- | --- | --- | --- | --- |
| 1 | `fig3_fidelity.png` | High-ranked replacement changes predictions about 1.0 raw-margin vs about 0.1 for low-ranked, in all 10 models, both k | **H3**, the main "explanations are faithful" evidence | Essential, but redraw: x labels overlap, legend covers bars, no CIs, and add a random-feature arm |
| 2 | `fig1_rank_stability.png` | Boxplots of per-borrower Spearman, top-3, top-5 for the three comparison families | **H2** and the "stable on average, weak tail" story | Essential. Keep; add readable axis titles. The long lower whiskers are the finding |
| 3 | `fig4_performance_vs_reliability.png` | Explanation similarity vs accuracy gap per model pair | **H1** | Essential for H1. Left panel (ROC-AUC) is informative; right panel (log loss) is just two clusters, so do not draw a trend line or quote the -0.75 as a relationship. Fix overlapping x tick labels |
| 4 | `fig2_global_importance.png` | Mean |SHAP| per feature, unweighted vs weighted | Context: utilisation, 30-59 late and age dominate, so high rank agreement is partly expected | Useful context figure or appendix; also backs the limitation "top features dominated by a few variables" |

### Plots the plan needs but P2 does not yet have
| Needed plot | Why | Data source |
| --- | --- | --- |
| **Attribution stability by feature** (sign consistency and magnitude CV, per feature and condition) | One of the plan's three core measures has only a table | `attribution_stability_summary.csv` |
| **Fidelity with random-feature baseline** (high vs random vs low, with CIs) | Makes the H3 claim defensible against the "high arm changes more features" objection | needs new run on P1 models |
| **One borrower example figure** (SHAP of every feature across the 10 runs for 2 to 3 borrowers) | Makes "same borrower, different explanation" visible; ideal for a viva slide | `examples.csv` |
| **Rank-stability tail** (histogram or ECDF of per-borrower top-3 agreement, within vs between) | Shows the mean hides the least stable borrowers | `rank_stability.csv.gz` |

### Recommended figure set for the paper (5 figures, 1 table)
1. **Table 1 (core evaluation table):** rank, attribution, fidelity: question, metric, result. Built from the three A summaries.
2. **Fig A:** rank stability boxplots (fig1) or ECDF of top-3 agreement.
3. **Fig B:** attribution stability per feature (new).
4. **Fig C:** fidelity high vs random vs low (redrawn fig3).
5. **Fig D:** accuracy gap vs explanation similarity (fig4, ROC-AUC panel plus log-loss panel labelled as two clusters).
6. **Fig E:** borrower example across 10 runs (new). Fig2 (global importance) goes to the appendix.

### Plot-to-claim map (for P3 so every claim has evidence)
| Claim in paper | Evidence |
| --- | --- |
| Explanations are mostly but not perfectly stable | Table 1, Fig A |
| The least stable borrowers are much worse than the average | Fig A tail, `examples.md` |
| SHAP signs are reliable; magnitudes less so for DebtRatio and MonthlyIncome | Fig B |
| Top-ranked features really drive the model | Fig C (after random baseline), `fidelity_summary.csv` |
| Near-identical AUC does not mean identical explanations | Fig D, `performance_vs_reliability.csv` (state that log loss also differs) |
| Findings are not an artefact of leakage or SHAP mode | `sensitivity_*` files (appendix) |

## Part 3. Cautions when using these outputs
- All confidence intervals cover borrower sampling for these ten fixed models; they say nothing about other seeds, splits or datasets.
- Correlations across the 25 model pairs are not independent; present fig4 descriptively, no p-values.
- Fidelity shows model sensitivity, not causal effect.
- Between-condition probability changes are not comparable (weighted models are differently calibrated); use rank metrics and raw-margin changes.
