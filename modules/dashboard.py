import streamlit as st
import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go

from utils.theme import PASTEL, CHART_COLORS, plotly_layout
from utils.helpers import format_currency


# =====================================================
# MAIN DASHBOARD
# =====================================================
def render():

    df = st.session_state.get("df")

    if df is None:
        st.warning("⚠️ Please upload data first.")
        return

    col_map = st.session_state.get("col_map", {})

    sales_col = col_map.get("sales")
    date_col  = col_map.get("date")
    prod_col  = col_map.get("product")
    reg_col   = col_map.get("region")
    cust_col  = col_map.get("customer")
    qty_col   = col_map.get("quantity")

    # =====================================================
    # STYLES + ANIMATIONS
    # =====================================================

    st.markdown("""
    <style>

    .dashboard-header{
        padding:2rem;
        border-radius:24px;
        background:
            linear-gradient(
                135deg,
                rgba(139,92,246,0.18),
                rgba(6,182,212,0.12)
            );
        border:1px solid rgba(255,255,255,0.08);
        backdrop-filter: blur(14px);
        animation: fadeUp 1s ease;
        margin-bottom:20px;
    }

    @keyframes fadeUp {

        from{
            opacity:0;
            transform:translateY(20px);
        }

        to{
            opacity:1;
            transform:translateY(0px);
        }
    }

    div[data-testid="metric-container"]{

        background:
            rgba(17,24,39,0.75);

        border:
            1px solid rgba(255,255,255,0.06);

        padding:18px;

        border-radius:18px;

        transition:0.3s;

        animation:fadeUp 1s ease;
    }

    div[data-testid="metric-container"]:hover{

        transform:
            translateY(-4px);

        box-shadow:
            0 0 18px rgba(139,92,246,0.35);
    }

    .stTabs [data-baseweb="tab"]{

        background:
            rgba(17,24,39,0.7);

        border-radius:14px;

        padding:10px 18px;

        margin-right:8px;

        transition:0.3s;
    }

    .stTabs [data-baseweb="tab"]:hover{

        transform:
            translateY(-2px);

        background:
            rgba(139,92,246,0.25);
    }

    .js-plotly-plot{

        animation:
            fadeUp 0.8s ease;
    }

    </style>
    """, unsafe_allow_html=True)

    # =====================================================
    # HEADER
    # =====================================================

    st.markdown(f"""
    <div class="dashboard-header">

    <h1 style="
        color:white;
        font-size:2.6rem;
        font-weight:800;
        margin-bottom:8px;
    ">
    📊 Sales Intelligence Dashboard
    </h1>

    <p style="
        color:#CBD5E1;
        font-size:1.05rem;
    ">
    Interactive AI-powered business intelligence analytics platform.
    </p>

    </div>
    """, unsafe_allow_html=True)

    # =====================================================
    # SAFE DATA PREPARATION
    # =====================================================

    df = df.copy()

    if date_col:
        df[date_col] = pd.to_datetime(
            df[date_col],
            errors="coerce"
        )

        df = df.dropna(subset=[date_col])

    if sales_col:
        df = df.dropna(subset=[sales_col])

    if df.empty:
        st.warning("No valid data available.")
        return

    # =====================================================
    # KPI CARDS
    # =====================================================

    if sales_col:

        total_revenue = df[sales_col].sum()
        avg_sales = df[sales_col].mean()
        max_sales = df[sales_col].max()
        total_txn = len(df)

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "💰 Total Revenue",
            format_currency(total_revenue)
        )

        c2.metric(
            "📊 Avg Sale",
            format_currency(avg_sales)
        )

        c3.metric(
            "🧾 Transactions",
            f"{total_txn:,}"
        )

        if qty_col:

            c4.metric(
                "📦 Units Sold",
                f"{df[qty_col].sum():,}"
            )

        else:

            c4.metric(
                "👥 Customers",
                f"{df[cust_col].nunique() if cust_col else 0}"
            )

    st.divider()

    # =====================================================
    # FILTERS
    # =====================================================

    with st.expander(
        "🔍 Dashboard Filters",
        expanded=True
    ):

        c1, c2, c3 = st.columns(3)

        # DATE FILTER
        if date_col:

            min_d = df[date_col].min().date()
            max_d = df[date_col].max().date()

            date_range = c1.date_input(
                "Date Range",
                [min_d, max_d]
            )

        else:
            date_range = None

        # PRODUCT FILTER
        if prod_col:

            products = (
                ["All"] +
                list(df[prod_col].dropna().unique())
            )

            sel_prod = c2.multiselect(
                "Products",
                products,
                default=["All"]
            )

        else:
            sel_prod = ["All"]

        # REGION FILTER
        if reg_col:

            regions = (
                ["All"] +
                list(df[reg_col].dropna().unique())
            )

            sel_reg = c3.multiselect(
                "Regions",
                regions,
                default=["All"]
            )

        else:
            sel_reg = ["All"]

    # =====================================================
    # APPLY FILTERS
    # =====================================================

    fdf = df.copy()

    if date_range and date_col:

        if len(date_range) == 2:

            fdf = fdf[
                (fdf[date_col].dt.date >= date_range[0]) &
                (fdf[date_col].dt.date <= date_range[1])
            ]

    if prod_col and "All" not in sel_prod:

        fdf = fdf[
            fdf[prod_col].isin(sel_prod)
        ]

    if reg_col and "All" not in sel_reg:

        fdf = fdf[
            fdf[reg_col].isin(sel_reg)
        ]

    if fdf.empty:

        st.warning("No data after filters.")
        return

    st.success(
        f"✅ Showing {len(fdf):,} filtered records"
    )

    st.divider()

    # =====================================================
    # TABS
    # =====================================================

    tabs = st.tabs([
        "📈 Trend",
        "🛍 Products",
        "👤 Customers",
        "🌍 Regions",
        "📊 Summary"
    ])

    # =====================================================
    # TREND TAB
    # =====================================================

    with tabs[0]:

        if date_col and sales_col:

            ts = (
                fdf.groupby(date_col)[sales_col]
                .sum()
                .reset_index()
            )

            fig = px.area(
                ts,
                x=date_col,
                y=sales_col,
                line_shape="spline",
                color_discrete_sequence=[
                    PASTEL["purple"]
                ]
            )

            fig.update_traces(
                mode="lines+markers"
            )

            fig.update_layout(
                **plotly_layout(
                    "Revenue Trend"
                ),
                transition_duration=1200
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            growth = (
                ts[sales_col]
                .pct_change()
                .fillna(0)
                .mean() * 100
            )

            st.metric(
                "📈 Avg Growth",
                f"{growth:.2f}%"
            )

    # =====================================================
    # PRODUCTS TAB
    # =====================================================

    with tabs[1]:

        if prod_col and sales_col:

            top_products = (
                fdf.groupby(prod_col)[sales_col]
                .sum()
                .nlargest(10)
                .reset_index()
            )

            fig = px.bar(
                top_products,
                x=sales_col,
                y=prod_col,
                orientation="h",
                color=sales_col,
                color_continuous_scale=[
                    "#A78BFA",
                    "#7DD3FC",
                    "#86EFAC"
                ]
            )

            fig.update_layout(
                **plotly_layout(
                    "Top Products"
                ),
                transition_duration=1200
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # =====================================================
    # CUSTOMERS TAB
    # =====================================================

    with tabs[2]:

        if cust_col and sales_col:

            top_customers = (
                fdf.groupby(cust_col)[sales_col]
                .sum()
                .nlargest(10)
                .reset_index()
            )

            st.dataframe(
                top_customers,
                use_container_width=True
            )

    # =====================================================
    # REGIONS TAB
    # =====================================================

    with tabs[3]:

        if reg_col and sales_col:

            region_df = (
                fdf.groupby(reg_col)[sales_col]
                .sum()
                .reset_index()
            )

            fig = px.treemap(
                region_df,
                path=[reg_col],
                values=sales_col,
                color=sales_col,
                color_continuous_scale="viridis"
            )

            fig.update_layout(
                **plotly_layout(
                    "Regional Revenue"
                ),
                transition_duration=1200
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # =====================================================
    # SUMMARY TAB
    # =====================================================

    with tabs[4]:

        summary = pd.DataFrame({

            "Metric": [

                "Total Revenue",

                "Average Sales",

                "Maximum Sale",

                "Minimum Sale",

                "Transactions"
            ],

            "Value": [

                round(fdf[sales_col].sum(), 2),

                round(fdf[sales_col].mean(), 2),

                round(fdf[sales_col].max(), 2),

                round(fdf[sales_col].min(), 2),

                len(fdf)
            ]
        })

        st.dataframe(
            summary,
            use_container_width=True
        )

        st.download_button(

            "⬇ Download Report",

            summary.to_csv(index=False),

            "dashboard_report.csv",

            "text/csv"
        )