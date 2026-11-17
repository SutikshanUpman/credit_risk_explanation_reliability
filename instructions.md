# Instructions for the implementation agent

Read `plan.md` and inspect `Plan.jpeg` before starting. The image is the original assignment; the plan turns it into an executable workflow. Work within this project folder and preserve the original data.

## Priorities

1. Always ask yourself: **Is this line necessary?** Remove code, comments, files, and dependencies that do not help the experiment or make its reasoning clearer.
2. Always ask yourself: **Can this be done with simpler code?** Prefer straightforward steps over clever expressions, dense one-liners, and unnecessary abstractions.
3. **Logic is the most important part.** A student should be able to explain what each step does, why it exists, and how it supports the research question.
4. **Code quality will not be the grading focus; logic and novelty will be.** Do not overengineer. Correctness, reproducibility, and readable code still matter because they make the research evidence trustworthy.

## Working rules

- Prefer a few short Python scripts or a clearly ordered notebook. No web app, API, dashboard, framework, or elaborate package structure.
- Use descriptive names, ordinary loops, and small functions where they eliminate repetition. Avoid classes unless genuinely needed.
- Simpler means easier to understand, not merely fewer characters.
- Comment on **why** a choice was made. Avoid comments that only repeat the code.
- Explain important equations and assumptions in plain language alongside the implementation or in the handover.
- Use familiar libraries. Add a dependency only when it solves a real requirement.
- Keep experiment settings together. Avoid scattered magic numbers and hidden notebook state.
- Do not introduce extra models, datasets, feature engineering, tuning, or experiments without a research reason.
- Preserve raw files. Never overwrite them with cleaned data.
- Prevent leakage: fit preprocessing and balancing on training data only; keep held-out borrowers fixed.
- Save enough evidence to reproduce each result. Never fabricate metrics, citations, successful checks, or completed work.
- Use a few meaningful checks for split separation, input alignment, and prediction reproducibility. Do not build a large test framework for this college project.
- Keep progress updates short. State assumptions and material changes. Resolve ordinary implementation choices autonomously within this plan.
- If a requirement cannot be completed, document exactly what is missing and how the next person can continue.

## Research writing

- Distinguish a proposed contribution from a verified literature gap.
- Do not claim XGBoost, SHAP, class balancing, or explanation stability is new.
- Support novelty with verified references and actual experiments. Do not invent references from the image's abbreviated literature list.
- Report negative or mixed findings honestly. Do not change hypotheses after seeing results without labeling the change exploratory.
- Explain limitations, especially the fixed dataset/split, small number of runs, and assumptions behind perturbation tests.

Useful review words: **necessary, simple, readable, explicit, reproducible, leakage-free, controlled, evidence-backed**.

Before handing over, ask: Can another student reproduce this work and explain its logic without guessing?
