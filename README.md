# HTBI Bedside Clinical Decision Support (Web Calculator)

An interactive, clinical decision support web application translating the **Host-Tumor Biophysical Index (HTBI)** into individualized post-resection recurrence risk, 60-month survival trajectories, and analytical ctDNA lead time projections.

**Author:** Luca Celebrano, MD Candidate  
*Department of Clinical Medicine and Surgery, School of Medicine and Surgery, Università degli Studi di Napoli Federico II, Naples, Italy*  
**License:** MIT License  

---

## 🔬 Biophysical and Clinical Rational

Standard clinical oncology relies heavily on anatomical TNM staging and somatic NGS driver alterations. However, identical pathologic stage tumors frequently exhibit divergent clinical courses:
1. **The $R_0$ Resection Relapse Paradox:** Curatively resected solid tumors with negative microscopic margins often recur rapidly within 12–24 months.
2. **The Post-Adjuvant Rebound:** In the landmark ADAURA trial, 67.9% of all recurrence events cluster after the planned 36-month targeted therapy cessation (with 57.9% occurring within the first 12 months post-cessation).

The **HTBI framework** integrates Stephen Paget's classic "Seed and Soil" paradigm with continuum physics:
* **The Seed (Cellular Polarity Integrity, $1 - P_{\text{hist}}$):** Evaluates loss of apical-basal polarity and glandular differentiation (IASLC/WHO grading).
* **The Mechanical Barrier (Desmoplasia & IFP, $M_{\text{mech}}$):** Accounts for elevated interstitial fluid pressure ($\text{IFP} \approx 20\text{--}35\text{ mmHg}$) and microvascular compression, formalizing the $31.28\%$ sub-therapeutic annular cord sanctuary ($r > 165.89\ \mu\text{m}$) via modified Bessel functions of the second kind ($K_0$).
* **The Soil (Systemic Inflammatory Tension, $\Phi_{\text{blood}}$):** Integrates routine pre-operative blood markers (neutrophil-to-lymphocyte ratio [NLR], serum hs-CRP, and albumin via the modified Glasgow Prognostic Score [mGPS]) reflecting host immune exhaustion pressure.

$$\text{HTBI} = 0.40 \cdot (1 - P_{\text{hist}}) + 0.35 \cdot M_{\text{mech}} + 0.25 \cdot \Phi_{\text{blood}}$$

---

## 📊 Clinical Cohort Calibrations

The scoring and predictive hazard functions are empirically calibrated across verified clinical cohorts:
* **MSKCC Lung Adenocarcinoma Discovery Cohort ($N = 604$, 98 recurrences):** Multivariable continuous $\text{HR} = 2.49$ ($95\%\text{ CI: } 1.00\text{--}6.18$, $p = 0.050$), binary $\text{HR} = 1.89$ ($p = 0.029$), with incremental discrimination gain $\Delta C\text{-index} = +0.050$ ($p = 0.044$).
* **Surgical GI Complete-Case Blood Chemistry Cohort ($N = 1,056$):** 5-year overall survival stratified from $69.4\%$ (Low HTBI) to $56.7\%$ (High HTBI) (Log-rank $p = 3.81 \times 10^{-7}$, multivariable $\text{HR} = 1.434$, $p = 0.00224$).
* **ctDNA Lead Time Invariant:** Analytically reproduces the empirical $5.45\text{-month}$ median lead time between molecular ctDNA detection and radiographic CT imaging progression.

---

## 🚀 Quick Start (Local Execution)

### Prerequisites
* Python 3.9+
* pip

### Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/Lukecele/htbi-bedside-calculator.git
cd htbi-bedside-calculator
pip install -r requirements.txt
```

### Running the Web App
Launch the interactive Streamlit dashboard:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🌐 Deploy to Streamlit Community Cloud (Free)

1. Push this repository to your GitHub profile (`Lukecele/htbi-bedside-calculator`).
2. Visit [share.streamlit.io](https://share.streamlit.io).
3. Connect your GitHub account and select this repository.
4. Set Main file path to `app.py`.
5. Click **Deploy!** Your clinical calculator will be live on a public URL accessible from any mobile or desktop browser.

---

## 📄 Disclaimer
This software and mathematical framework are developed for investigational, translational research, and educational purposes only. It is not intended as a substitute for individualized clinical judgment or formal multidisciplinary tumor board recommendations.
