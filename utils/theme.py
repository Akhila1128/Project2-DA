# utils/theme.py

PASTEL = {
    "pink":   "#FF69B4",
    "light_pink": "#FFB6C1",
    "baby":   "#FFF0F5",
    "rose":   "#FF1493",
    "purple": "#8A2BE2",
    "blue":   "#1E90FF",
    "green":  "#32CD32",
    "yellow": "#FFD700",
    "orange": "#FF8C00",
    "red":    "#FF4C4C",
    "teal":   "#20B2AA",
}

# STRONG / THICK COLORS for charts (fixes dull visuals)
CHART_COLORS = [
    "#FF1493", "#FF69B4", "#8A2BE2", "#1E90FF",
    "#32CD32", "#FFD700", "#FF8C00", "#FF4C4C"
]

BG_DARK = "#FFF0F5"
BG_CARD = "#FFE4EC"
BG_CARD2 = "#FFD6E8"
TEXT_MAIN = "#2B2B2B"
TEXT_SUB = "#555555"


def inject_css():
    import streamlit as st

    st.markdown(f"""
    <style>

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        background-color: {BG_DARK};
        color: {TEXT_MAIN};
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: {BG_CARD} !important;
    }}

    /* Cards */
    .metric-card {{
        background: {BG_CARD2};
        border-radius: 16px;
        padding: 18px;
        border-left: 5px solid {PASTEL["pink"]};
    }}

    .metric-value {{
        font-size: 1.6rem;
        font-weight: 700;
        color: {PASTEL["rose"]};
    }}

    .metric-label {{
        font-size: 0.85rem;
        color: {TEXT_SUB};
    }}

    .section-header {{
        font-size: 1.4rem;
        font-weight: 700;
        color: {PASTEL["pink"]};
        border-left: 5px solid {PASTEL["rose"]};
        padding-left: 10px;
        margin: 20px 0;
    }}

    /* Buttons */
    .stButton > button {{
        background: linear-gradient(90deg, #FF69B4, #FF1493);
        color: white;
        border-radius: 10px;
        font-weight: 600;
    }}

    /* Tables */
    table {{
        border-radius: 10px;
    }}

    </style>
    """, unsafe_allow_html=True)


def plotly_layout(title="", height=420):
    return dict(
        title=title,
        paper_bgcolor="#FFF0F5",
        plot_bgcolor="#FFE4EC",
        font=dict(color=TEXT_MAIN),
        height=height,
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor="#FFB6C1"),
        yaxis=dict(gridcolor="#FFB6C1"),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )