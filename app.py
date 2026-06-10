import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Sales Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- THEME ----------------
from utils.theme import inject_css
inject_css()

# ---------------- MODULES ----------------
import modules.data_upload      as data_upload
import modules.preprocessing    as preprocessing
import modules.eda              as eda
import modules.forecasting      as forecasting
import modules.model_training   as model_training
import modules.dashboard        as dashboard
import modules.report_generator as report_generator

# ---------------- SAFE PAGE MAP ----------------
pages = {
    "📂 Data Upload": data_upload,
    "⚙️ Preprocessing": preprocessing,
    "📊 EDA Analysis": eda,
    "📈 Sales Forecasting": forecasting,
    "🤖 Model Training": model_training,
    "💡 Dashboard": dashboard,
    "📑 Reports": report_generator,
}

# ---------------- TOP NAV BAR ----------------
st.markdown("""
<style>
.topbar {
    background: linear-gradient(90deg, #F9A8D4, #FBCFE8);
    padding: 14px 18px;
    border-radius: 14px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.brand {
    font-size: 20px;
    font-weight: 700;
    color: #1F2937;
}

.sub {
    font-size: 12px;
    color: #6B7280;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="topbar">
    <div>
        <div class="brand">📊 Sales Intelligence</div>
        <div class="sub">BI + ML Dashboard</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- TOP NAVIGATION ----------------
selected = st.radio(
    "Navigation",
    list(pages.keys()),
    horizontal=True,
    label_visibility="collapsed"
)

# ---------------- DATA STATUS CARD ----------------
if st.session_state.get("df") is not None:
    df = st.session_state["df"]
    st.success(f"Dataset Loaded ✔ Rows: {len(df):,} | Columns: {df.shape[1]}")
else:
    st.warning("No dataset loaded yet")

st.markdown("---")

# ---------------- PAGE RENDER ----------------
pages[selected].render()