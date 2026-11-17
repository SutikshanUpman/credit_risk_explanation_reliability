"""P2: SHAP stability and perturbation-fidelity analysis of the ten saved P1 XGBoost models.

Run from the project root:  python run_p2.py            (all stages, ~20-40 min on one CPU)
                            python run_p2.py --stage explain   (only the slow SHAP step)
                            python run_p2.py --stage analyze   (everything after SHAP)

All choices are frozen in outputs/p2/analysis_protocol.md, written before this script was run.
P1 files are only read, never modified.
"""
import argparse
import itertools
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parent
P1 = ROOT / "outputs/p1"
P2 = ROOT / "outputs/p2"

# ---------------- settings (see analysis_protocol.md) ----------------
SEEDS = [11, 22, 33, 44, 55]
CONDITIONS = ["unweighted", "weighted"]
RUNS = [f"{c}_seed{s}" for c in CONDITIONS for s in SEEDS]
BACKGROUND_SIZE, BACKGROUND_SEED = 100, 2026
ADDITIVITY_TOL = 1e-4
NEAR_ZERO = 1e-3          # log-odds; 100x above float32 additivity error
TOP_KS = [3, 5]
N_BOOT, BOOT_SEED = 2000, 7
SHAP_BATCH = 5000


def load_inputs():
    schema = json.loads((P1 / "feature_schema.json").read_text())
    features, medians = schema["features"], schema["imputation_medians"]
    kw = dict(index_col="borrower_id", float_precision="round_trip")
    X_test = pd.read_csv(P1 / "processed/X_test.csv", **kw)
    X_train = pd.read_csv(P1 / "processed/X_train.csv", **kw)
    y_test = pd.read_csv(P1 / "processed/y_test.csv", **kw)
    assert list(X_test.columns) == features and list(X_train.columns) == features
    assert X_test.index.equals(y_test.index)
    median_vector = np.array([medians[f] for f in features])
    return features, median_vector, X_train, X_test, y_test


def load_booster(run):
    booster = xgb.Booster()
    booster.load_model(P1 / "runs" / run / "model.ubj")
    booster.set_param({"nthread": 1})
    return booster


# ---------------- stage 1: SHAP values ----------------
def explain(features, X_train, X_test):
    import shap

    folder = P2 / "explanations"
    folder.mkdir(parents=True, exist_ok=True)
    background = X_train.sample(BACKGROUND_SIZE, random_state=BACKGROUND_SEED)
    background.index.to_series().to_csv(P2 / "background_ids.csv", index=False)
    X_test.index.to_series().to_csv(P2 / "cohort_ids.csv", index=False)

    dmatrix = xgb.DMatrix(X_test, feature_names=features)
    for run in RUNS:
        target = folder / f"{run}.npz"
        if target.exists():
            print("skip (exists):", target.name)
            continue
        start = time.time()
        booster = load_booster(run)
        explainer = shap.TreeExplainer(booster, data=background,
                                       feature_perturbation="interventional", model_output="raw")
        values = np.vstack([explainer.shap_values(X_test.iloc[i:i + SHAP_BATCH])
                            for i in range(0, len(X_test), SHAP_BATCH)])
        base = float(np.ravel(explainer.expected_value)[0])
        margin = booster.predict(dmatrix, output_margin=True)
        error = np.abs(values.sum(axis=1) + base - margin).max()
        assert error < ADDITIVITY_TOL, f"{run}: additivity error {error}"

        # Sensitivity only: XGBoost's native tree-path-dependent contributions
        native = booster.predict(dmatrix, pred_contribs=True, approx_contribs=False)
        native_error = np.abs(native.sum(axis=1) - margin).max()
        assert native_error < ADDITIVITY_TOL, f"{run}: native additivity error {native_error}"

        np.savez_compressed(target, shap=values, expected_value=base, raw_margin=margin,
                            probability=booster.predict(dmatrix), additivity_error=error,
                            native_shap=native[:, :-1], native_bias=native[:, -1],
                            native_additivity_error=native_error,
                            borrower_id=X_test.index.to_numpy())
        print(f"{run}: SHAP done in {time.time() - start:.0f}s, additivity error {error:.2e}", flush=True)


