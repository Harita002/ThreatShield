import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report
)

from xgboost import XGBClassifier


# ============================================================
# 1. LOAD DATA
# ============================================================

DATA_PATH = "../../dataset/insider_threat_clean_dataset.csv"

df = pd.read_csv(DATA_PATH)

print("=" * 70)
print("FINAL MODEL EVALUATION")
print("=" * 70)

print("Original shape:", df.shape)


# ============================================================
# 2. CLEAN DATA
# ============================================================

df.columns = df.columns.str.strip()

for col in df.select_dtypes(
    include=["object", "string"]
).columns:
    df[col] = df[col].str.strip()

df = df.dropna()
df = df.drop_duplicates()


# ============================================================
# 3. FEATURE ENGINEERING
# ============================================================

df["off_hour_print_ratio"] = (
    df["num_printed_pages_off_hours"]
    / (df["total_printed_pages"] + 1)
)

df["burn_ratio"] = (
    df["total_files_burned"]
    / (df["num_entries"] + 1)
)

df["mobility_risk"] = (
    df["num_unique_campus"]
    * df["is_abroad"]
)

df["behavior_risk_score"] = (
    df["late_exit_flag"]
    + df["entry_during_weekend"]
    + df["burned_from_other"]
    + df["has_criminal_record"]
)

df["access_frequency_score"] = (
    df["num_entries"]
    / (df["trip_day_number"] + 1)
)


# ============================================================
# 4. FEATURES / TARGET
# ============================================================

X = df.drop(
    columns=["is_malicious"]
)

y = df["is_malicious"].astype(int)


# ============================================================
# 5. SAME SPLIT AS BEFORE
# ============================================================

X_temp, X_test, y_temp, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=42
)

X_train, X_val, y_train, y_val = train_test_split(
    X_temp,
    y_temp,
    test_size=0.25,
    stratify=y_temp,
    random_state=42
)


print("\nDataset Split:")
print("Train:", X_train.shape)
print("Validation:", X_val.shape)
print("Test:", X_test.shape)


# ============================================================
# 6. CATEGORICAL FEATURES
# ============================================================

categorical_features = X.select_dtypes(
    include=["object", "string"]
).columns.tolist()


# ============================================================
# 7. PREPROCESSING
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        )
    ],
    remainder="passthrough"
)


# ============================================================
# 8. CLASS IMBALANCE
# ============================================================

negative_count = (y_train == 0).sum()
positive_count = (y_train == 1).sum()

scale_pos_weight = (
    negative_count / positive_count
)

print("\nScale Pos Weight:")
print(round(scale_pos_weight, 4))


# ============================================================
# 9. FINAL MODEL A
# ============================================================

model = XGBClassifier(

    n_estimators=400,

    max_depth=6,

    learning_rate=0.05,

    min_child_weight=3,

    subsample=0.8,

    colsample_bytree=0.8,

    reg_lambda=1.0,

    reg_alpha=0,

    scale_pos_weight=scale_pos_weight,

    objective="binary:logistic",

    eval_metric="logloss",

    random_state=42,

    n_jobs=-1
)


# ============================================================
# 10. FIT PREPROCESSOR ON TRAINING DATA
# ============================================================

X_train_processed = preprocessor.fit_transform(
    X_train
)

X_test_processed = preprocessor.transform(
    X_test
)


# ============================================================
# 11. TRAIN FINAL MODEL
# ============================================================

print("\nTraining final Model A...")

model.fit(
    X_train_processed,
    y_train
)

print("Training completed.")


# ============================================================
# 12. FINAL THRESHOLD
# ============================================================

FINAL_THRESHOLD = 0.65


# ============================================================
# 13. TEST PREDICTIONS
# ============================================================

test_probabilities = model.predict_proba(
    X_test_processed
)[:, 1]

test_predictions = (
    test_probabilities >= FINAL_THRESHOLD
).astype(int)

# ============================================================
# PREDICTED VS ACTUAL
# ============================================================

comparison_df = pd.DataFrame({
    "Actual": y_test.values,
    "Predicted": test_predictions,
    "Probability": test_probabilities
})

comparison_df["Actual Label"] = comparison_df["Actual"].map({
    0: "Normal",
    1: "Suspicious"
})

comparison_df["Predicted Label"] = comparison_df["Predicted"].map({
    0: "Normal",
    1: "Suspicious"
})

comparison_df["Correct"] = (
    comparison_df["Actual"]
    == comparison_df["Predicted"]
)

print("\nPredicted vs Actual - First 20 Records")

print(
    comparison_df.head(20).to_string(
        index=False
    )
)

correct_predictions = comparison_df["Correct"].sum()
incorrect_predictions = (
    len(comparison_df)
    - correct_predictions
)

print("\nTotal Test Records:", len(comparison_df))
print("Correct Predictions:", correct_predictions)
print("Incorrect Predictions:", incorrect_predictions)
# ============================================================
# 14. METRICS
# ============================================================

accuracy = accuracy_score(
    y_test,
    test_predictions
)

precision = precision_score(
    y_test,
    test_predictions,
    zero_division=0
)

recall = recall_score(
    y_test,
    test_predictions,
    zero_division=0
)

f1 = f1_score(
    y_test,
    test_predictions,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    test_probabilities
)

pr_auc = average_precision_score(
    y_test,
    test_probabilities
)


# ============================================================
# 15. RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("FINAL TEST RESULTS")
print("=" * 70)

print(
    "Threshold :", FINAL_THRESHOLD
)

print(
    "Accuracy  :",
    round(accuracy, 4)
)

print(
    "Precision :",
    round(precision, 4)
)

print(
    "Recall    :",
    round(recall, 4)
)

print(
    "F1 Score  :",
    round(f1, 4)
)

print(
    "ROC-AUC   :",
    round(roc_auc, 4)
)

print(
    "PR-AUC    :",
    round(pr_auc, 4)
)


# ============================================================
# 16. CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    test_predictions
)

print("\nConfusion Matrix:")
print(cm)


# ============================================================
# 17. CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        test_predictions,
        target_names=[
            "Normal",
            "Suspicious"
        ],
        digits=4
    )
)


# ============================================================
# 18. SAVE FINAL MODEL
# ============================================================

joblib.dump(
    model,
    "final_xgboost_model2.pkl"
)

joblib.dump(
    preprocessor,
    "final_preprocessor2.pkl"
)

joblib.dump(
    FINAL_THRESHOLD,
    "final_threshold2.pkl"
)

print("\nFinal model saved successfully.")