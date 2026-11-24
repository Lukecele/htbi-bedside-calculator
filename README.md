# HTBI Research Explorer: Interactive Biophysical Risk Modeler

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.24393471-blue)](https://doi.org/10.5281/zenodo.24393471)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://htbi-bedside-calculator-yu8jwzkifktp2bvvs4ped4.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![bio.tools](https://img.shields.io/badge/bio.tools-htbi--bedside--app--v2-blue.svg)](https://bio.tools/htbi-bedside-app-v2)
[![GitHub Stars](https://img.shields.io/github/stars/Lukecele/htbi-bedside-calculator?style=social)](https://github.com/Lukecele/htbi-bedside-calculator)

[![Analysis Pipeline Zenodo DOI](https://img.shields.io/badge/Pipeline_DOI-10.5281%2Fzenodo.24118328-blue.svg)](https://doi.org/10.5281/zenodo.24118328)

An interactive *in silico* translational and educational dashboard evaluating the **Host-Tumor Biophysical Index (HTBI)** across post-resection solid oncology cohorts.

* **Live Web Application:** [https://htbi-bedside-calculator-yu8jwzkifktp2bvvs4ped4.streamlit.app/](https://htbi-bedside-calculator-yu8jwzkifktp2bvvs4ped4.streamlit.app/)
* **Author:** Luca Celebrano, MD Candidate ([ORCID: 0009-0007-0931-3555](https://orcid.org/0009-0007-0931-3555))  
  *Independent Researcher, Naples, Italy*
* **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
* **ELIXIR bio.tools ID:** [`biotools:htbi-bedside-app-v2`](https://bio.tools/htbi-bedside-app-v2)

---

## ⚖️ Regulatory & Ethical Disclaimer: Research Use Only (RUO)

> **IMPORTANT NOTICE:**  
> This software and computational model are developed **strictly for academic, translational, and research purposes only (RUO)**.  
> It is **NOT** a certified medical device (Software as a Medical Device - SaMD under EU MDR 2017/745 or US FDA digital health regulations), has not undergone prospective interventional clinical trial clearance, and is **NOT intended to provide individualized clinical diagnosis, prognosis, treatment recommendations, or patient management decisions**. All clinical care must be directed by qualified healthcare professionals and multidisciplinary tumor boards.

---

## 🔬 Scientific Rationale

Standard clinical oncology relies on anatomical TNM staging and somatic NGS driver alterations. However, identically staged tumors frequently exhibit divergent clinical courses:
1. **The $R_0$ Resection Relapse Paradox:** Curatively resected solid tumors with negative microscopic margins often recur within 12–24 months due to dormant micrometastases in hostile biophysical niches.
2. **The Post-Adjuvant Rebound:** In the ADAURA trial, 67.9% of all recurrence events cluster after the planned 36-month targeted therapy cessation (with 57.9% occurring within the first 12 months post-cessation).

The **HTBI framework** integrates Stephen Paget's classic "Seed and Soil" paradigm with continuum biophysics:
* **The Seed (Cellular Polarity Integrity, $1 - P_{\text{hist}}$):** Loss of apical-basal polarity and glandular differentiation (IASLC/WHO grading).
* **The Mechanical Barrier (Desmoplasia & IFP, $M_{\text{mech}}$):** Elevated interstitial fluid pressure ($\text{IFP} \approx 20\text{--}35\text{ mmHg}$) and microvascular compression, formalizing the $31.28\%$ sub-therapeutic annular cord sanctuary ($r > 165.89\ \mu\text{m}$) via modified Bessel functions of the second kind ($K_0$).
* **The Soil (Systemic Inflammatory Tension, $\Phi_{\text{blood}}$):** Pre-operative blood chemistry (neutrophil-to-lymphocyte ratio [NLR], serum hs-CRP, and albumin via the modified Glasgow Prognostic Score [mGPS]) reflecting host immune exhaustion pressure.

$$\text{HTBI} = 0.40 \cdot (1 - P_{\text{hist}}) + 0.35 \cdot M_{\text{mech}} + 0.25 \cdot \Phi_{\text{blood}}$$

---

## 📊 Retrospective Cohort Calibrations

The model is empirically calibrated on retrospective cohorts:
* **MSKCC Lung Adenocarcinoma Discovery Cohort ($N = 604$, 98 recurrences):** Multivariable continuous $\text{HR} = 2.49$ ($95\%\text{ CI: } 1.00\text{--}6.18$, $p = 0.050$), binary $\text{HR} = 1.89$ ($p = 0.029$), bootstrap $\Delta C\text{-index} = +0.050$ ($p = 0.044$).
* **Independent High-Grade Component Multi-Center Replication ($N = 1,539$):** Real-world Stage I surgical cohort (Liang et al., *Cancer Med* 2026, DOI: [10.1002/cam4.72439](https://doi.org/10.1002/cam4.72439)) independently validating the $(1 - P_{\text{hist}})$ solid/micropapillary penalty with DFS $\text{HR} = 3.95$ ($95\%\text{ CI: } 1.53\text{--}10.15$, $p < 0.001$).
* **Surgical GI Complete-Case Blood Chemistry Cohort ($N = 1,056$):** 5-year overall survival stratified from $69.4\%$ (Low HTBI) to $56.7\%$ (High HTBI) (Log-rank $p = 3.81 \times 10^{-7}$, multivariable $\text{HR} = 1.434$, $p = 0.00224$).
* **ctDNA Lead Time Invariant:** Analytically reproduces the empirical $5.45\text{-month}$ median lead time between molecular ctDNA detection and radiographic CT imaging progression.

---

## 🚀 Quick Start (Local Execution)

```bash
git clone https://github.com/Lukecele/htbi-bedside-calculator.git
cd htbi-bedside-calculator
pip install -r requirements.txt

# Option A: Launch the interactive web dashboard
streamlit run app.py

# Option B: Run headless calculation directly in terminal
python3 cli.py --stage "Stage II" --grade G2 --desmoplasia Moderate
```
For web dashboard, open `http://localhost:8501` in your browser.

---

## 📖 How to Cite

If you use this software, computational framework, or the interactive explorer in your research, please cite:

### Software Citation (Zenodo DOI):
> Celebrano, L. (2026). *HTBI Research Explorer: Interactive Biophysical Risk Modeler* (Version 1.0.0). Zenodo. https://doi.org/10.5281/zenodo.24393471

### Associated Research Article:
> Celebrano, L. (2026). *Continuum Biophysics of Post-Resection Relapse Kinetics: Resolving the R0 Margins Paradox and ADAURA Post-Adjuvant Rebound via a Validated Host-Tumor Biophysical Index (HTBI)*. Research Square. 

### BibTeX:
```bibtex
@software{Celebrano_HTBI_Explorer_2026,
  author = {Celebrano, Luca},
  title = {{HTBI Research Explorer: Interactive Biophysical Risk Modeler}},
  year = {2026},
  version = {1.0.0},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.24241000},
  url = {https://doi.org/10.5281/zenodo.24393471},
  license = {CC-BY-4.0}
}

@article{Celebrano_HTBI_Biophysics_2026,
  author = {Celebrano, Luca},
  title = {{Continuum Biophysics of Post-Resection Relapse Kinetics: Resolving the R0 Margins Paradox and ADAURA Post-Adjuvant Rebound via a Validated Host-Tumor Biophysical Index (HTBI)}},
  journal = {Research Square},
  year = {2026},
  doi = {}
}
```

---

## ⭐ Support the Research

If this biophysical model or interactive explorer aids your computational oncology research or educational coursework, please consider **starring this repository** on GitHub!

---

## 📄 License

This project is licensed under the **Creative Commons Attribution 4.0 International Public License (CC BY 4.0)**.  
You are free to share and adapt the material for any purpose, provided appropriate credit is given to the author. See the [LICENSE](LICENSE) file for complete legal details.
