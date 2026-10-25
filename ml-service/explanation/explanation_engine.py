import json


# ============================================================
# FEATURE DISPLAY NAMES
# ============================================================

FEATURE_NAMES = {

    "burned_from_other":
        "Files burned from another source",

    "entry_during_weekend":
        "Weekend access",

    "burn_ratio":
        "File burn ratio",

    "num_printed_pages_off_hours":
        "After-hours printed pages",

    "trip_day_number":
        "Trip day activity",

    "off_hour_print_ratio":
        "After-hours printing ratio",

    "total_files_burned":
        "Total files burned",

    "total_printed_pages":
        "Total printed pages",

    "is_abroad":
        "Travel activity",

    "num_entries":
        "Number of entries",

    "num_unique_campus":
        "Number of unique campuses",

    "late_exit_flag":
        "Late exit activity",

    "mobility_risk":
        "Mobility activity",

    "behavior_risk_score":
        "Behavior risk score",

    "access_frequency_score":
        "Access frequency"
}


# ============================================================
# RISK LEVEL
# ============================================================

def determine_risk_level(
    risk_score
):

    if risk_score >= 80:

        return "HIGH"

    elif risk_score >= 50:

        return "MEDIUM"

    else:

        return "LOW"


# ============================================================
# FEATURE NAME
# ============================================================

def get_display_name(
    feature
):

    return FEATURE_NAMES.get(
        feature,
        feature.replace(
            "_",
            " "
        ).title()
    )


# ============================================================
# GENERATE FACTOR DESCRIPTION
# ============================================================

def describe_factor(
    feature,
    value,
    direction
):

    display_name = get_display_name(
        feature
    )

    # ========================================================
    # FEATURE-SPECIFIC EXPLANATIONS
    # ========================================================

    descriptions = {

        "burned_from_other": {
            "INCREASED_RISK":
                "File activity involving files burned from another source increased the model's risk assessment.",

            "DECREASED_RISK":
                "The observed file-burning pattern contributed toward a lower model risk assessment."
        },

        "entry_during_weekend": {
            "INCREASED_RISK":
                "Weekend access activity increased the model's risk assessment.",

            "DECREASED_RISK":
                "The observed weekend-access pattern contributed toward a lower model risk assessment."
        },

        "burn_ratio": {
            "INCREASED_RISK":
                "The file-burning ratio contributed toward a higher model risk assessment.",

            "DECREASED_RISK":
                "The file-burning ratio contributed toward a lower model risk assessment."
        },

        "num_printed_pages_off_hours": {
            "INCREASED_RISK":
                "After-hours printing activity contributed toward a higher model risk assessment.",

            "DECREASED_RISK":
                "After-hours printing activity contributed toward a lower model risk assessment."
        },

        "off_hour_print_ratio": {
            "INCREASED_RISK":
                "The proportion of printing performed during off-hours contributed toward a higher model risk assessment.",

            "DECREASED_RISK":
                "The observed off-hours printing ratio contributed toward a lower model risk assessment."
        },

        "total_files_burned": {
            "INCREASED_RISK":
                "The amount of file-burning activity contributed toward a higher model risk assessment.",

            "DECREASED_RISK":
                "The observed file-burning activity contributed toward a lower model risk assessment."
        },

        "total_printed_pages": {
            "INCREASED_RISK":
                "The volume of printed pages contributed toward a higher model risk assessment.",

            "DECREASED_RISK":
                "The observed printing volume contributed toward a lower model risk assessment."
        },

        "trip_day_number": {
            "INCREASED_RISK":
                "The employee's travel-day activity contributed toward a higher model risk assessment.",

            "DECREASED_RISK":
                "The observed travel-day activity contributed toward a lower model risk assessment."
        },

        "is_abroad": {
            "INCREASED_RISK":
                "Travel-related activity contributed toward a higher model risk assessment.",

            "DECREASED_RISK":
                "The observed travel-related activity contributed toward a lower model risk assessment."
        },

        "num_entries": {
            "INCREASED_RISK":
                "The number of access entries contributed toward a higher model risk assessment.",

            "DECREASED_RISK":
                "The observed access-entry pattern contributed toward a lower model risk assessment."
        },

        "num_unique_campus": {
            "INCREASED_RISK":
                "Access across multiple campuses contributed toward a higher model risk assessment.",

            "DECREASED_RISK":
                "The observed campus-access pattern contributed toward a lower model risk assessment."
        },

        "late_exit_flag": {
            "INCREASED_RISK":
                "Late-exit activity contributed toward a higher model risk assessment.",

            "DECREASED_RISK":
                "The observed exit-time pattern contributed toward a lower model risk assessment."
        },

        "mobility_risk": {
            "INCREASED_RISK":
                "The combined mobility pattern contributed toward a higher model risk assessment.",

            "DECREASED_RISK":
                "The observed mobility pattern contributed toward a lower model risk assessment."
        },

        "behavior_risk_score": {
            "INCREASED_RISK":
                "The combined behavioral activity score contributed toward a higher model risk assessment.",

            "DECREASED_RISK":
                "The combined behavioral activity score contributed toward a lower model risk assessment."
        },

        "access_frequency_score": {
            "INCREASED_RISK":
                "The observed access frequency contributed toward a higher model risk assessment.",

            "DECREASED_RISK":
                "The observed access frequency contributed toward a lower model risk assessment."
        }
    }


    # ========================================================
    # RETURN SPECIFIC DESCRIPTION
    # ========================================================

    if feature in descriptions:

        return descriptions[
            feature
        ][direction]


    # ========================================================
    # FALLBACK
    # ========================================================

    if direction == "INCREASED_RISK":

        return (
            f"{display_name} "
            "contributed toward a higher "
            "model risk assessment."
        )

    else:

        return (
            f"{display_name} "
            "contributed toward a lower "
            "model risk assessment."
        )

