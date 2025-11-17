import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------
# 1) Load dataset
# ---------------------------------------------------------
file = "Annual_Macroeconomic_Factors.xlsx"
sheet = "in"

#T = pd.read_excel(file, sheet_name=sheet)
import os

# Use relative path that works in Streamlit Cloud
file_path = "data/MacroFactors.xlsx"
if os.path.exists(file_path):
    T = pd.read_excel(file_path, sheet_name=sheet)
else:
    # Fallback for different path structures
    file_path = "../data/MacroFactors.xlsx"
    T = pd.read_excel(file_path, sheet_name=sheet) 

# Ensure Date is datetime
if not np.issubdtype(T["Date"].dtype, np.datetime64):
    try:
        T["Date"] = pd.to_datetime(T["Date"])
    except:
        T["Date"] = pd.to_datetime(T["Date"], format="%Y-%m-%d")

# ---------------------------------------------------------
# 2) Handle missing/invalid values
# ---------------------------------------------------------
numVars = [c for c in T.columns if c != "Date"]

# Convert string-like numeric fields
for col in numVars:
    if T[col].dtype == object:
        T[col] = pd.to_numeric(T[col], errors="coerce")

# Drop rows where all numerical variables are missing
allNumMissing = T[numVars].isna().all(axis=1)
Tclean = T[~allNumMissing].copy()

# ---------------------------------------------------------
# 3) Summary statistics
# ---------------------------------------------------------
varsForStats = [
    "House_Price_Index",
    "Mortgage_Rate",
    "Unemployment_Rate",
    "Real_Disposable_Income",
    "Real_GDP"
]

print("=== Summary Statistics (ignoring missing) ===")

for v in varsForStats:
    x = Tclean[v].dropna()
    if len(x) == 0:
        continue

    print(f"\nVariable: {v}")
    print(f"  Count: {x.count()}")
    print(f"  Mean: {x.mean():.4f}")
    print(f"  Std:  {x.std():.4f}")
    print(f"  Min:  {x.min():.4f}")
    print(f"  Med:  {x.median():.4f}")
    print(f"  Max:  {x.max():.4f}")
    print(f"  Sum:  {x.sum():.4f}")

# ---------------------------------------------------------
# 4) Decadal grouping
# ---------------------------------------------------------
Tclean["Decade"] = (Tclean["Date"].dt.year // 10) * 10

decTbl = (
    Tclean.groupby("Decade")[["Mortgage_Rate", "Unemployment_Rate"]]
    .mean()
    .reset_index()
    .rename(columns={
        "Mortgage_Rate": "Avg_Mortgage_Rate",
        "Unemployment_Rate": "Avg_Unemployment_Rate"
    })
)

# ---------------------------------------------------------
# 5) Visualizations
# ---------------------------------------------------------
plt.figure(figsize=(7,4))
plt.plot(Tclean["Date"], Tclean["House_Price_Index"])
plt.grid(True)
plt.xlabel("Year")
plt.ylabel("Index")
plt.title("House Price Index over Time")
plt.show()

plt.figure(figsize=(7,4))
plt.plot(Tclean["Date"], Tclean["Mortgage_Rate"])
plt.grid(True)
plt.xlabel("Year")
plt.ylabel("Percent")
plt.title("Mortgage Rate over Time")
plt.show()

plt.figure(figsize=(7,4))
plt.plot(Tclean["Date"], Tclean["Unemployment_Rate"])
plt.grid(True)
plt.xlabel("Year")
plt.ylabel("Percent")
plt.title("Unemployment Rate over Time")
plt.show()

plt.figure(figsize=(7,4))
plt.plot(Tclean["Date"], Tclean["Real_Disposable_Income"])
plt.grid(True)
plt.xlabel("Year")
plt.ylabel("Real Dollars")
plt.title("Real Disposable Income over Time")
plt.show()

# --- Histogram ---
plt.figure(figsize=(7,4))
plt.hist(Tclean["Mortgage_Rate"], bins=15)
plt.grid(True)
plt.xlabel("Mortgage Rate (%)")
plt.ylabel("Count")
plt.title("Distribution of Mortgage Rates")
plt.show()

# --- Bar: Decadal Avg Mortgage Rate ---
plt.figure(figsize=(7,4))
plt.bar(decTbl["Decade"], decTbl["Avg_Mortgage_Rate"])
plt.grid(True)
plt.xlabel("Decade")
plt.ylabel("Avg Mortgage Rate (%)")
plt.title("Average Mortgage Rate by Decade")
plt.show()

# --- Bar: Decadal Avg Unemployment Rate ---
plt.figure(figsize=(7,4))
plt.bar(decTbl["Decade"], decTbl["Avg_Unemployment_Rate"])
plt.grid(True)
plt.xlabel("Decade")
plt.ylabel("Avg Unemployment Rate (%)")
plt.title("Average Unemployment Rate by Decade")
plt.show()

# ---------------------------------------------------------
# 6) Save cleaned outputs
# ---------------------------------------------------------
os.makedirs("output", exist_ok=True)

Tclean.to_csv("output/Annual_Macro_Clean.csv", index=False)
decTbl.to_csv("output/Annual_Macro_Decadal_Summary.csv", index=False)

print("Done. Clean CSV and summaries saved in /output")
