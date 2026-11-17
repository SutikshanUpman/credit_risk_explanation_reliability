"""One controlled data split, two loss-weight conditions, five seeds, ten models."""

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone
from time import perf_counter

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    average_precision_score, brier_score_loss, confusion_matrix, f1_score,
    log_loss, precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import StratifiedGroupKFold
from xgboost import XGBClassifier


ROOT = Path(__file__).resolve().parent
TARGET = "SeriousDlqin2yrs"
SEEDS = [11, 22, 33, 44, 55]
SPLIT_SEED = 42
THRESHOLD = 0.5
TOLERANCE = 1e-7
MODEL_SETTINGS = {
    "objective": "binary:logistic", "n_estimators": 300, "max_depth": 4,
    "learning_rate": 0.05, "subsample": 0.8, "colsample_bytree": 0.8,
    "tree_method": "hist", "device": "cpu", "n_jobs": 4,
    "min_child_weight": 1, "gamma": 0, "reg_alpha": 0, "reg_lambda": 1,
    "max_bin": 256, "eval_metric": "logloss", "verbosity": 0,
    # Fix the initial probability too, so automatic intercept estimation is not a confound.
    "base_score": 0.5,
}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_data():
    frame = pd.read_csv(ROOT / "Data/cs-training.csv", float_precision="round_trip")
    frame = frame.rename(columns={frame.columns[0]: "borrower_id"}).set_index("borrower_id")
    if not frame.index.is_unique or frame.index.hasnans:
        raise ValueError("Borrower IDs must be present and unique.")
    if frame[TARGET].isna().any() or set(frame[TARGET].unique()) != {0, 1}:
        raise ValueError("Expected complete binary training labels.")
    y = frame[TARGET].astype(int)
    raw = frame.drop(columns=TARGET)
    dictionary = pd.read_excel(ROOT / "Data/Data Dictionary.xls", header=1)
    definitions = {
        row["Variable Name"]: {"description": row["Description"].strip(), "type": row["Type"]}
        for _, row in dictionary.dropna(subset=["Variable Name"]).iterrows()
    }
    if set(raw.columns) != set(definitions) - {TARGET} or len(raw.columns) != 10:
        raise ValueError("Predictor schema does not match the local dictionary.")
    if not all(pd.api.types.is_numeric_dtype(raw[name]) for name in raw):
        raise ValueError("This experiment expects ten numeric predictors.")
    if np.isinf(raw.to_numpy()).any():
        raise ValueError("Infinite inputs require an explicit cleaning decision.")
    cleaned = raw.copy()
    # Zero/negative age cannot describe an adult borrower; no other outlier rule is assumed.
    cleaned.loc[cleaned["age"] <= 0, "age"] = np.nan
    return raw, cleaned, y, definitions


def profile_groups(features):
    # Group exact profiles, including shared missing values; IDs and labels are excluded.
    return features.groupby(list(features.columns), dropna=False, sort=False).ngroup()


