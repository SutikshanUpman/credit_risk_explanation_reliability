# Borrower examples (selected by the rule in analysis_protocol.md section 9)


## least_stable_p01: borrower_id 2157 (true label 0)

| feature | value | mean SHAP unweighted | range unweighted | mean SHAP weighted | range weighted |
| --- | --- | --- | --- | --- | --- |
| RevolvingUtilizationOfUnsecuredLines | 0.001891 | -0.898 | -0.921 to -0.883 | -0.890 | -0.934 to -0.827 |
| age | 51 | +0.093 | +0.060 to +0.132 | +0.126 | +0.108 to +0.141 |
| NumberOfTime30-59DaysPastDueNotWorse | 0 | -0.295 | -0.298 to -0.292 | -0.295 | -0.301 to -0.291 |
| DebtRatio | 0.4456 | +0.111 | +0.092 to +0.129 | +0.144 | +0.124 to +0.165 |
| MonthlyIncome | 3881 | +0.121 | +0.095 to +0.150 | +0.134 | +0.107 to +0.161 |
| NumberOfOpenCreditLinesAndLoans | 10 | +0.110 | +0.096 to +0.135 | +0.129 | +0.105 to +0.148 |
| NumberOfTimes90DaysLate | 0 | -0.049 | -0.050 to -0.047 | -0.048 | -0.049 to -0.047 |
| NumberRealEstateLoansOrLines | 1 | -0.074 | -0.078 to -0.069 | -0.083 | -0.096 to -0.070 |
| NumberOfTime60-89DaysPastDueNotWorse | 0 | -0.200 | -0.203 to -0.192 | -0.199 | -0.202 to -0.194 |
| NumberOfDependents | 3 | +0.098 | +0.080 to +0.131 | +0.117 | +0.072 to +0.162 |

- unweighted_seed11 top-3: RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse, NumberOfTime60-89DaysPastDueNotWorse

- unweighted_seed22 top-3: RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse, NumberOfTime60-89DaysPastDueNotWorse

- unweighted_seed33 top-3: RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse, NumberOfTime60-89DaysPastDueNotWorse

- unweighted_seed44 top-3: RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse, NumberOfTime60-89DaysPastDueNotWorse

- unweighted_seed55 top-3: RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse, NumberOfTime60-89DaysPastDueNotWorse

- weighted_seed11 top-3: RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse, NumberOfTime60-89DaysPastDueNotWorse

- weighted_seed22 top-3: RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse, NumberOfTime60-89DaysPastDueNotWorse

- weighted_seed33 top-3: RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse, NumberOfTime60-89DaysPastDueNotWorse

- weighted_seed44 top-3: RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse, NumberOfTime60-89DaysPastDueNotWorse

- weighted_seed55 top-3: RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse, NumberOfTime60-89DaysPastDueNotWorse

Fidelity k=3 (abs probability change, high arm vs low arm): unweighted_seed11: 0.0122 vs 0.0000; unweighted_seed22: 0.0118 vs 0.0000; unweighted_seed33: 0.0105 vs 0.0000; unweighted_seed44: 0.0155 vs 0.0018; unweighted_seed55: 0.0111 vs 0.0017; weighted_seed11: 0.0958 vs 0.0182; weighted_seed22: 0.0746 vs 0.0015; weighted_seed33: 0.1070 vs 0.0078; weighted_seed44: 0.1095 vs 0.0224; weighted_seed55: 0.1041 vs 0.0125

## median_stability_p50: borrower_id 123 (true label 0)

| feature | value | mean SHAP unweighted | range unweighted | mean SHAP weighted | range weighted |
| --- | --- | --- | --- | --- | --- |
| RevolvingUtilizationOfUnsecuredLines | 0.2976 | +0.018 | -0.012 to +0.047 | +0.003 | -0.027 to +0.026 |
| age | 67 | -0.440 | -0.481 to -0.402 | -0.503 | -0.528 to -0.465 |
| NumberOfTime30-59DaysPastDueNotWorse | 0 | -0.273 | -0.277 to -0.271 | -0.294 | -0.297 to -0.291 |
| DebtRatio | 0.2395 | -0.092 | -0.123 to -0.060 | -0.062 | -0.084 to -0.042 |
| MonthlyIncome | 4145 | +0.097 | +0.080 to +0.121 | +0.084 | +0.064 to +0.103 |
| NumberOfOpenCreditLinesAndLoans | 13 | +0.206 | +0.180 to +0.224 | +0.238 | +0.211 to +0.264 |
| NumberOfTimes90DaysLate | 0 | -0.040 | -0.042 to -0.039 | -0.043 | -0.043 to -0.043 |
| NumberRealEstateLoansOrLines | 0 | +0.069 | +0.058 to +0.081 | +0.102 | +0.090 to +0.122 |
| NumberOfTime60-89DaysPastDueNotWorse | 0 | -0.176 | -0.181 to -0.172 | -0.184 | -0.190 to -0.178 |
| NumberOfDependents | 0 | -0.017 | -0.022 to -0.009 | -0.019 | -0.021 to -0.015 |

