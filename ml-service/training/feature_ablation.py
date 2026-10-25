import pandas as pd
import numpy as np



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
    confusion_matrix
)

from xgboost import XGBClassifier


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "../../dataset/insider_threat_clean_dataset.csv"

RANDOM_STATE = 42

FINAL_THRESHOLD = 0.65


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("THREATSHIELD - FEATURE GROUP ABLATION")
print("=" * 70)

df = pd.read_csv(DATA_PATH)

print("\nOriginal dataset:")
print(df.shape)


# ============================================================
# CLEAN DATA
# ============================================================

df.columns = df.columns.str.strip()

for col in df.select_dtypes(
    include=["object", "string"]
).columns:

    df[col] = df[col].str.strip()


df = df.dropna()
df = df.drop_duplicates()


# ============================================================
# FEATURE ENGINEERING
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
# TARGET
# ============================================================

X = df.drop(
    columns=["is_malicious"]
)

y = df["is_malicious"].astype(int)


# ============================================================
# OFFICIAL 60 / 20 / 20 SPLIT
# ============================================================

X_temp, X_test, y_temp, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    stratify=y,

    random_state=RANDOM_STATE
)


X_train, X_val, y_train, y_val = train_test_split(

    X_temp,
    y_temp,

    test_size=0.25,

    stratify=y_temp,

    random_state=RANDOM_STATE
)


print("\nDataset Split:")
print("Training   :", X_train.shape)
print("Validation :", X_val.shape)
print("Testing    :", X_test.shape)


# ============================================================
# FEATURE GROUPS
# ============================================================

FEATURE_GROUPS = {

    "Origin Country": [
        "employee_origin_country"
    ],

    "Position": [
        "employee_position"
    ],

    "Department": [
        "employee_department"
    ],

    "Campus": [
        "employee_campus"
    ]
}


# ============================================================
# MODEL FUNCTION
# ============================================================

def evaluate_model(
    model_name,
    features_to_remove
):

    print("\n")
    print("=" * 70)
    print(model_name)
    print("=" * 70)


    # --------------------------------------------------------
    # SELECT FEATURES
    # --------------------------------------------------------

    selected_features = [
        col
        for col in X.columns
        if col not in features_to_remove
    ]


    X_train_current = (
        X_train[selected_features]
    )

    X_val_current = (
        X_val[selected_features]
    )

    X_test_current = (
        X_test[selected_features]
    )


    # --------------------------------------------------------
    # CATEGORICAL FEATURES
    # --------------------------------------------------------

    categorical_features = (
        X_train_current
        .select_dtypes(
            include=["object", "string"]
        )
        .columns
        .tolist()
    )


    # --------------------------------------------------------
    # PREPROCESSOR
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # PREPROCESS
    # --------------------------------------------------------

    X_train_processed = (
        preprocessor.fit_transform(
            X_train_current
        )
    )

    X_val_processed = (
        preprocessor.transform(
            X_val_current
        )
    )

    X_test_processed = (
        preprocessor.transform(
            X_test_current
        )
    )


    # --------------------------------------------------------
    # CLASS IMBALANCE
    # --------------------------------------------------------

    negative_count = (
        y_train == 0
    ).sum()

    positive_count = (
        y_train == 1
    ).sum()

    scale_pos_weight = (
        negative_count /
        positive_count
    )


    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

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

        random_state=RANDOM_STATE,

        n_jobs=-1
    )


    print("\nTraining...")

    model.fit(
        X_train_processed,
        y_train
    )

    print("Training completed.")


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    val_probabilities = (
        model.predict_proba(
            X_val_processed
        )[:, 1]
    )

    val_predictions = (
        val_probabilities >= FINAL_THRESHOLD
    ).astype(int)


    val_f1 = f1_score(
        y_val,
        val_predictions,
        zero_division=0
    )


    # --------------------------------------------------------
    # TEST
    # --------------------------------------------------------

    test_probabilities = (
        model.predict_proba(
            X_test_processed
        )[:, 1]
    )

    test_predictions = (
        test_probabilities >= FINAL_THRESHOLD
    ).astype(int)


    # --------------------------------------------------------
    # TEST METRICS
    # --------------------------------------------------------

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


    print("\nValidation F1:")
    print(
        round(val_f1, 4)
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
        "F1       :",
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

        "Model": model_name,

        "Removed": (
            ", ".join(
                features_to_remove
            )
            if features_to_remove
            else "None"
        ),

        "Validation_F1": val_f1,

        "Accuracy": accuracy,

        "Precision": precision,

        "Recall": recall,

        "F1": f1,

        "ROC-AUC": roc_auc,

        "PR-AUC": pr_auc
    }


# ============================================================
# RUN ABLATION EXPERIMENTS
# ============================================================

results = []


# ------------------------------------------------------------
# BASELINE
# ------------------------------------------------------------

results.append(
    evaluate_model(
        "Model 0 - All Features",
        []
    )
)


# ------------------------------------------------------------
# REMOVE ORIGIN COUNTRY
# ------------------------------------------------------------

results.append(
    evaluate_model(
        "Model 1 - Without Origin Country",
        FEATURE_GROUPS[
            "Origin Country"
        ]
    )
)


# ------------------------------------------------------------
# REMOVE POSITION
# ------------------------------------------------------------

results.append(
    evaluate_model(
        "Model 2 - Without Position",
        FEATURE_GROUPS[
            "Position"
        ]
    )
)


# ------------------------------------------------------------
# REMOVE DEPARTMENT
# ------------------------------------------------------------

results.append(
    evaluate_model(
        "Model 3 - Without Department",
        FEATURE_GROUPS[
            "Department"
        ]
    )
)


# ------------------------------------------------------------
# REMOVE CAMPUS
# ------------------------------------------------------------

results.append(
    evaluate_model(
        "Model 4 - Without Campus",
        FEATURE_GROUPS[
            "Campus"
        ]
    )
)


# ============================================================
# COMPARISON
# ============================================================

comparison = pd.DataFrame(
    results
)


print("\n")
print("=" * 90)
print("FEATURE GROUP ABLATION COMPARISON")
print("=" * 90)

print(
    comparison.to_string(
        index=False
    )
)


# ============================================================
# SAVE RESULTS
# ============================================================

comparison.to_csv(
    "feature_ablation_results.csv",
    index=False
)


print("\n")
print(
    "Saved: feature_ablation_results.csv"
)