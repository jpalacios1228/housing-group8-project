import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from pathlib import Path

def main():
    # Configuration
    in_file = 'PovertyReport.xlsx'
    in_sheet = 'PovertyReport'
    out_dir = 'output'
    
    # Create output directory
    Path(out_dir).mkdir(exist_ok=True)
    
    # 1) Read raw data and detect header row
    raw = pd.read_excel(in_file, sheet_name=in_sheet, header=None)
    n_rows, n_cols = raw.shape
    
    # Helper function to test emptiness
    def is_empty_cell(v):
        if pd.isna(v) or v is None:
            return True
        if isinstance(v, str) and v.strip() == "":
            return True
        return False
    
    # Find header row (first non-empty cell == "Name")
    hdr_row = None
    for r in range(n_rows):
        row = [raw.iloc[r, c] for c in range(n_cols)]
        # Find first non-empty cell in this row
        for c, val in enumerate(row):
            if not is_empty_cell(val):
                if isinstance(val, str) and val.strip().lower() == 'name':
                    hdr_row = r
                    break
        if hdr_row is not None:
            break
    
    if hdr_row is None:
        raise ValueError('Header row not found (row containing "Name").')
    
    # Build header names from hdrRow, trim trailing empties
    hdr = [raw.iloc[hdr_row, c] for c in range(n_cols)]
    
    # Find last non-empty column
    last_col = None
    for c in range(n_cols-1, -1, -1):
        if not is_empty_cell(hdr[c]):
            last_col = c
            break
    
    if last_col is None:
        raise ValueError('Header row appears empty.')
    
    hdr = hdr[:last_col+1]
    
    # Data block: from next row until last row that has anything in first two cols
    data_start = hdr_row + 1
    is_data_row = [False] * n_rows
    
    for r in range(data_start, n_rows):
        c1 = raw.iloc[r, 0] if last_col >= 0 else None
        c2 = raw.iloc[r, 1] if last_col >= 1 else None
        is_data_row[r] = not (is_empty_cell(c1) and is_empty_cell(c2))
    
    data_end = None
    for r in range(n_rows-1, data_start-1, -1):
        if is_data_row[r]:
            data_end = r
            break
    
    if data_end is None:
        raise ValueError('No data rows found beneath the header.')
    
    # Extract data and create DataFrame
    data = raw.iloc[data_start:data_end+1, :last_col+1].reset_index(drop=True)
    data.columns = range(data.shape[1])
    
    # Make valid, normalized, and UNIQUE variable names
    def clean_column_name(name, existing_names=None):
        # Convert to string and clean
        name_str = str(name) if not pd.isna(name) else f"Column_{len(existing_names)}"
        
        # Replace non-alphanumeric with underscore and collapse multiple underscores
        name_clean = re.sub(r'[^A-Za-z0-9_]', '_', name_str)
        name_clean = re.sub(r'_+', '_', name_clean)
        
        # Ensure it starts with a letter/underscore and is valid
        if name_clean and not name_clean[0].isalpha() and name_clean[0] != '_':
            name_clean = '_' + name_clean
        
        # Make unique
        if existing_names is not None:
            base_name = name_clean
            counter = 1
            while name_clean in existing_names:
                name_clean = f"{base_name}_{counter}"
                counter += 1
        
        return name_clean
    
    raw_names = []
    existing_names_set = set()
    for i, name in enumerate(hdr):
        clean_name = clean_column_name(name, existing_names_set)
        raw_names.append(clean_name)
        existing_names_set.add(clean_name)
    
    data.columns = raw_names
    
    # 2) Identify columns (robust to duplicates)
    names = data.columns.tolist()
    lnames = [name.lower() for name in names]
    
    # Name column
    name_idx = None
    for i, name in enumerate(lnames):
        if 'name' in name:
            name_idx = i
            break
    
    if name_idx is None:
        raise ValueError('Could not find "Name" column.')
    
    # All percent/lower/upper columns
    percent_idx = [i for i, name in enumerate(lnames) if 'percent' in name]
    lb_idx = [i for i, name in enumerate(lnames) if 'lower' in name]
    ub_idx = [i for i, name in enumerate(lnames) if 'upper' in name]
    
    # We need at least two percent columns
    if len(percent_idx) < 2:
        raise ValueError('Could not find two "Percent" columns.')
    
    # Sort by column position (left -> right)
    percent_idx.sort()
    lb_idx.sort()
    ub_idx.sort()
    
    # Assign first Percent = All, second Percent = Children
    idx_all_percent = percent_idx[0]
    idx_child_percent = percent_idx[1]
    
    # For each Percent, take the first LB/UB that appear to its right
    idx_all_lb = next((i for i in lb_idx if i > idx_all_percent), None)
    idx_all_ub = next((i for i in ub_idx if i > idx_all_percent), None)
    idx_ch_lb = next((i for i in lb_idx if i > idx_child_percent), None)
    idx_ch_ub = next((i for i in ub_idx if i > idx_child_percent), None)
    
    if any(x is None for x in [idx_all_lb, idx_all_ub, idx_ch_lb, idx_ch_ub]):
        raise ValueError('Could not align Lower/Upper bounds with Percent columns.')
    
    # 3) Build clean table U
    U_data = {}
    U_data['Name'] = data.iloc[:, name_idx].astype(str)
    U_data['All_Poverty_Pct'] = data.iloc[:, idx_all_percent]
    U_data['All_Lower_Bound'] = data.iloc[:, idx_all_lb]
    U_data['All_Upper_Bound'] = data.iloc[:, idx_all_ub]
    U_data['Children_Poverty_Pct'] = data.iloc[:, idx_child_percent]
    U_data['Children_Lower_Bound'] = data.iloc[:, idx_ch_lb]
    U_data['Children_Upper_Bound'] = data.iloc[:, idx_ch_ub]
    
    U = pd.DataFrame(U_data)
    
    # Drop empty-name rows
    U = U[~U['Name'].isna() & (U['Name'] != "") & (U['Name'] != "nan")]
    
    # Coerce numerics
    numeric_cols = [col for col in U.columns if col != 'Name']
    for col in numeric_cols:
        U[col] = pd.to_numeric(U[col], errors='coerce')
    
    # Remove national aggregate if present
    U = U[~U['Name'].str.strip().str.lower().eq('united states')]
    
    print(f'✅ Cleaned {len(U)} rows. Columns: {", ".join(U.columns.tolist())}')
    
    # 4) Simple stats
    x = U['All_Poverty_Pct'].dropna()
    xc = U['Children_Poverty_Pct'].dropna()
    
    print('\n=== Summary: All People in Poverty (%%, 2023) ===')
    print(f'Count: {len(x)} | Mean: {x.mean():.2f} | Std: {x.std():.2f} | '
          f'Min: {x.min():.2f} | Median: {x.median():.2f} | Max: {x.max():.2f}')
    
    print('\n=== Summary: Children (0–17) in Poverty (%%, 2023) ===')
    print(f'Count: {len(xc)} | Mean: {xc.mean():.2f} | Std: {xc.std():.2f} | '
          f'Min: {xc.min():.2f} | Median: {xc.median():.2f} | Max: {xc.max():.2f}')
    
    sorted_df = U.sort_values('All_Poverty_Pct', ascending=False, na_position='last')
    top_n = min(10, len(U))
    print('Top 10 Highest Poverty (All people, %):')
    print(sorted_df[['Name', 'All_Poverty_Pct']].head(top_n).to_string(index=False))
    
    # 5) Visuals (simple & clear)
    # Histogram: All people
    plt.figure(figsize=(9, 4.8))
    plt.hist(U['All_Poverty_Pct'], bins=15)
    plt.grid(True)
    plt.xlabel('Poverty rate (%), All people')
    plt.ylabel('Number of states')
    plt.title('Distribution of Poverty Rates (All People, 2023)')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'poverty_all_hist.png'))
    plt.close()
    
    # Histogram: Children
    plt.figure(figsize=(9, 4.8))
    plt.hist(U['Children_Poverty_Pct'], bins=15)
    plt.grid(True)
    plt.xlabel('Poverty rate (%), Children 0–17')
    plt.ylabel('Number of states')
    plt.title('Distribution of Poverty Rates (Children, 2023)')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'poverty_children_hist.png'))
    plt.close()
    
    # Barh: Top 10 (All people)
    plt.figure(figsize=(9, 5.6))
    top_10 = sorted_df.head(top_n)
    y_pos = range(len(top_10))
    plt.barh(y_pos, top_10['All_Poverty_Pct'])
    plt.yticks(y_pos, top_10['Name'])
    plt.gca().invert_yaxis()
    plt.grid(True)
    plt.xlabel('Poverty rate (%)')
    plt.ylabel('State')
    plt.title('Top 10 Highest Poverty (All People, 2023)')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'poverty_all_top10.png'))
    plt.close()
    
    # Scatter: Children vs All
    plt.figure(figsize=(9, 6.2))
    plt.scatter(U['All_Poverty_Pct'], U['Children_Poverty_Pct'], s=36)
    plt.grid(True)
    plt.xlabel('All people poverty rate (%)')
    plt.ylabel('Children 0–17 poverty rate (%)')
    plt.title('Children vs All Poverty Rates (2023)')
    
    max_val = max(U['All_Poverty_Pct'].max(), U['Children_Poverty_Pct'].max()) * 1.05
    plt.plot([0, max_val], [0, max_val], '--', label='y = x')
    plt.xlim(0, max_val)
    plt.ylim(0, max_val)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'poverty_children_vs_all_scatter.png'))
    plt.close()
    
    # 6) Save cleaned output
    U.to_csv(os.path.join(out_dir, 'Poverty_Clean.csv'), index=False)
    print('✅ Clean table and figures saved in /output')

if __name__ == '__main__':
    main()
