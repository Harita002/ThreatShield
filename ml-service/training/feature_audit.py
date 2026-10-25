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

THRESHOLD = 0.65


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("THREATSHIELD - FEATURE AUDIT")
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
# DEFINE FEATURE GROUPS
# ============================================================

BEHAVIORAL_FEATURES = [

    "employee_seniority_years",

    "is_contractor",
    "employee_classification",

    "total_printed_pages",
    "num_printed_pages_off_hours",

    "total_files_burned",
    "burned_from_other",

    "is_abroad",
    "trip_day_number",
    "hostility_country_level",

    "num_entries",
    "num_unique_campus",

    "late_exit_flag",
    "entry_during_weekend",

    "off_hour_print_ratio",
    "burn_ratio",
    "mobility_risk",
    "behavior_risk_score",
    "access_frequency_score"
]


# These are organizational / demographic attributes
# that we want to audit.

ORGANIZATIONAL_FEATURES = [

    "employee_department",
    "employee_campus",
    "employee_position",
    "employee_origin_country"
]


# ============================================================
# CHECK FEATURES
# ============================================================

print("\n")
print("=" * 70)
print("FEATURE GROUPS")
print("=" * 70)

print(
    "\nBehavioral features:",
    len(BEHAVIORAL_FEATURES)
)

print(
    "Organizational/demographic features:",
    len(ORGANIZATIONAL_FEATURES)
)


missing_behavioral = [
    col
    for col in BEHAVIORAL_FEATURES
    if col not in X.columns
]

missing_organizational = [
    col
    for col in ORGANIZATIONAL_FEATURES
    if col not in X.columns
]

if missing_behavioral:

    print(
        "\nMissing behavioral features:",
        missing_behavioral
    )

if missing_organizational:

    print(
        "\nMissing organizational features:",
        missing_organizational
    )


# ============================================================
# DATA SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    stratify=y,

    random_state=RANDOM_STATE
)


# ============================================================
# FUNCTION TO TRAIN MODEL
# ============================================================

def train_and_evaluate(
    model_name,
    X_train,
    X_test,
    y_train,
    y_test
):

    print("\n")
    print("=" * 70)
    print(model_name)
    print("=" * 70)


    categorical_features = (
        X_train
        .select_dtypes(
            include=["object", "string"]
        )
        .columns
        .tolist()
    )


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


    print(
        "\nscale_pos_weight:",
        round(
            scale_pos_weight,
            4
        )
    )


    # --------------------------------------------------------
    # PREPROCESS
    # --------------------------------------------------------

    X_train_processed = (
        preprocessor.fit_transform(
            X_train
        )
    )

    X_test_processed = (
        preprocessor.transform(
            X_test
        )
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

    print(
        "Training completed."
    )


    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    probabilities = (
        model.predict_proba(
            X_test_processed
        )[:, 1]
    )


    predictions = (
        probabilities >= THRESHOLD
    ).astype(int)


    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y_test,
        probabilities
    )

    pr_auc = average_precision_score(
        y_test,
        probabilities
    )

    cm = confusion_matrix(
        y_test,
        predictions
    )


    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    print("\nResults:")

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

    print(
        "\nConfusion Matrix:"
    )

    print(cm)


    return {

        "Model": model_name,

        "Accuracy": accuracy,

        "Precision": precision,

        "Recall": recall,

        "F1": f1,

        "ROC-AUC": roc_auc,

        "PR-AUC": pr_auc

    }


# ============================================================
# MODEL 1 — CURRENT FEATURE SET
# ============================================================

current_result = train_and_evaluate(

    "Current Model - All Features",

    X_train,

    X_test,

    y_train,

    y_test
)


# ============================================================
# MODEL 2 — BEHAVIORAL FEATURES ONLY
# ============================================================

X_behavior = X[
    BEHAVIORAL_FEATURES
]


X_behavior_train, X_behavior_test, \
y_behavior_train, y_behavior_test = train_test_split(

    X_behavior,

    y,

    test_size=0.20,

    stratify=y,

    random_state=RANDOM_STATE
)


behavior_result = train_and_evaluate(

    "Behavioral Features Only",

    X_behavior_train,

    X_behavior_test,

    y_behavior_train,

    y_behavior_test
)


# ============================================================
# FINAL COMPARISON
# ============================================================

comparison = pd.DataFrame(

    [
        current_result,
        behavior_result
    ]
)


print("\n")
print("=" * 70)
print("FEATURE AUDIT COMPARISON")
print("=" * 70)

print(
    comparison.to_string(
        index=False
    )
)


# ============================================================
# SAVE RESULTS
# ============================================================

comparison.to_csv(
    "feature_audit_results.csv",
    index=False
)


print("\n")
print(
    "Saved: feature_audit_results.csv"
)