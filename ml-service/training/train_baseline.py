import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
# bundles preprocessing + model together as one single object.
from sklearn.ensemble import RandomForestClassifier

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


# ============================================================
# 1. LOAD ORIGINAL DATASET
# ============================================================

DATA_PATH = "../../dataset/insider_threat_clean_dataset.csv"

df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("ORIGINAL DATASET")
print("=" * 60)

print("Shape:", df.shape)
print("\nClass Distribution:")
print(df["is_malicious"].value_counts())


# ============================================================
# 2. BASIC CLEANING
# ============================================================

df.columns = df.columns.str.strip()

for col in df.select_dtypes(include=["object", "string"]).columns:
    df[col] = df[col].str.strip()


# Remove completely invalid rows
df = df.dropna()

# Remove duplicates
df = df.drop_duplicates()

print("\nAfter Cleaning:")
print("Shape:", df.shape)

print("\nClass Distribution:")
print(df["is_malicious"].value_counts())


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
# 4. SEPARATE FEATURES AND TARGET
# ============================================================

X = df.drop(columns=["is_malicious"])
y = df["is_malicious"].astype(int)


# ============================================================
# 5. IDENTIFY CATEGORICAL FEATURES
# ============================================================

categorical_features = X.select_dtypes(
    include=["object", "string"]
).columns.tolist()

numerical_features = [
    col for col in X.columns
    if col not in categorical_features
]


print("\nCategorical Features:")
print(categorical_features)

print("\nNumerical Features:")
print(numerical_features)


# ============================================================
# 6. TRAIN / VALIDATION / TEST SPLIT
# ============================================================

# First: 80% train+validation, 20% untouched test
X_temp, X_test, y_temp, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=42
)

# Then: 75% train, 25% validation from remaining 80%
# Final proportions:
# Train      = 60%
# Validation = 20%
# Test       = 20%

X_train, X_val, y_train, y_val = train_test_split(
    X_temp,
    y_temp,
    test_size=0.25,
    stratify=y_temp,
    random_state=42
)


print("\nDataset Split:")
print("Training:", X_train.shape)
print("Validation:", X_val.shape)
print("Testing:", X_test.shape)


print("\nTraining Class Distribution:")
print(y_train.value_counts())

print("\nValidation Class Distribution:")
print(y_val.value_counts())

print("\nTesting Class Distribution:")
print(y_test.value_counts())


# ============================================================
# 7. PREPROCESSING
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
                # . Imagine your model was trained on employees from ["Engineering", "Sales", "IT"] departments only.
                # . Now, during inference, you encounter a new department "Marketing".
                # . If you don't handle unknown categories, the model will throw an error.
            ),
            categorical_features
        )
    ],
    remainder="passthrough"
)


# ============================================================
# 8. RANDOM FOREST BASELINE
# ============================================================

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,

    # Important for class imbalance
    class_weight="balanced",

    random_state=42,
    n_jobs=-1
)


# ============================================================
# 9. COMPLETE ML PIPELINE
# ============================================================

pipeline = Pipeline(
    steps=[
        ("preprocessing", preprocessor),
        ("model", model)
    ]
)


# ============================================================
# 10. TRAIN
# ============================================================

print("\nTraining Random Forest...")

pipeline.fit(
    X_train,
    y_train
)

print("Training completed.")


# ============================================================
# 11. VALIDATION PROBABILITIES
# ============================================================

val_probabilities = pipeline.predict_proba(X_val)[:, 1]


# ============================================================
# 12. FIND BEST THRESHOLD USING VALIDATION SET
# ============================================================

threshold_results = []

for threshold in np.arange(0.20, 0.71, 0.01):

    val_predictions = (
        val_probabilities >= threshold
    ).astype(int)

    precision = precision_score(
        y_val,
        val_predictions,
        zero_division=0
    )

    recall = recall_score(
        y_val,
        val_predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_val,
        val_predictions,
        zero_division=0
    )

    threshold_results.append(
        {
            "threshold": round(threshold, 2),
            "precision": precision,
            "recall": recall,
            "f1": f1
        }
    )


threshold_df = pd.DataFrame(
    threshold_results
)

best_row = threshold_df.loc[
    threshold_df["f1"].idxmax()
]

BEST_THRESHOLD = float(
    best_row["threshold"]
)


print("\nBest Validation Threshold:")
print("Threshold :", BEST_THRESHOLD)
print("Precision :", round(best_row["precision"], 4))
print("Recall    :", round(best_row["recall"], 4))
print("F1 Score  :", round(best_row["f1"], 4))


# ============================================================
# 13. FINAL TEST EVALUATION
# ============================================================

test_probabilities = pipeline.predict_proba(
    X_test
)[:, 1]

test_predictions = (
    test_probabilities >= BEST_THRESHOLD
).astype(int)


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


print("\n" + "=" * 60)
print("FINAL TEST PERFORMANCE")
print("=" * 60)

print("Accuracy :", round(accuracy, 4))
print("Precision:", round(precision, 4))
print("Recall   :", round(recall, 4))
print("F1 Score :", round(f1, 4))
print("ROC-AUC  :", round(roc_auc, 4))
print("PR-AUC   :", round(pr_auc, 4))


# ============================================================
# 15. CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    test_predictions
)

print("\nConfusion Matrix:")
print(cm)


# ============================================================
# 16. CLASSIFICATION REPORT
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
# 17. SAVE MODEL
# ============================================================

joblib.dump(
    pipeline,
    "threatshield_rf_pipeline.pkl"
)

joblib.dump(
    BEST_THRESHOLD,
    "decision_threshold.pkl"
)

print("\nModel saved successfully.")