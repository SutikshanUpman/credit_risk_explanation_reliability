# Handover to P3: research and integration

> Historical P1 handover. P2 results are now available in `outputs/p2/handover.md`; the current surface inspection and qualifications are in `SURFACE_REVIEW.md`.

Reviewed on 11 November 2026. Read `instructions.md`, `plan.md`, [review.md](review.md), and [handover_p2.md](handover_p2.md).

**P1 is complete and checked. You can write the data/modelling Methods and predictive Results now. The literature gap, SHAP reliability results, and final research conclusions remain to be completed.**

## 1. Research objective and contribution

Working title: **Explainable Credit-Risk Prediction with Quantitative Evaluation of SHAP Explanation Reliability**.

Investigate whether explanations for the same held-out borrower records remain consistent and faithful to the model when training randomness and positive-class weighting change. Jointly examine rank stability, signed attribution stability, and perturbation sensitivity alongside predictive performance.

The proposed contribution is a reproducible experiment integrating these measurements. Its novelty is provisional until the literature review establishes how it differs from previous work. XGBoost, SHAP, explanation stability, and imbalance treatment are established concepts. Do not claim that SHAP stability has never been studied.

## 2. What P1 actually did

| Item | Actual implementation |
| --- | --- |
| Dataset | Give Me Some Credit, local `Data/cs-training.csv` |
| Target | `SeriousDlqin2yrs`: 90-day delinquency or worse within two years |
| Data size | 150,000 labelled records, 10 numeric predictors, 10,026 positives (6.684%) |
| Held-out data | One fixed group-aware split: 30,013 rows, 1,991 positives (6.6338%) |
| Training data | 119,987 rows, 8,035 positives (6.6966%) |
| Split rule | First held-out fold of StratifiedGroupKFold(5, shuffle=True, random_state=42); other folds form training |
| Groups | Exact cleaned predictor profiles, including matching missing values, excluding IDs and labels |
| Cleaning | One nonpositive age set missing; other extreme values retained |
| Missing values | 29,731 missing incomes and 3,924 missing dependent counts in raw labelled data |
| Preprocessing | One median imputer fitted on training rows; no scaling, extra indicators, or feature selection |
| Predictor exclusion | Original row ID and target excluded from features |
| Models | XGBoost, 300 trees, depth 4, learning rate 0.05, row/column subsampling 0.8 |
| Other controls | CPU hist method, four threads, fixed starting probability 0.5; full settings saved per run |
| Conditions | Unweighted loss (positive weight 1) versus weighted loss (13.933042937149969) |
| Seeds | 11, 22, 33, 44, 55 in both conditions: ten models total |
| Reporting threshold | 0.5, fixed; not tuned or proposed as a lending policy |
| Scope | No tuning, best-model selection, SMOTE, bootstrap, second dataset, or full cross-validation performance estimate |

The competition `cs-test.csv` contains no labels and is not the study's held-out evaluation data. `sampleEntry.csv` is a submission example, not ground truth. The split is approximately 80/20 rather than exactly 120,000/30,000 because profile groups are kept together.

Suggested factual Methods wording:

> We evaluated ten XGBoost classifiers on a fixed held-out partition of the Give Me Some Credit labelled dataset. Exact cleaned predictor profiles were grouped before stratified group splitting to prevent those profiles crossing partitions. A median imputer was fitted only on training data and reused for all runs. Five seeds were evaluated under unweighted and positive-class-weighted loss, with all other specified model settings fixed. Predictive performance was measured on the same 30,013 held-out records for every model.

Expand from the saved protocol/configuration; describe the 55 post-imputation overlap profiles as a limitation rather than claiming all model-input profiles are distinct across partitions.

## 3. Verified predictive results

Source: `outputs/p1/metrics_summary.csv`; values are mean +/- **sample SD across five seeds**.

| Condition | ROC-AUC | Average precision | Log loss | Brier score |
| --- | --- | --- | --- | --- |
| Unweighted | 0.86504 +/- 0.00021 | 0.39797 +/- 0.00129 | 0.17658 +/- 0.00012 | 0.04864 +/- 0.00004 |
| Weighted | 0.86529 +/- 0.00029 | 0.39919 +/- 0.00046 | 0.43289 +/- 0.00025 | 0.13681 +/- 0.00010 |

| Condition | Precision at 0.5 | Recall at 0.5 | F1 at 0.5 |
| --- | --- | --- | --- |
| Unweighted | 0.61333 +/- 0.00273 | 0.19407 +/- 0.00131 | 0.29485 +/- 0.00180 |
| Weighted | 0.22023 +/- 0.00074 | 0.76273 +/- 0.00290 | 0.34178 +/- 0.00107 |

