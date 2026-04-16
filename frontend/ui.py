import streamlit as st
import httpx

API_URL = "http://localhost:8000"

NEIGHBORHOOD_MAP = {
    "North Ridge Heights": "NridgHt",
    "College Creek": "CollgCr",
    "Somerset": "Somerst",
    "Gilbert": "Gilbert",
    "Northwest Ames": "NWAmes",
    "North Ames": "NAmes",
    "Sawyer": "Sawyer",
    "Sawyer West": "SawyerW",
    "Old Town": "OldTown",
    "Edwards": "Edwards",
    "Brookside": "BrkSide",
    "Crawford": "Crawfor",
    "Mitchell": "Mitchel",
    "North Ridge": "NoRidge",
    "Timberland": "Timber",
    "Stone Brook": "StoneBr",
    "Clear Creek": "ClearCr",
    "Bloomington Heights": "Blmngtn",
    "Meadow Village": "MeadowV",
    "Briardale": "BrDale",
    "Iowa DOT and Rail Road": "IDOTRR",
    "South & West of ISU": "SWISU",
    "Northpark Villa": "NPkVill",
    "Greens": "Greens",
}

NEIGHBORHOOD_REVERSE = {v: k for k, v in NEIGHBORHOOD_MAP.items()}

FIELD_LABELS = {
    "overall_qual":   "Overall Quality",
    "gr_liv_area":    "Living Area (sqft)",
    "garage_cars":    "Garage Cars",
    "total_bsmt_sf":  "Total Basement SF",
    "first_flr_sf":   "1st Floor SF",
    "year_built":     "Year Built",
    "year_remod_add": "Year Remodeled",
    "full_bath":      "Full Bathrooms",
    "neighborhood":   "Neighborhood",
    "kitchen_qual":   "Kitchen Quality",
    "bsmt_qual":      "Basement Quality",
}

QUAL_OPTIONS = ["Po", "Fa", "TA", "Gd", "Ex"]
QUAL_LABELS  = {
    "Po": "Poor",
    "Fa": "Fair",
    "TA": "Average",
    "Gd": "Good",
    "Ex": "Excellent"
}

