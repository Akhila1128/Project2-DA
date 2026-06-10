import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from utils.theme import PASTEL, plotly_layout


def render():
    df = st.session_state.get("df")

    if df is None:
        st.warning("⚠️ Please upload data first.")
        return

    st.markdown('<div class="section-header">⚙️ Data Preprocessing Dashboard</div>', unsafe_allow_html=True)

    col_map = st.session_state.get("col_map", {})

    # =========================
    # 📌 DATA OVERVIEW
    # =========================
    st.markdown("## 📊 Dataset Overview")

    c1, c2 = st.columns(2)
    c1.metric("Rows", df.shape[0])
    c2.metric("Columns", df.shape[1])

    st.dataframe(df.head(20))

    # =========================
    # 🔴 MISSING VALUES
    # =========================
    st.markdown("## 🔴 Missing Value Analysis")

    missing = df.isnull().mean() * 100
    missing = missing[missing > 0].reset_index()
    missing.columns = ["Column", "Missing %"]

    if len(missing) > 0:
        fig = px.bar(
            missing,
            x="Column",
            y="Missing %",
            color="Missing %",
            color_continuous_scale="Reds"
        )
        fig.update_layout(**plotly_layout("Missing Values"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No missing values found!")

    # =========================
    # 🔁 DUPLICATES
    # =========================
    st.markdown("## 🔁 Duplicate Rows")

    dup = df.duplicated().sum()

    fig = px.pie(
        names=["Unique Rows", "Duplicate Rows"],
        values=[len(df) - dup, dup],
        title="Duplicate Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

    if dup > 0 and st.button("Remove Duplicates"):
        df = df.drop_duplicates()
        st.session_state["df"] = df
        st.success(f"✅ Removed {dup} duplicates")

    # =========================
    # 📊 COLUMN TYPES
    # =========================
    st.markdown("## 📊 Column Type Distribution")

    dtype_counts = df.dtypes.astype(str).value_counts().reset_index()
    dtype_counts.columns = ["Type", "Count"]

    fig = px.bar(dtype_counts, x="Type", y="Count", color="Type")
    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 📈 NUMERIC DISTRIBUTION
    # =========================
    st.markdown("## 📈 Numeric Analysis")

    num_cols = df.select_dtypes(include=np.number).columns.tolist()

    if len(num_cols) > 0:
        col = st.selectbox("Select numeric column", num_cols)

        fig = px.histogram(df, x=col, nbins=30, title=f"Distribution of {col}")
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.box(df, y=col, title=f"Box Plot of {col}")
        st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # 🔥 CORRELATION HEATMAP
    # =========================
    st.markdown("## 🔥 Correlation Heatmap")

    if len(num_cols) > 1:
        corr = df[num_cols].corr()

        fig = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale="RdBu_r"
        )
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 📊 OUTLIER DETECTION
    # =========================
    st.markdown("## 📊 Outlier Detection")

    if len(num_cols) > 0:
        sel = st.selectbox("Select column for outliers", num_cols)

        Q1 = df[sel].quantile(0.25)
        Q3 = df[sel].quantile(0.75)
        IQR = Q3 - Q1

        outliers = df[(df[sel] < Q1 - 1.5 * IQR) | (df[sel] > Q3 + 1.5 * IQR)]

        c1, c2 = st.columns(2)
        c1.metric("Outliers", len(outliers))
        c2.metric("Non-Outliers", len(df) - len(outliers))

        fig = go.Figure()
        fig.add_trace(go.Box(y=df[sel], name=sel))
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 🛠 FEATURE ENGINEERING
    # =========================
    st.markdown("## 🛠 Feature Engineering")

    if "date" in col_map:
        date_col = col_map["date"]

        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

            if st.button("Extract Date Features"):
                df["year"] = df[date_col].dt.year
                df["month"] = df[date_col].dt.month
                df["day"] = df[date_col].dt.day
                df["weekday"] = df[date_col].dt.dayofweek

                st.session_state["df"] = df
                st.success("✅ Date features added")

    # =========================
    # 💰 SALES FEATURE (SAFE FIX)
    # =========================
    if "sales" in col_map and "quantity" in col_map:
        if st.button("Create Avg Order Value"):

            s = col_map["sales"]
            q = col_map["quantity"]

            df[s] = pd.to_numeric(df[s], errors="coerce").fillna(0)
            df[q] = pd.to_numeric(df[q], errors="coerce").replace(0, 1).fillna(1)

            df["avg_order_value"] = (df[s] / df[q]).round(2)

            st.session_state["df"] = df
            st.success("✅ avg_order_value created")

    # =========================
    # 🚀 EXTRA INSIGHT GRAPHS
    # =========================
    st.markdown("## 🚀 Extra Insights")

    # Skewness
    if len(num_cols) > 0:
        skew_data = df[num_cols].skew().reset_index()
        skew_data.columns = ["Column", "Skewness"]

        fig = px.bar(
            skew_data,
            x="Column",
            y="Skewness",
            color="Skewness",
            title="Skewness of Numeric Columns"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Data completeness
    missing_val = df.isnull().sum().sum()
    total_val = df.size - missing_val

    fig = px.pie(
        names=["Available Data", "Missing Data"],
        values=[total_val, missing_val],
        title="Data Completeness"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Top categorical values
    cat_cols = df.select_dtypes(include="object").columns.tolist()

    if len(cat_cols) > 0:
        col = cat_cols[0]

        top_vals = df[col].value_counts().head(10).reset_index()
        top_vals.columns = [col, "count"]

        fig = px.bar(top_vals, x=col, y="count", title=f"Top Values in {col}")
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # ✅ FINAL DATA
    # =========================
    st.markdown("## ✅ Final Cleaned Data")

    st.dataframe(df.head(50))

    st.info(f"Final Shape: {df.shape}")


# =========================
# 🧹 MISSING VALUE HANDLER
# =========================
def _handle_missing(df, strategy):
    num_cols = df.select_dtypes(include=np.number).columns

    if strategy == "Drop rows with nulls":
        df = df.dropna()

    elif strategy == "Fill numeric with median":
        df[num_cols] = df[num_cols].fillna(df[num_cols].median())

    elif strategy == "Fill numeric with mean":
        df[num_cols] = df[num_cols].fillna(df[num_cols].mean())

    elif strategy == "Fill with 0":
        df[num_cols] = df[num_cols].fillna(0)

    elif strategy == "Forward Fill":
        df = df.ffill()

    return df