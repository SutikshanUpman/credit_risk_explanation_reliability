"""Verify P1 artifacts from disk without fitting any models or changing results."""

import argparse
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from xgboost import XGBClassifier

from run_p1 import (
    ROOT, MODEL_SETTINGS, SEEDS, SPLIT_SEED, TARGET, THRESHOLD, TOLERANCE,
    evaluate, load_data, profile_groups, sha256,
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read_matrix(path):
    return pd.read_csv(path, index_col="borrower_id", float_precision="round_trip")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="outputs/p1")
    output = (ROOT / parser.parse_args().output).resolve()
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    require(manifest["status"] == "complete", "P1 has not finished.")
    for name, expected_hash in manifest["source_sha256"].items():
        require(sha256(ROOT / name) == expected_hash, f"Source changed: {name}")
    for name, expected_hash in manifest["artifact_sha256"].items():
        require(sha256(output / name) == expected_hash, f"Artifact changed: {name}")
    print("PASS: source and artifact hashes", flush=True)

    _, cleaned, y, _ = load_data()
    schema = json.loads((output / "feature_schema.json").read_text(encoding="utf-8"))
    features = schema["features"]
    require(features == list(cleaned.columns), "Feature order differs from original inputs.")
    require(TARGET not in features and "borrower_id" not in features, "Label or ID leakage.")
    train_ids = pd.read_csv(output / "splits/train_ids.csv").set_index("borrower_id")
    test_ids = pd.read_csv(output / "splits/test_ids.csv").set_index("borrower_id")
    require(train_ids.index.is_unique and test_ids.index.is_unique, "Repeated borrower IDs.")
    require(not set(train_ids.index) & set(test_ids.index), "Overlapping borrower IDs.")
    require(set(train_ids.index) | set(test_ids.index) == set(cleaned.index), "Missing or extra borrowers.")
    groups = profile_groups(cleaned)
    require(not set(groups.loc[train_ids.index]) & set(groups.loc[test_ids.index]), "Overlapping cleaned profiles.")
    for saved_ids in [train_ids, test_ids]:
        np.testing.assert_array_equal(saved_ids.profile_group, groups.loc[saved_ids.index])
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SPLIT_SEED)
    train_pos, test_pos = next(splitter.split(cleaned, y, groups))
    np.testing.assert_array_equal(train_ids.index, cleaned.iloc[train_pos].sort_index().index)
    np.testing.assert_array_equal(test_ids.index, cleaned.iloc[test_pos].sort_index().index)

    imputer = joblib.load(output / "processed/preprocessor.joblib")
    np.testing.assert_allclose(imputer.statistics_, cleaned.loc[train_ids.index].median().values, rtol=0, atol=0)
    np.testing.assert_array_equal(imputer.feature_names_in_, features)
    np.testing.assert_allclose(list(schema["imputation_medians"].values()), imputer.statistics_, rtol=0, atol=0)
    for name, ids in [("train", train_ids), ("test", test_ids)]:
        X = read_matrix(output / f"processed/X_{name}.csv")
        labels = read_matrix(output / f"processed/y_{name}.csv")
        np.testing.assert_array_equal(X.index, ids.index)
        np.testing.assert_array_equal(labels.index, ids.index)
        np.testing.assert_array_equal(labels[TARGET], y.loc[ids.index])
        require(list(X.columns) == features, "Processed feature order differs.")
        np.testing.assert_allclose(X.values, imputer.transform(cleaned.loc[ids.index]), rtol=0, atol=1e-10)
        require(np.isfinite(X.values).all(), "Nonfinite processed values.")
    X_test = read_matrix(output / "processed/X_test.csv")
    y_test = y.loc[X_test.index]
    weight = float((y.loc[train_ids.index] == 0).sum() / (y.loc[train_ids.index] == 1).sum())
    require(weight == manifest["positive_class_weight"], "Incorrect class weight.")
    print("PASS: recreated split, group separation, labels, feature order, training-only preprocessing", flush=True)

    expected_runs = {f"{condition}_seed{seed}" for condition in ["unweighted", "weighted"] for seed in SEEDS}
    require({path.name for path in (output / "runs").iterdir()} == expected_runs, "Unexpected run set.")
    all_metrics = pd.read_csv(output / "metrics_all_runs.csv", float_precision="round_trip").set_index("run_id")
    require(all_metrics.index.is_unique and set(all_metrics.index) == expected_runs, "Wrong metrics run IDs.")
    for run_id in sorted(expected_runs):
        folder = output / "runs" / run_id
        config = json.loads((folder / "config.json").read_text(encoding="utf-8"))
        condition, seed_text = run_id.split("_seed")
        seed = int(seed_text)
        expected_settings = {**MODEL_SETTINGS, "random_state": seed, "scale_pos_weight": weight if condition == "weighted" else 1.0}
        require(config["model_settings"] == expected_settings, f"Unexpected settings: {run_id}")
        require(config["threshold"] == THRESHOLD, "Unexpected threshold.")
        model = XGBClassifier()
        model.load_model(folder / "model.ubj")
        require(model.get_booster().feature_names == features, "Model feature order differs.")
        require(model.get_booster().num_boosted_rounds() == MODEL_SETTINGS["n_estimators"], "Wrong tree count.")
        probabilities = model.predict_proba(X_test)[:, 1]
        require(np.isfinite(probabilities).all() and ((probabilities >= 0) & (probabilities <= 1)).all(), "Invalid probabilities.")
        predictions = read_matrix(folder / "predictions.csv")
        np.testing.assert_array_equal(predictions.index, X_test.index)
        np.testing.assert_array_equal(predictions.y_true, y_test)
        np.testing.assert_array_equal(predictions.predicted_class, probabilities >= THRESHOLD)
        np.testing.assert_allclose(predictions.probability, probabilities, rtol=0, atol=TOLERANCE)
        metrics = evaluate(y_test, probabilities)
        saved_metrics = json.loads((folder / "metrics.json").read_text(encoding="utf-8"))
        for name, value in metrics.items():
            np.testing.assert_allclose(saved_metrics[name], value, rtol=0, atol=1e-12)
            np.testing.assert_allclose(all_metrics.loc[run_id, name], value, rtol=0, atol=1e-12)
        require(all_metrics.loc[run_id, "condition"] == condition and all_metrics.loc[run_id, "seed"] == seed, "Wrong run metadata.")
        print(f"PASS: {run_id} reload, predictions, metrics", flush=True)

    expected_summary = all_metrics.groupby("condition")[list(metrics)].agg(["mean", "std"])
    expected_summary.columns = [f"{name}_{stat}" for name, stat in expected_summary.columns]
    saved_summary = pd.read_csv(output / "metrics_summary.csv", index_col="condition", float_precision="round_trip")
    pd.testing.assert_frame_equal(saved_summary, expected_summary, check_exact=False, rtol=0, atol=1e-12)
    print("PASS: condition summaries. P1 disk-artifact verification complete; no explanation hypotheses were tested.", flush=True)


if __name__ == "__main__":
    main()
