import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import os
import streamlit as st


def main():
    """Housing Macroeconomic Factors Analysis (Streamlit-compatible)"""

    # ---------------------------------------------------
    # 1. Setup and Load
    # ---------------------------------------------------
    in_file = "Housing_Macroeconomic_Factors_US(good).xlsx"
    out_dir = "output"

    Path(out_dir).mkdir(exist_ok=True)

    st.title("🏡 US Housing Macroeconomic Factors Dashboard")

    if not os.path.exists(in_file):
        st.error(f'❌ File "{in_file}" not found in the working directory.')
        return

    # Load Excel
    try:
        df = pd.read_excel(in_file)
        st.success("📄 File loaded successfully.")
    except Exception as e:
        st.error(f"❌ Could not read Excel file: {e}")
        return

    # ---------------------------------------------------
    # 2. Validate Required Columns
    # ---------------------------------------------------
    required_cols = [
        "Date", "house_price_index", "mortgage_rate",
        "gdp", "employment_rate"
    ]

    for col in required_cols:
        if col not in df.columns:
            st.error(f'❌ Required column "{col}" is missing from spreadsheet.')
            return

    # Clean & Sort
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date")

    st.write("### 📊 Data Preview")
    st.dataframe(df.head())

    # ---------------------------------------------------
    # 3. Plot 1: House Prices vs Mortgage Rates (Dual Axis)
    # ---------------------------------------------------
    st.subheader("📈 House Price Index vs Mortgage Rates")

    fig1, ax1 = plt.subplots(figsize=(10, 5))

    ax1.plot(df["Date"], df["house_price_index"], linewidth=2,
             label="House Price Index")
    ax1.set_ylabel("House Price Index (HPI)")
    ax1.set_xlabel("Date")
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.plot(df["Date"], df["mortgage_rate"], linewidth=1.5,
             label="Mortgage Rate", linestyle="-")
    ax2.set_ylabel("Mortgage Rate (%)")

    lines = ax1.lines + ax2.lines
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc="best")

    fig1.suptitle("US Housing Market: Prices vs. Mortgage Rates", fontsize=14)

    st.pyplot(fig1)

    # Save image
    fig1.savefig(os.path.join(out_dir, "HPI_vs_Mortgage.png"),
                 dpi=300, bbox_inches="tight")

    # ---------------------------------------------------
    # 4. Plot 2: GDP & Employment (Two subplots)
    # ---------------------------------------------------
    st.subheader("📉 GDP Index and Employment Trend")

    fig2, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    axes[0].plot(df["Date"], df["gdp"], linewidth=1.5)
    axes[0].set_title("GDP Growth Index")
    axes[0].set_ylabel("GDP")
    axes[0].grid(True)

    axes[1].plot(df["Date"], df["employment_rate"], linewidth=1.5)
    axes[1].set_title("Employment Rate (%)")
    axes[1].set_ylabel("Employment %")
    axes[1].set_xlabel("Date")
    axes[1].grid(True)

    fig2.tight_layout()

    st.pyplot(fig2)

    fig2.savefig(os.path.join(out_dir, "Economic_Health.png"),
                 dpi=300, bbox_inches="tight")

    # ---------------------------------------------------
    # 5. Complete
    # ---------------------------------------------------
    st.success("✅ Housing Macroeconomic Factors analysis completed.")
