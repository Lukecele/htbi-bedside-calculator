# HTBI Research Explorer: Interactive Biophysical Risk Modeler

An interactive in silico research and translational exploratory dashboard evaluating the **Host-Tumor Biophysical Index (HTBI)** across post-resection solid oncology cohorts.

**Author:** Luca Celebrano, MD Candidate  
*Department of Clinical Medicine and Surgery, School of Medicine and Surgery, Università degli Studi di Napoli Federico II, Naples, Italy*  
**License:** MIT License  

---

## ⚖️ Regulatory & Ethical Disclaimer: Research Use Only (RUO)

> **IMPORTANT NOTICE:**  
> This software and computational model are developed **strictly for academic, translational, and research purposes only (RUO)**.  
> It is **NOT** a medical device (Software as a Medical Device - SaMD under EU MDR 2017/745 or US FDA digital health regulations), has not undergone prospective interventional clinical trial clearance, and is **NOT intended to provide individualized clinical diagnosis, prognosis, treatment recommendations, or patient management decisions**. All clinical care must be directed by qualified healthcare professionals and multidisciplinary tumor boards.

---

## 🔬 Scientific Rational

Standard clinical oncology relies on anatomical TNM staging and somatic NGS driver alterations. However, identically staged tumors frequently exhibit divergent clinical courses:
1. **The $R_0$ Resection Relapse Paradox:** Curatively resected solid tumors with negative microscopic margins often recur within 12–24 months.
2. **The Post-Adjuvant Rebound:** In the ADAURA trial, 67.9% of all recurrence events cluster after the planned 36-month targeted therapy cessation (with 57.9% occurring within the first 12 months post-cessation).

The **HTBI framework** integrates Stephen Paget's classic "Seed and Soil" paradigm with continuum biophysics:
* **The Seed (Cellular Polarity Integrity, $1 - P_{\text{hist}}$):** Loss of apical-basal polarity and glandular differentiation (IASLC/WHO grading).
* **The Mechanical Barrier (Desmoplasia & IFP, $M_{\text{mech}}$):** Accounts for elevated interstitial fluid pressure ($\text{IFP} \approx 20\text{--}35\text{ mmHg}$) and microvascular compression, formalizing the $31.28\%$ sub-therapeutic annular cord sanctuary ($r > 165.89\ \mu\text{m}$) via modified Bessel functions of the second kind ($K_0$).
* **The Soil (Systemic Inflammatory Tension, $\Phi_{\text{blood}}$):** Integrates routine pre-operative blood markers (neutrophil-to-lymphocyte ratio [NLR], serum hs-CRP, and albumin via the modified Glasgow Prognostic Score [mGPS]) reflecting host immune exhaustion pressure.

$$\text{HTBI} = 0.40 \cdot (1 - P_{\text{hist}}) + 0.35 \cdot M_{\text{mech}} + 0.25 \cdot \Phi_{\text{blood}}$$

---

## 📊 Retrospective Cohort Calibrations

The model is empirically calibrated on retrospective datasets:
* **MSKCC Lung Adenocarcinoma Discovery Cohort ($N = 604$, 98 recurrences):** Multivariable continuous $\text{HR} = 2.49$ ($95\%\text{ CI: } 1.00\text{--}6.18$, $p = 0.050$), binary $\text{HR} = 1.89$ ($p = 0.029$), bootstrap $\Delta C\text{-index} = +0.050$ ($p = 0.044$).
* **Surgical GI Complete-Case Blood Chemistry Cohort ($N = 1,056$):** 5-year overall survival stratified from $69.4\%$ (Low HTBI) to $56.7\%$ (High HTBI) (Log-rank $p = 3.81 \times 10^{-7}$, multivariable $\text{HR} = 1.434$, $p = 0.00224$).
* **ctDNA Lead Time Invariant:** Analytically reproduces the empirical $5.45\text{-month}$ median lead time between molecular ctDNA detection and radiographic CT imaging progression.

---

## 🚀 Quick Start (Local Execution)

```bash
git clone https://github.com/Lukecele/htbi-bedside-calculator.git
cd htbi-bedside-calculator
pip install -r requirements.txt
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 🌐 Deployment Options

### 1. Streamlit Community Cloud (Free 1-Click)
1. Push this repository to GitHub (`Lukecele/htbi-bedside-calculator`).
2. Log into [share.streamlit.io](https://share.streamlit.io) with GitHub.
3. Select this repository and set main file to `app.py`. Click **Deploy**.

### 2. Hugging Face Spaces
Create a new Space with SDK `Streamlit`, push these repository files, and it will be instantly hosted with an academic badge.
