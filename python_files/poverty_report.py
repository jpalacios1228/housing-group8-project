import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from pathlib import Path


def main():
    """Cleans the PovertyReport and generates figures (Streamlit-safe)."""

    in_file = "PovertyReport.xlsx"
    in_sheet = "PovertyReport"
    out_dir = "output"

    Path(out_dir).mkdir(exist_ok=True)

    # =============================
    # 1. Load sheet and detect header
    # =============================
    raw = pd.read_excel(in_file, sheet_name=in_sheet, header=None)
    n_rows, n_cols = raw.shape

    def is_empty_cell(v):
        if pd.isna(v) or v is None:
            return True
        if isinstance(v, str) and v.strip() == "":
            return True
        return False

    # Find row containing first "Name"
    hdr_row = None
    for r in range(n_rows):
        for c in range(n_cols):
            val = raw.iloc[r, c]
            if isinstance(val, str) and val.strip().lower() == "name":
                hdr_row = r
                break
        if hdr_row is not None:
            break

    if hdr_row is None:
        raise ValueError('Header row not found (cell containing "Name").')

    # Build header list up to last non-empty col
    hdr = [raw.iloc[hdr_row, c] for c in range(n_cols)]

    last_col = None
    for c in range(n_cols - 1, -1, -1):
        if not is_empty_cell(hdr[c]):
            last_col = c
            break

    if last_col is None:
        raise ValueError("Header row appears empty.")

    hdr = hdr[: last_col + 1]

    # =============================
    # 2. Extract data block
    # =============================
    data_start = hdr_row + 1
    is_data_row = [False] * n_rows

    for r in range(data_start, n_rows):
        c1 = raw.iloc[r, 0]
        c2 = raw.iloc[r, 1] if last_col >= 1 else None
        is_data_row[r] = not (is_empty_cell(c1) and is_empty_cell(c2))

    data_end = None
    for r in range(n_rows - 1, data_start - 1, -1):
        if is_data_row[r]:
            data_end = r
            break

    if data_end is None:
        raise ValueError("No data rows found beneath header.")

    data = raw.iloc[data_start : data_end + 1, : last_col + 1].reset_index(drop=True)
    data.columns = range(data.shape[1])

    # =============================
    # 3. Normalize & unique column names
    # =============================
    def clean_col(name, existing):
        s = str(name)
        s = re.sub(r"[^A-Za-z0-9_]", "_", s)
        s = re.sub(r"_+", "_", s)
        s = s.strip("_")
        if not s:
            s = "Column"

        base = s
        count = 1
        while s in existing:
            s = f"{base}_{count}"
            count += 1

        return s

    new_cols = []
    used = set()
    for c in hdr:
        new_name = clean_col(c, used)
        used.add(new_name)
        new_cols.append(new_name)

    data.columns = new_cols

    # =============================
    # 4. Identify needed columns
    # =============================
    lcols = [c.lower() for c in new_cols]

    # Name
    name_idx = next((i for i, c in enumerate(lcols) if "name" in c), None)
    if name_idx is None:
        raise ValueError('Could not find "Name" column.')

    # Percent columns
    percent_idx = [i for i, c in enumerate(lcols) if "percent" in c]
    percent_idx.sort()

    if len(percent_idx) < 2:
        raise ValueError("Expected at least two 'Percent' columns.")

    idx_all_percent = percent_idx[0]
    idx_child_percent = percent_idx[1]

    # Lower / Upper bounds
    lb_idx = [i for i, c in enumerate(lcols) if "lower" in c]
    ub_idx = [i for i, c in enumerate(lcols) if "upper" in c]
    lb_idx.sort()
    ub_idx.sort()

    idx_all_lb = next((i for i in lb_idx if i > idx_all_percent), None)
    idx_all_ub = next((i for i in ub_idx if i > idx_all_percent), None)
    idx_ch_lb = next((i for i in lb_idx if i > idx_child_percent), None)
    idx_ch_ub = next((i for i in ub_idx if i > idx_child_percent), None)

    if None in [idx_all_lb, idx_all_ub, idx_ch_lb, idx_ch_ub]:
        raise ValueError("Could not match LB/UB with Percent columns.")

    # =============================
    # 5. Build cleaned table U
    # =============================
    U = pd.DataFrame({
        "Name": data.iloc[:, name_idx].astype(str),
        "All_Poverty_Pct": data.iloc[:, idx_all_percent],
        "All_Lower_Bound": data.iloc[:, idx_all_lb],
        "All_Upper_Bound": data.iloc[:, idx_all_ub],
        "Children_Poverty_Pct": data.iloc[:, idx_child_percent],
        "Children_Lower_Bound": data.iloc[:, idx_ch_lb],
        "Children_Upper_Bound": data.iloc[:, idx_ch_ub],
    })

    # Drop empty names
    U = U[U["Name"].str.strip() != ""].copy()
    U = U[U["Name"].str.lower() != "nan"].copy()
    U = U[U["Name"].str.lower() != "united states"].copy()

    # Convert numerics
    num_cols = [c for c in U.columns if c != "Name"]
    for c in num_cols:
        U[c] = pd.to_numeric(U[c], errors="coerce")

    # =============================
    # 6. Plots → save to files
    # =============================
    # Hist: All people
    hist_all_path = os.path.join(out_dir, "poverty_all_hist.png")
    plt.figure(figsize=(9, 4.8))
    plt.hist(U["All_Poverty_Pct"].dropna(), bins=15)
    plt.xlabel("Poverty rate (%) – All people")
    plt.ylabel("States")
    plt.title("Distribution of Poverty Rates (All People)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(hist_all_path)
    plt.close()

    # Hist: Children
    hist_child_path = os.path.join(out_dir, "poverty_children_hist.png")
    plt.figure(figsize=(9, 4.8))
    plt.hist(U["Children_Poverty_Pct"].dropna(), bins=15)
    plt.xlabel("Poverty rate (%) – Children")
    plt.ylabel("States")
    plt.title("Distribution of Poverty Rates (Children)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(hist_child_path)
    plt.close()

    # Top 10 bar chart
    top10 = U.sort_values("All_Poverty_Pct", ascending=False).head(10)
    top10_path = os.path.join(out_dir, "poverty_all_top10.png")
    plt.figure(figsize=(9, 5.6))
    plt.barh(top10["Name"], top10["All_Poverty_Pct"])
    plt.gca().invert_yaxis()
    plt.xlabel("Poverty rate (%)")
    plt.title("Top 10 Highest Poverty (All People)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(top10_path)
    plt.close()

    # Scatter plot
    scatter_path = os.path.join(out_dir, "poverty_scatter.png")
    plt.figure(figsize=(9, 6.2))
    plt.scatter(U["All_Poverty_Pct"], U["Children_Poverty_Pct"], s=36)
    plt.xlabel("All People Poverty Rate (%)")
    plt.ylabel("Children Poverty Rate (%)")
    plt.title("Children vs All Poverty Rates")
    plt.grid(True)
    maxv = max(U["All_Poverty_Pct"].max(), U["Children_Poverty_Pct"].max()) * 1.05
    plt.plot([0, maxv], [0, maxv], "--")
    plt.tight_layout()
    plt.savefig(scatter_path)
    plt.close()

    # Save cleaned CSV
    out_csv = os.path.join(out_dir, "Poverty_Clean.csv")
    U.to_csv(out_csv, index=False)

    # Return to Streamlit
    return U, hist_all_path, hist_child_path, top10_path, scatter_path


if __name__ == "__main__":
    main()
