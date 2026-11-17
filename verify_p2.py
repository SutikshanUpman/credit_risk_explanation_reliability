"""Independent checks of the P2 outputs. Run from the project root:

    python verify_p2.py                    # run all checks, write outputs/p2/verification_p2.txt
    python verify_p2.py --write-manifest   # also (re)write outputs/p2/manifest_p2.json with file hashes

Where possible a result is recomputed with different, deliberately plain code (Python loops,
scipy.stats.spearmanr) on a random sample of borrowers and compared with the saved tables.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent
P1, P2 = ROOT / "outputs/p1", ROOT / "outputs/p2"
SEEDS = [11, 22, 33, 44, 55]
RUNS = [f"{c}_seed{s}" for c in ("unweighted", "weighted") for s in SEEDS]
NEAR_ZERO = 1e-3
LOG = []


def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    line = f"{status}: {name}" + (f"  [{detail}]" if detail else "")
    print(line, flush=True)
    LOG.append(line)
    if not condition:
        raise AssertionError(line)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()
    import shap

    kw = dict(index_col="borrower_id", float_precision="round_trip")
    schema = json.loads((P1 / "feature_schema.json").read_text())
    features, medians = schema["features"], np.array([schema["imputation_medians"][f] for f in schema["features"]])
    X_test = pd.read_csv(P1 / "processed/X_test.csv", **kw)
    X_train = pd.read_csv(P1 / "processed/X_train.csv", **kw)
    ids = X_test.index.to_numpy()

    # ---- 1. P1 inputs untouched ----
    manifest1 = json.loads((P1 / "manifest.json").read_text())
    bad = [n for n, h in manifest1["artifact_sha256"].items() if sha256(P1 / n) != h]
    check("P1 artifact hashes unchanged", not bad, f"{len(manifest1['artifact_sha256'])} files")
    check("training medians in schema equal medians of X_train", np.allclose(X_train.median().to_numpy(), medians, rtol=0, atol=1e-9))

    # ---- 2. cohort and background ----
    cohort = pd.read_csv(P2 / "cohort_ids.csv").iloc[:, 0].to_numpy()
    check("cohort = all 30,013 held-out rows in saved order", len(cohort) == 30013 and (cohort == ids).all())
    background_ids = pd.read_csv(P2 / "background_ids.csv").iloc[:, 0].to_numpy()
    check("background: 100 unique training rows, none from the test cohort",
          len(set(background_ids)) == 100 and set(background_ids) <= set(X_train.index) and not set(background_ids) & set(ids))
    check("background reproducible from seed 2026",
          (X_train.sample(100, random_state=2026).index.to_numpy() == background_ids).all())

    # ---- 3. explanation arrays ----
    rng = np.random.default_rng(99)
    sample_rows = np.sort(rng.choice(len(ids), 300, replace=False))
    background = X_train.loc[background_ids]
    values = {}
    for run in RUNS:
        data = np.load(P2 / "explanations" / f"{run}.npz")
        values[run] = data["shap"]
        check(f"{run}: ids/shape/finite", (data["borrower_id"] == ids).all() and data["shap"].shape == (30013, 10)
              and np.isfinite(data["shap"]).all())
        booster = xgb.Booster()
        booster.load_model(P1 / "runs" / run / "model.ubj")
        booster.set_param({"nthread": 1})
        margin = booster.predict(xgb.DMatrix(X_test, feature_names=features), output_margin=True)
        error = np.abs(data["shap"].sum(axis=1) + float(data["expected_value"]) - margin).max()
        check(f"{run}: SHAP additivity on raw margin", error < 1e-4, f"max error {error:.2e}")
        native_error = np.abs(data["native_shap"].sum(axis=1) + data["native_bias"] - margin).max()
        check(f"{run}: native contribution additivity", native_error < 1e-4, f"max error {native_error:.2e}")
        saved = pd.read_csv(P1 / "runs" / run / "predictions.csv", float_precision="round_trip")
        check(f"{run}: ids and probabilities equal P1 predictions", (saved["borrower_id"].to_numpy() == ids).all()
              and np.abs(data["probability"] - saved["probability"].to_numpy()).max() < 2e-7)  # P1 used 1e-7 on Windows; 2e-7 = ~2 float32 steps near 1, allows cross-platform rounding
        # fresh recomputation of SHAP for 300 random rows, different batch composition
        explainer = shap.TreeExplainer(booster, data=background, feature_perturbation="interventional", model_output="raw")
        fresh = explainer.shap_values(X_test.iloc[sample_rows])
        check(f"{run}: recomputed SHAP for 300 random rows matches saved", np.abs(fresh - data["shap"][sample_rows]).max() < 1e-6,
              f"max diff {np.abs(fresh - data['shap'][sample_rows]).max():.2e}")

    # ---- 4. rank stability recomputed with scipy / plain loops ----
    rank = pd.read_csv(P2 / "rank_stability.csv.gz")
    check("rank table size = 25 comparisons x 30,013 borrowers", len(rank) == 25 * 30013)
    check("comparison families: 20 within (10 per condition) + 5 between",
          rank.groupby(["family", "condition"])[["run_a", "run_b"]].apply(lambda g: len(g.drop_duplicates())).to_dict()
          == {("between", "unweighted_vs_weighted"): 5, ("within", "unweighted"): 10, ("within", "weighted"): 10})
    index_of = {b: i for i, b in enumerate(ids)}
    probe = rank.sample(3000, random_state=1)
    worst = {"spearman": 0.0, "top3": 0.0, "top5": 0.0}
    for row in probe.itertuples():
        i = index_of[row.borrower_id]
        a, b = np.abs(values[row.run_a][i]), np.abs(values[row.run_b][i])
        rho = spearmanr(a, b)[0] if a.std() > 0 and b.std() > 0 else np.nan
        if np.isnan(rho) or np.isnan(row.spearman):
            check("undefined Spearman flagged consistently", np.isnan(rho) and np.isnan(row.spearman))
        else:
            worst["spearman"] = max(worst["spearman"], abs(rho - row.spearman))
        for k in (3, 5):
            top_a = {j for j in sorted(range(10), key=lambda j: (-a[j], j))[:k]}
            top_b = {j for j in sorted(range(10), key=lambda j: (-b[j], j))[:k]}
            worst[f"top{k}"] = max(worst[f"top{k}"], abs(len(top_a & top_b) / k - getattr(row, f"top{k}_agreement")))
    check("3,000 random rank rows recomputed independently (Spearman, top-3, top-5)", max(worst.values()) < 1e-9, str(worst))
    check("Spearman and agreement values within valid ranges",
          rank["spearman"].dropna().between(-1 - 1e-9, 1 + 1e-9).all() and rank["top3_agreement"].between(0, 1).all()
          and rank["top5_agreement"].between(0, 1).all())

    # ---- 5. attribution stability recomputed in plain python ----
    attr = pd.read_csv(P2 / "attribution_stability.csv.gz")
    check("attribution table size = 30,013 x 10 features x 2 conditions", len(attr) == 600260)
    worst = 0.0
    for row in attr.sample(1500, random_state=2).itertuples():
        i, j = index_of[row.borrower_id], features.index(row.feature)
        s = np.array([values[f"{row.condition}_seed{seed}"][i, j] for seed in SEEDS])
        n_pos, n_neg = int((s > NEAR_ZERO).sum()), int((s < -NEAR_ZERO).sum())
        consistency = max(n_pos, n_neg) / (n_pos + n_neg) if n_pos + n_neg else np.nan
        cv = np.abs(s).std(ddof=1) / np.abs(s).mean() if np.abs(s).mean() >= NEAR_ZERO else np.nan
        pairs = [(s.std(ddof=1), row.signed_sd), (n_pos / 5, row.frac_positive), (n_neg / 5, row.frac_negative),
                 (consistency, row.sign_consistency), (cv, row.magnitude_cv)]
        for expected, got in pairs:
            if np.isnan(expected) or np.isnan(got):
                check("masked/undefined values agree", np.isnan(expected) and np.isnan(got))
            else:
                worst = max(worst, abs(expected - got))
    check("1,500 random attribution rows recomputed independently", worst < 1e-9, f"max diff {worst:.2e}")
    check("fractions of signs sum to 1", np.allclose(attr[["frac_positive", "frac_negative", "frac_near_zero"]].sum(axis=1), 1))

    # ---- 6. weighting change ----
    weight = pd.read_csv(P2 / "weighting_change.csv.gz")
    check("weighting table size = 5 seeds x 30,013 x 10", len(weight) == 5 * 30013 * 10)
    check("diff = weighted - unweighted and abs diff consistent",
          np.allclose(weight["diff_signed"], weight["shap_weighted"] - weight["shap_unweighted"], atol=1e-12)
          and np.allclose(weight["diff_abs"], weight["diff_signed"].abs()))

    # ---- 7. fidelity recomputed with a plain loop on 200 borrowers per run ----
    fid = pd.read_csv(P2 / "fidelity.csv.gz")
    check("fidelity table size = 10 runs x 2 k x 30,013", len(fid) == 10 * 2 * 30013)
    worst = 0.0
    sample_ids = ids[np.sort(rng.choice(len(ids), 200, replace=False))]
    for run in RUNS:
        booster = xgb.Booster()
        booster.load_model(P1 / "runs" / run / "model.ubj")
        booster.set_param({"nthread": 1})
        for k in (3, 5):
            table = fid[(fid["run"] == run) & (fid["k"] == k)].set_index("borrower_id")
            for borrower in sample_ids:
                i = index_of[borrower]
                order = sorted(range(10), key=lambda j: (-abs(values[run][i, j]), j))
                base = X_test.iloc[i].to_numpy(dtype=float)
                p0 = booster.predict(xgb.DMatrix(base.reshape(1, -1), feature_names=features))[0]
                for arm, chosen in (("high", order[:k]), ("low", order[-k:])):
                    x = base.copy()
                    changed = 0
                    for j in chosen:
                        changed += int(x[j] != medians[j])
                        x[j] = medians[j]
                    p1 = booster.predict(xgb.DMatrix(x.reshape(1, -1), feature_names=features))[0]
                    worst = max(worst, abs(abs(p1 - p0) - table.loc[borrower, f"{arm}_prob_change"]))
                    check_changed = table.loc[borrower, f"{arm}_n_changed"] == changed
                    if not check_changed:
                        check("n_changed matches plain-loop count", False, f"{run} k={k} {borrower} {arm}")
    check("fidelity recomputed independently for 200 borrowers x 10 runs x 2 k x 2 arms", worst < 1e-6, f"max diff {worst:.2e}")
    check("no-op flag equals (n_changed == 0)",
          ((fid["high_n_changed"] == 0) == fid["high_noop"]).all() and ((fid["low_n_changed"] == 0) == fid["low_noop"]).all())
    check("diff = high - low", np.allclose(fid["diff_prob"], fid["high_prob_change"] - fid["low_prob_change"], atol=1e-6))  # float32-derived columns

    # ---- 8. summaries and deliverables exist; overlap file is what the sensitivity used ----
    overlap = pd.read_csv(ROOT / "outputs/p1_review_overlap_test_ids.csv")
    check("overlap list has 99 test rows", len(overlap) == 99 and overlap["borrower_id"].isin(ids).all())
    required = ["analysis_protocol.md", "rank_stability_summary.csv", "attribution_stability_summary.csv",
                "weighting_change_summary.csv", "fidelity_summary.csv", "performance_vs_reliability.csv", "examples.md",
                "examples.csv", "sensitivity_path_dependent_rank_summary.csv", "sensitivity_overlap_excluded_rank_summary.csv",
                "sensitivity_overlap_excluded_fidelity_summary.csv", "figures/fig1_rank_stability.png",
                "figures/fig2_global_importance.png", "figures/fig3_fidelity.png", "figures/fig4_performance_vs_reliability.png"]
    missing = [name for name in required if not (P2 / name).exists()]
    check("all expected P2 deliverables exist", not missing, str(missing))
    protocol_time = (P2 / "analysis_protocol.md").stat().st_mtime
    first_result = min((P2 / "explanations" / f"{r}.npz").stat().st_mtime for r in RUNS)
    check("protocol file is older than every explanation array (mtime)", protocol_time < first_result)

    (P2 / "verification_p2.txt").write_text("\n".join(LOG) + "\n\nAll checks passed.\n")
    if args.write_manifest:
        files = sorted(p for p in P2.rglob("*") if p.is_file() and p.name not in ("manifest_p2.json", "verification_p2.txt"))
        manifest = {"files_sha256": {str(p.relative_to(P2)): sha256(p) for p in files},
                    "versions": {"python": sys.version.split()[0], "numpy": np.__version__, "pandas": pd.__version__,
                                 "shap": shap.__version__, "xgboost": xgb.__version__}}
        (P2 / "manifest_p2.json").write_text(json.dumps(manifest, indent=2))
        print("manifest written")
    print("ALL P2 CHECKS PASSED")


if __name__ == "__main__":
    main()
