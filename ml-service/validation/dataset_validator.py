import pandas as pd


# ============================================================
# REQUIRED RAW FEATURES
# ============================================================

REQUIRED_COLUMNS = {

    # Categorical
    "employee_department",
    "employee_campus",
    "employee_position",
    "employee_origin_country",

    # Employee information
    "employee_seniority_years",
    "is_contractor",
    "employee_classification",
    "has_foreign_citizenship",
    "has_criminal_record",
    "has_medical_history",

    # Printing / file activity
    "total_printed_pages",
    "num_printed_pages_off_hours",
    "total_files_burned",
    "burned_from_other",

    # Travel / mobility
    "is_abroad",
    "trip_day_number",
    "hostility_country_level",

    # Access behaviour
    "num_entries",
    "num_unique_campus",
    "late_exit_flag",
    "entry_during_weekend"
}


# ============================================================
# CATEGORICAL FEATURES
# ============================================================

CATEGORICAL_COLUMNS = {

    "employee_department",
    "employee_campus",
    "employee_position",
    "employee_origin_country"
}


# ============================================================
# BINARY FEATURES
# ============================================================

BINARY_COLUMNS = {

    "is_contractor",
    "has_foreign_citizenship",
    "has_criminal_record",
    "has_medical_history",
    "burned_from_other",
    "is_abroad",
    "late_exit_flag",
    "entry_during_weekend"
}


# ============================================================
# VALIDATE DATASET
# ============================================================

def validate_dataset(df):

    errors = []
    warnings = []

    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    if df is None:

        return {
            "valid": False,
            "errors": ["Dataset is empty."],
            "warnings": []
        }


    if df.empty:

        return {
            "valid": False,
            "errors": ["Uploaded dataset contains no records."],
            "warnings": []
        }


    # --------------------------------------------------------
    # Clean column names
    # --------------------------------------------------------

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )


    # --------------------------------------------------------
    # Number of employees
    # --------------------------------------------------------

    total_records = len(df)


    # --------------------------------------------------------
    # Check required columns
    # --------------------------------------------------------

    uploaded_columns = set(
        df.columns
    )

    missing_columns = sorted(
        REQUIRED_COLUMNS - uploaded_columns
    )

    extra_columns = sorted(
        uploaded_columns - REQUIRED_COLUMNS
    )


    if missing_columns:

        errors.append(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )


    # --------------------------------------------------------
    # Extra columns
    # --------------------------------------------------------

    if extra_columns:

        warnings.append(
            f"{len(extra_columns)} extra column(s) "
            "were found and will be ignored by the ML model."
        )


    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    missing_values = (
        df[
            list(
                REQUIRED_COLUMNS
                & uploaded_columns
            )
        ]
        .isnull()
        .sum()
    )

    missing_value_columns = (
        missing_values[
            missing_values > 0
        ]
        .to_dict()
        # converts to {"column_name": missing_count, ...} for easy JSON serialization and readability.
    )


    if missing_value_columns:

        warnings.append(
            "Missing values detected in: "
            + ", ".join(
                missing_value_columns.keys()
            )
        )


    # --------------------------------------------------------
    # Check binary columns
    # --------------------------------------------------------

    for column in (
        BINARY_COLUMNS
        & uploaded_columns
    ):

        values = (
            pd.to_numeric(
                df[column],
                errors="coerce"
                # anything that cannot be converted to a number will become NaN
            )
            .dropna()
            .unique()
        )

        invalid_values = [
            value
            for value in values
            if value not in [0, 1]
        ]

        if invalid_values:

            errors.append(
                f"Column '{column}' contains "
                f"invalid binary values: "
                f"{invalid_values}"
            )


    # --------------------------------------------------------
    # Check categorical columns
    # --------------------------------------------------------

    for column in (
        CATEGORICAL_COLUMNS
        & uploaded_columns
    ):

        if not (
            pd.api.types.is_object_dtype(
                df[column]
            )
            or
            pd.api.types.is_string_dtype(
                df[column]
            )
        ):

            warnings.append(
                f"Column '{column}' is not "
                "stored as text. It will be "
                "converted during preprocessing."
            )


    # --------------------------------------------------------
    # Check duplicate records
    # --------------------------------------------------------

    duplicate_count = int(
        df.duplicated().sum()
    )

    if duplicate_count > 0:

        warnings.append(
            f"{duplicate_count} duplicate "
            "record(s) detected."
        )


    # --------------------------------------------------------
    # Final validation result
    # --------------------------------------------------------

    valid = (
        len(errors) == 0
    )


    return {

        "valid":
            valid,

        "total_records":
            total_records,

        "required_columns":
            sorted(
                REQUIRED_COLUMNS
            ),

        "missing_columns":
            missing_columns,

        "extra_columns":
            extra_columns,

        "missing_values":
            missing_value_columns,

        "duplicate_records":
            duplicate_count,

        "errors":
            errors,

        "warnings":
            warnings
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    import json
    import sys

    print("=" * 70)
    print("THREATSHIELD - DATASET VALIDATOR TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # Dataset path
    # --------------------------------------------------------

    if len(sys.argv) < 2:

        print()
        print("Usage:")
        print(
            "python validation/dataset_validator.py <csv_path>"
        )
        print()

        sys.exit(1)

    dataset_path = sys.argv[1]

    print()
    print("Testing dataset:")
    print(dataset_path)
    print()

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    try:

        df = pd.read_csv(
            dataset_path
        )

    except FileNotFoundError:

        print("ERROR: Dataset not found.")
        sys.exit(1)

    except Exception as e:

        print(
            f"ERROR: Could not read dataset: {e}"
        )

        sys.exit(1)

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    result = validate_dataset(
        df
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print(
        json.dumps(
            result,
            indent=4,
            default=str
        )
    )

    print()

    if result["valid"]:

        print(
            "✓ DATASET VALIDATION PASSED"
        )

    else:

        print(
            "✗ DATASET VALIDATION FAILED"
        )
    