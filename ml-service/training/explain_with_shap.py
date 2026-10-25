
import pandas as pd
import numpy as np
import joblib
import shap
import json
from sklearn.model_selection import train_test_split


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = "final_xgboost_model.pkl"
PREPROCESSOR_PATH = "final_preprocessor.pkl"
THRESHOLD_PATH = "final_threshold.pkl"

DATA_PATH = "../../dataset/insider_threat_clean_dataset.csv"

SAMPLE_SIZE = 100
EMPLOYEE_INDEX = 0


# ============================================================
# USER-FACING BEHAVIORAL FEATURES
# ============================================================

BEHAVIORAL_FEATURES = {
    "total_printed_pages",
    "num_printed_pages_off_hours",
    "off_hour_print_ratio",
    "total_files_burned",
    "burned_from_other",
    "burn_ratio",
    "num_entries",
    "num_unique_campus",
    "late_exit_flag",
    "entry_during_weekend",
    "is_abroad",
    "trip_day_number",
    "mobility_risk",
    "behavior_risk_score",
    "access_frequency_score"
}


# ============================================================
# 1. LOAD MODEL
# ============================================================

model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)
threshold = joblib.load(THRESHOLD_PATH)

print("=" * 70)
print("THREATSHIELD - IMPROVED SHAP ENGINE")
print("=" * 70)

print("Model loaded.")
print("Classification threshold:", threshold)


# ============================================================
# 2. LOAD DATASET
# ============================================================

df = pd.read_csv(DATA_PATH)

print("\nOriginal dataset shape:", df.shape)


# ============================================================
# 3. CLEAN DATA
# ============================================================

df.columns = df.columns.str.strip()

for col in df.select_dtypes(
    include=["object", "string"]
).columns:

    df[col] = df[col].str.strip()


df = df.dropna()
df = df.drop_duplicates()


# ============================================================
# 4. FEATURE ENGINEERING
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
# 5. SEPARATE TARGET
# ============================================================

X = df.drop(
    columns=["is_malicious"]
)

y = df["is_malicious"].astype(int)


# ============================================================
# 6. SAME TRAIN / VALIDATION / TEST SPLIT
# ============================================================

X_temp, X_test, y_temp, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    # (preserves class balance)
    random_state=42
)

X_train, X_val, y_train, y_val = train_test_split(
    X_temp,
    y_temp,
    test_size=0.25,
    stratify=y_temp,
    random_state=42
)


X_test = X_test.reset_index(drop=True)
y_test = y_test.reset_index(drop=True)


# ============================================================
# 7. TRANSFORM TEST DATA
# ============================================================

print("\nTransforming test data...")

X_test_processed = preprocessor.transform(
    X_test
    # not .fit_transform(), to avoid data leakage
)

print(
    "Processed shape:",
    X_test_processed.shape
)


# ============================================================
# 8. CONVERT SPARSE → DENSE
# ============================================================

if hasattr(
    X_test_processed,
    "toarray"
):

    X_test_dense = (
        X_test_processed.toarray()
    )

else:

    X_test_dense = X_test_processed


print(
    "Dense shape:",
    X_test_dense.shape
)


# ============================================================
# 9. GET FEATURE NAMES
# ============================================================

feature_names = (
    preprocessor
    .get_feature_names_out()
)


# ============================================================
# 10. CREATE SHAP EXPLAINER
# ============================================================

print("\nCreating SHAP TreeExplainer...")

explainer = shap.TreeExplainer(
    model
)

print("SHAP explainer created.")


# ============================================================
# 11. SELECT SAMPLE
# ============================================================

sample_size = min(
    SAMPLE_SIZE,
    len(X_test_dense)
)

X_sample = X_test_dense[
    :sample_size
]

raw_sample = X_test.iloc[
    :sample_size
].copy()

y_sample = y_test.iloc[
    :sample_size
]


# ============================================================
# 12. CALCULATE SHAP VALUES
# ============================================================

print("\nCalculating SHAP values...")

shap_values = explainer.shap_values(
    X_sample
)

if isinstance(
    shap_values,
    list
):

    shap_values = shap_values[1]


print("SHAP calculation completed.")


# ============================================================
# 13. MAP ENCODED FEATURE TO ORIGINAL FEATURE
# ============================================================

