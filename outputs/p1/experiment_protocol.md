# P1 experiment protocol (written before model fitting)

Hypotheses from the source plan: H1, predictive similarity need not imply borrower-level explanation similarity; H2, explanation stability can change with training conditions; H3, perturbing high-ranked SHAP features should affect predictions more than low-ranked features. P1 generates model artifacts; it cannot evaluate these explanation hypotheses.

Use the first held-out fold from StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42); group exact cleaned predictor profiles, with missing values equal for grouping. Keep this split fixed. This is not five-fold performance evaluation. Sort both partitions by borrower ID. Do not tune or select a best model using held-out metrics.

Set age <= 0 missing, retain other unusual values, fit training-only median imputation once. Preserve all ten features and their original order. No validation-based early stopping or threshold tuning.

Model settings: `{"base_score": 0.5, "colsample_bytree": 0.8, "device": "cpu", "eval_metric": "logloss", "gamma": 0, "learning_rate": 0.05, "max_bin": 256, "max_depth": 4, "min_child_weight": 1, "n_estimators": 300, "n_jobs": 4, "objective": "binary:logistic", "reg_alpha": 0, "reg_lambda": 1, "subsample": 0.8, "tree_method": "hist", "verbosity": 0}`.

Seeds: [11, 22, 33, 44, 55]. Conditions: unweighted (`scale_pos_weight=1`) and weighted (`training negatives / training positives`). Pair equal seeds. Training rows stay identical: this tests randomness and loss weighting, not SMOTE or bootstrap/resampling. Fixed base_score=0.5 ensures both conditions start from the same intercept. Save every model.

Evaluate ROC-AUC, average precision, log loss, Brier score, precision/recall/F1 and confusion counts. Classification threshold: 0.5; it is a reporting convention. Summaries use mean and sample standard deviation over five seeds, not population confidence intervals. Verify model reloads with absolute probability tolerance 1e-07, relative tolerance zero.

P2/P3 decisions still required before explanation analysis: TreeSHAP mode/scale/background, borrower cohort, top-k/tie handling, near-zero CV handling, and perturbation procedure. The plan suggests raw-margin explanations and k=3,5. P1 does not silently freeze these decisions on P2's behalf. H1 should use continuous predictive-performance differences unless a justified equivalence threshold is defined before analysis. No novelty claim is established by predictive performance.
