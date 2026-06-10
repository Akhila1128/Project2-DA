import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from utils.theme import PASTEL, CHART_COLORS, plotly_layout

def render():
    df = st.session_state.get("df")
    if df is None:
        st.warning("⚠️ Please upload data first."); return

    col_map = st.session_state.get("col_map", {})
    sales_col = col_map.get("sales")
    if not sales_col:
        st.warning("⚠️ Sales column not detected."); return

    st.markdown('<div class="section-header">🤖 Model Training & Evaluation</div>', unsafe_allow_html=True)

    # ---- Prepare Features ----
    df_ml = df.copy()
    le = LabelEncoder()
    cat_cols = df_ml.select_dtypes(include="object").columns
    for c in cat_cols:
        df_ml[c] = le.fit_transform(df_ml[c].astype(str))

    date_cols = df_ml.select_dtypes(include="datetime64").columns
    for c in date_cols:
        df_ml[c + "_ts"] = df_ml[c].astype(np.int64) // 10**9
        df_ml.drop(c, axis=1, inplace=True)

    df_ml = df_ml.fillna(df_ml.median(numeric_only=True))
    feature_cols = [c for c in df_ml.columns if c != sales_col]

    with st.expander("⚙️ Training Configuration", expanded=True):
        c1, c2, c3 = st.columns(3)
        test_size  = c1.slider("Test Split %", 10, 40, 20) / 100
        sel_feats  = c2.multiselect("Feature Columns", feature_cols, default=feature_cols[:6])
        model_sel  = c3.multiselect("Models to Train",
                        ["Linear Regression","Ridge Regression","Random Forest","Gradient Boosting"],
                        default=["Random Forest","Gradient Boosting"])
        n_cv = st.slider("Cross-Validation Folds", 2, 10, 5)

    if not sel_feats:
        st.info("Select at least one feature."); return

    X = df_ml[sel_feats]
    y = df_ml[sales_col]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=test_size, random_state=42)

    if st.button("🚀 Train Selected Models"):
        model_map = {
            "Linear Regression": LinearRegression(),
            "Ridge Regression": Ridge(alpha=1.0),
            "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
            "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
        }

        results = []
        trained_models = {}
        prog = st.progress(0, "Training models...")

        for i, name in enumerate(model_sel):
            m = model_map[name]
            m.fit(X_train, y_train)
            pred  = m.predict(X_test)
            cv    = cross_val_score(m, X_scaled, y, cv=n_cv, scoring="r2")

            results.append({
                "Model": name,
                "R² Score": round(r2_score(y_test, pred), 4),
                "MAE": round(mean_absolute_error(y_test, pred), 2),
                "RMSE": round(np.sqrt(mean_squared_error(y_test, pred)), 2),
                f"CV R² (mean)": round(cv.mean(), 4),
                f"CV R² (std)": round(cv.std(), 4),
            })
            trained_models[name] = (m, pred)
            prog.progress((i + 1) / len(model_sel), f"Trained: {name}")

        prog.empty()
        results_df = pd.DataFrame(results)
        st.session_state["model_results"] = results_df

        # ---- Results Table ----
        st.markdown("#### 📊 Model Comparison")
        st.dataframe(
            results_df.style.highlight_max(subset=["R² Score", "CV R² (mean)"], color="#86EFAC33")
                            .highlight_min(subset=["MAE","RMSE"], color="#86EFAC33"),
            use_container_width=True
        )

        # Bar chart comparison
        fig = px.bar(results_df, x="Model", y=["R² Score","CV R² (mean)"],
                     barmode="group", color_discrete_sequence=[PASTEL["purple"], PASTEL["teal"]])
        fig.update_layout(**plotly_layout("Model R² Comparison"))
        st.plotly_chart(fig, use_container_width=True)

        # ---- Actual vs Predicted ----
        st.markdown("#### 🎯 Actual vs Predicted")
        best = max(trained_models, key=lambda n: r2_score(y_test, trained_models[n][1]))
        y_pred_best = trained_models[best][1]

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=y_test.values, y=y_pred_best,
                                  mode="markers", name="Predictions",
                                  marker=dict(color=PASTEL["purple"], opacity=0.6, size=5)))
        mn = min(y_test.min(), y_pred_best.min())
        mx = max(y_test.max(), y_pred_best.max())
        fig2.add_trace(go.Scatter(x=[mn,mx], y=[mn,mx],
                                  mode="lines", name="Perfect Fit",
                                  line=dict(color=PASTEL["green"], dash="dash")))
        fig2.update_layout(**plotly_layout(f"Actual vs Predicted — {best}"))
        st.plotly_chart(fig2, use_container_width=True)

        # ---- Feature Importance ----
        for name, (m, _) in trained_models.items():
            if hasattr(m, "feature_importances_"):
                st.markdown(f"#### 🔑 Feature Importance — {name}")
                imp_df = pd.DataFrame({"Feature": sel_feats, "Importance": m.feature_importances_})
                imp_df = imp_df.sort_values("Importance", ascending=False)
                fig3 = px.bar(imp_df, x="Importance", y="Feature", orientation="h",
                              color="Importance", color_continuous_scale=["#7DD3FC","#A78BFA"])
                fig3.update_layout(**plotly_layout("Feature Importances"))
                st.plotly_chart(fig3, use_container_width=True)
                break

        # ---- Residuals ----
        residuals = y_test.values - y_pred_best
        fig4 = px.histogram(residuals, nbins=40,
                            color_discrete_sequence=[PASTEL["pink"]])
        fig4.update_layout(**plotly_layout("Residual Distribution"))
        st.plotly_chart(fig4, use_container_width=True)