def evaluate(y, probabilities):
    predicted = (probabilities >= THRESHOLD).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, predicted, labels=[0, 1]).ravel()
    return {
        "roc_auc": float(roc_auc_score(y, probabilities)),
        "average_precision": float(average_precision_score(y, probabilities)),
        "log_loss": float(log_loss(y, probabilities, labels=[0, 1])),
        "brier_score": float(brier_score_loss(y, probabilities)),
        "precision": float(precision_score(y, predicted, zero_division=0)),
        "recall": float(recall_score(y, predicted, zero_division=0)),
        "f1": float(f1_score(y, predicted, zero_division=0)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def audit_data(raw, cleaned, y):
    raw_groups = profile_groups(raw)
    cleaned_groups = profile_groups(cleaned)
    counts = raw_groups.value_counts()
    conflicts = y.groupby(raw_groups).nunique()
    delinquency = [name for name in raw if "PastDue" in name or "90DaysLate" in name]
    return {
        "rows": len(raw), "predictors": len(raw.columns),
        "dtypes": raw.dtypes.astype(str).to_dict(),
        "class_counts": {str(k): int(v) for k, v in y.value_counts().sort_index().items()},
        "positive_rate": float(y.mean()),
        "missing_counts": raw.isna().sum().astype(int).to_dict(),
        "missing_percent": (100 * raw.isna().mean()).to_dict(),
        "exact_duplicate_rows_excluding_id_beyond_first": int(pd.concat([raw, y], axis=1).duplicated().sum()),
        "unique_raw_profiles": int(raw_groups.nunique()),
        "repeated_raw_profile_groups": int((counts > 1).sum()),
        "rows_in_repeated_raw_profiles": int(counts[counts > 1].sum()),
        "raw_profiles_with_conflicting_labels": int((conflicts > 1).sum()),
        "unique_cleaned_profiles": int(cleaned_groups.nunique()),
        "nonpositive_age_set_missing": int((raw.age <= 0).sum()),
        "age_above_100_retained": int((raw.age > 100).sum()),
        "utilization_above_one_retained": int((raw.RevolvingUtilizationOfUnsecuredLines > 1).sum()),
        "debt_ratio_above_one_retained": int((raw.DebtRatio > 1).sum()),
        "delinquency_counts_at_least_90_retained": {
            name: raw.loc[raw[name] >= 90, name].value_counts().sort_index().to_dict()
            for name in delinquency
        },
        "numeric_summary": raw.describe(percentiles=[0.01, 0.5, 0.99]).to_dict(),
        "policy": "Retain rows and extremes. Set age <= 0 missing; training-median imputation. No clipping, scaling, or feature selection.",
    }


def dataset_card(audit, definitions):
    features = "\n".join(f"| {name} | {item['description']} | {item['type']} |" for name, item in definitions.items())
    return f"""# Dataset card

Source: [Give Me Some Credit](https://www.kaggle.com/c/GiveMeSomeCredit/data), Credit Fusion and Will Cukierski, Kaggle (2011). Use is subject to competition rules. Variable definitions below were read from `Data/Data Dictionary.xls`.

The target `{TARGET}` is a binary indicator of 90-day delinquency or worse within the prediction horizon of two years. It is an operational credit-risk outcome, not a universal definition of default.

Labelled rows: {audit['rows']:,}. Predictors: {audit['predictors']}. Positive rate: {audit['positive_rate']:.4%}. Class counts: {audit['class_counts']}.

| Variable | Dictionary definition | Type |
| --- | --- | --- |
{features}

`borrower_id` is the original row index, retained only for joining artifacts. It is not a predictor or proof of a real person identity. The competition test file is unlabelled; the sample submission is not ground truth. Both are excluded from modelling and evaluation.

## Audit and cleaning

Missing counts: {audit['missing_counts']}.

There are {audit['exact_duplicate_rows_excluding_id_beyond_first']:,} duplicate observations beyond the first when IDs are excluded, {audit['repeated_raw_profile_groups']:,} repeated predictor-profile groups, and {audit['raw_profiles_with_conflicting_labels']:,} profiles with conflicting labels. Rows are retained; identical cleaned predictor profiles are grouped into one split partition. Do not interpret this as confirmed borrower-level identity grouping.

Nonpositive ages set to missing: {audit['nonpositive_age_set_missing']}. Fit median imputation only on training data. Keep all ten original predictors; no scaling, clipping, or extra indicators. Large ratios and delinquency counts (including 96/98 if present) remain because the dictionary does not document a reliable replacement rule. Their possible artifact/sentinel meaning is a limitation, not an established fact.

## Leakage review and limitations

The ID and label are excluded from inputs. Listed predictors describe borrower financial status/history; their precise collection timestamps are not available here, so temporal availability cannot be independently verified. No target-derived features are created. Imputation and loss weights use training rows only; test rows never fit a transformation or select model settings.

This historical competition sample has incomplete provenance and no usable timestamps for temporal validation. Generalization to current borrowers, other lenders, or future periods is untested. Remaining unusual values, missingness, retained repeated observations, and class imbalance can influence the models and explanations. A profile grouping policy cannot guarantee distinct real people across partitions. Post-imputation collisions between previously different profiles are reported separately.
"""


def protocol_text():
    return f"""# P1 experiment protocol (written before model fitting)

Hypotheses from the source plan: H1, predictive similarity need not imply borrower-level explanation similarity; H2, explanation stability can change with training conditions; H3, perturbing high-ranked SHAP features should affect predictions more than low-ranked features. P1 generates model artifacts; it cannot evaluate these explanation hypotheses.

Use the first held-out fold from StratifiedGroupKFold(n_splits=5, shuffle=True, random_state={SPLIT_SEED}); group exact cleaned predictor profiles, with missing values equal for grouping. Keep this split fixed. This is not five-fold performance evaluation. Sort both partitions by borrower ID. Do not tune or select a best model using held-out metrics.

Set age <= 0 missing, retain other unusual values, fit training-only median imputation once. Preserve all ten features and their original order. No validation-based early stopping or threshold tuning.

Model settings: `{json.dumps(MODEL_SETTINGS, sort_keys=True)}`.

Seeds: {SEEDS}. Conditions: unweighted (`scale_pos_weight=1`) and weighted (`training negatives / training positives`). Pair equal seeds. Training rows stay identical: this tests randomness and loss weighting, not SMOTE or bootstrap/resampling. Fixed base_score=0.5 ensures both conditions start from the same intercept. Save every model.

Evaluate ROC-AUC, average precision, log loss, Brier score, precision/recall/F1 and confusion counts. Classification threshold: {THRESHOLD}; it is a reporting convention. Summaries use mean and sample standard deviation over five seeds, not population confidence intervals. Verify model reloads with absolute probability tolerance {TOLERANCE}, relative tolerance zero.

P2/P3 decisions still required before explanation analysis: TreeSHAP mode/scale/background, borrower cohort, top-k/tie handling, near-zero CV handling, and perturbation procedure. The plan suggests raw-margin explanations and k=3,5. P1 does not silently freeze these decisions on P2's behalf. H1 should use continuous predictive-performance differences unless a justified equivalence threshold is defined before analysis. No novelty claim is established by predictive performance.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="outputs/p1", help="New or empty output folder")
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    if output.exists() and any(output.iterdir()):
        parser.error(f"Output folder is not empty: {output}. Use a new --output path.")
    output.mkdir(parents=True, exist_ok=True)
    for name in ["splits", "processed", "runs"]:
        (output / name).mkdir()

    source_names = ["Data/cs-training.csv", "Data/cs-test.csv", "Data/sampleEntry.csv", "Data/Data Dictionary.xls", "Plan.jpeg", "plan.md", "instructions.md", "run_p1.py", "verify_p1.py", "requirements.txt"]
    sources = {name: sha256(ROOT / name) for name in source_names}
    manifest = {
        "status": "in_progress", "started_utc": datetime.now(timezone.utc).isoformat(),
        "source_sha256": sources, "python": sys.version, "platform": platform.platform(),
        "processor": platform.processor(), "logical_cpus": os.cpu_count(),
        "packages": {name: importlib.metadata.version(name) for name in ["numpy", "pandas", "scipy", "scikit-learn", "xgboost", "joblib", "xlrd"]},
        "split_seed": SPLIT_SEED, "model_seeds": SEEDS, "threshold": THRESHOLD,
        "probability_absolute_tolerance": TOLERANCE,
    }
    write_json(output / "manifest.json", manifest)
    freeze = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
    (output / "environment_versions.txt").write_text(freeze, encoding="utf-8")
    raw, cleaned, y, definitions = load_data()
    audit = audit_data(raw, cleaned, y)
    competition_test = pd.read_csv(ROOT / "Data/cs-test.csv")
    audit["competition_test_rows"] = len(competition_test)
    audit["competition_test_labelled_rows"] = int(competition_test[TARGET].notna().sum())
    if audit["competition_test_labelled_rows"]:
        raise ValueError("Expected the original unlabelled competition test file.")

    groups = profile_groups(cleaned)
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SPLIT_SEED)
    train_pos, test_pos = next(splitter.split(cleaned, y, groups))
    train_raw = cleaned.iloc[train_pos].sort_index()
    test_raw = cleaned.iloc[test_pos].sort_index()
    y_train, y_test = y.loc[train_raw.index], y.loc[test_raw.index]
    if set(train_raw.index) & set(test_raw.index) or set(groups.loc[train_raw.index]) & set(groups.loc[test_raw.index]):
        raise AssertionError("Train/test separation failed.")
    for name, frame, labels in [("train", train_raw, y_train), ("test", test_raw, y_test)]:
        pd.DataFrame({"borrower_id": frame.index, "profile_group": groups.loc[frame.index].values}).to_csv(output / f"splits/{name}_ids.csv", index=False)
        manifest[name] = {"rows": len(frame), "positives": int(labels.sum()), "positive_rate": float(labels.mean())}
    manifest["split_method"] = "First fold of StratifiedGroupKFold(5, shuffle=True, random_state=42), grouped by exact cleaned profiles"

    imputer = SimpleImputer(strategy="median")
    X_train = pd.DataFrame(imputer.fit_transform(train_raw), index=train_raw.index, columns=raw.columns)
    X_test = pd.DataFrame(imputer.transform(test_raw), index=test_raw.index, columns=raw.columns)
    np.testing.assert_allclose(imputer.statistics_, train_raw.median().values, rtol=0, atol=0)
    if not np.isfinite(X_train.to_numpy()).all() or not np.isfinite(X_test.to_numpy()).all():
        raise AssertionError("Processed values must be finite.")
    # Report, rather than conceal, profiles that become equal only after imputation.
    processed_groups = profile_groups(pd.concat([X_train, X_test]).sort_index())
    audit["post_imputation_profiles_shared_across_partitions"] = len(set(processed_groups.loc[X_train.index]) & set(processed_groups.loc[X_test.index]))
    for name, features, labels in [("train", X_train, y_train), ("test", X_test, y_test)]:
        features.to_csv(output / f"processed/X_{name}.csv")
        labels.to_csv(output / f"processed/y_{name}.csv")
    joblib.dump(imputer, output / "processed/preprocessor.joblib")
    write_json(output / "feature_schema.json", {
        "id_column": "borrower_id", "target": TARGET, "features": list(raw.columns),
        "definitions": definitions, "imputation_medians": dict(zip(raw.columns, imputer.statistics_)),
    })
    write_json(output / "data_audit.json", audit)
    (output / "dataset_card.md").write_text(dataset_card(audit, definitions), encoding="utf-8")
    (output / "experiment_protocol.md").write_text(protocol_text(), encoding="utf-8")
    manifest["protocol_saved_before_training_utc"] = datetime.now(timezone.utc).isoformat()
    write_json(output / "manifest.json", manifest)
    print(f"Prepared {len(X_train):,} training / {len(X_test):,} held-out rows; positive rates {y_train.mean():.4%} / {y_test.mean():.4%}", flush=True)

    weight = float((y_train == 0).sum() / (y_train == 1).sum())
    results = []
    for condition, positive_weight in [("unweighted", 1.0), ("weighted", weight)]:
        for seed in SEEDS:
            run_id = f"{condition}_seed{seed}"
            folder = output / "runs" / run_id
            folder.mkdir()
            model = XGBClassifier(**MODEL_SETTINGS, random_state=seed, scale_pos_weight=positive_weight)
            started = perf_counter()
            model.fit(X_train, y_train)
            elapsed = perf_counter() - started
            probabilities = model.predict_proba(X_test)[:, 1]
            if not np.isfinite(probabilities).all() or not ((probabilities >= 0) & (probabilities <= 1)).all():
                raise AssertionError("Invalid probabilities.")
            metrics = evaluate(y_test, probabilities)
            model.save_model(folder / "model.ubj")
            reloaded = XGBClassifier()
            reloaded.load_model(folder / "model.ubj")
            np.testing.assert_allclose(reloaded.predict_proba(X_test)[:, 1], probabilities, rtol=0, atol=TOLERANCE)
            pd.DataFrame({"borrower_id": X_test.index, "y_true": y_test.values,
                          "probability": probabilities.astype(float),
                          "predicted_class": (probabilities >= THRESHOLD).astype(int)}).to_csv(folder / "predictions.csv", index=False)
            write_json(folder / "config.json", {
                "run_id": run_id, "condition": condition, "seed": seed,
                "model_settings": {**MODEL_SETTINGS, "random_state": seed, "scale_pos_weight": positive_weight},
                "training_seconds": elapsed, "threshold": THRESHOLD,
                "feature_schema": "../../feature_schema.json", "test_ids": "../../splits/test_ids.csv",
                "training_source_sha256": sources["Data/cs-training.csv"],
            })
            (folder / "effective_config.json").write_text(model.get_booster().save_config() + "\n", encoding="utf-8")
            write_json(folder / "metrics.json", metrics)
            results.append({"run_id": run_id, "condition": condition, "seed": seed, "training_seconds": elapsed, **metrics})
            print(f"{run_id}: ROC-AUC={metrics['roc_auc']:.5f}, AP={metrics['average_precision']:.5f}, {elapsed:.1f}s", flush=True)

    all_metrics = pd.DataFrame(results)
    all_metrics.to_csv(output / "metrics_all_runs.csv", index=False)
    metric_names = list(metrics)
    summary = all_metrics.groupby("condition")[metric_names].agg(["mean", "std"])
    summary.columns = [f"{name}_{stat}" for name, stat in summary.columns]
    summary.to_csv(output / "metrics_summary.csv")
    if sources != {name: sha256(ROOT / name) for name in source_names}:
        raise AssertionError("A source file changed during execution.")
    manifest["checks"] = {"split_ids_disjoint": True, "cleaned_profile_groups_disjoint": True,
                          "training_only_medians": True, "all_model_reload_predictions_match": True,
                          "source_files_unchanged": True, "run_count": len(results)}
    manifest["positive_class_weight"] = weight
    manifest["status"] = "complete"
    manifest["completed_utc"] = datetime.now(timezone.utc).isoformat()
    write_handover(output, manifest, audit, summary)
    manifest["artifact_sha256"] = {path.relative_to(output).as_posix(): sha256(path)
                                   for path in sorted(output.rglob("*")) if path.is_file() and path.name != "manifest.json"}
    write_json(output / "manifest.json", manifest)
    print(f"P1 complete: {output}. Run verify_p1.py for an independent disk-artifact check.", flush=True)


def write_handover(output, manifest, audit, summary):
    rows = []
    for condition, row in summary.iterrows():
        values = [f"{row[f'{metric}_mean']:.5f} +/- {row[f'{metric}_std']:.5f}" for metric in ["roc_auc", "average_precision", "log_loss", "brier_score"]]
        rows.append("| " + " | ".join([condition, *values]) + " |")
    text = f"""# P1 handover to P2 and P3

P1 is complete: ten XGBoost models, one fixed held-out population, training-only preprocessing, configurations, predictive metrics, and per-borrower probabilities. P2/P3 explanation analysis and literature integration are not yet completed. No explanation-reliability or novelty finding is claimed.

## Observed setup and results

Training: {manifest['train']['rows']:,} rows, positive rate {manifest['train']['positive_rate']:.4%}. Held-out: {manifest['test']['rows']:,} rows, positive rate {manifest['test']['positive_rate']:.4%}. Loss weight for positives: {manifest['positive_class_weight']:.6f} in weighted runs; 1 in unweighted runs. Five paired seeds: {SEEDS}.

| Condition | ROC-AUC | Average precision | Log loss | Brier score |
| --- | --- | --- | --- | --- |
{chr(10).join(rows)}

Values are mean +/- sample standard deviation across seeds, not confidence intervals. Weighting can trade ranking, calibration, and threshold behaviour; inspect `metrics_all_runs.csv` for precision/recall/F1 and confusion counts. Do not choose a winner using this held-out set. Threshold 0.5 is fixed and not a deployment policy.

## Files to use

- `processed/X_train.csv`, `X_test.csv`, `y_train.csv`, `y_test.csv`: load with `index_col="borrower_id", float_precision="round_trip"`.
- `processed/preprocessor.joblib`: training-fitted median imputer. Model input is the processed matrix, not the raw CSV.
- `feature_schema.json`: exact feature order, dictionary definitions, and training medians.
- `splits/`: frozen borrower IDs and cleaned-profile group IDs.
- `runs/<condition>_seed<seed>/model.ubj`: all ten native models, accompanied by configuration, effective booster configuration, metrics, and predictions.
- `data_audit.json`, `dataset_card.md`, `experiment_protocol.md`, `manifest.json`, `environment_versions.txt`: decisions, provenance, integrity, and environment.

Reproduce from the project root using the README commands and a new output folder. Check saved artifacts with `.\\.venv\\Scripts\\python.exe verify_p1.py --output {output.relative_to(ROOT).as_posix() if output.is_relative_to(ROOT) else output.as_posix()}`.

## Checks and limitations

Training checked ID/group separation, training-only imputer medians, finite inputs/probabilities, unchanged source hashes, and native model reload predictions (absolute tolerance {TOLERANCE}, relative tolerance zero). `verify_p1.py` separately checks artifacts read back from disk, recreates the split/preprocessing, and recomputes every model's metrics. Its console output is the evidence for that separate check; this document does not assume it has run.

Unusual-value policy: {audit['policy']} Post-imputation profiles shared between partitions: {audit['post_imputation_profiles_shared_across_partitions']}. Group separation applies to cleaned profiles before imputation, not verified identities. This experiment uses a single historical dataset and split. It tests randomness and class weighting, not resampling. Potential sentinel values and timestamp uncertainty remain. Neither causal effects nor modern deployment performance have been established.

## P2 next steps

Freeze the TreeSHAP configuration, output scale, cohort, top-k values/ties, and perturbation rules before inspecting explanations. Use all ten models on the same held-out borrower IDs in the same order. Keep a training-only background fixed if the chosen SHAP mode uses one. Check additivity on the declared scale.

Measure per-borrower rank stability (Spearman and top-k overlap), signed attribution variability/sign consistency (guard CV near zero), and high-versus-low feature perturbation sensitivity. Keep within-condition seed comparisons separate from matched-seed weighting comparisons. Pairwise model comparisons are dependent; do not treat them as independent samples. Save explanation arrays with run/borrower/feature mappings, per-borrower metrics, aggregate tables, plots, and transparently selected examples. Perturbation is model sensitivity, not causality.

## P3 next steps

Verify the JPEG's abbreviated citations, complete the literature matrix and gap statement, and confirm the analysis definitions before P2 sees explanation results. Predictive results now exist, so do not claim a later protocol is fully preregistered. For H1, use continuous differences unless an independently justified equivalence rule already exists. Integrate actual P1 and P2 outputs into Methods, Results, Discussion, and Limitations. Describe weighting accurately and report negative/mixed findings. Novelty requires verified literature plus the completed reliability experiments.

## Viva explanation

We keep the people being evaluated fixed, change only training randomness and class weighting, and save every model. This makes it possible for P2 to ask whether similar prediction quality comes with similar feature explanations. P1 provides the controlled comparison; P2 measures explanation reliability; P3 determines what the evidence contributes to existing research.
"""
    (output / "handover.md").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
