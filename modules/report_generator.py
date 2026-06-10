import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
from utils.theme import PASTEL


# ---------------- MAIN UI ---------------- #
def render():

    df = st.session_state.get("df")

    if df is None:
        st.warning("⚠️ Please upload data first.")
        return

    col_map  = st.session_state.get("col_map", {})
    forecast = st.session_state.get("forecast_df")
    churn    = st.session_state.get("churn_df")
    models   = st.session_state.get("model_results")

    st.markdown('<div class="section-header">📑 Report Generation</div>', unsafe_allow_html=True)

    with st.expander("⚙️ Report Settings"):
        report_title = st.text_input("Report Title", "Sales Intelligence Report")

        include_eda      = st.checkbox("Include EDA Summary", True)
        include_forecast = st.checkbox("Include Forecast Data", True)
        include_models   = st.checkbox("Include Model Results", True)
        include_churn    = st.checkbox("Include Churn Analysis", True)

    c1, c2 = st.columns(2)

    # ---------------- EXCEL ---------------- #
    with c1:
        if st.button("📊 Generate Excel Report", use_container_width=True):

            xlsx_bytes = _generate_excel(
                df, col_map, forecast, churn, models,
                include_eda, include_forecast,
                include_models, include_churn
            )

            xlsx_bytes = _safe_bytes(xlsx_bytes)

            st.download_button(
                label="⬇️ Download Excel",
                data=xlsx_bytes,
                file_name=f"Sales_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    # ---------------- PDF ---------------- #
    with c2:
        if st.button("📄 Generate PDF Report", use_container_width=True):

            pdf_bytes = _generate_pdf(
                df, col_map, forecast, churn, models, report_title
            )

            pdf_bytes = _safe_bytes(pdf_bytes)

            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_bytes,
                file_name=f"Sales_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    # ---------------- PREVIEW ---------------- #
    st.markdown("#### 👁️ Report Preview")

    tabs = st.tabs(["📋 Raw Data", "📈 Forecast", "🤖 Model Results", "🔄 Churn"])

    with tabs[0]:
        st.dataframe(df.head(200), use_container_width=True)

    with tabs[1]:
        if forecast is not None:
            st.dataframe(forecast, use_container_width=True)
        else:
            st.info("Run forecasting first.")

    with tabs[2]:
        if models is not None:
            st.dataframe(models, use_container_width=True)
        else:
            st.info("Run model training first.")

    with tabs[3]:
        if churn is not None:
            st.dataframe(churn.head(100), use_container_width=True)
        else:
            st.info("Run churn prediction first.")


# ---------------- SAFE BYTE FIX ---------------- #
def _safe_bytes(data):
    """Fix Streamlit download crash"""
    if isinstance(data, bytearray):
        return bytes(data)
    if isinstance(data, str):
        return data.encode("latin-1")
    return data


# ---------------- EXCEL GENERATION ---------------- #
def _generate_excel(df, col_map, forecast, churn, models,
                    inc_eda, inc_fore, inc_mod, inc_churn):

    buf = io.BytesIO()

    with pd.ExcelWriter(buf, engine="openpyxl") as writer:

        df.to_excel(writer, sheet_name="Raw Data", index=False)

        sales_col = col_map.get("sales")

        if sales_col and inc_eda:
            df.describe(include="all").T.to_excel(writer, sheet_name="EDA Summary")

        if forecast is not None and inc_fore:
            forecast.to_excel(writer, sheet_name="Forecast", index=False)

        if models is not None and inc_mod:
            models.to_excel(writer, sheet_name="Models", index=False)

        if churn is not None and inc_churn:
            churn.to_excel(writer, sheet_name="Churn", index=False)

        if sales_col and sales_col in df.columns:

            kpi = pd.DataFrame({
                "Metric": [
                    "Total Records", "Total Revenue", "Average Sale",
                    "Max Sale", "Min Sale", "Std Dev"
                ],
                "Value": [
                    len(df),
                    df[sales_col].sum(),
                    df[sales_col].mean(),
                    df[sales_col].max(),
                    df[sales_col].min(),
                    df[sales_col].std()
                ]
            })

            kpi.to_excel(writer, sheet_name="KPI", index=False)

    buf.seek(0)
    return buf.read()


# ---------------- PDF GENERATION ---------------- #
def _generate_pdf(df, col_map, forecast, churn, models, title):

    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, title, ln=True, align="C")

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
    pdf.ln(5)

    def section(text):
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, text, ln=True)

    def row(label, value):
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(90, 8, str(label))
        pdf.cell(0, 8, str(value), ln=True)

    # Dataset info
    section("Dataset Overview")
    row("Rows", len(df))
    row("Columns", df.shape[1])
    row("Missing Values", int(df.isnull().sum().sum()))
    row("Duplicates", int(df.duplicated().sum()))

    sales_col = col_map.get("sales")

    if sales_col and sales_col in df.columns:

        df[sales_col] = pd.to_numeric(df[sales_col], errors="coerce").fillna(0)

        section("Sales KPIs")
        row("Total Revenue", df[sales_col].sum())
        row("Average Sale", df[sales_col].mean())
        row("Max Sale", df[sales_col].max())
        row("Min Sale", df[sales_col].min())

    # Forecast
    if forecast is not None:
        section("Forecast Preview")
        pdf.cell(0, 8, str(forecast.head(10)), ln=True)

    # Models
    if models is not None:
        section("Model Results")
        pdf.cell(0, 8, str(models.head(10)), ln=True)

    # Churn
    if churn is not None:
        section("Churn Summary")

        total = len(churn)
        churned = churn["Churned"].sum() if "Churned" in churn.columns else 0

        row("Total Customers", total)
        row("Churned", churned)
        row("Retained", total - churned)

    # FINAL SAFE EXPORT (NO BYTEARRAY CRASH)
    pdf_output = pdf.output(dest="S")

    return bytes(pdf_output)