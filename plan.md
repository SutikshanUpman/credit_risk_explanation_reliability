# Credit-risk explanation reliability: implementation and handover plan

## Read first

Read `instructions.md`, then inspect `Plan.jpeg`, the source assignment. This file is an execution plan, not a report of completed experiments. The user is P3 and wants another agent to build the project and provide a usable handover.

Implement P1 first and produce a complete P1-to-P2/P3 handover. P2 and P3 work is specified below so the artifacts support their tasks; do not describe those stages as completed merely because P1 is finished. If asked to implement the entire project, proceed through these stages in order.

## 1. Goal and boundaries from the JPEG

Working direction: **Explainable Credit-Risk Prediction with Quantitative Evaluation of SHAP Explanation Reliability**.

Study the same held-out borrowers under controlled changes to model training. Jointly measure:

| Dimension | Question | Planned output |
| --- | --- | --- |
| Rank stability | Do the same features remain important? | Spearman correlation and top-k agreement |
| Attribution stability | Do signed SHAP values and magnitudes remain similar? | Variability, sign consistency, and carefully defined CV |
| Fidelity | Do highly ranked features actually affect model predictions? | Prediction changes after perturbation |

The proposed contribution is a compact, reproducible framework combining these checks with predictive performance. It is not a new predictor, and the claim that nobody has studied SHAP stability is explicitly excluded by the JPEG. Verify the literature before asserting a gap.

Hypotheses to record before experiments:

- H1: Similar predictive performance does not necessarily imply similar borrower-level explanations.
- H2: Explanation stability can change with modelling/resampling conditions.
- H3: Perturbing features ranked highly by SHAP produces larger prediction changes than perturbing low-ranked features.

Do not add a second dataset, deep ensemble, counterfactual system, broad model comparison, or large fairness study before the core experiment is complete. No extensive hyperparameter search.

## 2. Existing inputs and proposed decisions

Existing files: `Plan.jpeg`, `Data/cs-training.csv`, `Data/cs-test.csv`, `Data/sampleEntry.csv`, and `Data/Data Dictionary.xls`. Verify their presence and contents before use.

Use the local Give Me Some Credit data. Source: https://www.kaggle.com/c/GiveMeSomeCredit/data . Preserve source attribution and note that use is subject to the competition rules.

Read the local dictionary to confirm every feature and the target. `SeriousDlqin2yrs` represents serious delinquency within two years; describe this outcome precisely rather than treating it as every possible form of default. The competition test file has no labels and cannot be used to calculate our evaluation metrics. The sample submission is not ground truth.

The following are proposed implementation choices, not requirements stated verbatim in the JPEG:

- One fixed approximately 80/20 train/test split, seed 42.
- Five model seeds: 11, 22, 33, 44, 55.
- Two training conditions: original distribution/unweighted and positive-class weighting.
- Ten XGBoost models in total, with all other settings held constant.

The JPEG allows a feasible imbalance intervention such as SMOTE; weighting is the simpler proposed intervention. Name it accurately: it changes loss weights, not the sampled training rows. This experiment evaluates training randomness and weighting, not bootstrap/resampling effects. Do not claim to have tested resampling unless it is actually added and documented.

## 3. P1: ML and data implementation

### Step A: Audit and document the data

Create a dataset card and a concise audit with:

- Source, target semantics, feature meanings, shape, types, and class counts/rate.
- Missing-value counts and percentages per feature.
- Exact duplicate records and identical predictor profiles, including profiles with conflicting labels.
- Suspicious ages, extreme ratios, and unusually large delinquency counts.
- A leakage review: identifiers, target-derived information, or features unavailable at prediction time.

Preserve the original row identifier as `borrower_id` for alignment, never as a predictor. Do not assume matching IDs across the two separate competition files identify the same person. Inspect the dictionary before treating unusual values as sentinel codes. Do not silently drop outliers or cap values based on test outcomes. Record each cleaning decision and its rationale.

### Step B: Freeze the evaluation population

