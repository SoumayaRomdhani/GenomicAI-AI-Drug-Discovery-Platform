# GenomicAI (CPU-friendly build)

This variant disables heavy embedding dependencies in Docker so the app starts faster on normal laptops. The RAG module falls back to TF-IDF automatically.

# GenomicAI — Drug Discovery Platform

A **portfolio-grade, executable full-stack MVP** for early-stage drug discovery and genomic intelligence.

It combines:

- **Molecular analysis** from SMILES strings
- **Biomedical literature RAG**
- **Protein sequence analysis**
- **Drug-target interaction scoring**
- **AI research assistant** that routes user questions to the right tool

This repo is designed to be:

- **easy to run locally**
- **clean enough for recruiters to review**
- **modular enough to upgrade into a real research product**

## Why this project is strong for your portfolio

Most candidates show notebooks.  
This project shows that you can build:

- a real **FastAPI backend**
- a real **Next.js frontend**
- modular **AI services**
- retrieval over biomedical papers
- cheminformatics + bioinformatics + product thinking

That combination is rare and immediately understandable for recruiters in **AI health, biotech, pharma-tech, and applied ML**.

## What is included

### 1) Molecular Property Predictor
Input a **SMILES** string and get a structured ADMET-style profile.

Current MVP implementation:
- RDKit-based molecular parsing when available
- descriptor extraction
- explainable rule-based risk scoring for:
  - logP-like lipophilicity
  - solubility
  - hERG risk
  - BBB permeability

Why this is still valuable:
- it is **fully executable**
- the code structure is ready for swapping in a **GNN + ChemBERTa** model later

### 2) Biomedical Literature RAG
Ask a question about drug discovery or genomics and retrieve relevant biomedical documents.

Current MVP implementation:
- local document ingestion
- sentence-transformers embeddings when available
- Chroma persistence when available
- robust TF-IDF fallback so the app still runs without GPU or large model downloads
- citation-style source snippets returned to the UI

### 3) Protein Sequence Analyzer
Analyze an amino-acid sequence and compute:
- length
- amino-acid composition
- hydrophobic ratio
- polar ratio
- estimated molecular weight
- simple stability heuristics
- motif alerts

### 4) Drug-Target Interaction Scorer
Provide a SMILES string and a protein sequence to get:
- a normalized interaction score
- interpretability notes
- molecular and protein features used in scoring

### 5) AI Research Assistant
A lightweight agent layer that:
- detects whether the user is asking about molecules, proteins, literature, or interaction
- calls the correct backend tool
- returns structured results in one response

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
```

## Fast local start

### Option A — Docker
```bash
docker compose up --build
```

Then open:
- Frontend: `http://localhost:3000`
- Backend docs: `http://localhost:8000/docs`

### Option B — Run manually

#### Backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API routes

### Health
```http
GET /health
```

### ADMET prediction
```http
POST /predict/admet
{
  "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O"
}
```

### Protein analysis
```http
POST /analyze/protein
{
  "sequence": "MKWVTFISLLFLFSSAYSRGVFRRDAHKSEVAHRFKDLGE"
}
```

### Drug-target interaction
```http
POST /predict/dti
{
  "smiles": "CCO",
  "sequence": "MKWVTFISLLFLFSSAYSRGVFRRDAHKSEVAHRFKDLGE"
}
```

### Biomedical RAG
```http
POST /rag/query
{
  "query": "What do recent papers say about transformers in drug discovery?",
  "top_k": 3
}
```

### Research assistant
```http
POST /assistant/query
{
  "query": "Analyze this molecule CCO and tell me if it looks BBB permeable"
}
```

## Refresh the RAG corpus with real PubMed papers

This repo includes a demo JSON corpus so it works immediately.  
You can replace it with fresh PubMed data using NCBI E-utilities.

### Fetch papers
```bash
cd backend
python scripts/fetch_pubmed_seed.py --query "drug discovery transformer genomics" --retmax 20
```

### Rebuild the local index
```bash
python scripts/build_rag_index.py
```

## Upgrade path to a true SOTA version

This MVP is intentionally engineered to be **runnable on a normal laptop**.  
To evolve it into the exact system you described:

### Molecular module
Replace rule-based ADMET scoring with:
- RDKit graph construction
- PyTorch Geometric encoder
- ChemBERTa embeddings
- multitask prediction head

### Protein module
Add:
- ESM-2 embeddings
- subcellular localization or function classification head
- protein family clustering

### DTI module
Replace the current scorer with:
- molecule encoder + protein encoder
- cross-attention fusion
- BindingDB training pipeline

### Research assistant
Upgrade to:
- LLM tool-calling
- experiment memory
- benchmark / eval suite
- citation-grounded report generation

## Good recruiter talking points

You can describe this as:

> “I built an end-to-end AI platform for drug discovery with a FastAPI backend, Next.js frontend, biomedical RAG, cheminformatics analysis, protein sequence analysis, and a drug-target interaction service. The architecture is production-ready and modular, so heavier models like GNNs, ChemBERTa, and ESM-2 can be plugged in without changing the product layer.”

## Technical notes

- The backend is intentionally **robust to missing heavy dependencies**.
- If sentence-transformers or Chroma are not available, RAG falls back to TF-IDF.
- If RDKit is unavailable, the chemistry service uses a lightweight heuristic fallback.
- This makes the repo easier to run on Windows and on recruiter laptops during demos.

## Suggested improvements before you publish

1. Add screenshots or a short GIF demo.
2. Deploy the backend on Render, Railway, or Fly.io.
3. Deploy the frontend on Vercel.
4. Add a benchmark page with example inputs and outputs.
5. Add W&B logging for experiments.
6. Fine-tune one real model and attach results in the README.

## Why the stack is appropriate

FastAPI automatically exposes OpenAPI docs and interactive docs, which is ideal for a demoable ML backend. Next.js App Router supports modern server/client composition and route handlers. PyTorch Geometric is purpose-built for graph neural networks. PubMed content is programmatically accessible through NCBI E-utilities. ChEMBL is a curated database of bioactive molecules, and BindingDB is a public database of experimentally measured protein–ligand affinities. Chroma supports persistent local vector storage. citeturn502760search0turn502760search1turn502760search2turn502760search7turn424004search1turn839771search3turn424004search14