def load_explanations(ids, key="shap"):
    out = {}
    for run in RUNS:
        with np.load(P2 / "explanations" / f"{run}.npz") as data:
            if not np.array_equal(data["borrower_id"], ids):
                raise ValueError(f"{run}: explanation borrowers differ from the current test cohort")
            out[run] = data[key]
    return out


# ---------------- stage 2: rank metrics ----------------
def rank_ingredients(values):
    """Per-run: average ranks of |SHAP| and top-k membership masks (ties -> feature-schema order)."""
    absolute = np.abs(values)
    ranks = np.apply_along_axis(rankdata, 1, absolute)
    order = np.argsort(-absolute, axis=1, kind="stable")
    masks = {}
    for k in TOP_KS:
        mask = np.zeros(absolute.shape, dtype=bool)
        np.put_along_axis(mask, order[:, :k], True, axis=1)
        masks[k] = mask
    return ranks, masks


def spearman_rows(ranks_a, ranks_b):
    a = ranks_a - ranks_a.mean(axis=1, keepdims=True)
    b = ranks_b - ranks_b.mean(axis=1, keepdims=True)
    denominator = np.sqrt((a ** 2).sum(axis=1) * (b ** 2).sum(axis=1))
    with np.errstate(invalid="ignore", divide="ignore"):
        result = (a * b).sum(axis=1) / denominator
    result[denominator == 0] = np.nan       # constant vector: correlation undefined
    return result


def comparison_pairs():
    pairs = []
    for condition in CONDITIONS:
        for s1, s2 in itertools.combinations(SEEDS, 2):
            pairs.append(("within", condition, f"{condition}_seed{s1}", f"{condition}_seed{s2}"))
    for seed in SEEDS:
        pairs.append(("between", "unweighted_vs_weighted", f"unweighted_seed{seed}", f"weighted_seed{seed}"))
    return pairs


def rank_stability(values_by_run, ids):
    ingredients = {run: rank_ingredients(v) for run, v in values_by_run.items()}
    frames = []
    for family, condition, run_a, run_b in comparison_pairs():
        ranks_a, masks_a = ingredients[run_a]
        ranks_b, masks_b = ingredients[run_b]
        frame = pd.DataFrame({"borrower_id": ids, "family": family, "condition": condition,
                              "run_a": run_a, "run_b": run_b,
                              "spearman": spearman_rows(ranks_a, ranks_b)})
        for k in TOP_KS:
            frame[f"top{k}_agreement"] = (masks_a[k] & masks_b[k]).sum(axis=1) / k
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


# ---------------- stage 3: attribution stability (signed SHAP across seeds) ----------------
def attribution_stability(values_by_run, ids, features):
    frames = []
    for condition in CONDITIONS:
        stack = np.stack([values_by_run[f"{condition}_seed{s}"] for s in SEEDS])  # (5, N, 10)
        absolute = np.abs(stack)
        n_pos = (stack > NEAR_ZERO).sum(axis=0)
        n_neg = (stack < -NEAR_ZERO).sum(axis=0)
        n_zero = len(SEEDS) - n_pos - n_neg
        nonzero = n_pos + n_neg
        with np.errstate(invalid="ignore", divide="ignore"):
            consistency = np.where(nonzero > 0, np.maximum(n_pos, n_neg) / nonzero, np.nan)
            mean_abs = absolute.mean(axis=0)
            cv = absolute.std(axis=0, ddof=1) / mean_abs
        cv_valid = mean_abs >= NEAR_ZERO
        cv = np.where(cv_valid, cv, np.nan)
        for j, feature in enumerate(features):
            frames.append(pd.DataFrame({
                "borrower_id": ids, "feature": feature, "condition": condition,
                "mean_signed": stack[:, :, j].mean(axis=0), "signed_sd": stack[:, :, j].std(axis=0, ddof=1),
                "frac_positive": n_pos[:, j] / len(SEEDS), "frac_negative": n_neg[:, j] / len(SEEDS),
                "frac_near_zero": n_zero[:, j] / len(SEEDS), "sign_consistency": consistency[:, j],
                "mean_abs": mean_abs[:, j], "magnitude_cv": cv[:, j], "cv_valid": cv_valid[:, j]}))
    return pd.concat(frames, ignore_index=True)


