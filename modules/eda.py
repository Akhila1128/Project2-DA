import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def format_currency(value):
    try:
        return f"₹{value:,.2f}"
    except:
        return str(value)


def render():
    st.title("📊 Exploratory Data Analysis")

    df = st.session_state.get("df")

    if df is None:
        st.warning("Please upload data first.")
        return

    st.subheader("Dataset Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Rows", len(df))
    c2.metric("Columns", len(df.columns))
    c3.metric("Missing Values", int(df.isna().sum().sum()))
    c4.metric("Duplicates", int(df.duplicated().sum()))

    st.dataframe(df.head(20), use_container_width=True)

    st.divider()

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    date_cols = []
    for col in df.columns:
        try:
            pd.to_datetime(df[col])
            date_cols.append(col)
        except:
            pass

    sales_col = None

    if numeric_cols:
        sales_col = st.selectbox(
            "Select Sales Column",
            numeric_cols
        )

    date_col = None

    if date_cols:
        date_col = st.selectbox(
            "Select Date Column",
            date_cols
        )

    st.divider()

    tabs = st.tabs([
        "📈 Trend Analysis",
        "📦 Distribution",
        "🔥 Correlation",
        "📊 Statistics"
    ])

    # -------------------------------------------------
    # TREND ANALYSIS
    # -------------------------------------------------
    with tabs[0]:

        if sales_col and date_col:

            try:

                temp = df.copy()

                temp[date_col] = pd.to_datetime(
                    temp[date_col],
                    errors="coerce"
                )

                temp = temp.dropna(subset=[date_col])

                freq = st.selectbox(
                    "Aggregation",
                    ["Daily", "Weekly", "Monthly"]
                )

                freq_map = {
                    "Daily": "D",
                    "Weekly": "W",
                    "Monthly": "M"
                }

                ts = (
                    temp
                    .set_index(date_col)[sales_col]
                    .resample(freq_map[freq])
                    .sum()
                    .reset_index()
                )

                fig = go.Figure()

                fig.add_trace(
                    go.Scatter(
                        x=ts[date_col],
                        y=ts[sales_col],
                        mode="lines+markers",
                        name="Sales"
                    )
                )

                ts["Moving Average"] = (
                    ts[sales_col]
                    .rolling(4, min_periods=1)
                    .mean()
                )

                fig.add_trace(
                    go.Scatter(
                        x=ts[date_col],
                        y=ts["Moving Average"],
                        mode="lines",
                        name="Moving Average"
                    )
                )

                fig.update_layout(
                    title="Sales Trend",
                    height=500
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            except Exception as e:
                st.error(e)

    # -------------------------------------------------
    # DISTRIBUTION
    # -------------------------------------------------
    with tabs[1]:

        if numeric_cols:

            selected = st.selectbox(
                "Select Numeric Column",
                numeric_cols
            )

            c1, c2 = st.columns(2)

            with c1:

                fig = px.histogram(
                    df,
                    x=selected,
                    nbins=30
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            with c2:

                fig = px.box(
                    df,
                    y=selected
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            st.write("Skewness:", round(df[selected].skew(), 3))
            st.write("Kurtosis:", round(df[selected].kurtosis(), 3))

    # -------------------------------------------------
    # CORRELATION
    # -------------------------------------------------
    with tabs[2]:

        if len(numeric_cols) > 1:

            corr = df[numeric_cols].corr()

            fig = px.imshow(
                corr,
                text_auto=True,
                aspect="auto"
            )

            fig.update_layout(
                height=600,
                title="Correlation Matrix"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:
            st.info(
                "Need at least two numeric columns."
            )

    # -------------------------------------------------
    # STATISTICS
    # -------------------------------------------------
    with tabs[3]:

        st.subheader("Descriptive Statistics")

        st.dataframe(
            df.describe(include="all"),
            use_container_width=True
        )

        if sales_col:

            st.subheader("Sales Summary")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Total Sales",
                format_currency(df[sales_col].sum())
            )

            c2.metric(
                "Average Sales",
                format_currency(df[sales_col].mean())
            )

            c3.metric(
                "Maximum Sale",
                format_currency(df[sales_col].max())
            )

            c4.metric(
                "Minimum Sale",
                format_currency(df[sales_col].min())
            )

    st.divider()

    st.subheader("Missing Values")

    missing = (
        df.isnull()
        .sum()
        .reset_index()
    )

    missing.columns = [
        "Column",
        "Missing Count"
    ]

    st.dataframe(
        missing,
        use_container_width=True
    )