st.set_page_config(page_title="AI Real Estate Agent", page_icon="🏠", layout="wide")

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Base & background ── */
  .stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    min-height: 100vh;
  }

  /* Hide default Streamlit chrome decorations */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1100px;
  }

  /* ── Hero header ── */
  .hero {
    background: linear-gradient(135deg, rgba(99,102,241,0.25) 0%, rgba(168,85,247,0.15) 100%);
    border: 1px solid rgba(99,102,241,0.35);
    border-radius: 20px;
    padding: 2.5rem 2.5rem 2rem;
    margin-bottom: 1.8rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(99,102,241,0.2), 0 0 0 1px rgba(255,255,255,0.05);
  }
  .hero h1 {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.5px;
  }
  .hero p {
    color: rgba(200,200,220,0.75);
    font-size: 1.05rem;
    margin: 0;
  }

  /* ── Glass card ── */
  .glass-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.4rem;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.08);
  }

  .section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 1.1rem;
    display: flex;
    align-items: center;
    gap: 0.45rem;
    letter-spacing: 0.2px;
  }

  /* ── Confidence pill ── */
  .confidence-row {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-bottom: 1.2rem;
    align-items: center;
  }
  .pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.28rem 0.85rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.3px;
  }
  .pill-confidence-high   { background: rgba(52,211,153,0.18); border: 1px solid rgba(52,211,153,0.45); color: #6ee7b7; }
  .pill-confidence-medium { background: rgba(251,191,36,0.18);  border: 1px solid rgba(251,191,36,0.45);  color: #fde68a; }
  .pill-confidence-low    { background: rgba(239,68,68,0.18);   border: 1px solid rgba(239,68,68,0.45);   color: #fca5a5; }
  .pill-missing           { background: rgba(239,68,68,0.14);   border: 1px solid rgba(239,68,68,0.35);   color: #fca5a5; }
  .pill-complete          { background: rgba(52,211,153,0.14);  border: 1px solid rgba(52,211,153,0.35);  color: #6ee7b7; }

  /* ── Feature grid ── */
  .feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.85rem;
  }
  .feature-chip {
    border-radius: 12px;
    padding: 0.9rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }
  .feature-chip:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.35);
  }
  .feature-chip.found {
    background: linear-gradient(135deg, rgba(16,185,129,0.18) 0%, rgba(6,182,212,0.12) 100%);
    border: 1px solid rgba(16,185,129,0.4);
    box-shadow: 0 2px 10px rgba(16,185,129,0.12);
  }
  .feature-chip.missing {
    background: linear-gradient(135deg, rgba(239,68,68,0.15) 0%, rgba(217,70,239,0.1) 100%);
    border: 1px solid rgba(239,68,68,0.35);
    box-shadow: 0 2px 10px rgba(239,68,68,0.1);
  }
  .chip-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: rgba(180,180,200,0.7);
  }
  .chip-value {
    font-size: 1.05rem;
    font-weight: 700;
    color: #f1f5f9;
  }
  .chip-value.found  { color: #6ee7b7; }
  .chip-value.missing { color: #fca5a5; }
  .chip-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 4px;
  }
  .chip-dot.found   { background: #34d399; box-shadow: 0 0 6px #34d399; }
  .chip-dot.missing { background: #f87171; box-shadow: 0 0 6px #f87171; }

  /* ── Missing fields form ── */
  .missing-header {
    background: linear-gradient(90deg, rgba(239,68,68,0.15), rgba(217,70,239,0.1));
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 10px;
    padding: 0.7rem 1rem;
    margin-bottom: 1rem;
    color: #fca5a5;
    font-size: 0.88rem;
    font-weight: 500;
  }

  /* Streamlit widget overrides */
  div[data-testid="stTextArea"] textarea,
  div[data-testid="stNumberInput"] input,
  div[data-testid="stSelectbox"] > div {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
  }
  div[data-testid="stTextArea"] textarea:focus,
  div[data-testid="stNumberInput"] input:focus {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
  }
  label, .stSlider label { color: rgba(200,200,220,0.85) !important; font-size: 0.87rem !important; }

  /* Primary button */
  div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.55rem 2rem !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.3px !important;
    box-shadow: 0 4px 16px rgba(99,102,241,0.4) !important;
    transition: all 0.2s ease !important;
    color: white !important;
  }
  div[data-testid="stButton"] > button[kind="primary"]:hover {
    box-shadow: 0 6px 22px rgba(99,102,241,0.6) !important;
    transform: translateY(-1px) !important;
  }

  /* Form submit button */
  div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #10b981, #059669) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.5rem 1.8rem !important;
    font-weight: 700 !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(16,185,129,0.35) !important;
    transition: all 0.2s ease !important;
  }
  div[data-testid="stFormSubmitButton"] > button:hover {
    box-shadow: 0 6px 20px rgba(16,185,129,0.5) !important;
    transform: translateY(-1px) !important;
  }

  /* ── Price display ── */
  .price-card {
    background: linear-gradient(135deg, rgba(99,102,241,0.3) 0%, rgba(168,85,247,0.25) 50%, rgba(6,182,212,0.2) 100%);
    border: 1px solid rgba(99,102,241,0.5);
    border-radius: 20px;
    padding: 2.2rem;
    text-align: center;
    margin-bottom: 1.4rem;
    box-shadow: 0 8px 32px rgba(99,102,241,0.25), 0 0 60px rgba(168,85,247,0.1);
    backdrop-filter: blur(12px);
  }
  .price-label {
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: rgba(200,200,220,0.65);
    margin-bottom: 0.5rem;
  }
  .price-value {
    font-size: 3.2rem;
    font-weight: 900;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    letter-spacing: -1px;
  }
  .price-sub {
    font-size: 0.82rem;
    color: rgba(200,200,220,0.55);
    margin-top: 0.4rem;
  }

  /* ── AI interpretation ── */
  .interpretation-text {
    color: rgba(220,220,240,0.88);
    font-size: 0.97rem;
    line-height: 1.75;
    background: rgba(255,255,255,0.03);
    border-left: 3px solid #8b5cf6;
    padding: 1rem 1.2rem;
    border-radius: 0 10px 10px 0;
  }

  /* Spinner & alerts */
  div[data-testid="stAlert"] {
    border-radius: 12px !important;
  }

  /* ── How it works ── */
  .how-it-works {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1.8rem;
  }
  .step-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 14px;
    padding: 1.3rem 1.2rem 1.1rem;
    text-align: center;
    backdrop-filter: blur(8px);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }
  .step-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(0,0,0,0.35);
  }
  .step-icon {
    font-size: 2rem;
    margin-bottom: 0.55rem;
    display: block;
  }
  .step-num {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: rgba(167,139,250,0.7);
    margin-bottom: 0.25rem;
  }
  .step-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 0.35rem;
  }
  .step-desc {
    font-size: 0.78rem;
    color: rgba(180,180,210,0.65);
    line-height: 1.55;
  }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = None