# ============================================================
# GENERATE EXPLANATION
# ============================================================

def generate_explanation(
    shap_result
):

    prediction = shap_result[
        "prediction"
    ]

    probability = shap_result[
        "probability"
    ]

    risk_score = shap_result[
        "risk_score"
    ]

    threshold = shap_result[
        "classification_threshold"
    ]

    risk_factors = (
        shap_result.get(
            "risk_factors",
            []
        )
    )

    protective_factors = (
        shap_result.get(
            "protective_factors",
            []
        )
    )


    # --------------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------------

    risk_level = determine_risk_level(
        risk_score
    )


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    if prediction == "SUSPICIOUS":

        summary = (
            f"The model classified the activity as suspicious "
            f"with a risk score of {risk_score:.2f}%, "
            f"which is above the "
            f"{threshold * 100:.0f}% classification threshold."
        )

    else:

        summary = (
            f"The model classified the activity as normal "
            f"with a risk score of {risk_score:.2f}%, "
            f"which is below the "
            f"{threshold * 100:.0f}% classification threshold."
        )


    # --------------------------------------------------------
    # RISK FACTORS
    # --------------------------------------------------------

    formatted_risk_factors = []


    for factor in risk_factors:

        formatted_risk_factors.append(

            {
                "feature":
                    factor["feature"],

                "display_name":
                    get_display_name(
                        factor["feature"]
                    ),

                "value":
                    factor["value"],

                "shap_value":
                    factor["shap_value"],

                "direction":
                    factor["direction"],

                "description":
                    describe_factor(
                        factor["feature"],
                        factor["value"],
                        factor["direction"]
                    )
            }
        )


    # --------------------------------------------------------
    # PROTECTIVE FACTORS
    # --------------------------------------------------------

    formatted_protective_factors = []


    for factor in protective_factors:

        formatted_protective_factors.append(

            {
                "feature":
                    factor["feature"],

                "display_name":
                    get_display_name(
                        factor["feature"]
                    ),

                "value":
                    factor["value"],

                "shap_value":
                    factor["shap_value"],

                "direction":
                    factor["direction"],

                "description":
                    describe_factor(
                        factor["feature"],
                        factor["value"],
                        factor["direction"]
                    )
            }
        )

    # --------------------------------------------------------
    # RISK INTERPRETATION
    # --------------------------------------------------------

    if risk_level == "HIGH":

        risk_interpretation = (
            "The model assigns a high risk level. "
            "The activity should be reviewed using the "
            "available behavioral evidence."
        )

    elif risk_level == "MEDIUM":

        risk_interpretation = (
            "The model assigns a medium risk level. "
            "The activity may require additional review "
            "before any decision is made."
        )

    else:

        risk_interpretation = (
            "The model assigns a low risk level. "
            "The predicted probability is well below "
            "the suspicious classification threshold."
        )


    # --------------------------------------------------------
    # BUILD FINAL RESPONSE
    # --------------------------------------------------------

    explanation = {

        "prediction":
            prediction,

        "probability":
            probability,

        "risk_score":
            risk_score,

        "risk_level":
            risk_level,

        "classification_threshold":
            threshold,

        "summary":
            summary,

        "risk_factors":
            formatted_risk_factors,

        "protective_factors":
            formatted_protective_factors,

        "risk_interpretation":
            risk_interpretation,

        "explanation_note":
            (
                "SHAP values represent the contribution "
                "of features to the model prediction. "
                "They indicate model influence and "
                "should not be interpreted as causal evidence."
            )
    }


    return explanation


# ============================================================
# TEST FUNCTION
# ============================================================

if __name__ == "__main__":

    print(
        "=" * 70
    )

    print(
        "THREATSHIELD - EXPLANATION ENGINE TEST"
    )

    print(
        "=" * 70
    )


    # --------------------------------------------------------
    # LOAD SHAP JSON
    # --------------------------------------------------------

    with open(
        "training/shap_employee_explanation.json",
        "r",
        encoding="utf-8"
    ) as file:

        shap_result = json.load(
            file
        )


    # --------------------------------------------------------
    # GENERATE EXPLANATION
    # --------------------------------------------------------

    explanation = generate_explanation(
        shap_result
    )


    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    print(
        json.dumps(
            explanation,
            indent=4
        )
    )


    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    with open(
        "employee_explanation.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            explanation,
            file,
            indent=4
        )


    print(
        "\nExplanation generated successfully."
    )

    print(
        "Saved: employee_explanation.json"
    )