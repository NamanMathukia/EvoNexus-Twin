"""
api/main.py
FastAPI application factory for the EvoNexus-Twin backend.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.predict import router as predict_router
from api.schemas        import HealthResponse
from src.predict        import ModelRegistry


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-load all models at startup so first request isn't slow
    try:
        ModelRegistry.instance().load()
    except Exception as e:
        print(f"[WARNING] Could not pre-load models: {e}")
    yield


app = FastAPI(
    title="EvoNexus-Twin (ENT) API",
    description=(
        "Production-ready career placement prediction system combining "
        "Temporal Knowledge Graphs, LSTM trajectory models, LGDESetNet, "
        "survival analysis, and multi-agent NBA recommendations."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router, tags=["Prediction"])


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health() -> HealthResponse:
    reg = ModelRegistry()
    return HealthResponse(status="ok", models_loaded=reg._loaded)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "EvoNexus-Twin API is running.",
        "docs":    "/docs",
        "predict": "POST /predict",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