- unweighted_seed11 top-3: age, NumberOfTime30-59DaysPastDueNotWorse, NumberOfOpenCreditLinesAndLoans

- unweighted_seed22 top-3: age, NumberOfTime30-59DaysPastDueNotWorse, NumberOfOpenCreditLinesAndLoans

- unweighted_seed33 top-3: age, NumberOfTime30-59DaysPastDueNotWorse, NumberOfOpenCreditLinesAndLoans

- unweighted_seed44 top-3: age, NumberOfTime30-59DaysPastDueNotWorse, NumberOfOpenCreditLinesAndLoans

- unweighted_seed55 top-3: age, NumberOfTime30-59DaysPastDueNotWorse, NumberOfOpenCreditLinesAndLoans

- weighted_seed11 top-3: age, NumberOfTime30-59DaysPastDueNotWorse, NumberOfOpenCreditLinesAndLoans

- weighted_seed22 top-3: age, NumberOfTime30-59DaysPastDueNotWorse, NumberOfOpenCreditLinesAndLoans

- weighted_seed33 top-3: age, NumberOfTime30-59DaysPastDueNotWorse, NumberOfOpenCreditLinesAndLoans

- weighted_seed44 top-3: age, NumberOfTime30-59DaysPastDueNotWorse, NumberOfOpenCreditLinesAndLoans

- weighted_seed55 top-3: age, NumberOfTime30-59DaysPastDueNotWorse, NumberOfOpenCreditLinesAndLoans

Fidelity k=3 (abs probability change, high arm vs low arm): unweighted_seed11: 0.0069 vs 0.0051; unweighted_seed22: 0.0078 vs 0.0040; unweighted_seed33: 0.0081 vs 0.0054; unweighted_seed44: 0.0121 vs 0.0046; unweighted_seed55: 0.0092 vs 0.0043; weighted_seed11: 0.0683 vs 0.0358; weighted_seed22: 0.0764 vs 0.0530; weighted_seed33: 0.0820 vs 0.0389; weighted_seed44: 0.0819 vs 0.0177; weighted_seed55: 0.0713 vs 0.0396

## most_stable_p99: borrower_id 463 (true label 0)

| feature | value | mean SHAP unweighted | range unweighted | mean SHAP weighted | range weighted |
| --- | --- | --- | --- | --- | --- |
| RevolvingUtilizationOfUnsecuredLines | 1 | +0.718 | +0.707 to +0.744 | +0.769 | +0.731 to +0.798 |
| age | 33 | +0.275 | +0.268 to +0.285 | +0.293 | +0.268 to +0.323 |
| NumberOfTime30-59DaysPastDueNotWorse | 1 | +0.448 | +0.434 to +0.463 | +0.489 | +0.467 to +0.506 |
| DebtRatio | 0.2577 | -0.173 | -0.199 to -0.154 | -0.133 | -0.168 to -0.110 |
| MonthlyIncome | 5416 | -0.004 | -0.016 to +0.013 | +0.013 | +0.005 to +0.021 |
| NumberOfOpenCreditLinesAndLoans | 2 | -0.105 | -0.124 to -0.095 | -0.102 | -0.123 to -0.089 |
| NumberOfTimes90DaysLate | 2 | +2.068 | +2.052 to +2.085 | +2.066 | +2.037 to +2.082 |
| NumberRealEstateLoansOrLines | 1 | -0.035 | -0.041 to -0.032 | -0.051 | -0.058 to -0.046 |
| NumberOfTime60-89DaysPastDueNotWorse | 0 | -0.090 | -0.095 to -0.088 | -0.095 | -0.098 to -0.091 |
| NumberOfDependents | 1 | +0.025 | +0.017 to +0.035 | +0.059 | +0.052 to +0.074 |

- unweighted_seed11 top-3: NumberOfTimes90DaysLate, RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse

- unweighted_seed22 top-3: NumberOfTimes90DaysLate, RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse

- unweighted_seed33 top-3: NumberOfTimes90DaysLate, RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse

