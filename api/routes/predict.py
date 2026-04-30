"""
api/routes/predict.py
POST /predict  — core prediction endpoint.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import StudentInput, PredictionOutput
from src.predict  import predict_full

router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictionOutput,
    summary="Run full ENT prediction pipeline",
    description=(
        "Accepts a student profile and returns risk classification, salary estimate, "
        "time-to-placement, SHAP explanations, and multi-agent action recommendations."
    ),
)
async def predict(student: StudentInput) -> PredictionOutput:
    try:
        result = predict_full(student.model_dump())
        return PredictionOutput(**result)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Model files not found. Run `python train.py` first. ({e})",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
