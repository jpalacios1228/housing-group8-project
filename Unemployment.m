import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from pathlib import Path


def load_and_process_unemployment(file="UnemploymentReport.xlsx", sheet="UnemploymentReport", out_dir="output"):
    """
    Full unemployment processing pipeline:
    - Load raw sheet without trusting headers
    - Auto-detect header row
    - Detect data rows
    - Build cleaned table
    - Auto-detect unemployment percentage column using heuristics
    - Scale correctly (percent vs fraction)
    - Final cleaning (remove US row, remove numeric-only names)
    - Create histogram + top-10 bar plot
    - Save cleaned CSV
    - Return table + image paths
    """

    # Ensure output directory
    Path(out_dir).mkdir(exist_ok=True)

    # Load raw sheet without trusting headers
    raw = pd.read_excel(file, sheet_name=sheet, header=None, dtype=str)
    n_rows, n_cols = raw.shape

    # Helper for determining emptiness
    def empty(val):
        if val is None: return True
        if isinstance(val, float) and np.isnan(val): return True
        if isinstance(val, str) and val.strip() == "": return True
        return False

    # 1) Auto-detect header row
    best_row = None
    best_score = -1

    header_keywords = ["unemploy", "rate", "percent", "pct", "lower", "upper", "bound", "name", "state", "region", "fips"]

    for r in range(n_rows):
        row_vals = raw.iloc[r].astype(str)
        lv = row_vals.str.lower().str.strip()

        non_empty = sum(~lv.apply(empty))
        hits = sum(lv.str.contains("|".join(header_keywords), na=False))

        score = non_empty + 2 * hits
        if score > best_score:
            best_score = score
            best_row = r

    if best_row is None:
        raise ValueError("Could not detect header row.")

    # Trim empty columns
    hdr = raw.iloc[best_row].astype(str)
    valid_cols = hdr.replace("", np.nan).dropna().index
    last_col = valid_cols.max()
    hdr = hdr.loc[:last_col]

    # 2) Determine data rows
    data_start = best_row + 1
    is_data_row = []

    for r in range(data_start, n_rows):
        c1 = raw.iloc[r, 0]
        c2 = raw.iloc[r, 1] if last_col >= 1 else ""
        is_data_row.append(not (empty(c1) and empty(c2)))

    if not any(is_data_row):
        raise ValueError("No data rows under header.")

    data_end = data_start + np.where(is_data_row)[0].max()
    data = raw.iloc[data_start:data_end+1, :last_col+1]

    # Build DataFrame with cleaned column names
    df = data.copy()
    colnames = hdr.astype(str).str.replace("[^A-Za-z0-9_]", "_", regex=True)
    colnames = colnames.str.replace("_+", "_", regex=True)
    df.columns = colnames

    # 3) Detect name column
    lv = df.columns.str.lower()
    name_idx = None
    for key in ["name", "state", "region", "area", "geo"]:
        matches = lv.str.contains(key)
        if matches.any():
            name_idx = matches.argmax()
            break

    if name_idx is None:
        name_idx = 0
        df.rename(columns={df.columns[0]: "Name"}, inplace=True)

    # Build U table
    U = pd.DataFrame()
    U["Name"] = df.iloc[:, name_idx].astype(str)
    U = U[U["Name"].str.strip() != ""]

    # 4) Auto-detect unemployment % column
    bad_hdr = lv.str.contains("fips|code|id|number|cnt|count|total")
    cand_idx = [i for i in range(len(df.columns)) if i != name_idx and not bad_hdr[i]]

    best = {"idx": None, "score": -999, "scale": 1, "median": None, "p90": None, "max": None}

    for idx in cand_idx:
        colname = df.columns[idx]
        rawvals = df.iloc[:len(U), idx].astype(str)
        rawvals = rawvals.str.replace("%", "", regex=False)
        rawvals = rawvals.str.replace(",", "", regex=False)
        vals = pd.to_numeric(rawvals, errors="coerce")

        finite = vals.notna().mean()
        if finite < 0.75:
            continue

        med = vals.median()
        p90 = vals.quantile(0.90)
        mx = vals.max()

        score = 0
        lname = colname.lower()

        # Header keyword bonus
        if any(k in lname for k in ["unemploy", "rate", "percent", "pct"]):
            score += 3

        # Percent range
        if p90 <= 20 and mx <= 100 and 2 <= med <= 12:
            score += 5
            scale = 1

        # Fraction range
        elif p90 <= 1.0 and mx <= 1.2 and 0.02 <= med <= 0.12:
            score += 4
            scale = 100

        else:
            scale = 1
            # Penalize codes
            int_like = np.mean(np.abs(vals - np.round(vals)) < 1e-9)
            if int_like > 0.9 and mx > 50:
                score -= 4
            if mx <= 100 and p90 <= 30:
                score += 1

        if score > best["score"]:
            best.update({"idx": idx, "score": score, "scale": scale, "median": med, "p90": p90, "max": mx})

    if best["idx"] is None:
        raise ValueError("Could not detect unemployment percentage column.")

    # Build unemployment % column
    rawvals = df.iloc[:len(U), best["idx"]].astype(str)
    rawvals = rawvals.str.replace("%", "", regex=False)
    rawvals = rawvals.str.replace(",", "", regex=False)
    U["Unemployment_Pct"] = pd.to_numeric(rawvals, errors="coerce") * best["scale"]

    # 5) Final cleaning
    U = U[~U["Name"].str.lower().eq("united states")]
    U = U[~U["Name"].str.match(r"^\d+$")]
    U = U[(U["Unemployment_Pct"] >= 0) & (U["Unemployment_Pct"] <= 100)]

    # Save cleaned CSV
    out_csv = os.path.join(out_dir, "Unemployment_Clean.csv")
    U.to_csv(out_csv, index=False)

    # 6) Plots
    # Histogram
    plt.figure(figsize=(9, 5))
    plt.hist(U["Unemployment_Pct"], bins=15)
    plt.xlabel("Unemployment Rate (%)")
    plt.ylabel("Count")
    plt.title("Distribution of Unemployment Rates")
    hist_path = os.path.join(out_dir, "unemployment_hist.png")
    plt.savefig(hist_path)
    plt.close()

    # Top 10
    top10 = U.nlargest(10, "Unemployment_Pct")
    plt.figure(figsize=(9, 6))
    plt.barh(top10["Name"], top10["Unemployment_Pct"])
    plt.xlabel("Unemployment Rate (%)")
    plt.title("Top 10 Highest Unemployment")
    bar_path = os.path.join(out_dir, "unemployment_top10.png")
    plt.savefig(bar_path)
    plt.close()

    return U, hist_path, bar_path
