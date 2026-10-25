import pandas as pd

from inference.predictor import predict_employee
from validation.dataset_validator import validate_dataset


# ============================================================
# BATCH PREDICTION
# ============================================================

def predict_batch(df):

    # --------------------------------------------------------
    # Validate dataset
    # --------------------------------------------------------

    validation_result = validate_dataset(df)

    if not validation_result["valid"]:

        return {
            "success": False,
            "validation": validation_result
        }


    # --------------------------------------------------------
    # Clean copy
    # --------------------------------------------------------

    df = df.copy()

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )


    # --------------------------------------------------------
    # Remove duplicate records
    # --------------------------------------------------------

    df = df.drop_duplicates().reset_index(
        drop=True
    )


    # --------------------------------------------------------
    # Employee identifier
    # --------------------------------------------------------

    if "employee_id" in df.columns:

        employee_ids = (
            df["employee_id"]
            .astype(str)
            .tolist()
        )

    else:

        employee_ids = [
            f"EMP-{i + 1:05d}"
            for i in range(len(df))
        ]


    # --------------------------------------------------------
    # Analyze EVERY employee
    # --------------------------------------------------------

    all_results = []

    for index, row in df.iterrows():

        employee_data = row.to_dict()

        result = predict_employee(
            employee_data,
            explain=False
        )

        result["employee_id"] = (
            employee_ids[index]
        )
        result["employee_data"] = employee_data

        all_results.append(
            result
        )


    # --------------------------------------------------------
    # Convert to DataFrame
    # --------------------------------------------------------

    results_df = pd.DataFrame(
        all_results
    )


    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    total_analyzed = len(
        results_df
    )

    suspicious_results = (
        results_df[
            results_df["prediction"]
            == "SUSPICIOUS"
        ]
        .copy()
    )


    suspicious_count = len(
        suspicious_results
    )


    high_risk_count = len(
        results_df[
            results_df["risk_level"]
            == "HIGH"
        ]
    )


    medium_risk_count = len(
        results_df[
            results_df["risk_level"]
            == "MEDIUM"
        ]
    )


    low_risk_count = len(
        results_df[
            results_df["risk_level"]
            == "LOW"
        ]
    )


    # --------------------------------------------------------
    # Sort suspicious employees
    # --------------------------------------------------------

    suspicious_results = (
        suspicious_results
        .sort_values(
            by="risk_score",
            ascending=False
        )
    )


    # --------------------------------------------------------
    # Dashboard display rule
    # --------------------------------------------------------

    if total_analyzed <= 10:

        dashboard_results = (
            results_df
            .sort_values(
                by="risk_score",
                ascending=False
            )
        )

        display_mode = "ALL_RESULTS"

    else:

        dashboard_results = (
            suspicious_results
        )

        display_mode = "SUSPICIOUS_ONLY"


    # --------------------------------------------------------
    # Convert records to JSON-safe format
    # --------------------------------------------------------

    all_results_json = (
        results_df
        .to_dict(
            orient="records"
            # converts each DataFrame into a list of dicts — one dict per row,
        )
    )


    dashboard_results_json = (
        dashboard_results
        .to_dict(
            orient="records"
        )
    )


    suspicious_results_json = (
        suspicious_results
        .to_dict(
            orient="records"
        )
    )


    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {

        "success": True,

        "validation":
            validation_result,

        "summary": {

            "total_analyzed":
                total_analyzed,

            "suspicious_count":
                suspicious_count,

            "high_risk_count":
                high_risk_count,

            "medium_risk_count":
                medium_risk_count,

            "low_risk_count":
                low_risk_count
        },

        "display_mode":
            display_mode,

        "dashboard_results":
            dashboard_results_json,

        "suspicious_results":
            suspicious_results_json,

        "all_results":
            all_results_json
    }