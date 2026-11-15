import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ==============================================================================
# PAGE CONFIGURATION & ACADEMIC/RESEARCH STYLING
# ==============================================================================
st.set_page_config(
    page_title="HTBI Research Explorer | Biophysical Modeling",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for academic clarity, clinical-grade charts, and legal disclaimers
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
    .disclaimer-banner {
        background-color: #fffbeb;
        border: 1px solid #fef3c7;
        border-left: 5px solid #f59e0b;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 22px;
        font-size: 0.90rem;
        color: #92400e;
        line-height: 1.5;
    }
    .tier-banner-high {
        background-color: #fef2f2;
        border-left: 5px solid #ef4444;
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 20px;
    }
    .tier-banner-low {
        background-color: #f0fdf4;
        border-left: 5px solid #22c55e;
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CALCULATION ENGINE (Biophysical Reaction-Diffusion Parameterization)
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
    # Modified Glasgow Prognostic Score (mGPS)
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
        "risk_tier": "High Biophysical Risk" if htbi >= 0.45 else "Low Biophysical Risk",
        "p_seed_loss": p_seed_loss,
        "m_mech": m_mech,
        "phi_blood": phi_blood,
        "prob_24m": prob_24m,
        "prob_36m": prob_36m,
        "prob_5yr_os": prob_5yr_os,
        "lead_time": lead_time_months
    }

# ==============================================================================
# HEADER & MANDATORY RESEARCH USE ONLY (RUO) DISCLAIMER
# ==============================================================================
st.title("🔬 HTBI Research Explorer: Interactive Biophysical Risk Modeler")
st.markdown("""
**An In Silico Computational Tool Translating Microvascular Transport Mechanics, Desmoplasia, and Host Inflammatory Tension into Exploratory Risk Stratification.**  
**Author:** Luca Celebrano, MD Candidate · Department of Clinical Medicine and Surgery, Università degli Studi di Napoli Federico II
""")

st.markdown("""
<div class="disclaimer-banner">
    <strong>⚖️ STRICTLY FOR ACADEMIC, TRANSLATIONAL, AND RESEARCH USE ONLY (RUO)</strong><br>
    This software is an exploratory computational model developed to study continuum reaction-diffusion physics and retrospective prognostic associations in solid oncology (calibrated on MSKCC <em>N = 604</em> and Surgical GI <em>N = 1,056</em> cohorts). 
    <strong>It is NOT a medical device (SaMD), has NOT received regulatory clearance (CE-IVD / FDA), and must NOT be used for primary diagnostic, prognostic, or therapeutic decision-making in clinical care.</strong>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# SIDEBAR CONTROLS: RESEARCH SPECIMEN PARAMETERS
# ==============================================================================
st.sidebar.header("🔬 Input Research Parameters")

st.sidebar.subheader("1. Histopathological Architecture")
stage_input = st.sidebar.selectbox(
    "Pathologic TNM Stage",
    ["Stage I (Localized)", "Stage II (Locally Advanced)", "Stage III (Regional Nodal+)"],
    index=1
)

grade_input = st.sidebar.selectbox(
    "Glandular Differentiation / Architectural Grade",
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
    "Stromal Infiltrating Lymphocytes (TILs %)",
    min_value=0.0, max_value=60.0, value=15.0, step=1.0
)

st.sidebar.subheader("2. Pre-Operative Laboratory Biomarkers")
col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    nlr_input = st.number_input("CBC NLR (Ratio)", min_value=0.5, max_value=20.0, value=2.4, step=0.1)
with col_s2:
    crp_input = st.number_input("Serum hs-CRP (mg/L)", min_value=0.1, max_value=150.0, value=4.5, step=0.5)

alb_input = st.sidebar.number_input("Serum Albumin (g/L)", min_value=15.0, max_value=55.0, value=40.0, step=1.0)

st.sidebar.subheader("3. Host Baseline Background (Quasi-Static)")
smoking_input = st.sidebar.selectbox("Smoking History", ["Never Smoker", "Former Smoker", "Current Smoker"], index=1)
bmi_input = st.sidebar.number_input("Body Mass Index (BMI, kg/m²)", min_value=16.0, max_value=45.0, value=25.2, step=0.5)

# Execute Calculation
res = compute_htbi(
    stage_input, grade_input, desmo_input, tils_input,
    nlr_input, crp_input, alb_input, smoking_input, bmi_input
)

# ==============================================================================
# MAIN DASHBOARD: STRATIFICATION & VISUAL ANALYTICS
# ==============================================================================
col_main_left, col_main_right = st.columns([1, 1.2])

with col_main_left:
    st.subheader("🎯 Model Stratification Tier")
    
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
    fig_gauge.update_layout(height=270, margin=dict(l=20, r=20, t=35, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Stratification Status Banner
    if res["htbi"] >= 0.45:
        st.markdown(f"""
        <div class="tier-banner-high">
            <h4 style="color: #991b1b; margin:0;">⚠️ High Biophysical Risk Profile (HTBI = {res['htbi']:.3f})</h4>
            <p style="color: #7f1d1d; margin:5px 0 0 0; font-size: 0.90rem;">
                Model flags severe transport decay and elevated systemic inflammatory tension. Matches recurrence trajectories in high-risk retrospective subsets.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="tier-banner-low">
            <h4 style="color: #166534; margin:0;">✅ Low Biophysical Risk Profile (HTBI = {res['htbi']:.3f})</h4>
            <p style="color: #14532d; margin:5px 0 0 0; font-size: 0.90rem;">
                Preserved tissue polarity and low systemic inflammatory background correlate with favorable multi-year relapse-free survival.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # 3-Component Breakdown Radar Chart
    categories = ['Seed Polarity Loss', 'Stromal Transport Resistance', 'Systemic Inflammatory Tension']
    values = [res['p_seed_loss'], res['m_mech'], res['phi_blood']]
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.2)',
        line=dict(color='#2563eb', width=2),
        name='Biophysical Triad'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
        height=270,
        margin=dict(l=40, r=40, t=20, b=20)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col_main_right:
    st.subheader("📈 In Silico Projections & ctDNA Horizon")
    
    # Key Exploratory Metrics Cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Model 24-Mo Relapse Risk", f"{res['prob_24m']:.1f}%", delta=f"{'+' if res['prob_24m']>25 else '-'}{abs(res['prob_24m']-25):.1f}% vs cohort ref", delta_color="inverse")
    with c2:
        st.metric("Model 36-Mo Relapse Risk", f"{res['prob_36m']:.1f}%")
    with c3:
        st.metric("Analytical ctDNA Lead Time", f"{res['lead_time']:.1f} Mo", help="Theoretical window between micrometastatic ctDNA threshold and radiographic imaging detection.")

    # 60-Month Relapse-Free Survival Curve
    time_pts = np.linspace(0, 60, 61)
    stage_num = 1 if "Stage I" in stage_input else (2 if "Stage II" in stage_input else 3)
    pat_hazard = 0.08 * (stage_num ** 1.3) * np.exp(0.911 * res['htbi'])
    low_hazard = 0.08 * (stage_num ** 1.3) * np.exp(0.911 * 0.20)

    pat_surv = np.exp(-pat_hazard * (time_pts / 12.0)) * 100.0
    low_surv = np.exp(-low_hazard * (time_pts / 12.0)) * 100.0

    df_curves = pd.DataFrame({
        "Month": time_pts,
        "Simulated Patient Trajectory": pat_surv,
        "Optimal Host Reference": low_surv
    })

    fig_curves = go.Figure()
    fig_curves.add_trace(go.Scatter(x=df_curves["Month"], y=df_curves["Simulated Patient Trajectory"], mode='lines', name='Simulated Trajectory', line=dict(color='#ef4444' if res['htbi']>=0.45 else '#22c55e', width=3)))
    fig_curves.add_trace(go.Scatter(x=df_curves["Month"], y=df_curves["Optimal Host Reference"], mode='lines', name='Favorable Reference (HTBI 0.20)', line=dict(color='#94a3b8', width=2, dash='dash')))
    
    fig_curves.update_layout(
        title="Simulated Relapse-Free Trajectory (60 Months)",
        xaxis_title="Months Post-Resection",
        yaxis_title="Estimated RFS Probability (%)",
        yaxis_range=[0, 105],
        height=270,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_curves, use_container_width=True)

    # Mechanistic Research Insights
    st.markdown("### 🔬 Mechanistic & Exploratory Research Insights")
    if res["htbi"] >= 0.45:
        st.info("""
        **Biophysical Hypotheses for High-Risk Microenvironments:**
        * **Microvascular Cord Shielding:** High stromal desmoplasia ($M_{\\text{mech}}$) and elevated interstitial fluid pressure correlate with poor drug penetration into distal sleeves ($r > 165\\,\\mu\\text{m}$), providing a potential physical explanation for persister dormancy during adjuvant cycles.
        * **ctDNA Kinetic Window:** The model analytically calculates a median ~5.45-month interval between clonal surge and macroscopic CT recurrence, suggesting an optimal analytical cadence for longitudinal liquid biopsy study designs.
        * **Host Soil Pre-Conditioning:** High pre-operative inflammatory tone (NLR / mGPS) accelerates CD8+ T-cell exhaustion clock ($E_{\\text{imm}}$), supporting exploratory research into anti-inflammatory host co-modulation.
        """)
    else:
        st.success("""
        **Biophysical Characteristics of Favorable Microenvironments:**
        * **Preserved Transport Permeability:** Low desmoplastic resistance minimizes sub-therapeutic drug sanctuaries, facilitating complete cytotoxic/targeted clonal clearance.
        * **Endogenous Immunosurveillance:** Uncompromised baseline host soil correlates with sustained functional memory and low cumulative exhaustion pressure.
        """)

# ==============================================================================
# FOOTER & CITATION
# ==============================================================================
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem;">
    <strong>Host-Tumor Biophysical Index (HTBI) Research Framework</strong> · Conceptualized by Luca Celebrano (MD Candidate, Università degli Studi di Napoli Federico II).<br>
    Empirically evaluated across retrospective clinical cohorts (MSKCC <em>N = 604</em>; GI Surgical Blood <em>N = 1,056</em>; TCGA Pan-Cancer <em>N = 1,212</em>).<br>
    <em>Strictly for investigational, translational research, and computational modeling. Not for medical diagnosis or treatment decisions.</em>
</div>
""", unsafe_allow_html=True)