Split the labelled training file once. Aim for an approximately 20% held-out set with similar class proportions. If identical predictor profiles exist, keep each profile group within one partition to avoid identical profiles crossing the boundary. Use a reproducible group-aware procedure and report actual split sizes and class rates; do not force an exact 20% at the expense of group separation.

Save train/test borrower IDs and a split manifest. Verify disjoint IDs and, if grouping is used, disjoint profile groups. All runs must use identical test rows, labels, feature ordering, and borrower ordering.

No tuning is planned. If tuning is later necessary, create a validation split inside the training partition. Never select settings, thresholds, or the best model using held-out test results.

### Step C: Build minimal preprocessing

- Keep original predictors unless the audit justifies a change.
- Apply only documented deterministic cleaning rules.
- Fit numeric median imputation on training rows only.
- Save the fitted imputer, ordered feature names, and processed matrices.
- No scaling is needed for the proposed XGBoost-only pipeline.
- Because training rows are unchanged across the proposed runs, use the same fitted preprocessing throughout.
- Do not add missingness indicators by default; if needed, explain their effect on the feature schema and P2's explanations.

### Step D: Freeze the protocol before training

Save an experiment protocol/configuration before producing results. Use fixed starting settings such as:

| Setting | Proposed value |
| --- | --- |
| Objective | binary:logistic |
| Trees | 300 |
| Maximum depth | 4 |
| Learning rate | 0.05 |
| Row subsampling | 0.8 |
| Column subsampling | 0.8 |
| Tree method | hist |
| Model seeds | 11, 22, 33, 44, 55 |
| Classification threshold | 0.5 |

Explicitly record other effective model parameters, thread count, package versions, and hardware/runtime details needed to interpret reproducibility. Set a modest fixed thread count suited to the machine. The non-unit subsampling settings make seed variation meaningful.

Run both conditions for each seed:

1. Unweighted: `scale_pos_weight = 1`.
2. Weighted: `scale_pos_weight = training_negative_count / training_positive_count`.

Pair equal seeds across conditions. Save every model, not just the best one. If settings must change for a technical reason, document the reason and rerun all comparable conditions consistently. Do not alter settings to make hypotheses look correct.

### Step E: Evaluate and save outputs

For every run save:

- ROC-AUC and average precision (label it explicitly, not an ambiguous PR-AUC).
- Log loss and Brier score.
- Precision, recall, F1, and confusion matrix at the fixed threshold 0.5.
- Per-borrower true label, positive-class probability, and predicted class.
- Model, configuration, seed, condition, elapsed training time, and input artifact references/checksums.

Summarize mean and standard deviation across seeds within each condition. Report this as run-to-run variation, not a population confidence interval. A threshold of 0.5 is a reporting convention, not an optimized lending policy. Weighting may change calibration; do not report only ranking metrics.

### Step F: Validate and hand over

Perform practical checks:

- Training and test populations are disjoint under the chosen policy.
- IDs and target are absent from predictor matrices.
- Preprocessing statistics come only from training rows.
- All ten runs share the exact test IDs, labels, and feature order.
- Probabilities are finite and within [0, 1].
- Reloading each saved model reproduces its saved probabilities within a stated numerical tolerance.
- All expected artifacts exist and the documented command works.

Use a compact layout; this is a suggested structure, not a demand for many modules:

```text
instructions.md
plan.md
README.md
requirements.txt
run_p1.py
Data/                       # original files, unchanged
outputs/p1/
  dataset_card.md
  data_audit.json
  experiment_protocol.md
  feature_schema.json
  manifest.json             # source hashes, versions, seeds, split settings
  splits/                   # train/test IDs
  processed/                # train/test X and y, fitted preprocessing
  runs/<condition_seed>/    # model, config, metrics, predictions
  metrics_all_runs.csv
  metrics_summary.csv
  handover.md
```

Keep borrower IDs in exported data for alignment, but clearly exclude them when loading model inputs. Preserve sufficient numeric precision to reproduce predictions. Record how to recreate the environment and run the experiment from the project root. Do not overwrite a completed experiment silently when its configuration changes.

