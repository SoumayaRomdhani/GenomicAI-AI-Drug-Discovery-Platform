# GenomicAI — Drug Discovery Platform

GenomicAI is an AI-powered platform for early-stage drug discovery and genomic intelligence.

It combines molecular analysis, biomedical literature retrieval, protein sequence analysis, drug-target interaction scoring, and a routing layer that directs user queries to the appropriate analytical module.

This CPU-friendly build disables heavier embedding dependencies in Docker for faster startup on standard laptops. When embedding-based retrieval is unavailable, the RAG module falls back automatically to TF-IDF.

## Overview

GenomicAI supports five main workflows:

### 1) Molecular Property Predictor
Takes a SMILES string as input and returns a structured ADMET-style profile.

Current implementation includes:
- RDKit-based molecular parsing when available
- descriptor extraction
- rule-based risk scoring for:
  - lipophilicity
  - solubility
  - hERG risk
  - BBB permeability

The module is structured so that learned molecular models such as GNNs or ChemBERTa-based predictors can be integrated later without changing the product layer.

### 2) Biomedical Literature RAG
Supports question answering over biomedical and drug discovery documents.

Current implementation includes:
- local document ingestion
- sentence-transformers embeddings when available
- persistent Chroma indexing when available
- TF-IDF fallback for lightweight local execution
- citation-style source snippets returned to the interface

### 3) Protein Sequence Analyzer
Analyzes amino acid sequences and computes:
- sequence length
- amino acid composition
- hydrophobic ratio
- polar ratio
- estimated molecular weight
- simple stability heuristics
- motif alerts

### 4) Drug-Target Interaction Scorer
Takes a SMILES string and a protein sequence and returns:
- a normalized interaction score
- interpretability notes
- molecular and protein features used in scoring

### 5) AI Research Assistant
A lightweight routing layer that identifies whether a query relates to molecules, proteins, literature, or interaction scoring, then calls the appropriate backend service and returns structured results.

## Architecture

```text
genomicai_portfolio/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/config.py
│   │   ├── models/schemas.py
│   │   ├── services/
│   │   │   ├── chemistry.py
│   │   │   ├── admet.py
│   │   │   ├── protein.py
│   │   │   ├── dti.py
│   │   │   ├── rag.py
│   │   │   └── research_assistant.py
│   │   └── data/pubmed_demo.json
│   ├── scripts/
│   │   ├── build_rag_index.py
│   │   └── fetch_pubmed_seed.py
│   ├── tests/test_smoke.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   └── StatCard.tsx
│   ├── lib/api.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.mjs
│   └── Dockerfile
├── docker-compose.yml
└── README.md
