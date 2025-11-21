import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import os
import re
from pathlib import Path

def main():
    st.header("📈 US Population Report Analysis")

    # Config
    file = "PopulationReport.xlsx"
    sheet = "PopulationReport"
    out_dir = "output"
    Path(out_dir).mkdir(exist_ok=True)

    st.subheader("📂 Loading Dataset")
    try:
        raw = pd.read_excel(file, sheet_name=sheet, header=None)
        st.success(f"Loaded: {file}")
    except Exception as e:
        st.error(f"Error loading the dataset: {e}")
        return

    n_rows, n_cols = raw.shape

    def to_string(x):
        if pd.isna(x):
            return ""
        return str(x).strip()

    # --------------------------------------------
    # 1. Detect Header Row
    # --------------------------------------------
    hdr_row = None
    for r in range(n_rows):
        row = [to_string(raw.iloc[r, c]) for c in range(n_cols)]
        if any(cell.lower() == "name" for cell in row):
            pop_hits = sum("pop" in cell.lower() for cell in row)
            if pop_hits >= 2:
                hdr_row = r
                break

    # Backup detection if unclear
    if hdr_row is None:
        best_row = None
        best_score = -np.inf
        for r in range(n_rows):
            row = [to_string(raw.iloc[r, c]) for c in range(n_cols)]
            score = sum("pop" in cell.lower() for cell in row) + any(cell.lower() == "name" for cell in row)
            if score > best_score:
                best_score = score
                best_row = r
        hdr_row = best_row
        st.warning(f"Header row not obvious — using row {hdr_row}")

    hdr = [to_string(raw.iloc[hdr_row, c]) for c in range(n_cols)]

    # Last non-empty column
    last_col = None
    for c in range(n_cols - 1, -1, -1):
        if hdr[c] not in ["", "NA"] and not pd.isna(hdr[c]):
            last_col = c
            break

    if last_col is None:
        st.error("Header row is empty — cannot continue.")
        return

    hdr = hdr[:last_col + 1]

    # --------------------------------------------
    # 2. Extract data rows
    # --------------------------------------------
    data_start = hdr_row + 1
    is_data_row = [False] * n_rows

    def empty(v):
        if pd.isna(v) or v is None:
            return True
        if isinstance(v, str) and v.strip() == "":
            return True
        return False

    for r in range(data_start, n_rows):
        c1 = raw.iloc[r, 0]
        c2 = raw.iloc[r, 1] if last_col >= 1 else ""
        is_data_row[r] = not (empty(c1) and empty(c2))

    data_end = None
    for r in range(n_rows - 1, data_start - 1, -1):
        if is_data_row[r]:
            data_end = r
            break

    if data_end is None:
        st.error("No usable data rows found.")
        return

    data = raw.iloc[data_start:data_end+1, :last_col+1].reset_index(drop=True)
    data.columns = range(data.shape[1])

    # --------------------------------------------
    # 3. Normalize column names
    # --------------------------------------------
    def clean_column_name(name):
        name = re.sub(r"\s+", " ", name)
        name = re.sub(r"[^\w\. ]", "", name)
        name = re.sub(r"[^A-Za-z0-9_]", "_", name)
        name = re.sub(r"_+", "_", name)
        return name

    var_names = [clean_column_name(hdr[i]) for i in range(len(hdr))]
    data.columns = var_names

    st.subheader("🧭 Detected Columns")
    st.write(var_names)

    # --------------------------------------------
    # 4. Standardize column names
    # --------------------------------------------
    expected = ['Name', 'Pop_1990', 'Pop_2000', 'Pop_2010', 'Pop_2020', 'Pop_2023', 'Change_2020_23']
    cur = data.columns.tolist()
    canon = [name.lower().replace("_", "").replace(".", "").replace(" ", "") for name in cur]

    def find_match(token):
        target = token.lower().replace("_", "")
        for i, col in enumerate(canon):
            if target in col:
                return i
        return None

    idx = {name: find_match(name) for name in expected}

    # Build standardized df
    U_data = {}
    for col in expected:
        i = idx[col]
        if i is not None:
            U_data[col] = data.iloc[:, i]

    U = pd.DataFrame(U_data)

    # --------------------------------------------
    # 5. Clean dataset
    # --------------------------------------------
    st.subheader("🧼 Cleaning Data")

    if "Name" in U.columns:
        U = U[U["Name"].notna() & (U["Name"] != "")]

    # Convert numeric columns
    for col in U.columns:
        if col != "Name":
            U[col] = pd.to_numeric(U[col], errors="coerce")

    # Remove national row
    if "Name" in U.columns:
        U = U[~U["Name"].str.lower().eq("united states")]

    st.success(f"✔ Cleaned dataset: {len(U)} rows")

    # --------------------------------------------
    # 6. Stats + Visuals
    # --------------------------------------------
    if "Pop_2023" not in U.columns:
        st.warning("Population 2023 column missing — cannot compute visuals.")
    else:
        st.subheader("📊 Summary Statistics — Population 2023")

        x = U["Pop_2023"].dropna()

        st.write({
            "Count": len(x),
            "Mean": float(x.mean()),
            "Std": float(x.std()),
            "Min": float(x.min()),
            "Median": float(x.median()),
            "Max": float(x.max()),
            "Sum": float(x.sum())
        })

        # Histogram
        fig, ax = plt.subplots(figsize=(8,4))
        ax.hist(U["Pop_2023"] / 1e6, bins="auto")
        ax.grid(True)
        ax.set_xlabel("Population (millions)")
        ax.set_ylabel("States")
        ax.set_title("Distribution of Population (2023)")
        st.pyplot(fig)

        # Top 10
        if "Name" in U.columns:
            st.subheader("🏆 Top 10 Most Populated States (2023)")
            sorted_df = U.sort_values("Pop_2023", ascending=False)
            top10 = sorted_df.head(10)

            fig, ax = plt.subplots(figsize=(8,6))
            ax.barh(top10["Name"], top10["Pop_2023"] / 1e6)
            ax.invert_yaxis()
            ax.set_xlabel("Population (millions)")
            ax.set_title("Top 10 States by Population — 2023")
            ax.grid(True)
            st.pyplot(fig)

        # Scatter 1990 vs 2023
        if "Pop_1990" in U.columns:
            st.subheader("📈 Growth: 1990 → 2023")

            fig, ax = plt.subplots(figsize=(8,6))
            ax.scatter(U["Pop_1990"] / 1e6, U["Pop_2023"] / 1e6)
            ax.grid(True)
            ax.set_xlabel("Population 1990 (millions)")
            ax.set_ylabel("Population 2023 (millions)")
            ax.set_title("Population Growth Comparison")

            max_val = max(U["Pop_1990"].max(), U["Pop_2023"].max()) / 1e6 * 1.05
            ax.plot([0, max_val], [0, max_val], "--")
            st.pyplot(fig)

    # --------------------------------------------
    # 7. Save cleaned output
    # --------------------------------------------
    output_file = os.path.join(out_dir, "Population_Clean.csv")
    U.to_csv(output_file, index=False)
    st.success(f"💾 Cleaned population dataset saved to: `{output_file}`")

if __name__ == "__main__":
    main()
