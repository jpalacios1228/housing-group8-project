import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import os

def main():
    """Regional Cost of Living Analysis — Python version of MATLAB script"""

    # ---------------------------------------------------
    # 1. Setup and Load
    # ---------------------------------------------------
    in_file = "Regional Cost of Living.xlsx"
    out_dir = "output"

    Path(out_dir).mkdir(exist_ok=True)

    if not os.path.exists(in_file):
        raise FileNotFoundError(
            f'Could not read file. Make sure "{in_file}" is in the working directory.'
        )

    try:
        df = pd.read_excel(in_file)
        print("✅ File loaded successfully.")
    except Exception as e:
        raise RuntimeError(
            f'Could not read file. Ensure "{in_file}" exists and is a valid Excel file.'
        ) from e

    # ---------------------------------------------------
    # Clean: Remove invalid years
    # ---------------------------------------------------
    if "Year" in df.columns:
        df = df[df["Year"] > 1900]

    # ---------------------------------------------------
    # 2. Aggregate Data (Mean by Year)
    # ---------------------------------------------------
    vars_to_average = [
        "Average_Monthly_Income",
        "Cost_of_Living",
        "Housing_Cost_Percentage",
        "Tax_Rate",
        "Healthcare_Cost_Percentage",
        "Education_Cost_Percentage",
        "Transportation_Cost_Percentage"
    ]

    # Group by year and compute mean
    df_avg = df.groupby("Year")[vars_to_average].mean().reset_index()

    print("Data aggregated by Year.")

    # ---------------------------------------------------
    # 3. Visualization 1: Income vs Cost
    # ---------------------------------------------------
    years = df_avg["Year"]
    income = df_avg["Average_Monthly_Income"]
    cost = df_avg["Cost_of_Living"]

    plt.figure(figsize=(12, 6))

    plt.plot(years, income, "-o", linewidth=2, label="Avg Monthly Income")
    plt.plot(years, cost, "-x", linewidth=2, label="Cost of Living")

    plt.grid(True)
    plt.title("Average Trends: Income vs. Cost of Living")
    plt.xlabel("Year")
    plt.ylabel("Amount (USD)")
    plt.legend(loc="best")

    out_path1 = os.path.join(out_dir, "Income_vs_Cost_Trend.png")
    plt.savefig(out_path1, dpi=300, bbox_inches="tight")
    plt.close()

    # ---------------------------------------------------
    # 4. Visualization 2: Stacked Percentage Breakdown
    # ---------------------------------------------------
    percentage_cols = df_avg[
        [
            "Housing_Cost_Percentage",
            "Tax_Rate",
            "Healthcare_Cost_Percentage",
            "Education_Cost_Percentage",
            "Transportation_Cost_Percentage"
        ]
    ]

    legend_names = [
        "Housing",
        "Tax",
        "Healthcare",
        "Education",
        "Transportation"
    ]

    plt.figure(figsize=(12, 6))

    plt.bar(years, percentage_cols.values, stacked=True)

    plt.grid(True)
    plt.title("Average Cost of Living Breakdown by Year")
    plt.xlabel("Year")
    plt.ylabel("Percentage of Income (%)")
    plt.legend(legend_names, loc="center left", bbox_to_anchor=(1, 0.5))

    out_path2 = os.path.join(out_dir, "Cost_Breakdown_Stacked.png")
    plt.savefig(out_path2, dpi=300, bbox_inches="tight")
    plt.close()

    print("✅ Analysis complete. Graphs saved in 'output' folder.")
