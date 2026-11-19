#!/usr/bin/env python3
"""
HTBI Bedside Calculator — Command Line Interface (CLI)
Host-Tumor Biophysical Index (HTBI) Continuous Risk Modeler
Author: Luca Celebrano, Independent Researcher
License: Creative Commons Attribution 4.0 International (CC BY 4.0)
"""

import sys
import argparse
import numpy as np

BANNER = (
    "\x1b[1;36m┌────────────────────────────────────────────────────────────────────────┐\n"
    "│ \x1b[1;32m🧬 HTBI Bedside Calculator & Research Explorer v1.0.0\x1b[1;36m                  │\n"
    "│                                                                        │\n"
    "│ \x1b[1;33m⭐ If this in silico biophysical tool supports your research, please\x1b[1;36m   │\n"
    "│ \x1b[1;33m   consider giving the repository a star on GitHub:\x1b[1;36m                    │\n"
    "│ 👉 \x1b[1;34mhttps://github.com/Lukecele/htbi-bedside-calculator\x1b[1;36m                 │\n"
    "└────────────────────────────────────────────────────────────────────────┘\x1b[0m\n"
)


def compute_htbi(stage, grade, desmo, tils, nlr, crp, alb, smoking, bmi):
    grade_map = {
        "G1": 0.12,
        "G2": 0.50,
        "G3": 0.88,
    }
    p_seed_loss = grade_map.get(grade, 0.50)

    desmo_map = {"Minimal": 0.08, "Low": 0.32, "Moderate": 0.65, "High": 0.92}
    m_base = desmo_map.get(desmo, 0.65)

    tils_effect = ((15.0 - tils) / 35.0) * 0.18
    m_mech = float(np.clip(m_base + tils_effect, 0.02, 0.98))

    crp_norm = np.clip((np.log1p(crp) - np.log1p(0.5)) / (np.log1p(40.0) - np.log1p(0.5)), 0.0, 1.0)
    alb_norm = np.clip((46.0 - alb) / (46.0 - 28.0), 0.0, 1.0)
    nlr_norm = np.clip((np.log1p(nlr) - np.log1p(1.0)) / (np.log1p(7.0) - np.log1p(1.0)), 0.0, 1.0)

    smoke_val = {"Never": 0.0, "Former": 0.05, "Current": 0.12}.get(smoking, 0.0)
    bmi_val = np.clip((bmi - 22.0) / (36.0 - 22.0), 0.0, 1.0) * 0.10 if bmi >= 22.0 else np.clip((22.0 - bmi) / (22.0 - 16.0), 0.0, 1.0) * 0.08

    phi_blood = float(np.clip(0.35 * crp_norm + 0.25 * alb_norm + 0.30 * nlr_norm + smoke_val + bmi_val, 0.02, 0.98))
    htbi = float(np.clip(0.40 * p_seed_loss + 0.35 * m_mech + 0.25 * phi_blood, 0.01, 0.99))

    stage_mult = {"Stage I": 1.0, "Stage II": 1.85, "Stage III": 2.90}.get(stage, 1.85)
    base_hazard_per_year = 0.065 * stage_mult
    patient_hazard = base_hazard_per_year * np.exp(1.15 * (htbi - 0.45))

    prob_24m = float(np.clip((1.0 - np.exp(-patient_hazard * 2.0)) * 100.0, 3.0, 95.0))
    prob_36m = float(np.clip((1.0 - np.exp(-patient_hazard * 3.0)) * 100.0, 5.0, 98.0))

    base_lead_months = 5.45
    lead_time_months = float(base_lead_months * (1.0 - 0.30 * (m_mech - 0.50)))

    return {
        "htbi": htbi,
        "risk_tier": "High Biophysical Risk (HTBI >= 0.45)" if htbi >= 0.45 else "Low Biophysical Risk (HTBI < 0.45)",
        "p_seed_loss": p_seed_loss,
        "m_mech": m_mech,
        "phi_blood": phi_blood,
        "prob_24m": prob_24m,
        "prob_36m": prob_36m,
        "lead_time": lead_time_months,
        "patient_hazard": patient_hazard,
    }


def main():
    sys.stdout.write(BANNER)
    sys.stdout.flush()

    parser = argparse.ArgumentParser(
        description="HTBI Bedside Calculator — Biophysical Risk Explorer for Resected Solid Tumors (RUO)",
        epilog="Academic citation: Celebrano, L. (2026). HTBI Research Explorer. Zenodo. DOI: 10.5281/zenodo.24241000",
    )
    parser.add_argument("--stage", choices=["Stage I", "Stage II", "Stage III"], default="Stage II", help="Pathological TNM stage (default: Stage II)")
    parser.add_argument("--grade", choices=["G1", "G2", "G3"], default="G2", help="Tumor histological grade (default: G2)")
    parser.add_argument("--desmoplasia", choices=["Minimal", "Low", "Moderate", "High"], default="Moderate", help="Stromal desmoplasia intensity (default: Moderate)")
    parser.add_argument("--tils", type=float, default=15.0, help="Stromal tumor-infiltrating lymphocytes %% (default: 15.0)")
    parser.add_argument("--nlr", type=float, default=2.4, help="Neutrophil-to-Lymphocyte Ratio (default: 2.4)")
    parser.add_argument("--crp", type=float, default=3.2, help="High-sensitivity C-reactive protein in mg/L (default: 3.2)")
    parser.add_argument("--albumin", type=float, default=41.0, help="Serum albumin in g/L (default: 41.0)")
    parser.add_argument("--smoking", choices=["Never", "Former", "Current"], default="Never", help="Smoking status (default: Never)")
    parser.add_argument("--bmi", type=float, default=24.5, help="Body Mass Index in kg/m^2 (default: 24.5)")

    args = parser.parse_args()

    res = compute_htbi(
        stage=args.stage,
        grade=args.grade,
        desmo=args.desmoplasia,
        tils=args.tils,
        nlr=args.nlr,
        crp=args.crp,
        alb=args.albumin,
        smoking=args.smoking,
        bmi=args.bmi,
    )

    print("\x1b[1;37m" + "=" * 60 + "\x1b[0m")
    print(f"  \x1b[1;33mCOMPUTED HTBI SCORE:\x1b[0m \x1b[1;32m{res['htbi']:.4f}\x1b[0m")
    print(f"  \x1b[1;33mSTRATIFIED RISK TIER:\x1b[0m {res['risk_tier']}")
    print("-" * 60)
    print(f"  • Polarity / Seed Loss (P_hist):   {res['p_seed_loss']:.3f}")
    print(f"  • Stromal Resistance (M_mech):     {res['m_mech']:.3f}")
    print(f"  • Systemic Tension (Phi_blood):    {res['phi_blood']:.3f}")
    print("-" * 60)
    print(f"  • Projected 24-Month Relapse Risk: \x1b[1;31m{res['prob_24m']:.1f}%\x1b[0m")
    print(f"  • Projected 36-Month Relapse Risk: \x1b[1;31m{res['prob_36m']:.1f}%\x1b[0m")
    print(f"  • Analytical ctDNA Lead Time:      \x1b[1;36m{res['lead_time']:.2f} months\x1b[0m")
    print("\x1b[1;37m" + "=" * 60 + "\x1b[0m\n")


if __name__ == "__main__":
    main()
