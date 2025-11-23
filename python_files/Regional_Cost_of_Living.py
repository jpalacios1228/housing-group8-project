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

    st.title("📍 Regional Cost of Living Analysis")

    if not os.path.exists(in_file):
        st.error(f'❌ File "{in_file}" not found in the working directory.')
        return

    # Load Excel File
    try:
        df = pd.read_excel(in_file)
        st.success("📄 File loaded successfully.")
    except Exception as e:
        st.error(f'❌ Could not read file: {e}')
        return

    # ---------------------------------------------------
    # 2. Validate Required Columns
    # ---------------------------------------------------
    required_cols = [
        "Year",
        "Average_Monthly_Income",
        "Cost_of_Living",
        "Housing_Cost_Percentage",
        "Tax_Rate",
        "Healthcare_Cost_Percentage",
        "Education_Cost_Percentage",
        "Transportation_Cost_Percentage"
    ]

    for col in required_cols:
        if col not in df.columns:
            st.error(f'❌ Required column "{col}" missing from spreadsheet.')
            return

    # ---------------------------------------------------
    # Clean the Year Column
    # ---------------------------------------------------
    df = df[df["Year"] > 1900]

    # ---------------------------------------------------
    # 3. Aggregate Data (Mean by Year)
    # ---------------------------------------------------
    vars_to_avg = required_cols[1:]  # all except "Year"

    df_avg = df.groupby("Year")[vars_to_avg].mean().reset_index()

    st.write("### 📊 Aggregated Yearly Averages")
    st.dataframe(df_avg.head())

    # ---------------------------------------------------
    # 4. Visualization 1: Income vs Cost
    # ---------------------------------------------------
    st.subheader("💵 Income vs Cost of Living Trends")

    years = df_avg["Year"]
    income = df_avg["Average_Monthly_Income"]
    cost = df_avg["Cost_of_Living"]

    fig1, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(years, income, "-o", linewidth=2, label="Average Monthly Income")
    ax1.plot(years, cost, "-x", linewidth=2, label="Cost of Living")

    ax1.set_title("Average Trends: Income vs Cost of Living")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Amount (USD)")
    ax1.grid(True)
    ax1.legend(loc="best")

    st.pyplot(fig1)

    fig1.savefig(
        os.path.join(out_dir, "Income_vs_Cost_Trend.png"),
        dpi=300,
        bbox_inches="tight"
    )

    # ---------------------------------------------------
    # 5. Visualization 2: Stacked Cost Breakdown
    # ---------------------------------------------------
    st.subheader("📦 Cost of Living Breakdown (Stacked %)")

    fig2, ax2 = plt.subplots(figsize=(12, 6))

    breakdown_cols = [
        "Housing_Cost_Percentage",
        "Tax_Rate",
        "Healthcare_Cost_Percentage",
        "Education_Cost_Percentage",
        "Transportation_Cost_Percentage"
    ]

    legend_names = ["Housing", "Tax", "Healthcare", "Education", "Transportation"]

    bottom = None
    for i, col in enumerate(breakdown_cols):
        ax2.bar(
            years,
            df_avg[col],
            bottom=bottom,
            label=legend_names[i]
        )
        bottom = df_avg[col] if bottom is None else bottom + df_avg[col]

    ax2.set_title("Average Cost of Living Breakdown by Year")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Percentage of Income (%)")
    ax2.grid(True)
    ax2.legend(loc="center left", bbox_to_anchor=(1, 0.5))

    st.pyplot(fig2)

    fig2.savefig(
        os.path.join(out_dir, "Cost_Breakdown_Stacked.png"),
        dpi=300,
        bbox_inches="tight"
    )

    # ---------------------------------------------------
    # 6. Done
    # ---------------------------------------------------
    st.success("✅ Regional Cost of Living analysis completed successfully.")
