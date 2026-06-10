import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

from utils.helpers import detect_columns, safe_parse_dates


def render():

    st.title("📂 Data Upload & Validation")

    # ==================================================
    # FILE UPLOADER
    # ==================================================

    uploaded = st.file_uploader(
        "Upload Dataset",
        type=["csv", "xlsx", "xls"]
    )

    df = None

    # ==================================================
    # SAMPLE DATASETS
    # ==================================================

    if uploaded is None:

        sample_dir = Path("sample_data")

        if sample_dir.exists():

            csv_files = list(sample_dir.glob("*.csv"))

            if len(csv_files) > 0:

                dataset_names = [
                    file.stem.replace("_", " ").title()
                    for file in csv_files
                ]

                selected = st.selectbox(
                    "Choose Sample Dataset",
                    dataset_names
                )

                if st.button("📊 Load Sample Dataset"):

                    file_path = csv_files[
                        dataset_names.index(selected)
                    ]

                    try:

                        if file_path.stat().st_size == 0:

                            st.error(
                                "Selected sample file is empty."
                            )
                            return

                        df = pd.read_csv(file_path)

                        if df.empty:

                            st.error(
                                "Sample dataset contains no rows."
                            )
                            return

                        process_dataset(df)

                    except pd.errors.EmptyDataError:

                        st.error(
                            "Sample dataset contains no data."
                        )

                    except Exception as e:

                        st.error(
                            f"Failed to load sample dataset"
                        )

                        st.exception(e)

            else:

                st.info(
                    "No sample datasets found."
                )

        return

    # ==================================================
    # READ UPLOADED FILE
    # ==================================================

    try:

        if uploaded.name.lower().endswith(".csv"):

            try:

                df = pd.read_csv(uploaded)

            except UnicodeDecodeError:

                uploaded.seek(0)

                df = pd.read_csv(
                    uploaded,
                    encoding="latin1"
                )

        else:

            df = pd.read_excel(uploaded)

    except pd.errors.EmptyDataError:

        st.error(
            "Uploaded file contains no data."
        )
        return

    except Exception as e:

        st.error(
            "Failed to read uploaded file"
        )
        st.exception(e)
        return

    if df is None or df.empty:

        st.error(
            "Uploaded file is empty."
        )
        return

    process_dataset(df)


# ==================================================
# MAIN PROCESSING
# ==================================================

def process_dataset(df):

    df = df.copy()

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace("\n", " ")
    )

    try:

        col_map = detect_columns(df)

    except Exception:

        col_map = {}

    if "date" in col_map:

        try:

            df = safe_parse_dates(
                df,
                col_map["date"]
            )

        except Exception:
            pass

    st.session_state["df"] = df
    st.session_state["col_map"] = col_map

    st.success(
        f"Dataset Loaded Successfully ({len(df):,} rows)"
    )

    show_validation(df, col_map)

    show_dataset(df)


# ==================================================
# VALIDATION
# ==================================================

def show_validation(df, col_map):

    st.subheader("🔍 Dataset Validation")

    rows = len(df)
    cols = len(df.columns)

    missing = int(
        df.isnull().sum().sum()
    )

    duplicates = int(
        df.duplicated().sum()
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Rows", f"{rows:,}")
    c2.metric("Columns", cols)
    c3.metric("Missing", missing)
    c4.metric("Duplicates", duplicates)

    st.markdown("---")

    st.subheader("🗺 Column Mapping")

    roles = [
        "date",
        "sales",
        "customer",
        "product",
        "quantity",
        "region"
    ]

    mapping_df = pd.DataFrame({
        "Role": roles,
        "Detected Column": [
            col_map.get(role, "Not Found")
            for role in roles
        ]
    })

    st.dataframe(
        mapping_df,
        use_container_width=True,
        hide_index=True
    )

    with st.expander("⚙ Manual Column Mapping"):

        all_cols = ["(none)"] + list(df.columns)

        for role in roles:

            current = col_map.get(
                role,
                "(none)"
            )

            idx = (
                all_cols.index(current)
                if current in all_cols
                else 0
            )

            selected = st.selectbox(
                role.title(),
                all_cols,
                index=idx,
                key=f"map_{role}"
            )

            if selected != "(none)":

                col_map[role] = selected

        st.session_state["col_map"] = col_map


# ==================================================
# DATA PREVIEW
# ==================================================

def show_dataset(df):

    st.subheader("👁 Dataset Preview")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Raw Data",
        "Data Types",
        "Statistics",
        "Missing Values"
    ])

    # ==========================
    # RAW DATA
    # ==========================

    with tab1:

        st.dataframe(
            df.head(100),
            use_container_width=True
        )

    # ==========================
    # DATA TYPES
    # ==========================

    with tab2:

        dtype_df = pd.DataFrame({

            "Column":
                df.columns,

            "Data Type":
                df.dtypes.astype(str),

            "Non Null":
                df.notnull().sum(),

            "Null %":
                (
                    df.isnull().mean() * 100
                ).round(2)

        })

        st.dataframe(
            dtype_df,
            use_container_width=True
        )

    # ==========================
    # STATISTICS
    # ==========================

    with tab3:

        try:

            stats = (
                df.describe(
                    include="all"
                ).T
            )

            st.dataframe(
                stats,
                use_container_width=True
            )

        except Exception:

            st.info(
                "Statistics unavailable."
            )

    # ==========================
    # MISSING VALUES
    # ==========================

    with tab4:

        missing_df = pd.DataFrame({

            "Column":
                df.columns,

            "Missing":
                df.isnull().sum(),

            "Missing %":
                (
                    df.isnull().mean() * 100
                ).round(2)

        })

        st.dataframe(
            missing_df,
            use_container_width=True
        )

    # ==========================
    # DOWNLOAD CLEAN DATA
    # ==========================

    st.markdown("---")

    csv = df.to_csv(
        index=False
    )

    st.download_button(
        "⬇ Download Clean Dataset",
        csv,
        "clean_dataset.csv",
        "text/csv"
    )