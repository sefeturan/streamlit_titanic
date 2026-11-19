import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# 1. SAYFA YAPILANDIRMASI & RENK PALETİ (Navy & Teal)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Titanic Passenger Insights",
    page_icon="🚢",
    layout="wide"
)

PRIMARY_NAVY = "#1B365D"
ACCENT_TEAL = "#008080"
COLOR_MAP_SURVIVAL = {"Survived": ACCENT_TEAL, "Did Not Survive": PRIMARY_NAVY}

st.title("🚢 Titanic Passenger Insights")
st.markdown("Explore survival patterns across passenger groups")

# ---------------------------------------------------------
# 2. VERİ SETİNİ YÜKLEME (Load)
# ---------------------------------------------------------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv"
    return pd.read_csv(url)

df_raw = load_data()
selected_cols = ["survived", "pclass", "sex", "age", "fare", "embarked"]

# ---------------------------------------------------------
# 3. VERİ ÖN İŞLEME (Eksik Veriler, Normalizasyon, Gruplama, Kodlama)
# ---------------------------------------------------------
def preprocess_data(df):
    df_clean = df[selected_cols].copy()
    
    # Eksik verileri doldurma: age -> medyan, embarked -> en sık kategori (mod)
    age_median = df_clean["age"].median()
    embarked_mode = df_clean["embarked"].mode()[0]
    
    df_clean["age"] = df_clean["age"].fillna(age_median)
    df_clean["embarked"] = df_clean["embarked"].fillna(embarked_mode)
    
    # Yaş ayrıklaştırma (Discretization -> age_group)
    bins = [-0.1, 12, 18, 35, 60, 120]
    labels = ["Child", "Teen", "Young Adult", "Adult", "Older Adult"]
    df_clean["age_group"] = pd.cut(df_clean["age"], bins=bins, labels=labels)
    
    # Dönüştürülmüş veri seti kopyası
    df_trans = df_clean.copy()
    
    # Min-Max normalizasyon (orijinal age ve fare sütunları korunur)
    df_trans["age_norm"] = (df_trans["age"] - df_trans["age"].min()) / (df_trans["age"].max() - df_trans["age"].min())
    df_trans["fare_norm"] = (df_trans["fare"] - df_trans["fare"].min()) / (df_trans["fare"].max() - df_trans["fare"].min())
    
    # sex ve embarked sütunlarını tek sütunda sayısal kodlama (survived hariç, kodlanan sütunlara normalizasyon yok)
    sex_dummy = pd.get_dummies(df_trans["sex"], drop_first=True, dtype=int)
    df_trans["sex"] = sex_dummy["male"]
    df_trans["embarked"] = df_trans["embarked"].map({"C": 0, "Q": 1, "S": 2}).astype(int)
    
    return df_clean, df_trans, age_median, embarked_mode

df_clean, df_transformed, age_median, embarked_mode = preprocess_data(df_raw)

# ---------------------------------------------------------
# 4. KENAR ÇUBUĞU (SIDEBAR) FİLTRELERİ
# ---------------------------------------------------------
st.sidebar.header("Filter Passengers")

pclass_options = ["All"] + sorted(df_clean["pclass"].unique().tolist())
selected_pclass = st.sidebar.selectbox("Passenger Class", pclass_options)

sex_options = ["All"] + sorted(df_clean["sex"].unique().tolist())
selected_sex = st.sidebar.selectbox("Sex", sex_options)

age_group_options = ["All", "Child", "Teen", "Young Adult", "Adult", "Older Adult"]
selected_age_group = st.sidebar.selectbox("Age Group", age_group_options)

mask = pd.Series(True, index=df_clean.index)
if selected_pclass != "All":
    mask &= (df_clean["pclass"] == selected_pclass)
if selected_sex != "All":
    mask &= (df_clean["sex"] == selected_sex)
if selected_age_group != "All":
    mask &= (df_clean["age_group"] == selected_age_group)

# .loc kullanarak filtrelenmiş veri setlerini oluşturma
df_filtered = df_clean.loc[mask].copy()
df_raw_filtered = df_raw.loc[mask].copy()
df_trans_filtered = df_transformed.loc[mask].copy()

# ---------------------------------------------------------
# 5. DÖRT SEKMELİ ANA ARAYÜZ (TABS)
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Explore", "Preprocessing", "Data Explorer"])

