import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ==============================================================================
# PAGE CONFIGURATION & MEDICAL STYLING
# ==============================================================================
st.set_page_config(
    page_title="HTBI Bedside Clinical Calculator",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for high-clarity clinical typography and dashboard cards
st.markdown("""
<style>
    .reportview-container {
        background-color: #f8fafc;
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
    }
    .metric-value-high {
        font-size: 2.2rem;
        font-weight: 700;
        color: #dc2626;
    }
    .metric-value-low {
        font-size: 2.2rem;
        font-weight: 700;
        color: #16a34a;
    }
    .metric-label {
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #64748b;
        letter-spacing: 0.05em;
    }
    .clinical-banner-high {
        background-color: #fef2f2;
        border-left: 5px solid #ef4444;
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 20px;
    }
    .clinical-banner-low {
        background-color: #f0fdf4;
        border-left: 5px solid #22c55e;
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CALCULATION ENGINE (Coupled Reaction-Diffusion Translation)
# ==============================================================================
def compute_htbi(stage, grade, desmo, tils, nlr, crp, alb, smoking, bmi):
    # 1. Cellular Polarity Loss (1 - P_hist in [0.0, 1.0])
    grade_map = {
        "G1: Well-differentiated / Lepidic": 0.10,
        "G2: Moderately differentiated / Acinar / Papillary": 0.50,
        "G3: Poorly differentiated / Solid / Micropapillary": 0.90
    }
    p_seed_loss = grade_map.get(grade, 0.50)

    # 2. Stromal Mechanical Transport Resistance (M_mech in [0.0, 1.0])
    desmo_map = {"None / Minimal": 0.05, "Low": 0.30, "Moderate": 0.65, "High / Dense": 0.95}
    m_base = desmo_map.get(desmo, 0.65)
    tils_mod = (15.0 - tils) / 100.0
    m_mech = np.clip(m_base + tils_mod * 0.20, 0.0, 1.0)

    # 3. Systemic Inflammatory Tension (Phi_blood in [0.0, 1.0])
    # modified Glasgow Prognostic Score (mGPS)
    if crp > 10.0 and alb < 35.0:
        mgps = 2
    elif crp > 10.0 or alb < 35.0:
        mgps = 1
    else:
        mgps = 0
    mgps_score = mgps / 2.0

    # Log-normalized NLR component
    nlr_norm = np.clip((np.log1p(nlr) - np.log1p(2.0)) / (np.log1p(8.0) - np.log1p(2.0)), 0.0, 1.0)
    
    # Lifestyle / metabolic background (Quasi-static sigma_soil)
    smoke_mod = 0.10 if smoking == "Current Smoker" else (0.05 if smoking == "Former Smoker" else 0.0)
    bmi_mod = 0.08 if bmi >= 30.0 else (0.03 if bmi >= 25.0 else 0.0)

    phi_blood = np.clip(0.55 * mgps_score + 0.35 * nlr_norm + smoke_mod + bmi_mod, 0.0, 1.0)

    # Composite HTBI
    htbi = 0.40 * p_seed_loss + 0.35 * m_mech + 0.25 * phi_blood
    htbi = float(np.clip(htbi, 0.0, 1.0))

    # Recurrence & Survival Projections calibrated on MSKCC (N=604) and GI Surgical Blood (N=1,056)
    stage_num = 1 if "Stage I" in stage else (2 if "Stage II" in stage else 3)
    base_hazard = 0.08 * (stage_num ** 1.3)
    patient_hazard = base_hazard * (np.exp(0.911 * htbi))

    prob_24m = float(1.0 - np.exp(-patient_hazard * 2.0)) * 100.0
    prob_36m = float(1.0 - np.exp(-patient_hazard * 3.0)) * 100.0
    prob_5yr_os = float(np.exp(-patient_hazard * 1.5 * 5.0)) * 100.0

    # Analytical ctDNA Lead Time Invariant (months prior to CT imaging)
    # T_lead = (ln(10^8 / 10^6) / ln 2) * T_d adjusted for transport retention
    base_lead_days = 6.644 * 24.6  # 163.4 days ~ 5.45 months
    lead_time_months = (base_lead_days / 30.44) * (1.0 - 0.25 * m_mech)

    return {
        "htbi": htbi,
        "risk_tier": "High Risk" if htbi >= 0.45 else "Low Risk",
        "p_seed_loss": p_seed_loss,
        "m_mech": m_mech,
        "phi_blood": phi_blood,
        "prob_24m": prob_24m,
        "prob_36m": prob_36m,
        "prob_5yr_os": prob_5yr_os,
        "lead_time": lead_time_months
    }

# ==============================================================================
# HEADER SECTION
# ==============================================================================
st.title("🧬 HTBI Bedside Clinical Decision Support")
st.markdown("""
**Host-Tumor Biophysical Index (HTBI) Calculator for Resected Solid Malignancies**  
*Translating Multiscale Reaction-Diffusion Transport, Desmoplasia, and Host Systemic Inflammation into Individualized Recurrence Prognostics.*  
**Author:** Luca Celebrano, MD Candidate · Department of Clinical Medicine and Surgery, Università degli Studi di Napoli Federico II
""")
st.divider()

# ==============================================================================
# SIDEBAR CONTROLS: CLINICAL AND LABORATORY INPUTS
# ==============================================================================
st.sidebar.header("📋 Patient Clinical Parameters")

st.sidebar.subheader("1. Surgical Histopathology")
stage_input = st.sidebar.selectbox(
    "Pathologic TNM Stage",
    ["Stage I (Localized)", "Stage II (Locally Advanced)", "Stage III (Regional Nodal+)"],
    index=1
)

grade_input = st.sidebar.selectbox(
    "Histological Differentiation / Subtype",
    [
        "G1: Well-differentiated / Lepidic",
        "G2: Moderately differentiated / Acinar / Papillary",
        "G3: Poorly differentiated / Solid / Micropapillary"
    ],
    index=1
)

desmo_input = st.sidebar.selectbox(
    "Stromal Desmoplasia / Matrix Density",
    ["None / Minimal", "Low", "Moderate", "High / Dense"],
    index=2
)

tils_input = st.sidebar.slider(
    "Tumor Infiltrating Lymphocytes (TILs %)",
    min_value=0.0, max_value=60.0, value=15.0, step=1.0
)

st.sidebar.subheader("2. Routine Pre-Operative Blood")
col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    nlr_input = st.number_input("CBC NLR (Ratio)", min_value=0.5, max_value=20.0, value=2.4, step=0.1)
with col_s2:
    crp_input = st.number_input("Serum hs-CRP (mg/L)", min_value=0.1, max_value=150.0, value=4.5, step=0.5)

alb_input = st.sidebar.number_input("Serum Albumin (g/L)", min_value=15.0, max_value=55.0, value=40.0, step=1.0)

st.sidebar.subheader("3. Host Physiological Background")
smoking_input = st.sidebar.selectbox("Smoking History", ["Never Smoker", "Former Smoker", "Current Smoker"], index=1)
bmi_input = st.sidebar.number_input("Body Mass Index (BMI, kg/m²)", min_value=16.0, max_value=45.0, value=25.2, step=0.5)

# Execute Calculation
res = compute_htbi(
    stage_input, grade_input, desmo_input, tils_input,
    nlr_input, crp_input, alb_input, smoking_input, bmi_input
)

# ==============================================================================
# MAIN DASHBOARD LAYOUT
# ==============================================================================
col_main_left, col_main_right = st.columns([1, 1.2])

with col_main_left:
    st.subheader("🎯 Biophysical Risk Stratification")
    
    # HTBI Gauge Chart
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=res["htbi"],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Host-Tumor Biophysical Index (HTBI)", 'font': {'size': 18}},
        gauge={
            'axis': {'range': [0.0, 1.0], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#1e293b"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0.0, 0.45], 'color': '#bbf7d0'},
                {'range': [0.45, 0.70], 'color': '#fed7aa'},
                {'range': [0.70, 1.0], 'color': '#fecaca'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.8,
                'value': 0.45
            }
        }
    ))
    fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Risk Tier Banner
    if res["htbi"] >= 0.45:
        st.markdown(f"""
        <div class="clinical-banner-high">
            <h3 style="color: #991b1b; margin:0;">⚠️ High Biophysical Risk Tier (HTBI = {res['htbi']:.3f})</h3>
            <p style="color: #7f1d1d; margin:5px 0 0 0;">
                Microenvironmental conditions promote persister dormancy in sub-therapeutic cords and progressive immune exhaustion.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="clinical-banner-low">
            <h3 style="color: #166534; margin:0;">✅ Low Biophysical Risk Tier (HTBI = {res['htbi']:.3f})</h3>
            <p style="color: #14532d; margin:5px 0 0 0;">
                Preserved tissue architecture and low systemic inflammatory tension favor durable cytotoxic immune clearance.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # 3-Component Breakdown Radar Chart
    categories = ['Epithelial Polarity Loss (Seed)', 'Stromal Transport Resistance (Matrix)', 'Systemic Inflammatory Tension (Soil)']
    values = [res['p_seed_loss'], res['m_mech'], res['phi_blood']]
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.2)',
        line=dict(color='#2563eb', width=2),
        name='Patient Biophysical Fingerprint'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
        height=280,
        margin=dict(l=40, r=40, t=20, b=20)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col_main_right:
    st.subheader("📈 Prognostic Trajectories & ctDNA Window")
    
    # Key Prognostic Metrics Cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("24-Month Relapse Risk", f"{res['prob_24m']:.1f}%", delta=f"{'+' if res['prob_24m']>25 else '-'}{abs(res['prob_24m']-25):.1f}% vs baseline", delta_color="inverse")
    with c2:
        st.metric("36-Month Relapse Risk", f"{res['prob_36m']:.1f}%")
    with c3:
        st.metric("Predicted ctDNA Lead Time", f"{res['lead_time']:.1f} Mo", help="Expected median interval between molecular ctDNA surge and radiographic recurrence.")

    # 60-Month Relapse-Free Survival Curve
    time_pts = np.linspace(0, 60, 61)
    stage_num = 1 if "Stage I" in stage_input else (2 if "Stage II" in stage_input else 3)
    pat_hazard = 0.08 * (stage_num ** 1.3) * np.exp(0.911 * res['htbi'])
    low_hazard = 0.08 * (stage_num ** 1.3) * np.exp(0.911 * 0.20)

    pat_surv = np.exp(-pat_hazard * (time_pts / 12.0)) * 100.0
    low_surv = np.exp(-low_hazard * (time_pts / 12.0)) * 100.0

    df_curves = pd.DataFrame({
        "Month": time_pts,
        "Patient Trajectory": pat_surv,
        "Optimal Host Baseline": low_surv
    })

    fig_curves = go.Figure()
    fig_curves.add_trace(go.Scatter(x=df_curves["Month"], y=df_curves["Patient Trajectory"], mode='lines', name='Patient Trajectory', line=dict(color='#ef4444' if res['htbi']>=0.45 else '#22c55e', width=3)))
    fig_curves.add_trace(go.Scatter(x=df_curves["Month"], y=df_curves["Optimal Host Baseline"], mode='lines', name='Ideal Host Baseline (HTBI 0.20)', line=dict(color='#94a3b8', width=2, dash='dash')))
    
    fig_curves.update_layout(
        title="Projected Relapse-Free Trajectory (60 Months)",
        xaxis_title="Months Post-Resection",
        yaxis_title="Relapse-Free Survival (%)",
        yaxis_range=[0, 105],
        height=280,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_curves, use_container_width=True)

    # Actionable Clinical Recommendations Box
    st.markdown("### 🩺 Actionable Clinical Recommendations")
    if res["htbi"] >= 0.45:
        st.warning("""
        **Elevated Risk of Post-Discontinuation Relapse Detected:**
        * **1. Intensified Molecular Surveillance:** Initiate serial plasma ctDNA monitoring every 3 months. In desmoplastic / high-IFP tumors, dormant persisters shed ctDNA at reduced rates until an angiogenic surge breaches stromal cuffs (~5.45 months lead time before CT scan).
        * **2. Seed-Soil Co-Targeting Rationale:** Standard adjuvant targeted/chemotherapy alone may fail to sterilize the outer 31.28% annular cord sanctuary ($r > 165\\,\\mu\\text{m}$).
        * **3. Microenvironmental Decompression:** Consider host anti-inflammatory and lifestyle optimization (systemic hs-CRP normalization, metabolic optimization) to mitigate CD8+ T-cell exhaustion clock ($E_{\\text{imm}}$).
        """)
    else:
        st.success("""
        **Favorable Host-Tumor Microenvironment:**
        * **1. Routine Surveillance:** Standard clinical and radiographic follow-up according to NCCN guidelines.
        * **2. Low Occult Persistence Index:** Microvascular diffusion penetration and low cumulative host inflammatory damage favor durable remission.
        """)

# ==============================================================================
# FOOTER & CITATION
# ==============================================================================
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem;">
    <strong>Host-Tumor Biophysical Index (HTBI) Framework</strong> · Research Concept & Clinical Tool by Luca Celebrano (MD Candidate, Università degli Studi di Napoli Federico II).<br>
    Calibrated against MSKCC lung adenocarcinoma (<em>N = 604</em>) and Surgical GI complete-case blood biomarkers (<em>N = 1,056</em>).<br>
    <em>For investigational and educational use. Not a substitute for formal multidisciplinary clinical board decisions.</em>
</div>
""", unsafe_allow_html=True)
