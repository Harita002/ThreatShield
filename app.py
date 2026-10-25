import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt

st.markdown("""
    <style>
    .stApp {
        background-color: #eaf4fc;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# LOAD MODEL
# =========================
model = joblib.load("notebooks/malicious_detector.pkl")
training_columns = joblib.load("notebooks/training_columns.pkl")

# =========================
# CLEAN FUNCTION
# =========================
def clean_uploaded_data(df):

    df = df.drop_duplicates()
    df = df.dropna()

    df.columns = df.columns.str.strip()

    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.strip()

    return df

# =========================
# FEATURE ENGINEERING
# =========================
def engineer_features(df):

    df["off_hour_print_ratio"] = (
        df["num_printed_pages_off_hours"] /
        (df["total_printed_pages"] + 1)
    )

    df["burn_ratio"] = (
        df["total_files_burned"] /
        (df["num_entries"] + 1)
    )

    df["mobility_risk"] = (
        df["num_unique_campus"] *
        df["is_abroad"]
    )

    df["behavior_risk_score"] = (
        df["late_exit_flag"] +
        df["entry_during_weekend"] +
        df["burned_from_other"] +
        df["has_criminal_record"]
    )

    df["access_frequency_score"] = (
        df["num_entries"] /
        (df["trip_day_number"] + 1)
    )

    return df

# =========================
# UI START
# =========================
st.title("🔐 Insider Threat Detection Dashboard")

st.write("Upload employee dataset to detect malicious behavior.")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

# =========================
# MAIN PIPELINE
# =========================
if uploaded_file is not None:

    # Load data
    df = pd.read_csv(uploaded_file)

    # Preview
    st.subheader("📊 Uploaded Data Preview")
    st.dataframe(df.head())

    # Clean data
    df = clean_uploaded_data(df)

    # Store IDs
    employee_ids = df.index

    # Feature Engineering
    df = engineer_features(df)

    # Encoding
    df = pd.get_dummies(df, drop_first=True)

    # Match training columns
    df = df.reindex(columns=training_columns, fill_value=0)

    # Prediction
    probabilities = model.predict_proba(df)

    THRESHOLD = 0.40
    predictions = (probabilities[:,1] > THRESHOLD).astype(int)

    # =========================
    # RESULTS
    # =========================
    results = []

    for i in range(len(df)):

        prediction_text = (
            "Malicious"
            if predictions[i] == 1
            else "Not Malicious"
        )

        risk_score = probabilities[i][1] * 100

        if risk_score >= 80:
            threat_level = "HIGH"
        elif risk_score >= 50:
            threat_level = "MEDIUM"
        else:
            threat_level = "LOW"

        if prediction_text == "Malicious":
            results.append([
                employee_ids[i],
                prediction_text,
                round(risk_score, 2),
                threat_level
            ])

    results_df = pd.DataFrame(
        results,
        columns=[
            "Employee ID",
            "Prediction",
            "Risk Score (%)",
            "Threat Level"
        ]
    )
    results_df = results_df.sort_values(
    by="Risk Score (%)",
    ascending=False
)

    # =========================
    # DASHBOARD CARDS
    # =========================

    st.subheader("📊 Dashboard Summary")

    col1, col2, col3 = st.columns(3)

    # Total Records
    with col1:
        st.metric(label="Total Records", value=len(df))

    # Malicious Detected
    with col2:
        st.metric(label="Malicious Detected", value=len(results_df))

    # High Risk Count
    high_risk_count = len(results_df[results_df["Threat Level"] == "HIGH"])

    with col3:
        st.metric(label="High Risk Cases", value=high_risk_count)
    # =========================
    # DISPLAY RESULTS
    # =========================
    st.subheader("🚨 Malicious Employees Detected")

    if results_df.empty:
        st.success("No malicious employees detected.")
    else:
        def highlight_risk(row):
            if row["Threat Level"] == "HIGH":
                return ['background-color: #ffcccc'] * len(row)   # soft red
            elif row["Threat Level"] == "MEDIUM":
                return ['background-color: #ffe0b3'] * len(row)   # soft orange
            else:
                return ['background-color: #ccffcc'] * len(row)   # soft green

        styled_df = results_df.style.apply(highlight_risk, axis=1)

        st.dataframe(styled_df)
# =========================
    # DOWNLOAD BUTTON 👇 ADD HERE
    # =========================
    csv = results_df.to_csv(index=False)

    st.download_button(
        label="📥 Download Report",
        data=csv,
        file_name="malicious_report.csv",
        mime="text/csv"
    )
    # =========================
    # SUMMARY
    # =========================
    st.subheader("📈 Summary")

    st.write("Total Records:", len(df))
    st.write("Malicious Detected:", len(results_df))
    st.subheader("📊 Threat Level Distribution")

    threat_counts = results_df["Threat Level"].value_counts()
    plt.figure()
    threat_counts.plot(kind='bar')
    plt.xlabel("Threat Level")
    plt.ylabel("Count")

    st.pyplot(plt)