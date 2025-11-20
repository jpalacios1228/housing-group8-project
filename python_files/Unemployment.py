import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from pathlib import Path

def run_unemployment():
    """Run the UnemploymentReport cleaning and analysis."""

    # Configuration
    in_file = 'UnemploymentReport.xlsx'
    in_sheet = 'UnemploymentReport'
    out_dir = 'output'

    Path(out_dir).mkdir(exist_ok=True)

    # Load raw sheet
    raw_df = pd.read_excel(in_file, sheet_name=in_sheet, header=None)
    n_rows, n_cols = raw_df.shape

    def is_empty_cell(v):
        if pd.isna(v) or v == "" or v is None:
            return True
        if isinstance(v, str) and v.strip() == "":
            return True
        return False

    # Auto-detect header row
    best_row = None
    best_score = -float('inf')

    for r in range(n_rows):
        row_vals = raw_df.iloc[r].fillna('').astype(str).str.strip().str.lower()
        non_empty = sum(~raw_df.iloc[r].apply(is_empty_cell))
        key_hits = sum(row_vals.str.contains(
            'unemploy|rate|percent|pct|lower|upper|bound|name|state|region|fips',
            na=False
        ))
        score = non_empty + 2 * key_hits
        if score > best_score:
            best_score = score
            best_row = r

    hdr_row = best_row
    if hdr_row is None:
        raise ValueError("Could not detect header row.")

    hdr = raw_df.iloc[hdr_row].fillna('').astype(str)
    last_col = None
    for i in range(len(hdr) - 1, -1, -1):
        if not is_empty_cell(hdr.iloc[i]):
            last_col = i
            break

    if last_col is None:
        raise ValueError("Header row is empty.")

    hdr = hdr.iloc[:last_col + 1]

    # Detect data rows
    data_start = hdr_row + 1
    is_data_row = [False] * n_rows

    for r in range(data_start, n_rows):
        c1 = raw_df.iloc[r, 0] if last_col >= 0 else None
        c2 = raw_df.iloc[r, 1] if last_col >= 1 else None
        is_data_row[r] = not (is_empty_cell(c1) and is_empty_cell(c2))

    data_end = None
    for r in range(n_rows - 1, data_start - 1, -1):
        if is_data_row[r]:
            data_end = r
            break

    if data_end is None:
        raise ValueError("No data rows found under header.")

    # Extract clean data
    data = raw_df.iloc[data_start:data_end + 1, :last_col + 1].copy()
    data.columns = range(data.shape[1])

    # Create column names
    names = []
    for col_name in hdr:
        clean = re.sub(r'[^A-Za-z0-9_]', '_', str(col_name))
        clean = re.sub(r'_+', '_', clean).strip('_')
        if not clean:
            clean = "Column"
        base = clean
        count = 1
        while clean in names:
            clean = f"{base}_{count}"
            count += 1
        names.append(clean)

    data.columns = names

    # Find name column
    lv = data.columns.str.lower()
    name_idx = None
    for pattern in ["name", "state", "region", "area", "geo"]:
        matches = lv.str.contains(pattern)
        if matches.any():
            name_idx = matches.idxmax()
            break

    if name_idx is None:
        name_idx = 0
        cols = data.columns.tolist()
        cols[0] = "Name"
        data.columns = cols

    # Build U table
    U = pd.DataFrame()
    U["Name"] = data.iloc[:, name_idx].astype(str)
    U = U[U["Name"].str.strip() != ""].copy()

    # Identify unemployment %
    lv = data.columns.str.lower()
    remove = lv.str.contains("fips|code|id|cnt|total|number")
    cand_idx = [i for i in range(len(data.columns)) if not remove[i] and i != name_idx]

    best = {'idx': None, 'score': -float('inf'), 'scale': 1, 'hdr': ""}
    for idx in cand_idx:
        hdr_name = data.columns[idx]

        raw_vals = data.iloc[:len(U), idx].astype(str)
        raw_vals = raw_vals.str.replace('%', '', regex=False)
        raw_vals = raw_vals.str.replace(',', '', regex=False)
        vals = pd.to_numeric(raw_vals, errors='coerce')

        frac = vals.notna().mean()
        if frac < 0.75:
            continue

        med = vals.median()
        p90 = vals.quantile(0.90)
        mx = vals.max()
        score = 0

        if any(k in hdr_name.lower() for k in ["unemploy", "rate", "percent", "pct"]):
            score += 3

        if p90 <= 20 and mx <= 100:
            score += 5
            scale = 1
        elif p90 <= 1.2:
            score += 4
            scale = 100
        else:
            scale = 1

        if score > best["score"]:
            best.update({'idx': idx, 'score': score, 'scale': scale, 'hdr': hdr_name})

    if best["idx"] is None:
        raise ValueError("Could not detect unemployment % column.")

    # Build numeric %
    vals = data.iloc[:len(U), best["idx"]].astype(str)
    vals = vals.str.replace('%', '', regex=False)
    vals = vals.str.replace(',', '', regex=False)
    U["Unemployment_Pct"] = pd.to_numeric(vals, errors='coerce') * best["scale"]

    # Final cleaning
    U = U[~U["Name"].str.lower().eq("united states")].copy()
    U = U[~U["Name"].str.match(r'^\d+$', na=False)].copy()
    U = U[(U["Unemployment_Pct"] >= 0) & (U["Unemployment_Pct"] <= 100)]

    # Save cleaned CSV
    out_csv = os.path.join(out_dir, "Unemployment_Clean.csv")
    U.to_csv(out_csv, index=False)

    # Plot histogram
    plt.figure(figsize=(9, 5))
    plt.hist(U["Unemployment_Pct"], bins=15)
    plt.xlabel("Unemployment Rate (%)")
    plt.ylabel("Count")
    plt.title("Distribution of Unemployment Rates")
    hist_path = os.path.join(out_dir, "unemployment_hist.png")
    plt.savefig(hist_path)
    plt.close()

    # Plot top 10
    top10 = U.nlargest(10, "Unemployment_Pct")
    plt.figure(figsize=(9, 6))
    plt.barh(top10["Name"], top10["Unemployment_Pct"])
    plt.xlabel("Unemployment Rate (%)")
    plt.title("Top 10 Highest Unemployment")
    bar_path = os.path.join(out_dir, "unemployment_top10.png")
    plt.savefig(bar_path)
    plt.close()

    return U, hist_path, bar_path


# DO NOT AUTORUN WHEN IMPORTED INTO STREAMLIT
if __name__ == "__main__":
    run_unemployment()