def weighting_change(values_by_run, ids, features):
    frames = []
    for seed in SEEDS:
        unweighted = values_by_run[f"unweighted_seed{seed}"]
        weighted = values_by_run[f"weighted_seed{seed}"]
        for j, feature in enumerate(features):
            diff = weighted[:, j] - unweighted[:, j]
            frames.append(pd.DataFrame({"borrower_id": ids, "seed": seed, "feature": feature,
                                        "shap_unweighted": unweighted[:, j], "shap_weighted": weighted[:, j],
                                        "diff_signed": diff, "diff_abs": np.abs(diff)}))
    return pd.concat(frames, ignore_index=True)


# ---------------- stage 4: perturbation fidelity ----------------
def fidelity(values_by_run, ids, features, medians, X_test):
    dmatrix_base = xgb.DMatrix(X_test, feature_names=features)
    X_values = X_test.to_numpy()
    already_median = X_values == medians          # True where replacement would change nothing
    frames = []
    for run in RUNS:
        booster = load_booster(run)
        base_margin = booster.predict(dmatrix_base, output_margin=True)
        base_prob = booster.predict(dmatrix_base)
        order = np.argsort(-np.abs(values_by_run[run]), axis=1, kind="stable")
        for k in TOP_KS:
            record = {"borrower_id": ids, "run": run, "k": k}
            for arm, chosen in (("high", order[:, :k]), ("low", order[:, -k:])):
                mask = np.zeros(X_values.shape, dtype=bool)
                np.put_along_axis(mask, chosen, True, axis=1)
                perturbed = pd.DataFrame(np.where(mask, medians, X_values), columns=features)
                dmatrix = xgb.DMatrix(perturbed, feature_names=features)
                record[f"{arm}_prob_change"] = np.abs(booster.predict(dmatrix) - base_prob)
                record[f"{arm}_margin_change"] = np.abs(booster.predict(dmatrix, output_margin=True) - base_margin)
                changed = (mask & ~already_median).sum(axis=1)
                record[f"{arm}_n_changed"] = changed
                record[f"{arm}_noop"] = changed == 0
            frame = pd.DataFrame(record)
            frame["diff_prob"] = frame["high_prob_change"] - frame["low_prob_change"]
            frame["diff_margin"] = frame["high_margin_change"] - frame["low_margin_change"]
            frames.append(frame)
        print("fidelity done:", run, flush=True)
    return pd.concat(frames, ignore_index=True)


# ---------------- stage 5: summaries ----------------
def boot_ci(values):
    """Percentile bootstrap of the mean over borrowers (sampling unit = borrower; models fixed)."""
    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]
    if not len(values):
        return np.nan, np.nan
    rng = np.random.default_rng(BOOT_SEED)
    means = []
    for start in range(0, N_BOOT, 200):
        batch_size = min(200, N_BOOT - start)
        index = rng.integers(0, len(values), size=(batch_size, len(values)))
        means.append(values[index].mean(axis=1))
    means = np.concatenate(means)
    return np.percentile(means, 2.5), np.percentile(means, 97.5)


def describe(values):
    values = pd.Series(values)
    low, high = boot_ci(values.to_numpy())
    return {"n_borrowers": int(values.notna().sum()), "n_missing": int(values.isna().sum()),
            "mean": values.mean(), "ci95_low": low, "ci95_high": high, "median": values.median(),
            "p05": values.quantile(0.05), "p95": values.quantile(0.95)}