# ── Hero header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🏠 AI Real Estate Agent</h1>
  <p>Describe a property in plain English and get an instant ML-powered price prediction</p>
</div>
""", unsafe_allow_html=True)

# ── How It Works ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="how-it-works">
  <div class="step-card">
    <span class="step-icon">✍️</span>
    <div class="step-num">Step 1</div>
    <div class="step-title">Describe the Property</div>
    <div class="step-desc">Write a plain-English description — bedrooms, location, year built, garage, quality. No special format needed.</div>
  </div>
  <div class="step-card">
    <span class="step-icon">🤖</span>
    <div class="step-num">Step 2</div>
    <div class="step-title">AI Extracts Features</div>
    <div class="step-desc">Our LLM reads your text and pulls out the key property features that drive home value.</div>
  </div>
  <div class="step-card">
    <span class="step-icon">💰</span>
    <div class="step-num">Step 3</div>
    <div class="step-title">Get an Instant Estimate</div>
    <div class="step-desc">A trained ML regression model predicts the market price and an AI summary explains the result.</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
with st.container():
    user_query = st.text_area(
        "Describe the property:",
        placeholder="e.g. 3 bedroom house built in 1995 with excellent kitchen and 2 car garage in NridgHt",
        height=110,
        label_visibility="collapsed"
    )
    st.markdown("<div style='margin-top:-0.5rem'></div>", unsafe_allow_html=True)
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        analyze_clicked = st.button("🔍 Analyze Property", type="primary", use_container_width=True)

if analyze_clicked:
    if not user_query.strip():
        st.warning("Please describe a property first.")
    else:
        with st.spinner("Extracting features with AI..."):
            try:
                response = httpx.post(
                    f"{API_URL}/predict",
                    json={"query": user_query},
                    timeout=30
                )
                st.session_state.data = response.json()
            except Exception as e:
                st.error(f"Could not connect to server: {e}")

# ── Results ────────────────────────────────────────────────────────────────────
if st.session_state.data:
    data      = st.session_state.data
    features  = data["extracted_features"]
    missing   = features.get("missing_fields", [])
    confidence = features.get("confidence", "low")

    if data.get("error") and not data.get("predicted_price"):
        st.error(data["error"])
    else:
        # ── Extracted Features ─────────────────────────────────────────
        conf_class = f"pill-confidence-{confidence}"
        missing_count = len(missing)
        complete_count = 12 - missing_count

        confidence_html = f"""
        <div class="confidence-row">
          <span class="pill {conf_class}">● Confidence: {confidence.capitalize()}</span>
          <span class="pill pill-complete">✓ {complete_count} fields found</span>
          {"" if missing_count == 0 else f'<span class="pill pill-missing">✗ {missing_count} fields missing</span>'}
        </div>
        """

        # Build feature chip grid
        def chip(label, raw_value, display_value, in_missing):
            status = "missing" if in_missing else "found"
            dot    = f'<span class="chip-dot {status}"></span>'
            val    = display_value if display_value not in (None, "", "❓") else "Not found"
            return f"""
            <div class="feature-chip {status}">
              <span class="chip-label">{dot}{label}</span>
              <span class="chip-value {status}">{val}</span>
            </div>"""

        neighborhood_display = NEIGHBORHOOD_REVERSE.get(
            features.get("neighborhood"), features.get("neighborhood")
        ) or None
        garage_val = features.get("garage_cars")

        chips = [
            chip("Overall Quality",    features.get("overall_qual"),   features.get("overall_qual"),            "overall_qual"    in missing),
            chip("Living Area (sqft)", features.get("gr_liv_area"),    features.get("gr_liv_area"),             "gr_liv_area"     in missing),
            chip("Garage Cars",        garage_val,                      garage_val,                              "garage_cars"     in missing),
            chip("Total Basement SF",  features.get("total_bsmt_sf"),  features.get("total_bsmt_sf"),           "total_bsmt_sf"   in missing),
            chip("1st Floor SF",       features.get("first_flr_sf"),   features.get("first_flr_sf"),            "first_flr_sf"    in missing),
            chip("Year Built",         features.get("year_built"),      features.get("year_built"),              "year_built"      in missing),
            chip("Year Remodeled",     features.get("year_remod_add"), features.get("year_remod_add"),          "year_remod_add"  in missing),
            chip("Full Bathrooms",     features.get("full_bath"),       features.get("full_bath"),               "full_bath"       in missing),
            chip("Neighborhood",       features.get("neighborhood"),    neighborhood_display,                    "neighborhood"    in missing),
            chip("Kitchen Quality",    features.get("kitchen_qual"),
                 QUAL_LABELS.get(features.get("kitchen_qual"), features.get("kitchen_qual")),                   "kitchen_qual"    in missing),
            chip("Basement Quality",   features.get("bsmt_qual"),
                 QUAL_LABELS.get(features.get("bsmt_qual"), features.get("bsmt_qual")),                         "bsmt_qual"       in missing),
        ]

        st.markdown(f"""
        <div class="glass-card">
          <div class="section-title">📋 Extracted Features</div>
          {confidence_html}
          <div class="feature-grid">{''.join(chips)}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Fill Missing Fields ────────────────────────────────────────
        if missing:
            missing_labels = [FIELD_LABELS.get(f, f.replace("_", " ").title()) for f in missing]
            st.markdown(f"""
            <div class="glass-card">
              <div class="section-title">✏️ Fill Missing Fields</div>
              <div class="missing-header">
                ⚠️ The AI could not extract the following fields — please fill them in manually:<br>
                <strong>{', '.join(missing_labels)}</strong>
              </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("missing_fields_form"):
                filled = {}
                cols = st.columns(2)
                col_idx = 0
                for field in missing:
                    if field in ["missing_fields", "confidence"]:
                        continue
                    with cols[col_idx % 2]:
                        if field == "overall_qual":
                            filled[field] = st.slider("Overall Quality (1-10)", 1, 10, 6)
                        elif field == "neighborhood":
                            friendly = st.selectbox("Neighborhood", list(NEIGHBORHOOD_MAP.keys()))
                            filled[field] = NEIGHBORHOOD_MAP[friendly]
                        elif field == "year_built":
                            filled[field] = st.number_input("Year Built", 1800, 2025, 1972)
                        elif field == "year_remod_add":
                            filled[field] = st.number_input("Year Remodeled", 1800, 2025, 1992)
                        elif field == "gr_liv_area":
                            filled[field] = st.number_input("Living Area (sqft)", 100, 10000, 1440)
                        elif field == "total_bsmt_sf":
                            filled[field] = st.number_input("Total Basement SF", 0, 6000, 984)
                        elif field == "first_flr_sf":
                            filled[field] = st.number_input("1st Floor SF", 0, 6000, 1082)
                        elif field == "garage_cars":
                            filled[field] = st.number_input("Garage Cars", 0, 5, 2)
                        elif field == "full_bath":
                            filled[field] = st.number_input("Full Bathrooms", 0, 5, 2)
                        elif field == "kitchen_qual":
                            filled[field] = st.selectbox("Kitchen Quality", QUAL_OPTIONS,
                                                         format_func=lambda x: QUAL_LABELS[x])
                        elif field == "bsmt_qual":
                            filled[field] = st.selectbox("Basement Quality", QUAL_OPTIONS,
                                                         format_func=lambda x: QUAL_LABELS[x])
                    col_idx += 1

                submitted = st.form_submit_button("⚡ Predict with filled values", use_container_width=True)

            if submitted:
                with st.spinner("Running prediction model..."):
                    try:
                        response = httpx.post(
                            f"{API_URL}/predict/complete",
                            json={
                                "extracted_features": features,
                                "filled_features": filled
                            },
                            timeout=30
                        )
                        st.session_state.data = response.json()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        # ── Predicted Price ────────────────────────────────────────────
        if data.get("predicted_price"):
            price_fmt = f"${data['predicted_price']:,.0f}"
            st.markdown(f"""
            <div class="price-card">
              <div class="price-label">Estimated Market Value</div>
              <div class="price-value">{price_fmt}</div>
              <div class="price-sub">Based on Ames, Iowa housing data · ML regression model</div>
            </div>
            """, unsafe_allow_html=True)

        # ── AI Interpretation ──────────────────────────────────────────
        if data.get("interpretation"):
            st.markdown(f"""
            <div class="glass-card">
              <div class="section-title">🤖 AI Interpretation</div>
              <div class="interpretation-text">{data["interpretation"]}</div>
            </div>
            """, unsafe_allow_html=True)