**P1 completion criterion:** another student can reload every model, reproduce its predictions, and begin explaining the same borrowers without reconstructing missing decisions.

## 4. P1 to P2: SHAP and analysis handover

P1 must supply all ten models, processed matrices, labels, borrower IDs, feature order, preprocessing, run configurations, predictive metrics, and reproduction instructions.

P2 should finalize these choices before examining explanation results:

- TreeSHAP method, output scale, background strategy, and library version. A simple initial choice is raw-margin explanations with one explicit consistent TreeSHAP configuration. Do not mix raw-margin and probability explanations.
- If a background sample is used, choose it from training data only and keep it fixed across runs.
- Use all held-out borrowers if feasible. Otherwise freeze a reproducible borrower subset before inspecting explanations and document its selection and class composition.
- Prespecify top-k values (suggested 3 and 5 for ten predictors), tie handling, metric aggregation, and near-zero attribution handling.
- Define perturbation replacement values using training data and apply the same procedure across models and borrowers.

P2 tasks:

1. Compute and save signed SHAP arrays with explicit run, borrower, and feature mappings; check additivity on the declared output scale.
2. Rank features by absolute SHAP value per borrower. Compare runs using Spearman correlation and top-k intersection divided by k. Define behavior for constant rankings/ties.
3. Report signed-value variability and sign consistency. If reporting CV, specify its denominator and near-zero cutoff; do not interpret division by a near-zero mean as useful instability evidence.
4. Perturb high-ranked and low-ranked features using equal feature counts and the same replacement rule. Measure absolute probability changes and paired high-minus-low differences. Retain individual and aggregated results.
5. Keep within-condition seed comparisons separate from matched-seed comparisons between weighting conditions. Do not treat all pairwise comparisons as independent observations.
6. Produce stability/fidelity tables, concise plots, and a few transparently selected borrower examples. Include counterexamples if findings are mixed.

Perturbation measures model sensitivity, not causal effects. Replacing correlated financial features independently may create unrealistic borrowers; document this limitation. A train-median replacement is a simple baseline, not proof of causal fidelity.

P2 handover: analysis code, SHAP configuration, fixed cohort/background IDs if used, explanation arrays, metric definitions, per-borrower results, summary tables/figures, and limitations.

## 5. P3: research integration and final handover

Before results are seen:

- Verify the papers referenced in the JPEG. Build a literature matrix containing full citation/link, dataset, explanation method, reliability measure, experimental controls, findings, and limitations.
- Finalize the gap statement without claiming that SHAP stability is unstudied.
- Record research questions, hypotheses, model protocol, and P2 analysis definitions.
- Define what will count as similar predictive performance and how H1 will be assessed; justify any numerical tolerance rather than choosing it after seeing results. If no justified threshold is available, analyze performance differences continuously and avoid equivalence claims.

After P1/P2 results:

- Write Methods from the actual configuration and saved artifacts.
- Integrate predictive performance with rank stability, attribution stability, and fidelity results.
- Discuss evidence for or against each hypothesis; do not assume all hypotheses succeed.
- Explain the single-dataset/fixed-split scope, limited seeds, historical data, imbalance treatment, calibration, and perturbation limitations.
- Ensure every novelty claim is supported by literature and experiments.

Final handover should include:

1. What was implemented and what remains incomplete.
2. Exact setup/run commands and the artifact map.
3. Dataset/split/model/SHAP choices and their reasons.
4. Verified metrics and links to the generated tables and figures.
5. Checks performed and any unresolved issues.
6. A short plain-language explanation suitable for a college presentation or viva.

## 6. Definition of done

The full project is complete only when it contains one reproducible credit model family, the same borrowers explained across controlled runs, all three quantitative explanation-reliability measures, predictive-performance comparisons, concise figures/tables, and a research write-up grounded in observed evidence.

The intended distinction is between having an explanation and having a reliable explanation. Whether the experiments support that distinction, and to what degree, must come from the results.
