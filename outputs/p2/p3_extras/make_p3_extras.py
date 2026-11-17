"""Derives two small convenience tables for P3 from the saved P2 arrays/summaries (no new analysis choices).
Run from the project root: python outputs/p2/p3_extras/make_p3_extras.py"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
P2 = ROOT / "outputs/p2"
feats = json.loads((ROOT / "outputs/p1/feature_schema.json").read_text())["features"]
rows = []
for cond in ["unweighted","weighted"]:
    A = np.stack([np.abs(np.load(P2/f"explanations/{cond}_seed{s}.npz")["shap"]) for s in [11,22,33,44,55]])
    mean_abs = A.mean((0,1))
    order = np.argsort(-A, axis=2, kind="stable")
    ranks = (np.argsort(order, axis=2) + 1).mean((0,1))  # 1 = most important
    top1 = np.bincount(order[:,:,0].ravel(), minlength=len(feats))/A[:,:,0].size
    for i,f in enumerate(feats):
        rows.append(dict(condition=cond, feature=f, mean_abs_shap=mean_abs[i], mean_rank=ranks[i], share_borrower_models_ranked_first=top1[i]))
g = pd.DataFrame(rows); g["global_rank"] = g.groupby("condition")["mean_abs_shap"].rank(ascending=False).astype(int)
g.to_csv(P2/"p3_extras/global_importance_by_feature.csv", index=False)

r = pd.read_csv(P2/"rank_stability_summary.csv"); f = pd.read_csv(P2/"fidelity_summary.csv"); f = f[f.scope=="condition"]
key = [dict(block="rank_stability", item=f"{x.family}/{x.condition}/{x.metric}", value=x["mean"], ci95_low=x.ci95_low, ci95_high=x.ci95_high) for _,x in r.iterrows()]
key += [dict(block="fidelity_margin_diff", item=f"{x['name']}/k={x.k}", value=x.mean_diff_margin, ci95_low=x.diff_margin_ci95_low, ci95_high=x.diff_margin_ci95_high) for _,x in f.iterrows()]
pd.DataFrame(key).to_csv(P2/"p3_extras/key_results.csv", index=False)
print(g.round(3).to_string())
