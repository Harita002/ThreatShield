import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score
)

from xgboost import XGBClassifier


# ============================================================
# 1. LOAD DATASET
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
# 4. FEATURES AND TARGET
# ============================================================

X = df.drop(
    columns=["is_malicious"]
)

y = df["is_malicious"].astype(int)


# ============================================================
# 5. CATEGORICAL FEATURES
# ============================================================

categorical_features = X.select_dtypes(
    include=["object", "string"]
).columns.tolist()


# ============================================================
# 6. TRAIN / VALIDATION / TEST SPLIT
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

print("\nClass Imbalance:")
print("Normal:", negative_count)
print("Suspicious:", positive_count)
print(
    "scale_pos_weight:",
    round(scale_pos_weight, 4)
)


# ============================================================
# 9. PARAMETER CONFIGURATIONS
# ============================================================

parameter_sets = [

    {
        "name": "Model_A",
        "n_estimators": 400,
        "max_depth": 6,
        "learning_rate": 0.05,
        "min_child_weight": 3,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "reg_lambda": 1.0,
        "reg_alpha": 0
    },

    {
        "name": "Model_B",
        "n_estimators": 500,
        "max_depth": 5,
        "learning_rate": 0.05,
        "min_child_weight": 3,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "reg_lambda": 2.0,
        "reg_alpha": 0.1
    },

    {
        "name": "Model_C",
        "n_estimators": 500,
        "max_depth": 7,
        "learning_rate": 0.03,
        "min_child_weight": 5,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "reg_lambda": 2.0,
        "reg_alpha": 0.1
    },

    {
        "name": "Model_D",
        "n_estimators": 600,
        "max_depth": 5,
        "learning_rate": 0.03,
        "min_child_weight": 5,
        "subsample": 0.9,
        "colsample_bytree": 0.9,
        "reg_lambda": 3.0,
        "reg_alpha": 0.1
    }
]


# ============================================================
# 10. FIND BEST THRESHOLD
# ============================================================

def find_best_threshold(
    y_true,
    probabilities
):

    results = []

    for threshold in np.arange(
        0.20,
        0.81,
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

    result_df = pd.DataFrame(
        results
    )

    best = result_df.loc[
        result_df["f1"].idxmax()
    ]

    return best


# ============================================================
# 11. TRAIN AND VALIDATE EACH MODEL
# ============================================================

results = []

best_model = None
best_pipeline = None
best_f1 = -1
best_threshold = None


for params in parameter_sets:

    print("\n")
    print("=" * 70)
    print(
        "TRAINING:",
        params["name"]
    )
    print("=" * 70)

    model = XGBClassifier(

        n_estimators=params["n_estimators"],

        max_depth=params["max_depth"],

        learning_rate=params["learning_rate"],

        min_child_weight=params["min_child_weight"],

        subsample=params["subsample"],

        colsample_bytree=params["colsample_bytree"],

        reg_lambda=params["reg_lambda"],

        reg_alpha=params["reg_alpha"],

        scale_pos_weight=scale_pos_weight,

        objective="binary:logistic",

        eval_metric="logloss",

        random_state=42,

        n_jobs=-1
    )


    pipeline = Pipeline(
        steps=[
            (
                "preprocessing",
                preprocessor
            ),
            (
                "model",
                model
            )
        ]
    )


    print("Training...")

    pipeline.fit(
        X_train,
        y_train
    )

    print("Training completed.")


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    val_probabilities = (
        pipeline.predict_proba(
            X_val
        )[:, 1]
    )


    best = find_best_threshold(
        y_val,
        val_probabilities
    )


    threshold = float(
        best["threshold"]
    )

    precision = float(
        best["precision"]
    )

    recall = float(
        best["recall"]
    )

    f1 = float(
        best["f1"]
    )


    roc_auc = roc_auc_score(
        y_val,
        val_probabilities
    )

    pr_auc = average_precision_score(
        y_val,
        val_probabilities
    )


    print("\nValidation Results:")

    print(
        "Threshold:",
        threshold
    )

    print(
        "Precision:",
        round(
            precision,
            4
        )
    )

    print(
        "Recall:",
        round(
            recall,
            4
        )
    )

    print(
        "F1:",
        round(
            f1,
            4
        )
    )

    print(
        "ROC-AUC:",
        round(
            roc_auc,
            4
        )
    )

    print(
        "PR-AUC:",
        round(
            pr_auc,
            4
        )
    )


    results.append(
        {
            "Model": params["name"],
            "Threshold": threshold,
            "Precision": precision,
            "Recall": recall,
            "F1": f1,
            "ROC-AUC": roc_auc,
            "PR-AUC": pr_auc
        }
    )


    # --------------------------------------------------------
    # KEEP BEST MODEL
    # --------------------------------------------------------

    if f1 > best_f1:

        best_f1 = f1

        best_model = params

        best_pipeline = pipeline

        best_threshold = threshold


# ============================================================
# 12. SHOW COMPARISON
# ============================================================

comparison = pd.DataFrame(
    results
)

comparison = comparison.sort_values(
    by="F1",
    ascending=False
)


print("\n")
print("=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print(
    comparison.to_string(
        index=False
    )
)


# ============================================================
# 13. BEST MODEL
# ============================================================

print("\n")
print("=" * 70)
print("BEST MODEL")
print("=" * 70)

print(
    "Model:",
    best_model["name"]
)

print(
    "Threshold:",
    best_threshold
)

print(
    "Validation F1:",
    round(
        best_f1,
        4
    )
)

print("\nParameters:")

for key, value in best_model.items():

    if key != "name":

        print(
            key,
            "=",
            value
        )


# ============================================================
# 14. SAVE BEST MODEL
# ============================================================

import joblib

joblib.dump(
    best_pipeline,
    "best_xgboost_pipeline.pkl"
)

joblib.dump(
    best_threshold,
    "best_xgboost_threshold.pkl"
)

print("\nBest model saved successfully.")