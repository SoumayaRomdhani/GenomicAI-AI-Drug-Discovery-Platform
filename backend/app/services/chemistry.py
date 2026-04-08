from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict

try:
    from rdkit import Chem
    from rdkit.Chem import Crippen, Descriptors, Lipinski, rdMolDescriptors

    HAS_RDKIT = True
except Exception:
    HAS_RDKIT = False


@dataclass
class MoleculeFeatures:
    valid: bool
    smiles: str
    molecular_weight: float
    logp: float
    tpsa: float
    hbd: int
    hba: int
    rotatable_bonds: int
    aromatic_rings: int
    hetero_atoms: int
    halogens: int
    heavy_atoms: int
    mode: str


_ALLOWED_SMILES = re.compile(r"^[A-Za-z0-9@+\-\[\]\(\)=#$\\/%.]+$")


def _fallback_counts(smiles: str) -> Dict[str, int]:
    tokens = {
        "N": smiles.count("N") + smiles.count("n"),
        "O": smiles.count("O") + smiles.count("o"),
        "S": smiles.count("S") + smiles.count("s"),
        "F": smiles.count("F"),
        "Cl": smiles.count("Cl"),
        "Br": smiles.count("Br"),
        "I": smiles.count("I"),
        "P": smiles.count("P") + smiles.count("p"),
        "rings": sum(ch.isdigit() for ch in smiles),
        "double": smiles.count("="),
        "triple": smiles.count("#"),
        "branches": smiles.count("("),
        "aromatic": sum(smiles.count(ch) for ch in "cnosp"),
    }
    return tokens


def featurize_smiles(smiles: str) -> MoleculeFeatures:
    smiles = smiles.strip()
    if not smiles or not _ALLOWED_SMILES.match(smiles):
        return MoleculeFeatures(
            valid=False,
            smiles=smiles,
            molecular_weight=0.0,
            logp=0.0,
            tpsa=0.0,
            hbd=0,
            hba=0,
            rotatable_bonds=0,
            aromatic_rings=0,
            hetero_atoms=0,
            halogens=0,
            heavy_atoms=0,
            mode="invalid",
        )

    if HAS_RDKIT:
        mol = Chem.MolFromSmiles(smiles)
        if mol is not None:
            return MoleculeFeatures(
                valid=True,
                smiles=smiles,
                molecular_weight=float(Descriptors.MolWt(mol)),
                logp=float(Crippen.MolLogP(mol)),
                tpsa=float(rdMolDescriptors.CalcTPSA(mol)),
                hbd=int(Lipinski.NumHDonors(mol)),
                hba=int(Lipinski.NumHAcceptors(mol)),
                rotatable_bonds=int(Lipinski.NumRotatableBonds(mol)),
                aromatic_rings=int(rdMolDescriptors.CalcNumAromaticRings(mol)),
                hetero_atoms=int(rdMolDescriptors.CalcNumHeteroatoms(mol)),
                halogens=sum(smiles.count(x) for x in ["F", "Cl", "Br", "I"]),
                heavy_atoms=int(mol.GetNumHeavyAtoms()),
                mode="rdkit",
            )

    counts = _fallback_counts(smiles)
    carbon_count = smiles.count("C") + smiles.count("c")
    hydrogen_proxy = max(0, carbon_count * 2 - counts["double"] * 2 - counts["triple"] * 4)
    molecular_weight = (
        carbon_count * 12.01
        + hydrogen_proxy * 1.008
        + counts["N"] * 14.01
        + counts["O"] * 16.00
        + counts["S"] * 32.06
        + counts["P"] * 30.97
        + counts["F"] * 19.0
        + counts["Cl"] * 35.45
        + counts["Br"] * 79.90
        + counts["I"] * 126.9
    )
    hetero = counts["N"] + counts["O"] + counts["S"] + counts["P"]
    logp = round(0.54 * carbon_count + 0.28 * counts["aromatic"] - 0.35 * hetero - 1.5, 3)
    tpsa = round(counts["N"] * 12.0 + counts["O"] * 17.0 + counts["S"] * 25.0 + counts["P"] * 20.0, 2)

    return MoleculeFeatures(
        valid=True,
        smiles=smiles,
        molecular_weight=round(max(10.0, molecular_weight), 2),
        logp=float(logp),
        tpsa=float(tpsa),
        hbd=int(min(5, counts["N"] + counts["O"])),
        hba=int(min(10, counts["N"] + counts["O"] + counts["S"])),
        rotatable_bonds=int(max(0, counts["branches"])),
        aromatic_rings=int(counts["rings"] // 2 if counts["rings"] else counts["aromatic"] // 6),
        hetero_atoms=int(hetero),
        halogens=int(counts["F"] + counts["Cl"] + counts["Br"] + counts["I"]),
        heavy_atoms=int(carbon_count + hetero + counts["F"] + counts["Cl"] + counts["Br"] + counts["I"]),
        mode="heuristic",
    )
