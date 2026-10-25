import { useState } from "react";

import { analyzeDataset } from "../services/api";

import SummaryCards from "../components/SummaryCards";
import RiskCharts from "../components/RiskCharts";
import EmployeeTable from "../components/EmployeeTable";
import ScanningOverlay from "../components/ScanningOverlay";
import RiskAnalytics from "../components/RiskAnalytics";


function Dashboard({ user, onLogout }) {

    const [file, setFile] = useState(null);

    const [result, setResult] = useState(null);

    const [loading, setLoading] = useState(false);

    const [error, setError] = useState("");

    const [selectedEmployee, setSelectedEmployee] =
    useState(null);

    const [selectedExplanation, setSelectedExplanation] =
    useState(null);


    const handleFileChange = (event) => {

        const selectedFile =
            event.target.files[0];

        setFile(selectedFile);

        setResult(null);

        setError("");
    };

    const handleExplanation = (
        employee,
        explanation
    ) => {

        setSelectedEmployee(
            employee
        );

        setSelectedExplanation(
            explanation
        );
    };

    const handleAnalyze = async () => {

        if (!file) {

            setError(
                "Please select a CSV file."
            );

            return;
        }


        try {

            setLoading(true);

            setError("");


            const data =
                await analyzeDataset(file);


            if (!data.success) {

                setError(
                    data.error ||
                    "Dataset analysis failed."
                );

                return;
            }


            setResult(data);

        }

        catch (err) {

            console.error(err);

            setError(
                err.response?.data?.error ||
                "Unable to connect to ThreatShield API."
            );

        }

        finally {

            setLoading(false);
        }
    };


    return (

        <div className="dashboard">

            <ScanningOverlay
                active={loading}
            />

            {/* HEADER */}

<header className="dashboard-header">

    <div>
        <h1>
            ThreatShield
        </h1>

        <p>
            AI-Powered Insider Threat Detection
        </p>
    </div>

    <div className="user-section">

        <span>
            Welcome, {user?.name}
        </span>

        <span className="user-role">
            {user?.role}
        </span>

        <button onClick={onLogout}>
            Logout
        </button>

    </div>

</header>


            {/* UPLOAD */}

            <section className="upload-section">

                <h2>
                    Analyze Employee Dataset
                </h2>

                <div className="upload-controls">

                    <input
                        type="file"
                        accept=".csv"
                        onChange={handleFileChange}
                    />

                    <button
                        onClick={handleAnalyze}
                        disabled={loading}
                    >

                        {loading
                            ? "Analyzing..."
                            : "Analyze Dataset"
                        }

                    </button>

                </div>


                {file && (

                    <p className="selected-file">

                        Selected:
                        {" "}
                        {file.name}

                    </p>

                )}


                {error && (

                    <div className="error-message">

                        {error}

                    </div>

                )}

            </section>


            {/* RESULTS */}

            {result && (

                <>

                    <SummaryCards
                        summary={result.summary}
                    />

                    <RiskAnalytics
                        summary={result.summary}
                    />


                    <RiskCharts
                        summary={result.summary}
                    />

                    <div className="mode-message">

                        {result.display_mode ===
                        "SUSPICIOUS_ONLY"

                            ? "Showing suspicious employees only because the dataset contains more than 10 employees."

                            : "Showing all analyzed employees."
                        }

                    </div>


                    <EmployeeTable
                        employees={
                            result.dashboard_results
                        }
                        onExplanation={
                            handleExplanation
                        }
                    />

{selectedExplanation && (

    <div className="explanation-panel">

        {/* HEADER */}

        <div className="explanation-header">

            <div>

                <p className="explanation-label">
                    AI INVESTIGATION
                </p>

                <h2>
                    Employee Risk Analysis
                </h2>

                <p className="employee-reference">
                    {selectedEmployee.employee_id}
                </p>

            </div>

            <button
                className="close-explanation"
                onClick={() => {
                    setSelectedExplanation(null);
                    setSelectedEmployee(null);
                }}
            >
                ×
            </button>

        </div>


        {/* RISK OVERVIEW */}

        <div className="risk-overview">

            <div className="risk-score-box">

                <span>
                    RISK SCORE
                </span>

                <strong>
                    {
                        selectedExplanation
                            .explanation
                            .risk_score
                            .toFixed(2)
                    }%
                </strong>

                <div className="explanation-risk-bar">

                    <div
                        className={
                            `explanation-risk-fill ${
                                selectedExplanation
                                    .explanation
                                    .risk_level
                                    .toLowerCase()
                            }`
                        }
                        style={{
                            width:
                                `${selectedExplanation.explanation.risk_score}%`
                        }}
                    />

                </div>

            </div>


            <div className="prediction-box">

                <span>
                    CLASSIFICATION
                </span>

                <strong
                    className={
                        selectedExplanation
                            .explanation
                            .prediction === "SUSPICIOUS"
                            ? "danger-text"
                            : "safe-text"
                    }
                >
                    {
                        selectedExplanation
                            .explanation
                            .prediction
                    }
                </strong>

            </div>


            <div className="risk-level-box">

                <span>
                    RISK LEVEL
                </span>

                <strong
                    className={
                        `risk-level-${
                            selectedExplanation
                                .explanation
                                .risk_level
                                .toLowerCase()
                        }`
                    }
                >
                    {
                        selectedExplanation
                            .explanation
                            .risk_level
                    }
                </strong>

            </div>

        </div>


        {/* AI SUMMARY */}

        <div className="explanation-summary">

            <span className="summary-heading">
                AI Assessment
            </span>

            <p>
                {
                    selectedExplanation
                        .explanation
                        .summary
                }
            </p>

        </div>


        {/* RISK FACTORS */}

        <div className="factor-section">

            <h3>

                <span className="factor-icon risk-icon">
                    ↑
                </span>

                Risk Factors

            </h3>

            <p className="section-description">
                Features that increased the model's
                risk assessment.
            </p>


            <div className="factor-list">

                {
                    selectedExplanation
                        .explanation
                        .risk_factors
                        .map((factor) => (

                            <div
                                className="factor-card risk-factor"
                                key={factor.feature}
                            >

                                <div className="factor-main">

                                    <div className="factor-title">

                                        <span className="factor-arrow">
                                            ↑
                                        </span>

                                        <strong>
                                            {
                                                factor.display_name ||
                                                factor.feature
                                            }
                                        </strong>

                                    </div>

                                    <p>
                                        {
                                            factor.description
                                        }
                                    </p>

                                </div>


                                <div className="shap-container">

                                    <div className="shap-bar">

                                        <div
                                            className="shap-bar-fill positive"
                                            style={{
                                                width:
                                                    `${Math.min(
                                                        Math.abs(
                                                            factor.shap_value
                                                        ) * 100,
                                                        100
                                                    )}%`
                                            }}
                                        />

                                    </div>

                                    <span className="shap-value positive">
                                        +
                                        {factor.shap_value.toFixed(4)}
                                    </span>

                                </div>

                            </div>

                        ))
                }

            </div>

        </div>


        {/* PROTECTIVE FACTORS */}

        <div className="factor-section">

            <h3>

                <span className="factor-icon protective-icon">
                    ↓
                </span>

                Protective Factors

            </h3>

            <p className="section-description">
                Features that reduced the model's
                risk assessment.
            </p>


            <div className="factor-list">

                {
                    selectedExplanation
                        .explanation
                        .protective_factors
                        .map((factor) => (

                            <div
                                className="factor-card protective-factor"
                                key={factor.feature}
                            >

                                <div className="factor-main">

                                    <div className="factor-title">

                                        <span className="factor-arrow">
                                            ↓
                                        </span>

                                        <strong>
                                            {
                                                factor.display_name ||
                                                factor.feature
                                            }
                                        </strong>

                                    </div>

                                    <p>
                                        {
                                            factor.description
                                        }
                                    </p>

                                </div>


                                <div className="shap-container">

                                    <div className="shap-bar">

                                        <div
                                            className="shap-bar-fill negative"
                                            style={{
                                                width:
                                                    `${Math.min(
                                                        Math.abs(
                                                            factor.shap_value
                                                        ) * 100,
                                                        100
                                                    )}%`
                                            }}
                                        />

                                    </div>

                                    <span className="shap-value negative">
                                        {factor.shap_value.toFixed(4)}
                                    </span>

                                </div>

                            </div>

                        ))
                }

            </div>

        </div>


        {/* INTERPRETATION */}

        <div className="risk-interpretation">

            <div className="interpretation-icon">
                AI
            </div>

            <div>

                <strong>
                    Risk Interpretation
                </strong>

                <p>
                    {
                        selectedExplanation
                            .explanation
                            .risk_interpretation
                    }
                </p>

            </div>

        </div>


        {/* SHAP NOTE */}

        <div className="explanation-note">

            <strong>
                About SHAP
            </strong>

            <p>
                {
                    selectedExplanation
                        .explanation
                        .explanation_note
                }
            </p>

        </div>

    </div>

)}

                </>

            )}

        </div>
    );
}

export default Dashboard;