- unweighted_seed44 top-3: NumberOfTimes90DaysLate, RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse

- unweighted_seed55 top-3: NumberOfTimes90DaysLate, RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse

- weighted_seed11 top-3: NumberOfTimes90DaysLate, RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse

- weighted_seed22 top-3: NumberOfTimes90DaysLate, RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse

- weighted_seed33 top-3: NumberOfTimes90DaysLate, RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse

- weighted_seed44 top-3: NumberOfTimes90DaysLate, RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse

- weighted_seed55 top-3: NumberOfTimes90DaysLate, RevolvingUtilizationOfUnsecuredLines, NumberOfTime30-59DaysPastDueNotWorse

Fidelity k=3 (abs probability change, high arm vs low arm): unweighted_seed11: 0.4447 vs 0.0096; unweighted_seed22: 0.4380 vs 0.0119; unweighted_seed33: 0.4288 vs 0.0004; unweighted_seed44: 0.4433 vs 0.0101; unweighted_seed55: 0.4311 vs 0.0072; weighted_seed11: 0.7370 vs 0.0075; weighted_seed22: 0.7552 vs 0.0043; weighted_seed33: 0.7457 vs 0.0023; weighted_seed44: 0.7551 vs 0.0074; weighted_seed55: 0.7584 vs 0.0060

## fidelity_counterexample: borrower_id 33756 (true label 0)

| feature | value | mean SHAP unweighted | range unweighted | mean SHAP weighted | range weighted |
| --- | --- | --- | --- | --- | --- |
| RevolvingUtilizationOfUnsecuredLines | 0.3109 | +0.027 | -0.009 to +0.055 | -0.018 | -0.063 to +0.037 |
| age | 41 | +0.177 | +0.166 to +0.185 | +0.192 | +0.179 to +0.201 |
| NumberOfTime30-59DaysPastDueNotWorse | 0 | -0.262 | -0.270 to -0.257 | -0.290 | -0.295 to -0.285 |
| DebtRatio | 0.1078 | -0.089 | -0.106 to -0.073 | -0.086 | -0.132 to -0.050 |
| MonthlyIncome | 6800 | -0.110 | -0.147 to -0.074 | -0.097 | -0.108 to -0.081 |
| NumberOfOpenCreditLinesAndLoans | 5 | -0.122 | -0.133 to -0.117 | -0.176 | -0.194 to -0.166 |
| NumberOfTimes90DaysLate | 0 | -0.038 | -0.040 to -0.037 | -0.042 | -0.043 to -0.041 |
| NumberRealEstateLoansOrLines | 0 | +0.074 | +0.063 to +0.079 | +0.103 | +0.087 to +0.128 |
| NumberOfTime60-89DaysPastDueNotWorse | 0 | -0.163 | -0.166 to -0.159 | -0.173 | -0.180 to -0.169 |
| NumberOfDependents | 2 | +0.052 | +0.044 to +0.072 | +0.082 | +0.075 to +0.087 |

- unweighted_seed11 top-3: NumberOfTime30-59DaysPastDueNotWorse, age, NumberOfTime60-89DaysPastDueNotWorse

- unweighted_seed22 top-3: NumberOfTime30-59DaysPastDueNotWorse, age, NumberOfTime60-89DaysPastDueNotWorse

- unweighted_seed33 top-3: NumberOfTime30-59DaysPastDueNotWorse, age, NumberOfTime60-89DaysPastDueNotWorse

- unweighted_seed44 top-3: NumberOfTime30-59DaysPastDueNotWorse, age, NumberOfTime60-89DaysPastDueNotWorse

- unweighted_seed55 top-3: NumberOfTime30-59DaysPastDueNotWorse, age, NumberOfTime60-89DaysPastDueNotWorse

- weighted_seed11 top-3: NumberOfTime30-59DaysPastDueNotWorse, age, NumberOfOpenCreditLinesAndLoans

- weighted_seed22 top-3: NumberOfTime30-59DaysPastDueNotWorse, age, NumberOfOpenCreditLinesAndLoans

- weighted_seed33 top-3: NumberOfTime30-59DaysPastDueNotWorse, age, NumberOfTime60-89DaysPastDueNotWorse

- weighted_seed44 top-3: NumberOfTime30-59DaysPastDueNotWorse, age, NumberOfOpenCreditLinesAndLoans

- weighted_seed55 top-3: NumberOfTime30-59DaysPastDueNotWorse, age, NumberOfTime60-89DaysPastDueNotWorse

