from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.models.schemas import (
    AdmetPrediction,
    AdmetRequest,
    AssistantRequest,
    AssistantResponse,
    DTIRequest,
    DTIResponse,
    HealthResponse,
    ProteinAnalysis,
    ProteinRequest,
    RAGRequest,
    RAGResponse,
)
from app.services.admet import predict_admet
from app.services.dti import predict_dti
from app.services.protein import analyze_protein
from app.services.rag import BiomedicalRAGService
from app.services.research_assistant import ResearchAssistant

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Portfolio-grade API for drug discovery and genomic intelligence.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service = BiomedicalRAGService()
assistant = ResearchAssistant(rag_service)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", app=settings.app_name, version=settings.app_version)


@app.post("/predict/admet", response_model=AdmetPrediction)
def admet(req: AdmetRequest) -> AdmetPrediction:
    result = predict_admet(req.smiles)
    return AdmetPrediction(**result)


@app.post("/analyze/protein", response_model=ProteinAnalysis)
def protein(req: ProteinRequest) -> ProteinAnalysis:
    try:
        result = analyze_protein(req.sequence)
        return ProteinAnalysis(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/predict/dti", response_model=DTIResponse)
def dti(req: DTIRequest) -> DTIResponse:
    try:
        result = predict_dti(req.smiles, req.sequence)
        return DTIResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/rag/query", response_model=RAGResponse)
def rag_query(req: RAGRequest) -> RAGResponse:
    result = rag_service.query(req.query, top_k=req.top_k)
    return RAGResponse(**result)


@app.post("/assistant/query", response_model=AssistantResponse)
def assistant_query(req: AssistantRequest) -> AssistantResponse:
    try:
        result = assistant.handle(req.query)
        return AssistantResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