def summarise_rank(rank_table):
    metrics = ["spearman"] + [f"top{k}_agreement" for k in TOP_KS]
    rows = []
    for (family, condition), group in rank_table.groupby(["family", "condition"], sort=False):
        per_borrower = group.groupby("borrower_id")[metrics].mean()   # average over this family's pairs
        n_undefined = int(group["spearman"].isna().sum())
        for metric in metrics:
            rows.append({"family": family, "condition": condition, "metric": metric,
                         "n_pairs": group[["run_a", "run_b"]].drop_duplicates().shape[0],
                         "n_undefined_pair_values": n_undefined if metric == "spearman" else 0,
                         **describe(per_borrower[metric])})
    return pd.DataFrame(rows)


def summarise_attribution(attr, features):
    rows = []
    for (condition, feature), g in attr.groupby(["condition", "feature"], sort=False):
        valid = g[g["cv_valid"]]
        rows.append({"condition": condition, "feature": feature,
                     "global_mean_abs_shap": g["mean_abs"].mean(),
                     "median_signed_sd": g["signed_sd"].median(), "mean_signed_sd": g["signed_sd"].mean(),
                     "mean_frac_positive": g["frac_positive"].mean(), "mean_frac_negative": g["frac_negative"].mean(),
                     "mean_frac_near_zero": g["frac_near_zero"].mean(),
                     "mean_sign_consistency": g["sign_consistency"].mean(),
                     "n_sign_consistency_undefined": int(g["sign_consistency"].isna().sum()),
                     "median_magnitude_cv_valid": valid["magnitude_cv"].median(),
                     "mean_magnitude_cv_valid": valid["magnitude_cv"].mean(),
                     "n_cv_masked": int((~g["cv_valid"]).sum()),
                     "frac_cv_masked": float((~g["cv_valid"]).mean())})
    table = pd.DataFrame(rows)
    table["feature"] = pd.Categorical(table["feature"], features, ordered=True)
    return table.sort_values(["condition", "feature"]).reset_index(drop=True)


def summarise_weighting(weight_table, features):
    summary = weight_table.groupby("feature", sort=False).agg(
        mean_signed_diff=("diff_signed", "mean"), mean_abs_diff=("diff_abs", "mean"),
        mean_abs_shap_unweighted=("shap_unweighted", lambda v: np.abs(v).mean()),
        mean_abs_shap_weighted=("shap_weighted", lambda v: np.abs(v).mean())).reset_index()
    summary["feature"] = pd.Categorical(summary["feature"], features, ordered=True)
    return summary.sort_values("feature").reset_index(drop=True)


