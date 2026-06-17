# Geographic KNN Baseline Report

## Dataset handling
- Raw rows: 13640
- Sale rows after scope filtering: 6412
- Rows after missing-value removal: 6412
- Rows after invalid-coordinate removal: 6014
- Removed invalid `(0, 0)` coordinates: 398

## Validation results
| experiment | description | feature_columns | use_scaler | k | mae_mean | rmse_mean | r2_mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A_raw_no_norm | Raw longitude/latitude in degrees without normalization. | Longitude,Latitude | False | 1 | 1228.3757 | 2215.2414 | 0.5141 |
| A_raw_no_norm | Raw longitude/latitude in degrees without normalization. | Longitude,Latitude | False | 3 | 1152.2907 | 1922.2502 | 0.6357 |
| A_raw_no_norm | Raw longitude/latitude in degrees without normalization. | Longitude,Latitude | False | 5 | 1133.5214 | 1874.4435 | 0.6540 |
| A_raw_no_norm | Raw longitude/latitude in degrees without normalization. | Longitude,Latitude | False | 7 | 1142.5052 | 1884.9913 | 0.6503 |
| A_raw_no_norm | Raw longitude/latitude in degrees without normalization. | Longitude,Latitude | False | 9 | 1148.7404 | 1890.4530 | 0.6484 |
| A_raw_no_norm | Raw longitude/latitude in degrees without normalization. | Longitude,Latitude | False | 11 | 1159.9587 | 1896.3512 | 0.6462 |
| A_raw_no_norm | Raw longitude/latitude in degrees without normalization. | Longitude,Latitude | False | 15 | 1173.3795 | 1893.5655 | 0.6473 |
| A_raw_no_norm | Raw longitude/latitude in degrees without normalization. | Longitude,Latitude | False | 21 | 1187.7890 | 1903.7895 | 0.6434 |
| B_metric_no_norm | Projected metric coordinates without normalization. | x,y | False | 1 | 1220.2372 | 2158.2509 | 0.5386 |
| B_metric_no_norm | Projected metric coordinates without normalization. | x,y | False | 3 | 1148.0148 | 1900.5537 | 0.6436 |
| B_metric_no_norm | Projected metric coordinates without normalization. | x,y | False | 5 | 1136.8401 | 1875.1574 | 0.6538 |
| B_metric_no_norm | Projected metric coordinates without normalization. | x,y | False | 7 | 1143.4021 | 1893.5102 | 0.6473 |
| B_metric_no_norm | Projected metric coordinates without normalization. | x,y | False | 9 | 1151.4916 | 1892.5089 | 0.6477 |
| B_metric_no_norm | Projected metric coordinates without normalization. | x,y | False | 11 | 1162.1512 | 1902.6424 | 0.6439 |
| B_metric_no_norm | Projected metric coordinates without normalization. | x,y | False | 15 | 1174.4619 | 1897.6421 | 0.6458 |
| B_metric_no_norm | Projected metric coordinates without normalization. | x,y | False | 21 | 1188.1431 | 1904.4490 | 0.6432 |
| C_metric_std | Projected metric coordinates with StandardScaler. | x,y | True | 1 | 1256.8587 | 2269.4684 | 0.4907 |
| C_metric_std | Projected metric coordinates with StandardScaler. | x,y | True | 3 | 1153.2380 | 1922.8398 | 0.6354 |
| C_metric_std | Projected metric coordinates with StandardScaler. | x,y | True | 5 | 1134.0203 | 1876.4095 | 0.6533 |
| C_metric_std | Projected metric coordinates with StandardScaler. | x,y | True | 7 | 1148.9308 | 1890.2722 | 0.6484 |
| C_metric_std | Projected metric coordinates with StandardScaler. | x,y | True | 9 | 1157.3848 | 1895.1528 | 0.6467 |
| C_metric_std | Projected metric coordinates with StandardScaler. | x,y | True | 11 | 1165.6451 | 1898.3926 | 0.6455 |
| C_metric_std | Projected metric coordinates with StandardScaler. | x,y | True | 15 | 1176.6473 | 1896.1751 | 0.6463 |
| C_metric_std | Projected metric coordinates with StandardScaler. | x,y | True | 21 | 1194.0431 | 1908.8472 | 0.6415 |

## Best overall experiment
{
  "experiment": "A_raw_no_norm",
  "description": "Raw longitude/latitude in degrees without normalization.",
  "feature_columns": "Longitude,Latitude",
  "use_scaler": false,
  "k": 5,
  "mae_mean": 1133.521444879971,
  "rmse_mean": 1874.4435336586587,
  "r2_mean": 0.6540120038410839
}

## Selected baseline model
{
  "experiment": "B_metric_no_norm",
  "description": "Projected metric coordinates without normalization.",
  "feature_columns": "x,y",
  "use_scaler": false,
  "k": 5,
  "mae_mean": 1136.840128693316,
  "rmse_mean": 1875.1573789544059,
  "r2_mean": 0.6538092612066124
}

## Interpretation
Lower MAE and RMSE are better. Higher R² is better. The selected baseline model is constrained to metric coordinates `[x, y]`, so the final deployed baseline is chosen from experiments B and C even if experiment A wins the ablation.
