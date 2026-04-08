from typing import Any, List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str


class AdmetRequest(BaseModel):
    smiles: str = Field(..., min_length=1, description="Molecule SMILES string")


class AdmetPrediction(BaseModel):
    smiles: str
    valid: bool
    molecular_weight: float
    logp: float
    tpsa: float
    hbd: int
    hba: int
    rotatable_bonds: int
    aromatic_rings: int
    solubility_class: str
    herg_risk: str
    bbb_permeability: str
    explanation: List[str]
    mode: str


class ProteinRequest(BaseModel):
    sequence: str = Field(..., min_length=10, description="Protein sequence")


class ProteinAnalysis(BaseModel):
    sequence_length: int
    molecular_weight_estimate: float
    hydrophobic_ratio: float
    polar_ratio: float
    aromatic_ratio: float
    instability_risk: str
    motif_alerts: List[str]
    top_amino_acids: List[dict]
    mode: str


class DTIRequest(BaseModel):
    smiles: str
    sequence: str


class DTIResponse(BaseModel):
    interaction_score: float
    score_band: str
    molecule_summary: dict
    protein_summary: dict
    rationale: List[str]


class RAGRequest(BaseModel):
    query: str
    top_k: int = Field(3, ge=1, le=8)


class RAGDocument(BaseModel):
    doc_id: str
    title: str
    source: str
    year: Optional[int] = None
    score: float
    snippet: str


class RAGResponse(BaseModel):
    query: str
    answer: str
    documents: List[RAGDocument]
    backend: str


class AssistantRequest(BaseModel):
    query: str


class AssistantResponse(BaseModel):
    route: str
    summary: str
    details: Any
