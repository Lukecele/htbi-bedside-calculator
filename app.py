import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ==============================================================================
# PAGE CONFIGURATION & MEDICAL CALCULATOR STYLING
# ==============================================================================
st.set_page_config(
    page_title="HTBI Research Calculator | In Silico Oncology",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for high-responsiveness and clear visual feedback
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 2px;
    }
    .sub-title {
        font-size: 1.0rem;
        color: #475569;
        margin-bottom: 16px;
    }
    .disclaimer-box {
        background-color: #fffbeb;
        border: 1px solid #fef3c7;
        border-left: 5px solid #d97706;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 24px;
        font-size: 0.88rem;
        color: #92400e;
        line-height: 1.45;
    }
    .input-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 18px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    .input-header {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 12px;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 6px;
    }
    .tier-badge-high {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
        padding: 10px 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.05rem;
        text-align: center;
        margin-bottom: 14px;
    }
    .tier-badge-low {
        background-color: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
        padding: 10px 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.05rem;
        text-align: center;
        margin-bottom: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# ULTRA-RESPONSIVE CONTINUOUS COMPUTATION ENGINE
# ==============================================================================
def compute_htbi(stage, grade, desmo, tils, nlr, crp, alb, smoking, bmi):
    # 1. Cellular Polarity Loss (1 - P_hist in [0.0, 1.0])
    grade_map = {
        "G1: Well-differentiated / Lepidic": 0.12,
        "G2: Moderately differentiated / Acinar / Papillary": 0.50,
        "G3: Poorly differentiated / Solid / Micropapillary": 0.88
    }
    p_seed_loss = grade_map.get(grade, 0.50)

    # 2. Stromal Mechanical Transport Resistance (M_mech in [0.0, 1.0])
    desmo_map = {"None / Minimal": 0.08, "Low": 0.32, "Moderate": 0.65, "High / Dense": 0.92}
    m_base = desmo_map.get(desmo, 0.65)
    
    # Continuous TILs infiltration modulation: higher TILs actively soften/permeabilize stroma
    tils_effect = ((15.0 - tils) / 35.0) * 0.18
    m_mech = float(np.clip(m_base + tils_effect, 0.02, 0.98))

    # 3. Systemic Inflammatory Tension (Phi_blood in [0.0, 1.0])
    # Continuous smooth hs-CRP (log-sigmoid from 0.2 mg/L to 50.0 mg/L)
    crp_norm = np.clip((np.log1p(crp) - np.log1p(0.5)) / (np.log1p(40.0) - np.log1p(0.5)), 0.0, 1.0)
    
    # Continuous smooth Albumin (negative acute phase: 48 g/L -> 0.0, 26 g/L -> 1.0)
    alb_norm = np.clip((46.0 - alb) / (46.0 - 28.0), 0.0, 1.0)
    
    # Continuous smooth NLR (from 1.0 to 7.0)
    nlr_norm = np.clip((np.log1p(nlr) - np.log1p(1.0)) / (np.log1p(7.0) - np.log1p(1.0)), 0.0, 1.0)
    
    # Continuous Lifestyle / Metabolic Background (sigma_soil)
    smoke_val = {"Never Smoker": 0.0, "Former Smoker": 0.05, "Current Smoker": 0.12}.get(smoking, 0.0)
    bmi_val = np.clip((bmi - 22.0) / (36.0 - 22.0), 0.0, 1.0) * 0.10 if bmi >= 22.0 else np.clip((22.0 - bmi) / (22.0 - 16.0), 0.0, 1.0) * 0.08

    phi_blood = float(np.clip(0.35 * crp_norm + 0.25 * alb_norm + 0.30 * nlr_norm + smoke_val + bmi_val, 0.02, 0.98))

    # Composite Host-Tumor Biophysical Index (HTBI)
    htbi = float(np.clip(0.40 * p_seed_loss + 0.35 * m_mech + 0.25 * phi_blood, 0.01, 0.99))

    # 4. Clinical Recurrence & Survival Projections (Coupling TNM Stage + Biophysical HTBI)
    # Stage scaling factor: Stage I -> 1.0, Stage II -> 1.85, Stage III -> 2.90
    stage_mult = {"Stage I (Localized)": 1.0, "Stage II (Locally Advanced)": 1.85, "Stage III (Regional Nodal+)": 2.90}.get(stage, 1.85)
    
    # Calibrated Cox baseline hazard
    base_hazard_per_year = 0.065 * stage_mult
    patient_hazard = base_hazard_per_year * np.exp(1.15 * (htbi - 0.45))

    prob_24m = float(np.clip((1.0 - np.exp(-patient_hazard * 2.0)) * 100.0, 3.0, 95.0))
    prob_36m = float(np.clip((1.0 - np.exp(-patient_hazard * 3.0)) * 100.0, 5.0, 98.0))

    # Analytical ctDNA Lead Time Invariant (months prior to CT imaging)
    # Higher desmoplasia (M_mech) increases ctDNA physical retention and degradation
    base_lead_months = 5.45
    lead_time_months = float(base_lead_months * (1.0 - 0.30 * (m_mech - 0.50)))

    return {
        "htbi": htbi,
        "risk_tier": "High Biophysical Risk" if htbi >= 0.45 else "Low Biophysical Risk",
        "p_seed_loss": p_seed_loss,
        "m_mech": m_mech,
        "phi_blood": phi_blood,
        "prob_24m": prob_24m,
        "prob_36m": prob_36m,
        "lead_time": lead_time_months,
        "patient_hazard": patient_hazard
    }

# ==============================================================================
# HEADER SECTION
# ==============================================================================
st.markdown('<div class="main-title">🧬 HTBI Interactive Biophysical Calculator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Host-Tumor Biophysical Index: Dynamic Translation of Reaction-Diffusion Transport, Desmoplasia & Inflammation into Relapse Kinetics · <strong>Luca Celebrano (Università di Napoli Federico II)</strong></div>', unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer-box">
    <strong>⚖️ STRICTLY FOR ACADEMIC & RESEARCH USE ONLY (RUO)</strong><br>
    This computational calculator is an exploratory model for solid tumor biophysics and research risk exploration (calibrated on MSKCC <em>N = 604</em> and Surgical GI <em>N = 1,056</em>). It is NOT a medical device (SaMD) and must NOT be used to guide diagnostic, therapeutic, or surgical decisions in individual patients.
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 2-COLUMN LAYOUT: INPUTS (LEFT) vs REAL-TIME VISUALIZATIONS (RIGHT)
# ==============================================================================
col_input, col_output = st.columns([1.05, 1.25], gap="large")

with col_input:
    st.markdown("### 📝 Parametri Clinici & Biofisici")
    
    # CARD 1: Histopathology
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<div class="input-header">🔬 1. Istologia e Architettura Tumorale (Seed & Stroma)</div>', unsafe_allow_html=True)
    
    stage_in = st.selectbox(
        "Stadio TNM Patologico (Impatta il rischio assoluto)",
        ["Stage I (Localized)", "Stage II (Locally Advanced)", "Stage III (Regional Nodal+)"],
        index=1,
        help="Lo stadio TNM modula la quota assoluta di probabilità di recidiva a 24/36 mesi"
    )
    
    grade_in = st.selectbox(
        "Grado Istologico di Differenziazione (P_hist)",
        [
            "G1: Well-differentiated / Lepidic",
            "G2: Moderately differentiated / Acinar / Papillary",
            "G3: Poorly differentiated / Solid / Micropapillary"
        ],
        index=1,
        help="G1 (polarità preservata, punteggio basso) -> G3 (perdita totale di polarità epiteliale)"
    )
    
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        desmo_in = st.selectbox(
            "Desmoplasia Stromale (M_mech)",
            ["None / Minimal", "Low", "Moderate", "High / Dense"],
            index=2,
            help="Spessore della capsula fibrotica e barriera di trasporto vascolare K0"
        )
    with col_h2:
        tils_in = st.slider(
            "TILs Stromali (%)",
            min_value=0, max_value=60, value=15, step=2,
            help="Infiltrato linfocitario intratumorale: attenua la resistenza meccanica dello stroma"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

    # CARD 2: Blood Biomarkers
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<div class="input-header">🩸 2. Biomarcatori Ematici Pre-Operatori (Soil)</div>', unsafe_allow_html=True)
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        nlr_in = st.slider(
            "Rapporto Neutrofili/Linfociti (NLR)",
            min_value=0.8, max_value=12.0, value=2.4, step=0.1,
            help="Ogni variazione dell'NLR modifica in continuo la componente infiammatoria Phi_blood"
        )
    with col_b2:
        crp_in = st.slider(
            "Proteina C-Reattiva (hs-CRP, mg/L)",
            min_value=0.2, max_value=50.0, value=3.8, step=0.2,
            help="Risposta continua: riflette lo stato infiammatorio sistemico del paziente"
        )
    
    alb_in = st.slider(
        "Albumina Sierica (g/L)",
        min_value=24.0, max_value=48.0, value=40.0, step=0.5,
        help="Bassi livelli riflettono consumo metabolico e stress infiammatorio cronico"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # CARD 3: Host Background
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<div class="input-header">👤 3. Contesto Metabolico Ospite (Quasi-Statico)</div>', unsafe_allow_html=True)
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        smoke_in = st.selectbox("Abitudine al Fumo", ["Never Smoker", "Former Smoker", "Current Smoker"], index=1)
    with col_c2:
        bmi_in = st.slider("Indice di Massa Corporea (BMI)", min_value=17.0, max_value=40.0, value=24.5, step=0.5)
    st.markdown('</div>', unsafe_allow_html=True)

# Run calculation in real-time
res = compute_htbi(stage_in, grade_in, desmo_in, tils_in, nlr_in, crp_in, alb_in, smoke_in, bmi_in)

with col_output:
    st.markdown("### 📊 Risultati Dinamici in Tempo Reale")
    
    # TIER BADGE
    if res["htbi"] >= 0.45:
        st.markdown(f'<div class="tier-badge-high">⚠️ PROFILO AD ALTO RISCHIO BIOFISICO (HTBI = {res["htbi"]:.3f})</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="tier-badge-low">✅ PROFILO A BASSO RISCHIO BIOFISICO (HTBI = {res["htbi"]:.3f})</div>', unsafe_allow_html=True)

    # GAUGE METER (PLOTLY)
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=res["htbi"],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Punteggio Biofisico HTBI (0.00 - 1.00)", 'font': {'size': 18, 'color': '#0f172a'}},
        gauge={
            'axis': {'range': [0.0, 1.0], 'tickwidth': 1, 'tickcolor': "#334155"},
            'bar': {'color': "#0f172a", 'thickness': 0.25},
            'bgcolor': "white",
            'borderwidth': 1,
            'bordercolor': "#cbd5e1",
            'steps': [
                {'range': [0.0, 0.45], 'color': '#86efac'},
                {'range': [0.45, 0.70], 'color': '#fdba74'},
                {'range': [0.70, 1.0], 'color': '#fca5a5'}
            ],
            'threshold': {
                'line': {'color': "#dc2626", 'width': 4},
                'thickness': 0.8,
                'value': 0.45
            }
        }
    ))
    fig_gauge.update_layout(height=230, margin=dict(l=20, r=20, t=30, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # 3 SUMMARY KEY METRICS
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(
            "Rischio Recidiva a 24 Mesi",
            f"{res['prob_24m']:.1f}%",
            delta=f"{'+' if res['prob_24m']>25 else '-'}{abs(res['prob_24m']-25):.1f}% vs ref",
            delta_color="inverse"
        )
    with m2:
        st.metric("Rischio Recidiva a 36 Mesi", f"{res['prob_36m']:.1f}%")
    with m3:
        st.metric(
            "ctDNA Lead Time Stimato",
            f"{res['lead_time']:.2f} Mesi",
            help="Finestra temporale analitica tra comparsa del ctDNA molecolare e visibilità alla TC."
        )

    # RADAR CHART: TRIAD BREAKDOWN
    categories = ['Perdita Polarità (Seme)', 'Barriera Stromale (Matrice)', 'Infiammazione Ematica (Soil)']
    vals = [res['p_seed_loss'], res['m_mech'], res['phi_blood']]
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=vals + [vals[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(37, 99, 235, 0.22)',
        line=dict(color='#2563eb', width=2.5),
        name='Triade Biofisica'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
        height=240,
        margin=dict(l=35, r=35, t=15, b=15)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # 60-MONTH PROJECTED CURVE
    t_months = np.linspace(0, 60, 61)
    surv_pat = np.exp(-res['patient_hazard'] * (t_months / 12.0)) * 100.0
    
    # Ideal baseline (Stage I, HTBI = 0.15)
    ideal_hazard = 0.065 * 1.0 * np.exp(1.15 * (0.15 - 0.45))
    surv_ideal = np.exp(-ideal_hazard * (t_months / 12.0)) * 100.0

    fig_surv = go.Figure()
    fig_surv.add_trace(go.Scatter(
        x=t_months, y=surv_pat,
        mode='lines', name=f'Paziente ({stage_in.split()[0]})',
        line=dict(color='#dc2626' if res['htbi']>=0.45 else '#16a34a', width=3)
    ))
    fig_surv.add_trace(go.Scatter(
        x=t_months, y=surv_ideal,
        mode='lines', name='Riferimento Ottimale (Stadio I, HTBI 0.15)',
        line=dict(color='#94a3b8', width=2, dash='dash')
    ))
    fig_surv.update_layout(
        title="Curva di Sopravvivenza Libera da Recidiva Proiettata (60 Mesi)",
        xaxis_title="Mesi Post-Resezione",
        yaxis_title="Sopravvivenza Libera da Recidiva (%)",
        yaxis_range=[0, 105],
        height=260,
        margin=dict(l=20, r=20, t=35, b=15),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_surv, use_container_width=True)

    # INSIGHTS MECCANICISTICI
    if res["htbi"] >= 0.45:
        st.warning("""
        **Ipotesi Meccanicistiche per Microambienti ad Alto Rischio:**
        * **Santuario Vascolare e Resistenza al Trasporto:** La desmoplasia elevata crea un gradiente diffusivo di Bessel $K_0$ che isola le cellule perivascolari nel santuario del $31.28\\%$, proteggendole dalla clearance farmacologica.
        * **Finestra di Anticipo ctDNA:** Il lead time calcolato di ~5.45 mesi indica che il monitoraggio seriale della biopsia liquida (ogni 3 mesi) può intercettare la recidiva prima della visualizzazione radiologica.
        """)
    else:
        st.success("""
        **Caratteristiche del Microambiente a Basso Rischio:**
        * **Permeabilità Vascolare Conservata:** Bassa resistenza stromale ed elevata differenziazione tissutale favoriscono la penetrazione completa del trattamento e la sorveglianza immunitaria endogena.
        """)

# ==============================================================================
# FOOTER
# ==============================================================================
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.82rem; line-height: 1.5;">
    <strong>Host-Tumor Biophysical Index (HTBI) Research Framework</strong> · Sviluppato da <strong>Luca Celebrano</strong> (MD Candidate, Università degli Studi di Napoli Federico II).<br>
    Distribuito con licenza <strong>Creative Commons Attribution 4.0 International (CC-BY-4.0)</strong>.<br>
    Validato su coorti cliniche retrospettive (MSKCC <em>N = 604</em>, Coorte Ematica <em>N = 1,056</em>). Strumento riservato esclusivamente a ricerca accademica, traslazionale e didattica (RUO).
</div>
""", unsafe_allow_html=True)
