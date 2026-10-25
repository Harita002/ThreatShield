import json

from explanation_engine import generate_explanation


# ============================================================
# TEST CASES
# ============================================================

TEST_CASES = [

    {
        "name": "LOW RISK",

        "data": {
            "prediction": "NORMAL",
            "probability": 0.12,
            "risk_score": 12.0,
            "classification_threshold": 0.65,

            "risk_factors": [
                {
                    "feature": "entry_during_weekend",
                    "value": 0,
                    "shap_value": 0.25,
                    "direction": "INCREASED_RISK"
                }
            ],

            "protective_factors": [
                {
                    "feature": "total_printed_pages",
                    "value": 20,
                    "shap_value": -0.40,
                    "direction": "DECREASED_RISK"
                }
            ]
        }
    },

    {
        "name": "MEDIUM RISK",

        "data": {
            "prediction": "NORMAL",
            "probability": 0.60,
            "risk_score": 60.0,
            "classification_threshold": 0.65,

            "risk_factors": [
                {
                    "feature": "burn_ratio",
                    "value": 2.5,
                    "shap_value": 0.65,
                    "direction": "INCREASED_RISK"
                },

                {
                    "feature": "num_entries",
                    "value": 15,
                    "shap_value": 0.35,
                    "direction": "INCREASED_RISK"
                }
            ],

            "protective_factors": [
                {
                    "feature": "off_hour_print_ratio",
                    "value": 0.10,
                    "shap_value": -0.15,
                    "direction": "DECREASED_RISK"
                }
            ]
        }
    },

    {
        "name": "HIGH RISK",

        "data": {
            "prediction": "SUSPICIOUS",
            "probability": 0.92,
            "risk_score": 92.0,
            "classification_threshold": 0.65,

            "risk_factors": [
                {
                    "feature": "burned_from_other",
                    "value": 1,
                    "shap_value": 1.20,
                    "direction": "INCREASED_RISK"
                },

                {
                    "feature": "entry_during_weekend",
                    "value": 1,
                    "shap_value": 0.95,
                    "direction": "INCREASED_RISK"
                },

                {
                    "feature": "num_printed_pages_off_hours",
                    "value": 200,
                    "shap_value": 0.80,
                    "direction": "INCREASED_RISK"
                }
            ],

            "protective_factors": [
                {
                    "feature": "num_entries",
                    "value": 2,
                    "shap_value": -0.10,
                    "direction": "DECREASED_RISK"
                }
            ]
        }
    }
]


# ============================================================
# VALIDATION
# ============================================================

print("=" * 70)
print("THREATSHIELD - EXPLANATION ENGINE VALIDATION")
print("=" * 70)


passed = 0
failed = 0


for test in TEST_CASES:

    print("\n")
    print("-" * 70)
    print(test["name"])
    print("-" * 70)


    result = generate_explanation(
        test["data"]
    )


    print(
        "Prediction:",
        result["prediction"]
    )

    print(
        "Risk Score:",
        result["risk_score"]
    )

    print(
        "Risk Level:",
        result["risk_level"]
    )


    # ========================================================
    # EXPECTED RISK LEVEL
    # ========================================================

    expected_score = (
        test["data"]["risk_score"]
    )


    if expected_score >= 80:

        expected_level = "HIGH"

    elif expected_score >= 50:

        expected_level = "MEDIUM"

    else:

        expected_level = "LOW"


    # ========================================================
    # CHECK 1 — RISK LEVEL
    # ========================================================

    if result["risk_level"] == expected_level:

        print("✓ Risk level test PASSED")

        passed += 1

    else:

        print(
            "✗ Risk level test FAILED"
        )

        failed += 1


    # ========================================================
    # CHECK 2 — PREDICTION
    # ========================================================

    expected_prediction = (
        test["data"]["prediction"]
    )


    if result["prediction"] == expected_prediction:

        print(
            "✓ Prediction test PASSED"
        )

        passed += 1

    else:

        print(
            "✗ Prediction test FAILED"
        )

        failed += 1


    # ========================================================
    # CHECK 3 — RISK FACTORS
    # ========================================================

    original_risk_count = len(
        test["data"]["risk_factors"]
    )

    generated_risk_count = len(
        result["risk_factors"]
    )


    if (
        original_risk_count
        == generated_risk_count
    ):

        print(
            "✓ Risk factor test PASSED"
        )

        passed += 1

    else:

        print(
            "✗ Risk factor test FAILED"
        )

        failed += 1


    # ========================================================
    # CHECK 4 — PROTECTIVE FACTORS
    # ========================================================

    original_protective_count = len(
        test["data"]["protective_factors"]
    )

    generated_protective_count = len(
        result["protective_factors"]
    )


    if (
        original_protective_count
        == generated_protective_count
    ):

        print(
            "✓ Protective factor test PASSED"
        )

        passed += 1

    else:

        print(
            "✗ Protective factor test FAILED"
        )

        failed += 1


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)

print(
    "Tests Passed:",
    passed
)

print(
    "Tests Failed:",
    failed
)


if failed == 0:

    print(
        "\n✓ ALL EXPLANATION ENGINE TESTS PASSED"
    )

else:

    print(
        "\n✗ SOME TESTS FAILED"
    )