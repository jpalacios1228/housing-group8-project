import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from pathlib import Path

def main():
    # Configuration
    file = 'PopulationReport.xlsx'
    sheet = 'PopulationReport'
    out_dir = 'output'
    
    # Create output directory
    Path(out_dir).mkdir(exist_ok=True)
    
    # 1) Read everything as raw; detect header row
    raw = pd.read_excel(file, sheet_name=sheet, header=None)
    n_rows, n_cols = raw.shape
    
    # Helper function to convert to string safely
    def to_string(x):
        if pd.isna(x):
            return ""
        return str(x).strip()
    
    # Find header row
    hdr_row = None
    for r in range(n_rows):
        row = [to_string(raw.iloc[r, c]) for c in range(n_cols)]
        if any(cell.lower() == "name" for cell in row):
            pop_hits = sum("pop" in cell.lower() for cell in row)
            if pop_hits >= 2:
                hdr_row = r
                break
    
    # Fallback: find row with most "pop" tokens
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
        print(f'⚠️ Header row not obvious; using row {hdr_row} based on tokens.')
    
    # Build header names
    hdr = [to_string(raw.iloc[hdr_row, c]) for c in range(n_cols)]
    
    # Find last non-empty column
    last_col = None
    for c in range(n_cols-1, -1, -1):
        if hdr[c] not in ["", "NA"] and not pd.isna(hdr[c]):
            last_col = c
            break
    
    if last_col is None:
        raise ValueError('Header row appears empty.')
    
    hdr = hdr[:last_col+1]
    
    # Find data rows (start after header, end at last row with data in first 2 columns)
    data_start = hdr_row + 1
    is_data_row = [False] * n_rows
    
    for r in range(data_start, n_rows):
        c1 = raw.iloc[r, 0] if last_col >= 0 else None
        c2 = raw.iloc[r, 1] if last_col >= 1 else None
        
        def is_empty(val):
            if pd.isna(val) or val is None:
                return True
            if isinstance(val, str) and val.strip() == "":
                return True
            return False
        
        is_data_row[r] = not (is_empty(c1) and is_empty(c2))
    
    data_end = None
    for r in range(n_rows-1, data_start-1, -1):
        if is_data_row[r]:
            data_end = r
            break
    
    if data_end is None:
        raise ValueError(f'No data rows found below the detected header row ({hdr_row}).')
    
    # Extract data and create DataFrame
    data = raw.iloc[data_start:data_end+1, :last_col+1].reset_index(drop=True)
    data.columns = range(data.shape[1])
    
    # Normalize column names
    def clean_column_name(name):
        name = re.sub(r'\s+', ' ', name)  # collapse spaces
        name = re.sub(r'[^\w\. ]', '', name)  # drop odd chars
        name = re.sub(r'[^A-Za-z0-9_]', '_', name)  # replace invalid chars with underscore
        name = re.sub(r'_+', '_', name)  # collapse multiple underscores
        return name
    
    var_names = [clean_column_name(hdr[i]) for i in range(len(hdr))]
    data.columns = var_names
    
    print(f'Detected header row: {hdr_row}')
    print('Raw column names:')
    print(data.columns.tolist())
    
    # 2) Map headers to expected names
    expected = ['Name', 'Pop_1990', 'Pop_2000', 'Pop_2010', 'Pop_2020', 'Pop_2023', 'Change_2020_23']
    
    cur = data.columns.tolist()
    canon = [name.lower().replace('_', '').replace('.', '').replace(' ', '') for name in cur]
    
    def find_match(token):
        target = token.lower().replace('_', '').replace('.', '').replace(' ', '')
        for i, col in enumerate(canon):
            if target in col:
                return i
        return None
    
    idx = {}
    idx['Name'] = find_match('Name')
    idx['Pop_1990'] = find_match('Pop_1990')
    idx['Pop_2000'] = find_match('Pop_2000')
    idx['Pop_2010'] = find_match('Pop_2010')
    idx['Pop_2020'] = find_match('Pop_2020')
    idx['Pop_2023'] = find_match('Pop_2023')
    idx['Change_2020_23'] = find_match('Change_2020_23')
    
    # Build standardized DataFrame
    U_data = {}
    if idx['Name'] is not None:
        U_data['Name'] = data.iloc[:, idx['Name']].astype(str)
    if idx['Pop_1990'] is not None:
        U_data['Pop_1990'] = data.iloc[:, idx['Pop_1990']]
    if idx['Pop_2000'] is not None:
        U_data['Pop_2000'] = data.iloc[:, idx['Pop_2000']]
    if idx['Pop_2010'] is not None:
        U_data['Pop_2010'] = data.iloc[:, idx['Pop_2010']]
    if idx['Pop_2020'] is not None:
        U_data['Pop_2020'] = data.iloc[:, idx['Pop_2020']]
    if idx['Pop_2023'] is not None:
        U_data['Pop_2023'] = data.iloc[:, idx['Pop_2023']]
    if idx['Change_2020_23'] is not None:
        U_data['Change_2020_23'] = data.iloc[:, idx['Change_2020_23']]
    
    U = pd.DataFrame(U_data)
    print(f'✅ Standardized columns present: {", ".join(U.columns.tolist())}')
    
    # 3) Clean: drop empty names, numeric coercion, remove national row
    if 'Name' in U.columns:
        U = U[~U['Name'].isna() & (U['Name'] != "") & (U['Name'] != "nan")]
    
    # Convert numeric columns
    num_vars = [col for col in U.columns if col != 'Name']
    for col in num_vars:
        U[col] = pd.to_numeric(U[col], errors='coerce')
    
    if 'Name' in U.columns:
        U = U[~U['Name'].str.strip().str.lower().eq('united states')]
    
    print(f'✅ Loaded {len(U)} data rows after cleaning.')
    
    # 4) Basic summary + visuals (only if required cols exist)
    req = ['Pop_1990', 'Pop_2023']
    has_req = all(col in U.columns for col in req)
    
    if not has_req:
        print(f'Warning: Required columns missing for visuals: need Pop_1990 and Pop_2023. Available: {", ".join(U.columns.tolist())}')
    else:
        x = U['Pop_2023'].dropna()
        print('\n=== Summary: Population 2023 ===')
        print(f'Count: {len(x)} | Mean: {x.mean():.0f} | Std: {x.std():.0f} | '
              f'Min: {x.min():.0f} | Median: {x.median():.0f} | '
              f'Max: {x.max():.0f} | Sum: {x.sum():.0f}')
        
        if 'Name' in U.columns:
            sorted_df = U.sort_values('Pop_2023', ascending=False, na_position='last')
            print('Top 5 Most Populated (2023):')
            print(sorted_df['Name'].head(5).tolist())
            print('Bottom 5 Least Populated (2023):')
            print(sorted_df['Name'].tail(5).tolist())
        
        # Histogram
        plt.figure(figsize=(9, 4.8))
        plt.hist(U['Pop_2023'] / 1e6, bins='auto')
        plt.grid(True)
        plt.xlabel('Population (millions)')
        plt.ylabel('Number of States')
        plt.title('Distribution of State Populations (2023)')
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, 'pop_hist_2023.png'))
        plt.close()
        
        # Top 10 chart
        if 'Name' in U.columns:
            top_n = min(10, len(U))
            top_10 = sorted_df.head(top_n)
            
            plt.figure(figsize=(9, 5.6))
            plt.barh(range(len(top_10)), top_10['Pop_2023'] / 1e6)
            plt.yticks(range(len(top_10)), top_10['Name'])
            plt.gca().invert_yaxis()
            plt.grid(True)
            plt.xlabel('Population (millions)')
            plt.ylabel('State')
            plt.title('Top 10 Most Populated States (2023)')
            plt.tight_layout()
            plt.savefig(os.path.join(out_dir, 'top10_pop_2023.png'))
            plt.close()
        
        # Scatter plot 1990 vs 2023
        plt.figure(figsize=(9, 6.2))
        plt.scatter(U['Pop_1990'] / 1e6, U['Pop_2023'] / 1e6, s=38)
        plt.grid(True)
        plt.xlabel('Population 1990 (millions)')
        plt.ylabel('Population 2023 (millions)')
        plt.title('State Population Growth (1990 → 2023)')
        
        max_val = max(U['Pop_1990'].max(), U['Pop_2023'].max()) / 1e6 * 1.05
        plt.plot([0, max_val], [0, max_val], '--', linewidth=1, label='y = x')
        plt.xlim(0, max_val)
        plt.ylim(0, max_val)
        plt.legend(loc='upper left')
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, 'scatter_1990_vs_2023.png'))
        plt.close()
    
    # 5) Save cleaned output
    U.to_csv(os.path.join(out_dir, 'Population_Clean.csv'), index=False)
    print('✅ Clean table saved in /output')

if __name__ == '__main__':
    main()