# ==================== TAB 1: OVERVIEW ====================
with tab1:
    st.subheader("Key Survival Metrics")
    
    total_passengers = len(df_filtered)
    survivors = int(df_filtered["survived"].sum()) if total_passengers > 0 else 0
    survival_rate = (survivors / total_passengers * 100) if total_passengers > 0 else 0.0
    avg_fare = df_filtered["fare"].mean() if total_passengers > 0 else 0.0
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Passengers in Selection", str(total_passengers))
    kpi2.metric("Survivors", str(survivors))
    kpi3.metric("Survival Rate", f"{survival_rate:.1f}%")
    kpi4.metric("Average Fare", chr(36) + f"{avg_fare:.2f}")
    
    st.divider()
    
    if total_passengers == 0:
        st.warning("No passengers match the selected filter criteria.")
    else:
        col_left, col_right = st.columns(2)
        
        with col_left:
            surv_counts = df_filtered["survived"].map({1: "Survived", 0: "Did Not Survive"}).value_counts().reset_index()
            surv_counts.columns = ["Outcome", "Count"]
            fig_counts = px.bar(
                surv_counts,
                x="Outcome",
                y="Count",
                color="Outcome",
                color_discrete_map=COLOR_MAP_SURVIVAL,
                title="Passenger Survival Counts",
                labels={"Outcome": "Survival Status", "Count": "Number of Passengers"},
                text_auto=True
            )
            fig_counts.update_layout(showlegend=False)
            st.plotly_chart(fig_counts, use_container_width=True)
            
        with col_right:
            class_surv = df_filtered.groupby("pclass", as_index=False)["survived"].mean()
            class_surv["Survival Rate (%)"] = class_surv["survived"] * 100
            class_surv["Passenger Class"] = class_surv["pclass"].astype(str)
            fig_class = px.bar(
                class_surv,
                x="Passenger Class",
                y="Survival Rate (%)",
                title="Survival Rate by Passenger Class",
                labels={"Passenger Class": "Passenger Class (1 = 1st, 2 = 2nd, 3 = 3rd)", "Survival Rate (%)": "Survival Rate (%)"},
                color_discrete_sequence=[ACCENT_TEAL],
                text_auto=".1f"
            )
            fig_class.update_yaxes(range=[0, 100])
            st.plotly_chart(fig_class, use_container_width=True)
            
        st.caption("Note: Survival counts and rates describe this dataset only and reflect the active sidebar filters.")

# ==================== TAB 2: EXPLORE ====================
with tab2:
    st.subheader("Compare Passenger Groups")
    
    if len(df_filtered) == 0:
        st.warning("No passengers match the selected filter criteria.")
    else:
        row1_col1, row1_col2 = st.columns(2)
        
        with row1_col1:
            class_rate = df_filtered.groupby("pclass", as_index=False)["survived"].mean()
            class_rate["Survival Rate (%)"] = class_rate["survived"] * 100
            class_rate["pclass"] = class_rate["pclass"].astype(str)
            fig_exp_class = px.bar(
                class_rate,
                x="pclass",
                y="Survival Rate (%)",
                title="Survival Rate by Passenger Class",
                labels={"pclass": "Passenger Class", "Survival Rate (%)": "Survival Rate (%)"},
                color_discrete_sequence=[PRIMARY_NAVY],
                text_auto=".1f"
            )
            fig_exp_class.update_yaxes(range=[0, 100])
            st.plotly_chart(fig_exp_class, use_container_width=True)
            
        with row1_col2:
            sex_rate = df_filtered.groupby("sex", as_index=False)["survived"].mean()
            sex_rate["Survival Rate (%)"] = sex_rate["survived"] * 100
            fig_exp_sex = px.bar(
                sex_rate,
                x="sex",
                y="Survival Rate (%)",
                title="Survival Rate by Sex",
                labels={"sex": "Sex", "Survival Rate (%)": "Survival Rate (%)"},
                color_discrete_sequence=[ACCENT_TEAL],
                text_auto=".1f"
            )
            fig_exp_sex.update_yaxes(range=[0, 100])
            st.plotly_chart(fig_exp_sex, use_container_width=True)
            
        row2_col1, row2_col2 = st.columns(2)
        
        with row2_col1:
            df_hist = df_filtered.copy()
            df_hist["Status"] = df_hist["survived"].map({1: "Survived", 0: "Did Not Survive"})
            fig_age_hist = px.histogram(
                df_hist,
                x="age",
                color="Status",
                barmode="overlay",
                nbins=25,
                title="Age Distribution by Survival Status",
                labels={"age": "Age (Years)", "count": "Number of Passengers"},
                color_discrete_map=COLOR_MAP_SURVIVAL
            )
            st.plotly_chart(fig_age_hist, use_container_width=True)
            
        with row2_col2:
            df_fare_box = df_filtered.copy()
            df_fare_box["pclass"] = df_fare_box["pclass"].astype(str)
            fig_fare_class = px.box(
                df_fare_box,
                x="pclass",
                y="fare",
                title="Fare Distribution by Passenger Class",
                labels={"pclass": "Passenger Class", "fare": "Ticket Fare (USD)"},
                color_discrete_sequence=[PRIMARY_NAVY]
            )
            st.plotly_chart(fig_fare_class, use_container_width=True)
            
        st.info("**Observed Finding:** In this dataset, higher survival rates are associated with female passengers and those traveling in higher passenger classes (1st class compared to 3rd class).")

