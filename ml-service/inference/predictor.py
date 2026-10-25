import os
import sys
import joblib
import pandas as pd
import shap


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(
        0,
        PROJECT_ROOT
    )


# ============================================================
# EXPLANATION ENGINE
# ============================================================

from explanation.explanation_engine import generate_explanation

# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "training",
    "best_xgboost_pipeline.pkl"
)

THRESHOLD_PATH = os.path.join(
    BASE_DIR,
    "training",
    "best_xgboost_threshold.pkl"
)


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading ThreatShield model...")

pipeline = joblib.load(
    MODEL_PATH
)
# ============================================================
# SHAP COMPONENTS
# ============================================================

preprocessor = pipeline.named_steps["preprocessing"]
xgb_model = pipeline.named_steps["model"]

explainer = shap.TreeExplainer(
    xgb_model
)

threshold = float(
    joblib.load(
        THRESHOLD_PATH
    )
)

print(
    f"Model loaded successfully."
)

print(
    f"Classification threshold: {threshold}"
)


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def engineer_features(df):

    df = df.copy()

    # --------------------------------------------------------
    # Clean column names
    # --------------------------------------------------------

    df.columns = (
        df.columns
        .str.strip()
    )


    # --------------------------------------------------------
    # Clean categorical values
    # --------------------------------------------------------

    for col in df.select_dtypes(
        include=["object", "string"]
    ).columns:

        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
        )


    # --------------------------------------------------------
    # Feature 1
    # --------------------------------------------------------

    df["off_hour_print_ratio"] = (

        df["num_printed_pages_off_hours"]

        /

        (
            df["total_printed_pages"]
            + 1
            # to avoid division by zero
        )
    )


    # --------------------------------------------------------
    # Feature 2
    # --------------------------------------------------------

    df["burn_ratio"] = (

        df["total_files_burned"]

        /

        (
            df["num_entries"]
            + 1
        )
    )


    # --------------------------------------------------------
    # Feature 3
    # --------------------------------------------------------

    df["mobility_risk"] = (

        df["num_unique_campus"]

        *

        df["is_abroad"]
    )


    # --------------------------------------------------------
    # Feature 4
    # --------------------------------------------------------

    df["behavior_risk_score"] = (

        df["late_exit_flag"]

        +

        df["entry_during_weekend"]

        +

        df["burned_from_other"]

        +

        df["has_criminal_record"]
    )


    # --------------------------------------------------------
    # Feature 5
    # --------------------------------------------------------

    df["access_frequency_score"] = (

        df["num_entries"]

        /

        (
            df["trip_day_number"]
            + 1
        )
    )


    return df


# ============================================================
# RISK LEVEL
# ============================================================

def get_risk_level(
    risk_score
):

    if risk_score >= 80:

        return "HIGH"

    elif risk_score >= 50:

        return "MEDIUM"

    else:

        return "LOW"

def calculate_shap_explanation(df):

    # Transform raw employee data using
    # the EXACT preprocessing used during training
    transformed_data = preprocessor.transform(df)

    # Convert sparse matrix to dense
    if hasattr(
        transformed_data,
        "toarray"
    ):
        transformed_data = (
            transformed_data.toarray()
        )

    # Calculate SHAP values
    shap_values = explainer.shap_values(
        transformed_data
    )

    # XGBoost binary classification
    if isinstance(shap_values, list):

        shap_values = shap_values[1]

    shap_values = shap_values[0]

    # Get feature names after OneHotEncoding
    feature_names = (
        preprocessor
        .get_feature_names_out()
    )

    explanations = []

    for feature, value, shap_value in zip(
        feature_names,
        transformed_data[0],
        shap_values
    ):

        value = float(value)
        shap_value = float(shap_value)

        # ========================================================
        # IGNORE INACTIVE ONE-HOT CATEGORIES
        # ========================================================
        #
        # OneHotEncoder creates features such as:
        #
        # employee_position_Data Scientist
        # employee_position_Manager
        # employee_position_Engineer
        #
        # Only the active category has value 1.
        #
        # We don't want to tell the user that a category with
        # value 0 caused the employee's risk.
        # ========================================================

        if feature.startswith("categorical__"):

            if value == 0:

                continue

        # ========================================================
        # CLEAN FEATURE NAME
        # ========================================================

        readable_feature = feature

        if readable_feature.startswith("remainder__"):

            readable_feature = readable_feature.replace(
                "remainder__",
                ""
            )

        elif readable_feature.startswith("categorical__"):

            readable_feature = readable_feature.replace(
                "categorical__",
                ""
            )

        # ========================================================
        # DIRECTION
        # ========================================================

        direction = (

            "INCREASED_RISK"

            if shap_value > 0

            else "DECREASED_RISK"
        )


        # ========================================================
        # STORE EXPLANATION
        # ========================================================

        explanations.append({

            "feature":
                readable_feature,

            "value":
                value,

            "shap_value":
                round(
                    shap_value,
                    6
                ),

            "direction":
                direction
        })

    # Sort by absolute SHAP contribution
    explanations.sort(
        key=lambda x:
            abs(x["shap_value"]),
        reverse=True
    )

    return explanations
