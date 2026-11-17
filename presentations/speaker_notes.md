# Presentation speaker notes (suggested 12–15 minute delivery)

## 1. Title
Introduce the project as an empirical study of whether SHAP explanations remain dependable when the same credit-risk modelling pipeline is retrained under controlled conditions. The paper integrates P1 model outputs, P2 SHAP analysis, and P3 research positioning.

## 2. Problem statement
Explain that predictive accuracy and explanation reliability are separate. ROC-AUC captures ranking, while a SHAP explanation depends on a particular fitted model and reference. The core issue is whether a borrower receives a similar account of the model after retraining or a loss-function change.

## 3. Solution overview
Describe the three audit dimensions. Rank stability asks whether the same features are important. Attribution stability asks whether direction and magnitude remain stable. Perturbation sensitivity asks whether the features ranked highly actually move the fitted model's output more under a controlled substitution test.

## 4. Example 1
Use borrower row 463 as the stable case. The top three features are identical across all ten models, and the 90-day delinquency attribution is large and consistently positive. Stress that this is one rule-selected example, not a population guarantee.

## 5. Example 2
Use borrower row 13186 to show within-condition repeatability but between-condition drift. Each condition is internally consistent across seeds, but weighting changes which features occupy positions two and three. This is the kind of model-version dependence the aggregate between-condition rank metrics capture.

## 6. Example 3
Use borrower row 33756 to explain why average results need counterexamples. In the unweighted models, the low-ranked arm causes a larger probability change than the high-ranked arm. This is not an error in the aggregate result; it shows that H3 does not hold for every borrower. Also mention row 2157: its overall rank correlation is low, but its top three are identical, so metrics are complementary.

## 7. Literature foundations
Position SHAP as a well-established attribution method, TreeSHAP as an efficient tree explanation method, and robustness/fidelity evaluation as an established concern. Make clear that the project does not invent SHAP or explanation-stability analysis.

## 8. Closest papers
Be direct about the two closest papers. Lin and Wang studied 100 XGBoost seeds on a 30,000-record credit-card dataset. Ballegeer and colleagues studied SHAP/LIME under instance-dependent cost sensitivity and imbalance across four datasets. Our distinction is the borrower-level multi-metric audit under one fixed shared cohort, not a claim of being first.

## 9. Proposed solution
Walk from one labelled dataset to ten models, then explain the exact same borrowers using one background. Finally compute rank, attribution and perturbation metrics. This layout isolates seed variation from a loss-weighting intervention without changing the test population.

## 10. Dataset and split
Define the target precisely: 90-days-past-due or worse within two years. Mention 150,000 rows, 6.684% positive class, and the fixed group-aware split. Clarify that the five-fold procedure supplied one holdout fold; it is not five-fold performance evaluation. Explain the post-imputation overlap as a limitation.

## 11. Models and SHAP
Explain the ten models: five seeds in each of two conditions. Weighting changes the loss contribution of the positive class, not the sample. TreeSHAP uses the same 100-row training-only background and raw-margin output for all models. Additivity checks passed to a maximum error of 7.44e-6.

## 12. Rank results
Point out the 0.959 and 0.949 within-condition Spearman values against 0.924 between conditions. Top-3 agreement likewise falls from about 0.93–0.95 to 0.898. The fifth percentile reaches 0.67 across conditions, so do not quote only means.

## 13. Attribution results
Clarify that sign consistency is high among attributions not classified as near-zero. Magnitude CV differs by feature: delinquency counts are low, while debt ratio and income are higher. Therefore direction may be dependable while magnitude varies more.

## 14. Perturbation results
Describe the paired high-minus-low raw-margin changes and positive borrower shares. Then immediately state the caveat: the high arm changes more features on average, while the low arm has nontrivial no-op rates at k=3. This is a sensitivity proxy, not causal fidelity, and random-k/matched-count controls are future work.

## 15. Predictive results
ROC-AUC barely changes under weighting, but log loss and Brier worsen substantially. Recall rises and precision falls at the fixed 0.5 threshold. This is why H1 is only partly supported: ranking discrimination is close, but the models are not equivalent across all metrics.

## 16. Hypotheses
Summarise each hypothesis with exact qualifications. H1 partly supported on the ROC-AUC dimension only. H2 supported for the between-condition gap but reference-mode-sensitive within conditions. H3 directionally supported on average but limited by unequal changed counts and counterexamples.

## 17. Conclusion
State the main message: explanations are mostly stable across seeds but are not invariant to the modelling condition. Different reliability dimensions tell different stories, so a single SHAP plot is not enough. The work is a bounded complementary case study.

## 18. Future work
Prioritise fixing the perturbation design, then broaden datasets/splits/seeds, examine reference assumptions, and add deployment-specific calibration/fairness/recourse validation only with the right data and expertise.

## 19. References
Mention the key foundations and the two close 2025 studies; the full paper contains complete citations and DOIs.

## 20. Close
End with the central distinction: a prediction can be accurate, but the explanation must also be checked for repeatability and model sensitivity before it is relied upon.