Higher ROC-AUC/average precision and lower log loss/Brier score are preferable. Weighting changes the trade-off: recall increases and precision decreases at 0.5; probability scoring worsens substantially. The small observed ROC-AUC difference is not proof of overall predictive equivalence, a statistically significant improvement, or superiority. Log loss and Brier score evaluate probability quality; without a calibration analysis, do not claim to have formally measured every aspect of calibration.

No confidence interval, hypothesis significance test, or population generalization result is established by these across-seed SDs. Full confusion counts and per-run values are in `metrics_all_runs.csv`.

## 4. Hypotheses: what can be concluded now

| Hypothesis from the plan | Evidence still required |
| --- | --- |
| H1: Similar predictive performance need not imply similar borrower explanations | P2 model-pair reliability metrics aligned with differences in ROC-AUC, AP, and probability scores; specify which performance dimension is being compared |
| H2: Explanation stability changes with training conditions | P2 within-condition seed variation and matched-seed weighting comparisons |
| H3: Perturbing highly ranked features causes larger model prediction changes than low-ranked features | P2 paired high/low perturbation results, equal feature counts, no-op reporting, and a stated replacement procedure |

None of these explanation hypotheses has been tested yet. Prefer continuous predictive-performance differences unless an independently justified similarity criterion is specified before explanation analysis. Do not choose a post hoc equivalence threshold to make H1 appear supported. Use model sensitivity language for H3; it does not establish effects on real borrower outcomes.

## 5. Your work before P2 analysis

1. Verify every relevant reference from the JPEG. Abbreviated author/year strings are not sufficient evidence. Do not invent titles, DOIs, findings, or study settings.
2. Build a literature matrix. Suggested columns: full citation/link, dataset, predictor, explanation method, rank/attribution/fidelity metrics, controls, findings, limitations, and the specific distinction from this project. Mark unread/unverified items explicitly.
3. Finalize research questions and a restrained gap statement supported by that matrix.
4. Agree with P2 on SHAP output scale/reference, cohort/background, top-k/ties, CV handling, perturbation and aggregation. Record these before the full explanation results.
5. Record that P1's model protocol preceded fitting, but predictive results now exist and this is not a fully preregistered study.

Suggested literature-matrix header:

```text
Citation | Verified link | Data | Predictor | SHAP setup | Rank stability |
Attribution stability | Fidelity test | Experimental controls | Findings |
Limitations | Difference from our design | Verification/read status
```

## 6. What to request from P2

See the detailed contract in `handover_p2.md`. Request the frozen protocol, explanation arrays with borrower/feature/run order, base values and additivity checks, all three metric families, per-borrower and aggregate results, figures, selection rules for examples, exact software versions, and reproduction commands.

P2 should separate 20 within-condition seed-pair comparisons from five matched-seed cross-condition comparisons. These share models and borrowers and are not independent repetitions. Require transparent near-zero CV handling and a fixed explanation reference strategy. A model-specific path-dependent reference and a common interventional background answer related but different questions.

## 7. Limitations to retain

- One historical dataset and one split; no external or temporal validation.
- Profile grouping is not verified real-person identity grouping; timestamps cannot be independently checked here.
- There are 609 duplicate observations beyond the first when IDs are excluded, and 37 raw predictor profiles have conflicting labels. Observations were retained, with identical cleaned profiles assigned together.
- Imputation collapses some different cleaned records into the same processed profile. There are **55 shared processed profiles affecting 99 held-out rows and 96 training rows**. These IDs are supplied for an explicitly labelled optional sensitivity analysis. This is not evidence that test labels fitted the imputer.
- Very large ratios and delinquency values 96/98 remain. The dictionary does not justify a specific recoding; their effect is an unresolved data limitation.
- Five seeds describe conditional training variation, not uncertainty over all populations/splits. Weighting is not a resampling experiment.
- Explanations are model-relative. Their reference distributions, correlated predictors, near-zero values, and probability saturation affect interpretation.
- Median perturbation can create unrealistic records or no-op changes and is not causal validation.
- The external `shap` package and full P2 analysis have not yet been executed. A small native TreeSHAP additivity check only establishes basic artifact compatibility.

## 8. Final research deliverables

Write the paper only to the extent supported by completed work:

- Introduction: precise question and verified literature gap.
- Methods: P1's actual data/model design and P2's recorded explanation/perturbation protocol.
- Results: predictive table plus rank, attribution, and fidelity evidence; include mixed findings.
- Discussion: which hypotheses the evidence supports, with no forced success narrative.
- Limitations: preserve the qualifications above and any issues P2 discovers.
- Reproducibility appendix: versions, seeds, split IDs, source attribution, run commands, and artifact map.

Completion requires a verified literature matrix, an evidence-backed contribution statement, all three P2 reliability results, and a report in which every numeric claim traces to a saved artifact. The full project is not complete merely because P1 is complete.

For a viva: **P1 controls and saves the models, P2 measures whether their explanations remain dependable, and P3 explains what that evidence contributes to existing research.**