# ============================================================
# PREDICT ONE EMPLOYEE
# ============================================================

def predict_employee(
    employee_data,explain=True):

    # --------------------------------------------------------
    # Convert input to DataFrame
    # --------------------------------------------------------

    if isinstance(
        employee_data,
        dict
    ):

        df = pd.DataFrame(
            [employee_data]
        )

    elif isinstance(
        employee_data,
        pd.DataFrame
    ):

        df = employee_data.copy()

    else:

        raise TypeError(
            "Input must be a dictionary "
            "or pandas DataFrame."
        )


    # --------------------------------------------------------
    # Feature engineering
    # --------------------------------------------------------

    df = engineer_features(
        df
    )


    # --------------------------------------------------------
    # Remove target if accidentally supplied
    # --------------------------------------------------------

    if "is_malicious" in df.columns:

        df = df.drop(
            columns=["is_malicious"]
        )


    # --------------------------------------------------------
    # MODEL PROBABILITY
    # --------------------------------------------------------

    probabilities = (
        pipeline.predict_proba(
            df
        )[:, 1]
        # probability of class 1 (suspicious/malicious).
    )


    probability = float(
        probabilities[0]
        # grabs the first (only) row, since we're predicting a single employee.
    )


    # --------------------------------------------------------
    # RISK SCORE
    # --------------------------------------------------------

    risk_score = (
        probability * 100
    )


    # --------------------------------------------------------
    # CLASSIFICATION
    # --------------------------------------------------------

    if probability >= threshold:

        prediction = "SUSPICIOUS"

    else:

        prediction = "NORMAL"


    # --------------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------------

    risk_level = get_risk_level(
        risk_score
    )


    # --------------------------------------------------------
    # SHAP EXPLANATION
    # --------------------------------------------------------

    if explain:

        shap_explanations = (
            calculate_shap_explanation(
                df
            )
        )


        # ----------------------------------------------------
        # TOP RISK FACTORS
        # ----------------------------------------------------

        risk_factors = [

            item

            for item in shap_explanations

            if item["direction"]
            == "INCREASED_RISK"

        ][:5]


        # ----------------------------------------------------
        # TOP PROTECTIVE FACTORS
        # ----------------------------------------------------

        protective_factors = [

            item

            for item in shap_explanations

            if item["direction"]
            == "DECREASED_RISK"

        ][:5]

    else:

        risk_factors = []

        protective_factors = []

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    # ============================================================
    # BUILD SHAP RESULT
    # ============================================================

    shap_result = {

        "prediction":
            prediction,

        "probability":
            probability,

        "risk_score":
            risk_score,

        "classification_threshold":
            threshold,

        "risk_factors":
            risk_factors,

        "protective_factors":
            protective_factors
    }


    # ============================================================
    # GENERATE BUSINESS EXPLANATION
    # ============================================================

    if explain:

        explanation = generate_explanation(
            shap_result
        )

        return explanation


    # ============================================================
    # SIMPLE BATCH RESULT
    # ============================================================

    return {

        "prediction":
            prediction,

        "probability":
            probability,

        "risk_score":
            risk_score,

        "risk_level":
            risk_level,

        "classification_threshold":
            threshold
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "=" * 70
    )

    print(
        "THREATSHIELD - DYNAMIC INFERENCE TEST"
    )

    print(
        "=" * 70
    )


    # --------------------------------------------------------
    # Example employee
    # --------------------------------------------------------

    employee = {

        "employee_department":
            "Engineering Department",

        "employee_campus":
            "Campus A",

        "employee_position":
            "Data Scientist",

        "employee_origin_country":
            "India",

        "employee_seniority_years":
            5,

        "is_contractor":
            0,

        "employee_classification":
            3,

        "has_foreign_citizenship":
            0,

        "has_criminal_record":
            0,

        "has_medical_history":
            0,

        "total_printed_pages":
            29,

        "num_printed_pages_off_hours":
            0,

        "total_files_burned":
            7,

        "burned_from_other":
            0,

        "is_abroad":
            0,

        "trip_day_number":
            0,

        "hostility_country_level":
            0,

        "num_entries":
            1,

        "num_unique_campus":
            1,

        "late_exit_flag":
            0,

        "entry_during_weekend":
            0
    }


    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    result = predict_employee(
        employee
    )


    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    import json

    print(
        json.dumps(
            result,
            indent=4
        )
    )