def get_base_feature(
    feature_name
):

    feature_name = feature_name.replace(
        "categorical__",
        ""
    )

    feature_name = feature_name.replace(
        "remainder__",
        ""
    )

    # Handle one-hot categorical features
    categorical_columns = [
        "employee_department",
        "employee_campus",
        "employee_position",
        "employee_origin_country"
    ]

    for col in categorical_columns:

        prefix = col + "_"

        if feature_name.startswith(prefix):

            return col

    return feature_name


# ============================================================
# 14. GLOBAL SHAP IMPORTANCE
# ============================================================

global_rows = []

for index, feature in enumerate(
    feature_names
):

    base_feature = get_base_feature(
        feature
    )

    mean_abs_value = np.mean(
        np.abs(
            shap_values[:, index]
        )
    )

    global_rows.append(
        {
            "Encoded_Feature": feature,
            "Base_Feature": base_feature,
            "Mean_Absolute_SHAP": mean_abs_value
        }
    )


global_encoded = pd.DataFrame(
    global_rows
)


# Aggregate one-hot features back
# into their original feature.

global_importance = (
    global_encoded
    .groupby(
        "Base_Feature",
        as_index=False
    )[
        "Mean_Absolute_SHAP"
    ]
    .sum()
    .sort_values(
        "Mean_Absolute_SHAP",
        ascending=False
    )
)


print("\n")
print("=" * 70)
print("GLOBAL SHAP IMPORTANCE")
print("=" * 70)

print(
    global_importance
    .head(20)
    .to_string(
        index=False
    )
)


# ============================================================
# 15. INDIVIDUAL EMPLOYEE
# ============================================================

employee_index = EMPLOYEE_INDEX

employee_probability = (
    model.predict_proba(
        X_sample[
            employee_index:
            employee_index + 1
        ]
    )[0][1]
)

risk_score = (
    employee_probability * 100
)


if employee_probability >= threshold:

    prediction = "SUSPICIOUS"

else:

    prediction = "NORMAL"


# ============================================================
# 16. PRINT ACTUAL PROBABILITY
# ============================================================

print("\n")
print("=" * 70)
print("INDIVIDUAL EMPLOYEE")
print("=" * 70)

print(
    "Prediction:",
    prediction
)

print(
    f"Probability: {employee_probability:.10f}"
)

print(
    f"Risk Score: {risk_score:.6f}%"
)

print(
    "Threshold:",
    threshold
)


# ============================================================
# 17. INDIVIDUAL SHAP CONTRIBUTIONS
# ============================================================

employee_rows = []

for index, feature in enumerate(
    feature_names
):

    base_feature = get_base_feature(
        feature
    )

    shap_value = (
        shap_values[
            employee_index,
            index
        ]
    )

    # For one-hot features:
    # only show the active category.
    if feature.startswith(
        "categorical__"
    ):

        encoded_value = (
            X_sample[
                employee_index,
                index
            ]
        )

        if encoded_value == 0:

            continue

    employee_rows.append(
        {
            "Encoded_Feature": feature,
            "Base_Feature": base_feature,
            "SHAP_Value": shap_value
        }
    )


employee_explanation = pd.DataFrame(
    employee_rows
)


# ============================================================
# 18. AGGREGATE BY ORIGINAL FEATURE
# ============================================================

employee_grouped = (
    employee_explanation
    .groupby(
        "Base_Feature",
        as_index=False
    )[
        "SHAP_Value"
    ]
    .sum()
)


# ============================================================
# 19. ADD ACTUAL RAW VALUES
# ============================================================

actual_values = (
    X_test.iloc[
        employee_index
    ]
)


def get_display_value(
    feature
):

    if feature in actual_values:

        value = actual_values[
            feature
        ]

        return value

    return "N/A"


employee_grouped[
    "Feature_Value"
] = employee_grouped[
    "Base_Feature"
].apply(
    get_display_value
)


# ============================================================
# 20. DIRECTION
# ============================================================

employee_grouped[
    "Direction"
] = np.where(
    employee_grouped[
        "SHAP_Value"
    ] > 0,
    "INCREASED_RISK",
    "DECREASED_RISK"
)


employee_grouped[
    "Absolute_SHAP"
] = np.abs(
    employee_grouped[
        "SHAP_Value"
    ]
)


employee_grouped = (
    employee_grouped
    .sort_values(
        "Absolute_SHAP",
        ascending=False
    )
)


# ============================================================
# 21. USER-FACING BEHAVIORAL EXPLANATIONS
# ============================================================

