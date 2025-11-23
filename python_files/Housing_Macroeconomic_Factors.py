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

    if not os.path.exists(in_file):
        st.error(f'❌ File "{in_file}" not found.')
        return None, None

    try:
        df = pd.read_excel(in_file)
        st.success("📄 File loaded successfully.")
    except Exception:
        st.error("❌ Could not read Excel file — check file format.")
        return None, None

    # ---------------------------------------------------
    # 2. Data Setup
    # ---------------------------------------------------
    if "Date" not in df.columns:
        st.error('❌ Column "Date" missing from spreadsheet.')
        return None, None

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date")

    st.write("### 📊 Data Preview", df.head())

    # ---------------------------------------------------
    # 3. Plot 1: House Prices vs Mortgage Rates (Dual Axis)
    # ---------------------------------------------------
    fig1, ax1 = plt.subplots(figsize=(10, 5))

    # Left axis — House Price Index
    ax1.plot(df["Date"], df["house_price_index"], linewidth=2,
             label="House Price Index")
    ax1.set_ylabel("House Price Index (HPI)")
    ax1.set_xlabel("Date")
    ax1.grid(True)

    # Right axis — Mortgage Rate
    ax2 = ax1.twinx()
    ax2.plot(df["Date"], df["mortgage_rate"], linewidth=1.5,
             label="Mortgage Rate", linestyle="-")
    ax2.set_ylabel("Mortgage Rate (%)")

    # Combine legends
    lines = ax1.lines + ax2.lines
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc="best")

    fig1.suptitle("US Housing Market: Prices vs. Mortgage Rates", fontsize=14)

    # Save PNG for output folder
    out_path1 = os.path.join(out_dir, "HPI_vs_Mortgage.png")
    fig1.savefig(out_path1, dpi=300, bbox_inches="tight")

    # ---------------------------------------------------
    # 4. Plot 2: GDP & Employment (Two subplots)
    # ---------------------------------------------------
    fig2, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    # GDP
    axes[0].plot(df["Date"], df["gdp"], linewidth=1.5)
    axes[0].set_title("GDP Growth Index")
    axes[0].set_ylabel("GDP")
    axes[0].grid(True)

    # Employment Rate
    axes[1].plot(df["Date"], df["employment_rate"], linewidth=1.5)
    axes[1].set_title("Employment Rate (%)")
    axes[1].set_ylabel("Employment %")
    axes[1].set_xlabel("Date")
    axes[1].grid(True)

    fig2.tight_layout()

    out_path2 = os.path.join(out_dir, "Economic_Health.png")
    fig2.savefig(out_path2, dpi=300, bbox_inches="tight")

    st.success("✅ Housing Macroeconomic Factors analysis completed.")

    # ---------------------------------------------------
    # 5. Return figures for Streamlit
    # ---------------------------------------------------
    return fig1, fig2
