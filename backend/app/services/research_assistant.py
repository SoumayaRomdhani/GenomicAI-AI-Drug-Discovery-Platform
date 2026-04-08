from __future__ import annotations

import re

from .admet import predict_admet
from .dti import predict_dti
from .protein import analyze_protein
from .rag import BiomedicalRAGService


class ResearchAssistant:
    def __init__(self, rag_service: BiomedicalRAGService) -> None:
        self.rag = rag_service

    def handle(self, query: str) -> dict:
        query = query.strip()

        smiles_match = re.search(r"([A-Za-z0-9@+\-\[\]\(\)=#$\\/%.]{3,})", query)
        protein_like = re.search(r"\b[A-Z]{12,}\b", query)

        lower = query.lower()

        if "interaction" in lower or ("target" in lower and smiles_match and protein_like):
            result = predict_dti(smiles_match.group(1), protein_like.group(0))
            return {
                "route": "dti",
                "summary": "The assistant detected a drug-target interaction request.",
                "details": result,
            }

        if any(word in lower for word in ["smiles", "molecule", "admet", "toxicity", "bbb", "herg"]) and smiles_match:
            result = predict_admet(smiles_match.group(1))
            return {
                "route": "admet",
                "summary": "The assistant detected a molecular property analysis request.",
                "details": result,
            }

        if any(word in lower for word in ["protein", "sequence", "motif"]) and protein_like:
            result = analyze_protein(protein_like.group(0))
            return {
                "route": "protein",
                "summary": "The assistant detected a protein sequence analysis request.",
                "details": result,
            }

        rag = self.rag.query(query, top_k=3)
        return {
            "route": "rag",
            "summary": "The assistant routed the question to the biomedical literature retrieval engine.",
            "details": rag,
        }