behavioral_explanations = (
    employee_grouped[
        employee_grouped[
            "Base_Feature"
        ].isin(
            BEHAVIORAL_FEATURES
        )
    ]
)


# ============================================================
# 22. TOP POSITIVE BEHAVIORAL FACTORS
# ============================================================

positive_factors = (
    behavioral_explanations[
        behavioral_explanations[
            "SHAP_Value"
        ] > 0
    ]
    .sort_values(
        "Absolute_SHAP",
        ascending=False
    )
    .head(5)
)


print("\n")
print("=" * 70)
print("TOP BEHAVIORAL FACTORS INCREASING RISK")
print("=" * 70)

if positive_factors.empty:

    print(
        "No significant positive behavioral factors found."
    )

else:

    print(
        positive_factors[
            [
                "Base_Feature",
                "Feature_Value",
                "SHAP_Value",
                "Direction"
            ]
        ].to_string(
            index=False
        )
    )


# ============================================================
# 23. TOP NEGATIVE BEHAVIORAL FACTORS
# ============================================================

negative_factors = (
    behavioral_explanations[
        behavioral_explanations[
            "SHAP_Value"
        ] < 0
    ]
    .sort_values(
        "Absolute_SHAP",
        ascending=False
    )
    .head(5)
)


print("\n")
print("=" * 70)
print("TOP BEHAVIORAL FACTORS DECREASING RISK")
print("=" * 70)

if negative_factors.empty:

    print(
        "No significant negative behavioral factors found."
    )

else:

    print(
        negative_factors[
            [
                "Base_Feature",
                "Feature_Value",
                "SHAP_Value",
                "Direction"
            ]
        ].to_string(
            index=False
        )
    )


# ============================================================
# 24. SAVE GLOBAL RESULTS
# ============================================================

global_importance.to_csv(
    "shap_global_importance.csv",
    index=False
)


# ============================================================
# 25. SAVE COMPLETE INDIVIDUAL RESULTS
# ============================================================

employee_grouped[
    [
        "Base_Feature",
        "Feature_Value",
        "SHAP_Value",
        "Direction"
    ]
].to_csv(
    "shap_employee_explanation2.csv",
    index=False
)


# ============================================================
# 26. SAVE USER-FACING BEHAVIORAL RESULTS
# ============================================================

behavioral_explanations[
    [
        "Base_Feature",
        "Feature_Value",
        "SHAP_Value",
        "Direction"
    ]
].to_csv(
    "shap_behavioral_explanation2.csv",
    index=False
)

# ============================================================
# 28. CREATE STRUCTURED JSON EXPLANATION
# ============================================================

risk_factors = []

for _, row in positive_factors.iterrows():

    risk_factors.append(
        {
            "feature": row["Base_Feature"],
            "value": row["Feature_Value"],
            "shap_value": round(
                float(row["SHAP_Value"]),
                6
            ),
            "direction": "INCREASED_RISK"
        }
    )


protective_factors = []

for _, row in negative_factors.iterrows():

    protective_factors.append(
        {
            "feature": row["Base_Feature"],
            "value": row["Feature_Value"],
            "shap_value": round(
                float(row["SHAP_Value"]),
                6
            ),
            "direction": "DECREASED_RISK"
        }
    )


# ============================================================
# RISK LEVEL
# ============================================================

if risk_score >= 80:

    risk_level = "HIGH"

elif risk_score >= 50:

    risk_level = "MEDIUM"

else:

    risk_level = "LOW"


# ============================================================
# FINAL EXPLANATION OBJECT
# ============================================================

explanation = {

    "prediction": prediction,

    "probability": round(
        float(employee_probability),
        10
    ),

    "risk_score": round(
        float(risk_score),
        6
    ),

    "risk_level": risk_level,

    "classification_threshold": threshold,

    "risk_factors": risk_factors,

    "protective_factors": protective_factors
}


# ============================================================
# SAVE JSON
# ============================================================

with open(
    "shap_employee_explanation.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        explanation,
        file,
        indent=4
    )


print(
    "Saved: shap_employee_explanation.json"
)
# ============================================================
# 27. COMPLETION
# ============================================================

print("\n")
print("=" * 70)
print("SHAP ENGINE COMPLETED")
print("=" * 70)

print(
    "Saved: shap_global_importance2.csv"
)

print(
    "Saved: shap_employee_explanation2.csv"
)

print(
    "Saved: shap_behavioral_explanation2.csv"
)
