from __future__ import annotations

from collections import Counter
from typing import List

AA_WEIGHTS = {
    "A": 89.09, "R": 174.20, "N": 132.12, "D": 133.10, "C": 121.15,
    "E": 147.13, "Q": 146.15, "G": 75.07, "H": 155.16, "I": 131.17,
    "L": 131.17, "K": 146.19, "M": 149.21, "F": 165.19, "P": 115.13,
    "S": 105.09, "T": 119.12, "W": 204.23, "Y": 181.19, "V": 117.15,
}
HYDROPHOBIC = set("AILMFWVPGC")
POLAR = set("STNQY")
AROMATIC = set("FWYH")
VALID_AA = set(AA_WEIGHTS)


def clean_sequence(sequence: str) -> str:
    return "".join(ch for ch in sequence.upper().strip() if ch.isalpha())


def analyze_protein(sequence: str) -> dict:
    seq = clean_sequence(sequence)
    filtered = "".join(ch for ch in seq if ch in VALID_AA)
    if len(filtered) < 10:
        raise ValueError("Protein sequence is too short or contains too many invalid characters.")

    counts = Counter(filtered)
    length = len(filtered)
    mw = sum(AA_WEIGHTS[aa] for aa in filtered) - (length - 1) * 18.015
    hydrophobic_ratio = sum(counts[aa] for aa in HYDROPHOBIC) / length
    polar_ratio = sum(counts[aa] for aa in POLAR) / length
    aromatic_ratio = sum(counts[aa] for aa in AROMATIC) / length

    motif_alerts: List[str] = []
    if "RGD" in filtered:
        motif_alerts.append("Contains RGD-like adhesion motif.")
    if filtered.startswith("M"):
        motif_alerts.append("Starts with methionine, consistent with translated protein sequences.")
    if "KK" in filtered or "RR" in filtered:
        motif_alerts.append("Basic residue cluster may indicate nucleic-acid or localization interactions.")
    if filtered.count("C") >= 4:
        motif_alerts.append("Cysteine-rich sequence may support disulfide-bond formation.")

    instability_score = (
        0.5 * (counts["P"] + counts["G"])
        + 0.3 * (counts["D"] + counts["E"])
        - 0.25 * (counts["L"] + counts["V"] + counts["I"])
    ) / max(1, length) * 100

    if instability_score > 8:
        instability_risk = "High"
    elif instability_score > 4:
        instability_risk = "Moderate"
    else:
        instability_risk = "Low"

    top_amino_acids = [
        {"amino_acid": aa, "count": count, "frequency": round(count / length, 3)}
        for aa, count in counts.most_common(5)
    ]

    return {
        "sequence_length": length,
        "molecular_weight_estimate": round(mw, 2),
        "hydrophobic_ratio": round(hydrophobic_ratio, 3),
        "polar_ratio": round(polar_ratio, 3),
        "aromatic_ratio": round(aromatic_ratio, 3),
        "instability_risk": instability_risk,
        "motif_alerts": motif_alerts or ["No strong heuristic motifs detected."],
        "top_amino_acids": top_amino_acids,
        "mode": "heuristic_bioinformatics",
    }
