import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import os
import streamlit as st


def main():
    """Regional Cost of Living Analysis — Streamlit Compatible"""

    # ---------------------------------------------------
    # 1. Setup and Load
    # ---------------------------------------------------
    in_file = "Regional Cost of Living.xlsx"
    out_dir = "output"

    Path(out_dir).mkdir(exist_ok=True)

    if not os.path.exists(in_file):
        st.error(f'❌ File "{in_file}" not found in the working directory.')
        return None, None

    try:
        df = pd.read_excel(in_file)
        st.success("📄 File loaded successfully.")
    except Exception:
        st.error(f'❌ Could not read file. Ensure "{in_file}" is valid.')
        return None, None

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

    df_avg = df.groupby("Year")[vars_to_average].mean().reset_index()
    st.write("### 📊 Aggregated Data (Yearly Means)", df_avg.head())

    # ---------------------------------------------------
    # 3. Visualization 1: Income vs Cost
    # ---------------------------------------------------
    years = df_avg["Year"]
    income = df_avg["Average_Monthly_Income"]
    cost = df_avg["Cost_of_Living"]

    fig1, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(years, income, "-o", linewidth=2, label="Avg Monthly Income")
    ax1.plot(years, cost, "-x", linewidth=2, label="Cost of Living")

    ax1.set_title("Average Trends: Income vs. Cost of Living")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Amount (USD)")
    ax1.grid(True)
    ax1.legend(loc="best")

    out_path1 = os.path.join(out_dir, "Income_vs_Cost_Trend.png")
    fig1.savefig(out_path1, dpi=300, bbox_inches="tight")

    # ---------------------------------------------------
    # 4. Visualization 2: Stacked Percentage Breakdown
    # ---------------------------------------------------
    fig2, ax2 = plt.subplots(figsize=(12, 6))

    percentage_df = df_avg[
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

    bottom = None

    for i, col in enumerate(percentage_df.columns):
        ax2.bar(years, percentage_df[col], bottom=bottom, label=legend_names[i])
        bottom = percentage_df[col] if bottom is None else bottom + percentage_df[col]

    ax2.set_title("Average Cost of Living Breakdown by Year")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Percentage of Income (%)")
    ax2.grid(True)
    ax2.legend(loc="center left", bbox_to_anchor=(1, 0.5))

    out_path2 = os.path.join(out_dir, "Cost_Breakdown_Stacked.png")
    fig2.savefig(out_path2, dpi=300, bbox_inches="tight")

    st.success("✅ Regional Cost of Living plots completed.")

    return fig1, fig2