def summarise_fidelity(fid):
    rows = []
    fid = fid.assign(condition=fid["run"].str.split("_").str[0])
    # per run and k, then per condition and k (borrower average over the 5 seeds)
    for scope, key in (("run", "run"), ("condition", "condition")):
        for (name, k), g in fid.groupby([key, "k"], sort=False):
            per_borrower = g.groupby("borrower_id")[["high_prob_change", "low_prob_change", "diff_prob",
                                                      "high_margin_change", "low_margin_change", "diff_margin"]].mean()
            row = {"scope": scope, "name": name, "k": k,
                   "mean_high_prob_change": per_borrower["high_prob_change"].mean(),
                   "mean_low_prob_change": per_borrower["low_prob_change"].mean(),
                   "mean_high_margin_change": per_borrower["high_margin_change"].mean(),
                   "mean_low_margin_change": per_borrower["low_margin_change"].mean(),
                   "mean_diff_prob": per_borrower["diff_prob"].mean(),
                   "median_diff_prob": per_borrower["diff_prob"].median(),
                   "mean_diff_margin": per_borrower["diff_margin"].mean(),
                   "share_diff_positive": (g["diff_margin"] > 0).mean(),
                   "share_diff_negative": (g["diff_margin"] < 0).mean(),
                   "share_diff_zero": (g["diff_margin"] == 0).mean(),
                   "share_high_noop": g["high_noop"].mean(), "share_low_noop": g["low_noop"].mean(),
                   "mean_high_n_changed": g["high_n_changed"].mean(), "mean_low_n_changed": g["low_n_changed"].mean()}
            low, high = boot_ci(per_borrower["diff_prob"].to_numpy())
            row["diff_prob_ci95_low"], row["diff_prob_ci95_high"] = low, high
            low, high = boot_ci(per_borrower["diff_margin"].to_numpy())
            row["diff_margin_ci95_low"], row["diff_margin_ci95_high"] = low, high
            # secondary: only borrowers/models where both arms actually changed something
            both = g[~g["high_noop"] & ~g["low_noop"]]
            row["secondary_n_rows"] = len(both)
            row["secondary_mean_diff_prob"] = both["diff_prob"].mean()
            row["secondary_mean_diff_margin"] = both["diff_margin"].mean()
            rows.append(row)
    return pd.DataFrame(rows)


def build_performance_table(rank_table):
    metrics = pd.read_csv(P1 / "metrics_all_runs.csv")
    key = "run_id" if "run_id" in metrics.columns else metrics.columns[0]
    metrics = metrics.set_index(key)
    pairs = rank_table.groupby(["family", "condition", "run_a", "run_b"], sort=False)[
        ["spearman", "top3_agreement", "top5_agreement"]].mean().reset_index()
    for name in ["roc_auc", "log_loss", "brier_score", "average_precision"]:
        pairs[f"abs_delta_{name}"] = [abs(metrics.loc[a, name] - metrics.loc[b, name])
                                      for a, b in zip(pairs["run_a"], pairs["run_b"])]
    return pairs.rename(columns={"spearman": "mean_spearman", "top3_agreement": "mean_top3_agreement",
                                 "top5_agreement": "mean_top5_agreement"})


def pick_examples(rank_table, fid, ids):
    order = np.argsort(ids, kind="stable")          # tie rule: lowest borrower_id
    chosen = {}
    unweighted = rank_table[rank_table["condition"] == "unweighted"].groupby("borrower_id")["spearman"].mean().reindex(ids)
    values = unweighted.to_numpy()
    for label, q in (("least_stable_p01", 0.01), ("median_stability_p50", 0.5), ("most_stable_p99", 0.99)):
        target = np.nanquantile(values, q)
        distance = np.abs(values[order] - target)
        chosen[label] = ids[order][np.nanargmin(distance)]
    diff = fid[fid["k"] == 3].groupby("borrower_id")["diff_margin"].mean().reindex(ids).to_numpy()
    chosen["fidelity_counterexample"] = ids[order][np.nanargmin(diff[order])]
    between = rank_table[rank_table["family"] == "between"].groupby("borrower_id")["top3_agreement"].mean().reindex(ids).to_numpy()
    chosen["lowest_between_condition_top3"] = ids[order][np.nanargmin(between[order])]
    return chosen


