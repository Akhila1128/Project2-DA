import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from sklearn.linear_model import LinearRegression


def render():

    st.title("📈 Sales Forecasting Dashboard")

    df = st.session_state.get("df")

    if df is None:
        st.warning("⚠️ Please upload a dataset first.")
        return

    # =====================================================
    # COLUMN SELECTION
    # =====================================================

    st.subheader("📌 Forecast Settings")

    date_candidates = []

    for col in df.columns:

        try:
            test = pd.to_datetime(
                df[col],
                errors="coerce"
            )

            if test.notna().sum() > len(df) * 0.5:
                date_candidates.append(col)

        except:
            pass

    if len(date_candidates) == 0:
        st.error("❌ No valid date column found.")
        return

    numeric_cols = (
        df.select_dtypes(include=np.number)
        .columns
        .tolist()
    )

    if len(numeric_cols) == 0:
        st.error("❌ No numeric columns found.")
        return

    c1, c2 = st.columns(2)

    date_col = c1.selectbox(
        "Select Date Column",
        date_candidates
    )

    metric_col = c2.selectbox(
        "Select Metric",
        numeric_cols
    )

    c3, c4 = st.columns(2)

    forecast_periods = c3.slider(
        "Forecast Periods",
        1,
        24,
        6
    )

    agg_level = c4.selectbox(
        "Aggregation Level",
        ["Daily", "Weekly", "Monthly"]
    )

    # =====================================================
    # DATA PREPARATION
    # =====================================================

    data = df[[date_col, metric_col]].copy()

    data[date_col] = pd.to_datetime(
        data[date_col],
        errors="coerce"
    )

    data[metric_col] = pd.to_numeric(
        data[metric_col],
        errors="coerce"
    )

    data = data.dropna()

    if len(data) == 0:
        st.error("❌ No usable data found.")
        return

    freq_map = {
        "Daily": "D",
        "Weekly": "W",
        "Monthly": "M"
    }

    ts = (
        data
        .set_index(date_col)[metric_col]
        .resample(freq_map[agg_level])
        .sum()
        .reset_index()
    )

    ts.columns = ["Date", "Value"]

    if len(ts) < 3:
        st.error(
            "❌ Not enough time periods for forecasting."
        )
        return

    # =====================================================
    # KPI CARDS
    # =====================================================

    st.subheader("📊 Dataset KPIs")

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Rows", len(df))
    k2.metric("Columns", len(df.columns))
    k3.metric("Periods", len(ts))
    k4.metric(
        "Total Value",
        f"{ts['Value'].sum():,.0f}"
    )

    # =====================================================
    # DATA TABS
    # =====================================================

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📄 Dataset",
            "📊 Statistics",
            "🔗 Correlation",
            "📈 Trend"
        ]
    )

    with tab1:

        st.dataframe(
            df.head(100),
            use_container_width=True
        )

    with tab2:

        st.dataframe(
            df.describe(
                include="all"
            ),
            use_container_width=True
        )

    with tab3:

        numeric_df = df.select_dtypes(
            include=np.number
        )

        if len(numeric_df.columns) > 1:

            corr = numeric_df.corr()

            fig_corr = px.imshow(
                corr,
                text_auto=True,
                title="Correlation Matrix"
            )

            st.plotly_chart(
                fig_corr,
                use_container_width=True
            )

        else:
            st.info(
                "Need at least 2 numeric columns."
            )

    with tab4:

        fig_hist = px.line(
            ts,
            x="Date",
            y="Value",
            markers=True,
            title="Historical Trend"
        )

        st.plotly_chart(
            fig_hist,
            use_container_width=True
        )

    # =====================================================
    # FORECAST MODEL
    # =====================================================

    ts["t"] = np.arange(len(ts))

    X = ts[["t"]]
    y = ts["Value"]

    model = LinearRegression()

    model.fit(X, y)

    future_index = np.arange(
        len(ts),
        len(ts) + forecast_periods
    )

    forecast_values = model.predict(
        future_index.reshape(-1, 1)
    )

    future_dates = pd.date_range(
        start=ts["Date"].max(),
        periods=forecast_periods + 1,
        freq=freq_map[agg_level]
    )[1:]

    forecast_df = pd.DataFrame({
        "Date": future_dates,
        "Forecast": np.round(
            forecast_values,
            2
        )
    })

    # =====================================================
    # FORECAST KPI
    # =====================================================

    st.subheader("📌 Forecast KPIs")

    f1, f2, f3, f4 = st.columns(4)

    f1.metric(
        "Historical Avg",
        f"{ts['Value'].mean():,.2f}"
    )

    f2.metric(
        "Forecast Avg",
        f"{forecast_df['Forecast'].mean():,.2f}"
    )

    f3.metric(
        "Maximum Forecast",
        f"{forecast_df['Forecast'].max():,.2f}"
    )

    f4.metric(
        "Minimum Forecast",
        f"{forecast_df['Forecast'].min():,.2f}"
    )

    # =====================================================
    # FORECAST GRAPH
    # =====================================================

    st.subheader("📉 Forecast Visualization")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=ts["Date"],
            y=ts["Value"],
            mode="lines+markers",
            name="Historical"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=forecast_df["Date"],
            y=forecast_df["Forecast"],
            mode="lines+markers",
            name="Forecast"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================================
    # FORECAST TABLE
    # =====================================================

    st.subheader("📋 Forecast Results")

    st.dataframe(
        forecast_df,
        use_container_width=True
    )

    # =====================================================
    # SUMMARY
    # =====================================================

    growth = (
        (
            forecast_df["Forecast"].mean()
            - ts["Value"].mean()
        )
        / ts["Value"].mean()
    ) * 100

    summary = pd.DataFrame({
        "Metric": [
            "Historical Average",
            "Forecast Average",
            "Growth %",
            "Max Forecast",
            "Min Forecast"
        ],
        "Value": [
            round(ts["Value"].mean(), 2),
            round(
                forecast_df["Forecast"].mean(),
                2
            ),
            round(growth, 2),
            round(
                forecast_df["Forecast"].max(),
                2
            ),
            round(
                forecast_df["Forecast"].min(),
                2
            )
        ]
    })

    st.subheader("📑 Forecast Summary")

    st.dataframe(
        summary,
        use_container_width=True
    )

    # =====================================================
    # INSIGHTS
    # =====================================================

    st.subheader("💡 Business Insights")

    if growth > 10:
        st.success(
            f"Strong growth expected ({growth:.2f}%)"
        )

    elif growth > 0:
        st.info(
            f"Moderate growth expected ({growth:.2f}%)"
        )

    else:
        st.warning(
            f"Decline expected ({growth:.2f}%)"
        )

    # =====================================================
    # DOWNLOAD
    # =====================================================

    csv = forecast_df.to_csv(
        index=False
    )

    st.download_button(
        "⬇ Download Forecast CSV",
        csv,
        "forecast_results.csv",
        "text/csv"
    )