# P1 handover to P2 and P3

P1 is complete: ten XGBoost models, one fixed held-out population, training-only preprocessing, configurations, predictive metrics, and per-borrower probabilities. P2/P3 explanation analysis and literature integration are not yet completed. No explanation-reliability or novelty finding is claimed.

## Observed setup and results

Training: 119,987 rows, positive rate 6.6966%. Held-out: 30,013 rows, positive rate 6.6338%. Loss weight for positives: 13.933043 in weighted runs; 1 in unweighted runs. Five paired seeds: [11, 22, 33, 44, 55].

| Condition | ROC-AUC | Average precision | Log loss | Brier score |
| --- | --- | --- | --- | --- |
| unweighted | 0.86504 +/- 0.00021 | 0.39797 +/- 0.00129 | 0.17658 +/- 0.00012 | 0.04864 +/- 0.00004 |
| weighted | 0.86529 +/- 0.00029 | 0.39919 +/- 0.00046 | 0.43289 +/- 0.00025 | 0.13681 +/- 0.00010 |

Values are mean +/- sample standard deviation across seeds, not confidence intervals. Weighting can trade ranking, calibration, and threshold behaviour; inspect `metrics_all_runs.csv` for precision/recall/F1 and confusion counts. Do not choose a winner using this held-out set. Threshold 0.5 is fixed and not a deployment policy.

## Files to use

- `processed/X_train.csv`, `X_test.csv`, `y_train.csv`, `y_test.csv`: load with `index_col="borrower_id", float_precision="round_trip"`.
- `processed/preprocessor.joblib`: training-fitted median imputer. Model input is the processed matrix, not the raw CSV.
- `feature_schema.json`: exact feature order, dictionary definitions, and training medians.
- `splits/`: frozen borrower IDs and cleaned-profile group IDs.
- `runs/<condition>_seed<seed>/model.ubj`: all ten native models, accompanied by configuration, effective booster configuration, metrics, and predictions.
- `data_audit.json`, `dataset_card.md`, `experiment_protocol.md`, `manifest.json`, `environment_versions.txt`: decisions, provenance, integrity, and environment.

Reproduce from the project root using the README commands and a new output folder. Check saved artifacts with `.\.venv\Scripts\python.exe verify_p1.py --output outputs/p1`.

## Checks and limitations

Training checked ID/group separation, training-only imputer medians, finite inputs/probabilities, unchanged source hashes, and native model reload predictions (absolute tolerance 1e-07, relative tolerance zero). `verify_p1.py` separately checks artifacts read back from disk, recreates the split/preprocessing, and recomputes every model's metrics. Its console output is the evidence for that separate check; this document does not assume it has run.

Unusual-value policy: Retain rows and extremes. Set age <= 0 missing; training-median imputation. No clipping, scaling, or feature selection. Post-imputation profiles shared between partitions: 55. Group separation applies to cleaned profiles before imputation, not verified identities. This experiment uses a single historical dataset and split. It tests randomness and class weighting, not resampling. Potential sentinel values and timestamp uncertainty remain. Neither causal effects nor modern deployment performance have been established.

## P2 next steps

Freeze the TreeSHAP configuration, output scale, cohort, top-k values/ties, and perturbation rules before inspecting explanations. Use all ten models on the same held-out borrower IDs in the same order. Keep a training-only background fixed if the chosen SHAP mode uses one. Check additivity on the declared scale.

Measure per-borrower rank stability (Spearman and top-k overlap), signed attribution variability/sign consistency (guard CV near zero), and high-versus-low feature perturbation sensitivity. Keep within-condition seed comparisons separate from matched-seed weighting comparisons. Pairwise model comparisons are dependent; do not treat them as independent samples. Save explanation arrays with run/borrower/feature mappings, per-borrower metrics, aggregate tables, plots, and transparently selected examples. Perturbation is model sensitivity, not causality.

## P3 next steps

Verify the JPEG's abbreviated citations, complete the literature matrix and gap statement, and confirm the analysis definitions before P2 sees explanation results. Predictive results now exist, so do not claim a later protocol is fully preregistered. For H1, use continuous differences unless an independently justified equivalence rule already exists. Integrate actual P1 and P2 outputs into Methods, Results, Discussion, and Limitations. Describe weighting accurately and report negative/mixed findings. Novelty requires verified literature plus the completed reliability experiments.

## Viva explanation

We keep the people being evaluated fixed, change only training randomness and class weighting, and save every model. This makes it possible for P2 to ask whether similar prediction quality comes with similar feature explanations. P1 provides the controlled comparison; P2 measures explanation reliability; P3 determines what the evidence contributes to existing research.