def write_examples(chosen, values_by_run, ids, features, X_test, y_test, fid):
    rows, lines = [], ["# Borrower examples (selected by the rule in analysis_protocol.md section 9)\n"]
    position = {b: i for i, b in enumerate(ids)}
    for label, borrower in chosen.items():
        i = position[borrower]
        lines.append(f"\n## {label}: borrower_id {borrower} (true label {int(y_test.iloc[i, 0])})\n")
        lines.append("| feature | value | mean SHAP unweighted | range unweighted | mean SHAP weighted | range weighted |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for j, feature in enumerate(features):
            cells = []
            for condition in CONDITIONS:
                shap_values = np.array([values_by_run[f"{condition}_seed{s}"][i, j] for s in SEEDS])
                cells += [f"{shap_values.mean():+.3f}", f"{shap_values.min():+.3f} to {shap_values.max():+.3f}"]
            lines.append(f"| {feature} | {X_test.iloc[i, j]:.4g} | " + " | ".join(cells) + " |")
        for run in RUNS:
            top3 = [features[j] for j in np.argsort(-np.abs(values_by_run[run][i]), kind="stable")[:3]]
            lines.append(f"\n- {run} top-3: {', '.join(top3)}")
            for j, feature in enumerate(features):
                rows.append({"example": label, "borrower_id": borrower, "run": run, "feature": feature,
                             "feature_value": X_test.iloc[i, j], "shap": values_by_run[run][i, j]})
        sub = fid[(fid["borrower_id"] == borrower) & (fid["k"] == 3)]
        lines.append("\nFidelity k=3 (abs probability change, high arm vs low arm): " +
                     "; ".join(f"{r.run}: {r.high_prob_change:.4f} vs {r.low_prob_change:.4f}" for r in sub.itertuples()))
    pd.DataFrame(rows).to_csv(P2 / "examples.csv", index=False)
    (P2 / "examples.md").write_text("\n".join(lines) + "\n")


# ---------------- figures ----------------
def make_figures(rank_table, attr_summary, fid_summary, performance, features):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    figures = P2 / "figures"
    figures.mkdir(exist_ok=True)

    # 1. distribution of per-borrower rank stability
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    families = [("within", "unweighted"), ("within", "weighted"), ("between", "unweighted_vs_weighted")]
    names = ["within\nunweighted", "within\nweighted", "between\n(same seed)"]
    for ax, metric, title in zip(axes, ["spearman", "top3_agreement", "top5_agreement"],
                                 ["Spearman of |SHAP|", "Top-3 agreement", "Top-5 agreement"]):
        data = [rank_table[(rank_table["family"] == f) & (rank_table["condition"] == c)]
                .groupby("borrower_id")[metric].mean().dropna() for f, c in families]
        ax.boxplot(data, tick_labels=names, showfliers=False)
        ax.set_title(title + " (per-borrower mean over pairs)", fontsize=9)
        ax.set_ylim(0, 1.02)
    fig.tight_layout()
    fig.savefig(figures / "fig1_rank_stability.png", dpi=150)
    plt.close(fig)

    # 2. global mean |SHAP| per feature by condition
    fig, ax = plt.subplots(figsize=(10, 4.5))
    width = 0.4
    for offset, condition in zip((-width / 2, width / 2), CONDITIONS):
        table = attr_summary[attr_summary["condition"] == condition].set_index("feature").loc[features]
        ax.bar(np.arange(len(features)) + offset, table["global_mean_abs_shap"], width, label=condition)
    ax.set_xticks(range(len(features)))
    ax.set_xticklabels([f.replace("NumberOf", "N").replace("DaysPastDueNotWorse", "") for f in features],
                       rotation=40, ha="right", fontsize=8)
    ax.set_ylabel("mean |SHAP| (log-odds), 5-seed average")
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures / "fig2_global_importance.png", dpi=150)
    plt.close(fig)

    # 3. fidelity: high vs low arm
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    table = fid_summary[fid_summary["scope"] == "run"]
    for ax, k in zip(axes, TOP_KS):
        sub = table[table["k"] == k]
        position = np.arange(len(sub))
        ax.bar(position - 0.2, sub["mean_high_margin_change"], 0.4, label="high-ranked replaced")
        ax.bar(position + 0.2, sub["mean_low_margin_change"], 0.4, label="low-ranked replaced")
        ax.set_xticks(position)
        ax.set_xticklabels(sub["name"].str.replace("_seed", "\ns"), fontsize=7)
        ax.set_title(f"k={k}: mean |raw-margin change|", fontsize=9)
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(figures / "fig3_fidelity.png", dpi=150)
    plt.close(fig)

    # 4. performance gap vs explanation similarity across the 25 model pairs
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    colors = {"within": "tab:blue", "between": "tab:red"}
    for ax, column, label in zip(axes, ["abs_delta_roc_auc", "abs_delta_log_loss"],
                                 ["|difference in ROC-AUC|", "|difference in log loss|"]):
        for family, group in performance.groupby("family"):
            ax.scatter(group[column], group["mean_spearman"], c=colors[family], label=family, s=25)
        ax.set_xlabel(label)
        ax.set_ylabel("mean Spearman of |SHAP| over borrowers")
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(figures / "fig4_performance_vs_reliability.png", dpi=150)
    plt.close(fig)


