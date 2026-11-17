# Speaker notes — revised IEEE-style research presentation

Suggested delivery: 12–15 minutes.

1. **Title.** Introduce the study as a controlled audit of borrower-level SHAP explanation reliability using ten saved XGBoost models.
2. **Problem.** Predictive discrimination and explanation repeatability are different properties. ROC-AUC does not tell us whether a borrower's explanation persists across model changes.
3. **Three checks.** Define rank agreement, attribution stability, and perturbation sensitivity. They answer different questions and should not be collapsed into one score.
4. **Borrower 463.** P2 selected this as the most-stable case. All ten models retain the same top three: 90+ days late, revolving utilisation, and 30–59 days past due. This is an example, not a population guarantee.
5. **Borrower 13186.** The top-three set is internally consistent within each condition but changes between weighting conditions. Emphasise the shift in the second/third features.
6. **Borrower 33756.** This is a counterexample to H3. In unweighted runs at k=3, low-ranked replacement changes probability by about 0.0065–0.0091, compared with about 0.0000–0.0005 for high-ranked replacement.
7. **Literature foundations.** SHAP and explanation-stability evaluation pre-exist. The study is not introducing a new attribution method.
8. **Closest studies.** Lin and Wang examine 100 XGBoost seeds and global SHAP ranking on a 30,000-record credit-card dataset. Ballegeer et al. study SHAP/LIME under instance-dependent cost sensitivity and imbalance across four datasets. Our contribution is narrower and complementary.
9. **Proposed solution.** Keep the same held-out borrowers and the same interventional background while comparing seed and loss-weighting conditions.
10. **Dataset.** Give Me Some Credit: 150,000 labelled rows, 10 predictors, 10,026 positives (6.684%). Target: 90-days-past-due or worse within two years. One fixed group-aware split: 119,987 train and 30,013 held out.
11. **Models and SHAP.** Five seeds per condition; positive-class loss weighting changes the loss, not the sample. TreeSHAP uses raw log-odds and the same 100-row training background. Additivity checks passed in P2.
12. **Rank results.** Read 0.959, 0.949, and 0.924. Then note between-condition top-3 agreement is 0.898 and the 5th percentile is 0.667.
13. **Attribution.** Sign consistency is high among non-near-zero attributions, but DebtRatio and MonthlyIncome magnitude CV is substantially higher than for delinquency-count features.
14. **Perturbation.** Report the four mean high-minus-low raw-margin contrasts. Immediately qualify them: the high and low arms change different numbers of features, and low-arm no-ops occur in 11.2%/12.7% of cases at k=3. This is not causality or Yeh et al.'s formal infidelity measure.
15. **Predictive metrics.** ROC-AUC barely changes, but log loss and Brier worsen materially. At threshold 0.5, recall rises from 0.194 to 0.763 while precision falls from 0.613 to 0.220. Do not call models equivalent.
16. **Hypotheses.** H1 is partly supported only on the ranking-discrimination dimension; H2 is supported for the between-condition gap but within-condition differences are reference-sensitive; H3 is an average directional sensitivity result with design limitations.
17. **Conclusion and future work.** Prioritise random-k and matched-change-count controls, then more seeds/splits and external/temporal datasets.
18. **References.** Mention the two close 2025 studies and the established SHAP/evaluation foundations.
19. **Close.** A prediction can be useful, but the explanation must also be checked for repeatability and model sensitivity.