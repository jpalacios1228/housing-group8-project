import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from pathlib import Path

def main():
    # Housing Group 8 — Unemployment Report (Auto-Detect Column, v3)
    in_file = 'UnemploymentReport.xlsx'
    in_sheet = 'UnemploymentReport'
    out_dir = 'output'
    
    # Create output directory if it doesn't exist
    Path(out_dir).mkdir(exist_ok=True)
    
    # Load sheet without trusting headers
    raw_df = pd.read_excel(in_file, sheet_name=in_sheet, header=None)
    n_rows, n_cols = raw_df.shape
    
    def is_empty_cell(v):
        if pd.isna(v) or v == "" or v is None:
            return True
        if isinstance(v, str) and v.strip() == "":
            return True
        return False
    
    # Pick the row that looks the most like a header
    best_row = None
    best_score = -float('inf')
    
    for r in range(n_rows):
        row_values = raw_df.iloc[r].fillna('').astype(str).str.strip().str.lower()
        non_empty = sum(~raw_df.iloc[r].apply(is_empty_cell))
        
        key_hits = sum(row_values.str.contains('unemploy|rate|percent|pct|lower|upper|bound|name|state|region|fips', na=False))
        score = non_empty + 2 * key_hits
        
        if score > best_score:
            best_score = score
            best_row = r
    
    hdr_row = best_row
    if hdr_row is None:
        raise ValueError('Could not find a suitable header row')
    
    # Find last non-empty column
    hdr = raw_df.iloc[hdr_row].fillna('').astype(str)
    last_col = None
    for i in range(len(hdr)-1, -1, -1):
        if not is_empty_cell(hdr.iloc[i]):
            last_col = i
            break
    
    if last_col is None:
        raise ValueError('Header row empty.')
    
    hdr = hdr.iloc[:last_col+1]
    
    # Find data rows
    data_start = hdr_row + 1
    is_data_row = [False] * n_rows
    
    for r in range(data_start, n_rows):
        c1 = raw_df.iloc[r, 0] if last_col >= 0 else None
        c2 = raw_df.iloc[r, 1] if last_col >= 1 else None
        
        is_data_row[r] = not (is_empty_cell(c1) and is_empty_cell(c2))
    
    data_end = None
    for r in range(n_rows-1, data_start-1, -1):
        if is_data_row[r]:
            data_end = r
            break
    
    if data_end is None:
        raise ValueError('No data rows under header.')
    
    # Extract data
    data = raw_df.iloc[data_start:data_end+1, :last_col+1].copy()
    data.columns = range(data.shape[1])  # Reset column indices
    
    # Create clean column names
    names = []
    for i, col_name in enumerate(hdr):
        clean_name = re.sub(r'[^A-Za-z0-9_]', '_', str(col_name))
        clean_name = re.sub(r'_+', '_', clean_name)
        clean_name = clean_name.strip('_')
        
        # Make unique
        base_name = clean_name
        counter = 1
        while clean_name in names:
            clean_name = f"{base_name}_{counter}"
            counter += 1
        names.append(clean_name)
    
    # Handle empty column names
    for i, name in enumerate(names):
        if not name:
            names[i] = f'Column_{i+1}'
    
    data.columns = names
    
    # Choose label column (state/region)
    v = data.columns.str.lower()
    name_idx = None
    for pattern in ["name", "state", "region", "area", "geo"]:
        matches = v.str.contains(pattern)
        if matches.any():
            name_idx = matches.idxmax()
            break
    
    if name_idx is None:
        name_idx = 0
        # Rename the first column to "Name"
        new_cols = data.columns.tolist()
        new_cols[0] = "Name"
        data.columns = new_cols
    
    # Create U dataframe
    U = pd.DataFrame()
    U['Name'] = data.iloc[:, name_idx].astype(str)
    
    # Drop blank names
    U = U[~U['Name'].isna() & (U['Name'].str.strip() != '')].copy()
    
    # Score all candidate numeric columns to find the unemployment percentage
    lv = data.columns.str.lower()
    bad_hdr = lv.str.contains('fips|code|id|number|cnt|count|total')
    cand_idx = [i for i in range(len(data.columns)) 
                if not bad_hdr[i] and i != name_idx]
    
    best = {
        'idx': None,
        'scale': 1,
        'score': -float('inf'),
        'median': np.nan,
        'p90': np.nan,
        'maxv': np.nan,
        'hdr': ''
    }
    
    debug_rows = []
    
    for idx in cand_idx:
        hdr_name = data.columns[idx]
        
        # Coerce to numeric, stripping % and commas
        raw_vals = data.iloc[:len(U), idx].astype(str)
        raw_vals = raw_vals.str.replace('%', '', regex=False)
        raw_vals = raw_vals.str.replace(',', '', regex=False)
        vals = pd.to_numeric(raw_vals, errors='coerce')
        
        finite_mask = vals.notna()
        frac_finite = finite_mask.mean()
        if frac_finite < 0.75:
            continue  # need mostly numeric
        
        medv = vals.median()
        p90 = vals.quantile(0.90)  # robust upper spread
        mx = vals.max()
        
        # Heuristics:
        #   prefer 0-20 range or (0-1 range -> fraction)
        score = 0
        hdr_lower = hdr_name.lower()
        if any(keyword in hdr_lower for keyword in ["unemploy", "rate", "percent", "pct"]):
            score += 3
        
        if (p90 <= 20 and mx <= 100 and medv >= 2 and medv <= 12):
            score += 5  # looks like percent already
            proposed_scale = 1
        elif (p90 <= 1.0 and mx <= 1.2 and medv >= 0.02 and medv <= 0.12):
            score += 4  # looks like fraction
            proposed_scale = 100
        else:
            # penalize integer-heavy large columns (likely codes or counts)
            int_like = ((vals - vals.round()).abs() < 1e-9).mean()
            if int_like > 0.9 and mx > 50:
                score -= 4
            # mild acceptance if mostly <=100
            if mx <= 100 and p90 <= 30:
                score += 1
            proposed_scale = 1
        
        # store for debug table
        debug_rows.append([hdr_name, frac_finite, medv, p90, mx, score, proposed_scale])
        
        if score > best['score']:
            best['idx'] = idx
            best['scale'] = proposed_scale
            best['score'] = score
            best['median'] = medv
            best['p90'] = p90
            best['maxv'] = mx
            best['hdr'] = hdr_name
    
    # Show candidates for transparency
    print('\nCandidate columns (most numeric → least filtered):')
    print('%-30s  finite%%  median   p90     max     score  scale' % 'Column Name')
    for row in debug_rows:
        print('%-30s  %6.2f  %7.2f  %6.2f  %7.2f   %5.1f   x%3d' % 
              (row[0], row[1]*100, row[2], row[3], row[4], row[5], row[6]))
    
    if best['idx'] is None or not np.isfinite(best['score']):
        raise ValueError('Could not detect a credible unemployment rate column.')
    
    # Build numeric percent column
    vals = data.iloc[:len(U), best['idx']].astype(str)
    vals = vals.str.replace('%', '', regex=False)
    vals = vals.str.replace(',', '', regex=False)
    vals = pd.to_numeric(vals, errors='coerce')
    U['Unemployment_Pct'] = vals * best['scale']
    
    # Final cleaning
    # Remove United States row
    U = U[~U['Name'].str.strip().str.lower().eq('united states')].copy()
    
    # Drop rows whose "Name" is all digits (FIPS-like) or starts with digits
    is_all_digits = U['Name'].str.match(r'^\d+$', na=False)
    U = U[~is_all_digits].copy()
    
    # Keep only sensible 0..100 %
    U = U[(U['Unemployment_Pct'] >= 0) & (U['Unemployment_Pct'] <= 100)].copy()
    
    print(f'\n✅ Using column "{best["hdr"]}" (scale x{best["scale"]}). Rows kept: {len(U)}')
    
    # Simple stats + plots
    x = U['Unemployment_Pct'].dropna()
    print('\n=== Summary: Unemployment Rate (%) ===')
    print(f'Count: {len(x)} | Mean: {x.mean():.2f} | Std: {x.std():.2f} | '
          f'Min: {x.min():.2f} | Median: {x.median():.2f} | Max: {x.max():.2f}')
    
    top10 = U.nlargest(10, 'Unemployment_Pct')[['Name', 'Unemployment_Pct']]
    
    # Create plots
    plt.figure(figsize=(9, 4.8), num='Histogram - Unemployment Rate')
    plt.hist(x, bins=15)
    plt.grid(True)
    plt.xlabel('Unemployment rate (%)')
    plt.ylabel('Number of states')
    plt.title('Distribution of Unemployment Rates')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'unemployment_hist.png'))
    
    plt.figure(figsize=(9, 5.6), num='Top 10 Highest Unemployment')
    plt.barh(top10['Name'], top10['Unemployment_Pct'])
    plt.grid(True)
    plt.xlabel('Unemployment rate (%)')
    plt.ylabel('State')
    plt.title('Top 10 Highest Unemployment')
    plt.xlim(0, top10['Unemployment_Pct'].max() * 1.15)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'unemployment_top10.png'))
    
    # Save cleaned data
    U.to_csv(os.path.join(out_dir, 'Unemployment_Clean.csv'), index=False)
    print('✅ Clean table and figures saved in /output')
    
    # Show plots
    plt.show()

if __name__ == '__main__':
    main()