# ---------------- main ----------------
def analyze(features, medians, X_test, y_test):
    ids = X_test.index.to_numpy()
    values = load_explanations(ids)

    rank_table = rank_stability(values, ids)
    attr = attribution_stability(values, ids, features)
    weight_table = weighting_change(values, ids, features)
    fid = fidelity(values, ids, features, medians, X_test)

    rank_table.to_csv(P2 / "rank_stability.csv.gz", index=False)
    attr.to_csv(P2 / "attribution_stability.csv.gz", index=False)
    weight_table.to_csv(P2 / "weighting_change.csv.gz", index=False)
    fid.to_csv(P2 / "fidelity.csv.gz", index=False)

    rank_summary = summarise_rank(rank_table)
    attr_summary = summarise_attribution(attr, features)
    fid_summary = summarise_fidelity(fid)
    performance = build_performance_table(rank_table)
    rank_summary.to_csv(P2 / "rank_stability_summary.csv", index=False)
    attr_summary.to_csv(P2 / "attribution_stability_summary.csv", index=False)
    summarise_weighting(weight_table, features).to_csv(P2 / "weighting_change_summary.csv", index=False)
    fid_summary.to_csv(P2 / "fidelity_summary.csv", index=False)
    performance.to_csv(P2 / "performance_vs_reliability.csv", index=False)

    # Sensitivity 1 (secondary): tree-path-dependent native contributions, rank metrics only
    native = load_explanations(ids, "native_shap")
    summarise_rank(rank_stability(native, ids)).to_csv(P2 / "sensitivity_path_dependent_rank_summary.csv", index=False)

    # Sensitivity 2 (secondary): exclude the 99 test rows whose processed profile also occurs in training
    overlap = pd.read_csv(ROOT / "outputs/p1_review_overlap_test_ids.csv").iloc[:, 0].to_numpy()
    keep_rank = ~rank_table["borrower_id"].isin(overlap)
    keep_fid = ~fid["borrower_id"].isin(overlap)
    summarise_rank(rank_table[keep_rank]).to_csv(P2 / "sensitivity_overlap_excluded_rank_summary.csv", index=False)
    summarise_fidelity(fid[keep_fid]).to_csv(P2 / "sensitivity_overlap_excluded_fidelity_summary.csv", index=False)

    chosen = pick_examples(rank_table, fid, ids)
    write_examples(chosen, values, ids, features, X_test, y_test, fid)
    make_figures(rank_table, attr_summary, fid_summary, performance, features)
    print("analysis done")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["all", "explain", "analyze"], default="all")
    parser.add_argument("--overwrite", action="store_true", help="Explicitly allow replacing existing analysis tables and figures")
    args = parser.parse_args()
    if args.stage in ("all", "analyze") and (P2 / "rank_stability.csv.gz").exists() and not args.overwrite:
        parser.error("P2 analysis already exists. Use --overwrite only when you intend to replace its tables and figures.")
    P2.mkdir(parents=True, exist_ok=True)
    features, medians, X_train, X_test, y_test = load_inputs()
    if args.stage in ("all", "explain"):
        explain(features, X_train, X_test)
    if args.stage in ("all", "analyze"):
        analyze(features, medians, X_test, y_test)


if __name__ == "__main__":
    main()
