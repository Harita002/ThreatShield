import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix
)

from xgboost import XGBClassifier


# ============================================================
# 1. LOAD DATA
# ============================================================

DATA_PATH = "../../dataset/insider_threat_clean_dataset.csv"

df = pd.read_csv(DATA_PATH)

print("=" * 70)
print("LOADING DATASET")
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
# 4. X / Y
# ============================================================

X = df.drop(columns=["is_malicious"])
y = df["is_malicious"].astype(int)


# ============================================================
# 5. CATEGORICAL / NUMERICAL FEATURES
# ============================================================

categorical_features = X.select_dtypes(
    include=["object", "string"]
).columns.tolist()

numerical_features = [
    col for col in X.columns
    if col not in categorical_features
]


# ============================================================
# 6. SAME STRATIFIED SPLIT AS BASELINE
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
# 7. PREPROCESSOR
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
# 8. RANDOM FOREST
# ============================================================

rf_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)


rf_pipeline = Pipeline(
    steps=[
        ("preprocessing", preprocessor),
        ("model", rf_model)
    ]
)


# ============================================================
# 9. XGBOOST
# ============================================================

negative_count = (y_train == 0).sum()
positive_count = (y_train == 1).sum()

scale_pos_weight = negative_count / positive_count

print("\nXGBoost scale_pos_weight:")
print(round(scale_pos_weight, 4))


xgb_model = XGBClassifier(
    n_estimators=400,
    max_depth=6,
    learning_rate=0.05,

    subsample=0.8,
    colsample_bytree=0.8,

    min_child_weight=3,

    reg_lambda=1.0,

    scale_pos_weight=scale_pos_weight,

    objective="binary:logistic",

    eval_metric="logloss",

    random_state=42,

    n_jobs=-1
)


xgb_pipeline = Pipeline(
    steps=[
        ("preprocessing", preprocessor),
        ("model", xgb_model)
    ]
)


# ============================================================
# 10. TRAIN RANDOM FOREST
# ============================================================

print("\n" + "=" * 70)
print("TRAINING RANDOM FOREST")
print("=" * 70)

rf_pipeline.fit(
    X_train,
    y_train
)

print("Random Forest training completed.")


# ============================================================
# 11. TRAIN XGBOOST
# ============================================================

print("\n" + "=" * 70)
print("TRAINING XGBOOST")
print("=" * 70)

xgb_pipeline.fit(
    X_train,
    y_train
)

print("XGBoost training completed.")


# ============================================================
# 12. THRESHOLD SEARCH FUNCTION
# ============================================================

def find_best_threshold(
    y_true,
    probabilities
):

    results = []

    for threshold in np.arange(
        0.20,
        0.71,
        0.01
    ):

        predictions = (
            probabilities >= threshold
        ).astype(int)

        precision = precision_score(
            y_true,
            predictions,
            zero_division=0
        )

        recall = recall_score(
            y_true,
            predictions,
            zero_division=0
        )

        f1 = f1_score(
            y_true,
            predictions,
            zero_division=0
        )

        results.append(
            {
                "threshold": round(
                    threshold,
                    2
                ),
                "precision": precision,
                "recall": recall,
                "f1": f1
            }
        )

    results_df = pd.DataFrame(results)

    best = results_df.loc[
        results_df["f1"].idxmax()
    ]

    return best


# ============================================================
# 13. EVALUATION FUNCTION
# ============================================================

def evaluate_model(
    name,
    model,
    X_val,
    y_val,
    X_test,
    y_test
):

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    # Validation probabilities
    val_probabilities = model.predict_proba(
        X_val
    )[:, 1]

    # Find threshold ONLY on validation
    best = find_best_threshold(
        y_val,
        val_probabilities
    )

    threshold = float(
        best["threshold"]
    )

    print("\nBest Validation Threshold:")
    print(
        "Threshold:",
        threshold
    )

    print(
        "Validation Precision:",
        round(best["precision"], 4)
    )

    print(
        "Validation Recall:",
        round(best["recall"], 4)
    )

    print(
        "Validation F1:",
        round(best["f1"], 4)
    )


    # ========================================================
    # TEST
    # ========================================================

    test_probabilities = model.predict_proba(
        X_test
    )[:, 1]

    test_predictions = (
        test_probabilities >= threshold
    ).astype(int)


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

    cm = confusion_matrix(
        y_test,
        test_predictions
    )


    print("\nFINAL TEST RESULTS")

    print(
        "Accuracy :",
        round(accuracy, 4)
    )

    print(
        "Precision:",
        round(precision, 4)
    )

    print(
        "Recall   :",
        round(recall, 4)
    )

    print(
        "F1 Score :",
        round(f1, 4)
    )

    print(
        "ROC-AUC  :",
        round(roc_auc, 4)
    )

    print(
        "PR-AUC   :",
        round(pr_auc, 4)
    )

    print("\nConfusion Matrix:")

    print(cm)


    return {
        "Model": name,
        "Threshold": threshold,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "ROC-AUC": roc_auc,
        "PR-AUC": pr_auc
    }


# ============================================================
# 14. EVALUATE BOTH MODELS
# ============================================================

rf_results = evaluate_model(
    "RANDOM FOREST",
    rf_pipeline,
    X_val,
    y_val,
    X_test,
    y_test
)


xgb_results = evaluate_model(
    "XGBOOST",
    xgb_pipeline,
    X_val,
    y_val,
    X_test,
    y_test
)


# ============================================================
# 15. FINAL COMPARISON
# ============================================================

comparison = pd.DataFrame(
    [
        rf_results,
        xgb_results
    ]
)

print("\n" + "=" * 70)
print("FINAL MODEL COMPARISON")
print("=" * 70)

print(
    comparison.to_string(
        index=False
    )
)