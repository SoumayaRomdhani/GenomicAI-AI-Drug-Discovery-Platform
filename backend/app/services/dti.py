from __future__ import annotations

from .admet import predict_admet
from .protein import analyze_protein


def predict_dti(smiles: str, sequence: str) -> dict:
    mol = predict_admet(smiles)
    prot = analyze_protein(sequence)

    score = 0.5
    rationale = []

    if mol["valid"]:
        if 1 <= mol["logp"] <= 4:
            score += 0.12
            rationale.append("Lipophilicity is in a drug-like range.")
        if mol["molecular_weight"] < 550:
            score += 0.08
            rationale.append("Molecular weight remains tractable for small-molecule screening.")
        if mol["aromatic_rings"] >= 1:
            score += 0.06
            rationale.append("Aromaticity may support hydrophobic pocket interactions.")
        if mol["solubility_class"] == "Low":
            score -= 0.05
            rationale.append("Low predicted solubility may reduce effective assay exposure.")
        if mol["herg_risk"] == "High":
            score -= 0.08
            rationale.append("High hERG risk weakens developability despite possible potency.")

    if prot["hydrophobic_ratio"] > 0.35:
        score += 0.06
        rationale.append("Protein hydrophobicity suggests plausible small-molecule pocket formation.")
    if prot["aromatic_ratio"] > 0.08:
        score += 0.04
        rationale.append("Aromatic residues can support pi-stacking interactions.")
    if prot["instability_risk"] == "High":
        score -= 0.03
        rationale.append("High protein instability may complicate experimental validation.")

    score = max(0.0, min(1.0, round(score, 3)))
    if score >= 0.72:
        band = "Promising"
    elif score >= 0.55:
        band = "Moderate"
    else:
        band = "Weak"

    return {
        "interaction_score": score,
        "score_band": band,
        "molecule_summary": {
            "logp": mol["logp"],
            "mw": mol["molecular_weight"],
            "solubility_class": mol["solubility_class"],
            "bbb_permeability": mol["bbb_permeability"],
        },
        "protein_summary": {
            "sequence_length": prot["sequence_length"],
            "hydrophobic_ratio": prot["hydrophobic_ratio"],
            "aromatic_ratio": prot["aromatic_ratio"],
            "instability_risk": prot["instability_risk"],
        },
        "rationale": rationale or ["No strong interaction signals detected from the current heuristic baseline."],
    }