# ==================== TAB 3: PREPROCESSING ====================
with tab3:
    st.subheader("Data Inspection & Transformation Pipeline")
    
    with st.expander("0. Initial Dataset Inspection (Shape, Column Names, Types, First 5 Rows & Missing Counts)", expanded=True):
        st.caption("Raw dataset structure before preprocessing; .loc is used to preview the first five rows of the selected columns.")
        st.write(f"**Dataset Shape:** {df_raw.shape[0]} rows, {df_raw.shape[1]} columns")
        st.write(f"**All Column Names ({len(df_raw.columns)}):** `{', '.join(df_raw.columns.tolist())}`")
        
        insp_col1, insp_col2 = st.columns(2)
        with insp_col1:
            st.write("**Column Names, Data Types & Missing Values:**")
            dtypes_df = pd.DataFrame({
                "Column Name": df_raw.columns,
                "Data Type": df_raw.dtypes.astype(str),
                "Raw Missing Count": df_raw.isnull().sum().values
            }).reset_index(drop=True)
            st.dataframe(dtypes_df, use_container_width=True, height=260, hide_index=True)
        with insp_col2:
            st.write("**First 5 Rows (`.loc[:4, selected_cols]`):**")
            st.dataframe(df_raw.loc[:4, selected_cols], use_container_width=True)

    with st.expander("1. Handling Missing Values (Before vs. After)", expanded=True):
        st.caption("Missing values in 'age' were imputed with the median and missing values in 'embarked' were imputed with the most frequent category, while 'deck' was excluded due to excessive missingness.")
        missing_compare_df = pd.DataFrame({
            "Column Name": selected_cols,
            "Missing Before": [df_raw[col].isnull().sum() for col in selected_cols],
            "Missing After": [df_clean[col].isnull().sum() for col in selected_cols],
            "Imputation Method": [
                "No missing values",
                "No missing values",
                "No missing values",
                f"Median ({age_median:.1f})",
                "No missing values",
                f"Mode ('{embarked_mode}')"
            ]
        })
        st.dataframe(missing_compare_df, use_container_width=True, hide_index=True)
        
    with st.expander("2. Min-Max Normalization", expanded=True):
        st.caption("Min-Max normalization rescales 'age' and 'fare' to a [0, 1] range while preserving the original columns for interpretability.")
        norm_preview = df_transformed.loc[:4, ["age", "age_norm", "fare", "fare_norm"]]
        st.dataframe(norm_preview, use_container_width=True)
        
    with st.expander("3. Age Discretization", expanded=True):
        st.caption("Continuous 'age' values were grouped into five interpretable life-stage categories (Child, Teen, Young Adult, Adult, Older Adult).")
        disc_preview = df_clean.loc[:7, ["age", "age_group"]]
        st.dataframe(disc_preview, use_container_width=True)
        
    with st.expander("4. Categorical Coding (Sex & Embarked)", expanded=True):
        st.caption("Categorical variables 'sex' (1 = male, 0 = female) and 'embarked' (0 = C, 1 = Q, 2 = S) were encoded into single numeric columns without altering 'survived'.")
        before_df = df_clean.loc[:4, ["sex", "embarked"]].rename(columns={"sex": "sex (before)", "embarked": "embarked (before)"})
        after_df = df_transformed.loc[:4, ["sex", "embarked"]].rename(columns={"sex": "sex (after: 1=male, 0=female)", "embarked": "embarked (after: 0=C, 1=Q, 2=S)"})
        dummy_compare = pd.concat([before_df, after_df], axis=1)
        st.dataframe(dummy_compare, use_container_width=True)

# ==================== TAB 4: DATA EXPLORER ====================
with tab4:
    st.subheader("Interactive Dataset Explorer")
    
    col_view, col_cols = st.columns([1, 2])
    with col_view:
        view_choice = st.radio("Select Dataset View:", ["Raw", "Cleaned", "Transformed"], horizontal=True)
        
    if view_choice == "Raw":
        active_df = df_raw_filtered
        default_cols = [c for c in selected_cols if c in active_df.columns]
    elif view_choice == "Cleaned":
        active_df = df_filtered
        default_cols = active_df.columns.tolist()
    else:
        active_df = df_trans_filtered
        default_cols = active_df.columns.tolist()
        
    with col_cols:
        chosen_columns = st.multiselect("Choose Columns to Display:", active_df.columns.tolist(), default=default_cols)
        
    st.markdown(f"**Showing {len(active_df)} rows** matching the current sidebar filters.")
    
    if chosen_columns:
        st.dataframe(active_df[chosen_columns], use_container_width=True, height=400)
    else:
        st.warning("Please select at least one column to display.")