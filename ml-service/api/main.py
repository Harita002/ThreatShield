import os
import sys
# import tempfile

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# PROJECT ROOT
# ============================================================
# __file__ → the path of main.py itself
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
        # converts it to a absolute path
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# IMPORT THREATSHIELD BATCH PREDICTOR
# ============================================================

from inference.batch_predictor import predict_batch
from inference.predictor import predict_employee

# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="ThreatShield API",
    description="AI-powered Insider Threat Detection API",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():

    return {
        "application": "ThreatShield",
        "status": "running",
        "service": "Insider Threat Detection API"
    }


@app.get("/health")
def health():
# tocheck is this server is alive or not
    return {
        "status": "healthy"
    }


# ============================================================
# CSV ANALYSIS ENDPOINT
# ============================================================

@app.post("/analyze")
async def analyze_dataset(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Validate file type
    # --------------------------------------------------------

    if not file.filename.lower().endswith(".csv"):

        return {
            "success": False,
            "error": "Only CSV files are supported."
        }


    # --------------------------------------------------------
    # Read uploaded CSV
    # --------------------------------------------------------

    try:

        contents = await file.read()

        import pandas as pd
        from io import BytesIO

        df = pd.read_csv(
            BytesIO(contents)
        )

    except Exception as e:

        return {
            "success": False,
            "error": f"Unable to read CSV file: {str(e)}"
        }


    # --------------------------------------------------------
    # Run ThreatShield batch pipeline
    # --------------------------------------------------------

    try:

        result = predict_batch(df)

        return result

    except Exception as e:

        return {
            "success": False,
            "error": f"ThreatShield analysis failed: {str(e)}"
        }

# ============================================================
# SINGLE EMPLOYEE EXPLANATION
# ============================================================

@app.post("/explain")
async def explain_employee(employee: dict):
    # FastAPI will parse the incoming JSON request body directly into a Python dictionary.

    try:

        result = predict_employee(
            employee,
            explain=True
        )

        return {
            "success": True,
            "employee_id": employee.get(
                "employee_id",
                "UNKNOWN"
            ),
            "explanation": result
        }

    except Exception as e:

        return {
            "success": False,
            "error": f"Unable to generate explanation: {str(e)}"
        }