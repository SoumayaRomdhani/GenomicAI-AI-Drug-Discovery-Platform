from __future__ import annotations

from typing import List

from .chemistry import featurize_smiles


def _solubility_class(logp: float, tpsa: float, mw: float) -> str:
    if logp < 1.5 and tpsa > 40:
        return "High"
    if logp < 3.0 and mw < 450:
        return "Moderate"
    return "Low"


def _herg_risk(logp: float, aromatic_rings: int, hba: int, halogens: int) -> str:
    score = 0
    if logp > 3:
        score += 2
    if aromatic_rings >= 2:
        score += 2
    if hba >= 5:
        score += 1
    if halogens >= 1:
        score += 1
    if score >= 4:
        return "High"
    if score >= 2:
        return "Moderate"
    return "Low"


def _bbb(logp: float, tpsa: float, mw: float, hbd: int) -> str:
    if mw < 450 and tpsa < 90 and hbd <= 2 and 1 <= logp <= 4:
        return "Likely permeable"
    if tpsa > 120 or hbd > 3:
        return "Unlikely permeable"
    return "Borderline"


def predict_admet(smiles: str) -> dict:
    feat = featurize_smiles(smiles)
    if not feat.valid:
        return {
            "smiles": smiles,
            "valid": False,
            "molecular_weight": 0.0,
            "logp": 0.0,
            "tpsa": 0.0,
            "hbd": 0,
            "hba": 0,
            "rotatable_bonds": 0,
            "aromatic_rings": 0,
            "solubility_class": "Unknown",
            "herg_risk": "Unknown",
            "bbb_permeability": "Unknown",
            "explanation": ["The SMILES string could not be parsed."],
            "mode": feat.mode,
        }

    solubility = _solubility_class(feat.logp, feat.tpsa, feat.molecular_weight)
    herg = _herg_risk(feat.logp, feat.aromatic_rings, feat.hba, feat.halogens)
    bbb = _bbb(feat.logp, feat.tpsa, feat.molecular_weight, feat.hbd)

    explanation: List[str] = [
        f"Estimated lipophilicity (logP) is {feat.logp:.2f}.",
        f"Estimated polarity (TPSA) is {feat.tpsa:.1f}.",
        f"Molecular weight is {feat.molecular_weight:.1f} Da.",
    ]
    if feat.aromatic_rings >= 2:
        explanation.append("Multiple aromatic rings may increase promiscuity and hERG risk.")
    if feat.tpsa > 120:
        explanation.append("High polar surface area usually reduces passive membrane diffusion.")
    if feat.rotatable_bonds > 8:
        explanation.append("High flexibility may reduce developability.")

    return {
        "smiles": feat.smiles,
        "valid": True,
        "molecular_weight": round(feat.molecular_weight, 3),
        "logp": round(feat.logp, 3),
        "tpsa": round(feat.tpsa, 3),
        "hbd": feat.hbd,
        "hba": feat.hba,
        "rotatable_bonds": feat.rotatable_bonds,
        "aromatic_rings": feat.aromatic_rings,
        "solubility_class": solubility,
        "herg_risk": herg,
        "bbb_permeability": bbb,
        "explanation": explanation,
        "mode": feat.mode,
    }