Fidelity k=3 (abs probability change, high arm vs low arm): unweighted_seed11: 0.0005 vs 0.0065; unweighted_seed22: 0.0004 vs 0.0091; unweighted_seed33: 0.0000 vs 0.0082; unweighted_seed44: 0.0001 vs 0.0080; unweighted_seed55: 0.0001 vs 0.0086; weighted_seed11: 0.0159 vs 0.0344; weighted_seed22: 0.0245 vs 0.0389; weighted_seed33: 0.0067 vs 0.0274; weighted_seed44: 0.0131 vs 0.0609; weighted_seed55: 0.0069 vs 0.0706

## lowest_between_condition_top3: borrower_id 13186 (true label 0)

| feature | value | mean SHAP unweighted | range unweighted | mean SHAP weighted | range weighted |
| --- | --- | --- | --- | --- | --- |
| RevolvingUtilizationOfUnsecuredLines | 0.2662 | -0.093 | -0.112 to -0.066 | -0.134 | -0.185 to -0.112 |
| age | 36 | +0.180 | +0.169 to +0.188 | +0.162 | +0.153 to +0.167 |
| NumberOfTime30-59DaysPastDueNotWorse | 0 | -0.273 | -0.275 to -0.270 | -0.299 | -0.306 to -0.296 |
| DebtRatio | 0.2349 | -0.099 | -0.106 to -0.087 | -0.094 | -0.125 to -0.079 |
| MonthlyIncome | 3333 | +0.146 | +0.137 to +0.154 | +0.196 | +0.183 to +0.210 |
| NumberOfOpenCreditLinesAndLoans | 5 | -0.143 | -0.163 to -0.133 | -0.208 | -0.219 to -0.199 |
| NumberOfTimes90DaysLate | 0 | -0.039 | -0.041 to -0.038 | -0.042 | -0.043 to -0.041 |
| NumberRealEstateLoansOrLines | 0 | +0.058 | +0.053 to +0.069 | +0.072 | +0.065 to +0.080 |
| NumberOfTime60-89DaysPastDueNotWorse | 0 | -0.171 | -0.177 to -0.166 | -0.177 | -0.182 to -0.172 |
| NumberOfDependents | 0 | -0.035 | -0.038 to -0.028 | -0.048 | -0.053 to -0.044 |

- unweighted_seed11 top-3: NumberOfTime30-59DaysPastDueNotWorse, age, NumberOfTime60-89DaysPastDueNotWorse

- unweighted_seed22 top-3: NumberOfTime30-59DaysPastDueNotWorse, age, NumberOfTime60-89DaysPastDueNotWorse

- unweighted_seed33 top-3: NumberOfTime30-59DaysPastDueNotWorse, age, NumberOfTime60-89DaysPastDueNotWorse

- unweighted_seed44 top-3: NumberOfTime30-59DaysPastDueNotWorse, age, NumberOfTime60-89DaysPastDueNotWorse

- unweighted_seed55 top-3: NumberOfTime30-59DaysPastDueNotWorse, age, NumberOfTime60-89DaysPastDueNotWorse

- weighted_seed11 top-3: NumberOfTime30-59DaysPastDueNotWorse, NumberOfOpenCreditLinesAndLoans, MonthlyIncome

- weighted_seed22 top-3: NumberOfTime30-59DaysPastDueNotWorse, NumberOfOpenCreditLinesAndLoans, MonthlyIncome

- weighted_seed33 top-3: NumberOfTime30-59DaysPastDueNotWorse, NumberOfOpenCreditLinesAndLoans, RevolvingUtilizationOfUnsecuredLines

- weighted_seed44 top-3: NumberOfTime30-59DaysPastDueNotWorse, NumberOfOpenCreditLinesAndLoans, MonthlyIncome

- weighted_seed55 top-3: NumberOfTime30-59DaysPastDueNotWorse, MonthlyIncome, NumberOfOpenCreditLinesAndLoans

Fidelity k=3 (abs probability change, high arm vs low arm): unweighted_seed11: 0.0014 vs 0.0035; unweighted_seed22: 0.0009 vs 0.0031; unweighted_seed33: 0.0017 vs 0.0031; unweighted_seed44: 0.0019 vs 0.0029; unweighted_seed55: 0.0025 vs 0.0022; weighted_seed11: 0.0121 vs 0.0278; weighted_seed22: 0.0026 vs 0.0245; weighted_seed33: 0.0372 vs 0.0244; weighted_seed44: 0.0124 vs 0.0337; weighted_seed55: 0.0142 vs 0.0171
