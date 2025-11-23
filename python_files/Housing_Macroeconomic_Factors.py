import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import os

def main():
    """Housing Macroeconomic Factors Analysis (Python version of MATLAB script)"""

    # ---------------------------------------------------
    # 1. Setup and Load
    # ---------------------------------------------------
    in_file = "Housing_Macroeconomic_Factors_US(good).xlsx"
    out_dir = "output"

    Path(out_dir).mkdir(exist_ok=True)

    if not os.path.exists(in_file):
        raise FileNotFoundError(
            f'Could not read file. Make sure "{in_file}" is in the working folder.'
        )

    try:
        df = pd.read_excel(in_file)
        print("✅ File loaded successfully.")
    except Exception as e:
        raise RuntimeError(
            f'Could not read file. Ensure "{in_file}" exists and is a valid Excel file.'
        ) from e

    # ---------------------------------------------------
    # 2. Data Setup
    # ---------------------------------------------------
    if "Date" not in df.columns:
        raise KeyError('This file does not appear to contain a "Date" column.')

    # Convert Date column to datetime
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Drop invalid dates
    df = df.dropna(subset=["Date"])

    # Sort rows by Date
    df = df.sort_values("Date")

    # ---------------------------------------------------
    # 3. Plot 1: House Prices vs Mortgage Rates (Dual Axis)
    # ---------------------------------------------------
    plt.figure(figsize=(10, 5))

    # Left axis: House Price Index
    ax1 = plt.gca()
    ax1.plot(df["Date"], df["house_price_index"], linewidth=2, label="House Price Index")
    ax1.set_ylabel("House Price Index (HPI)")
    ax1.set_xlabel("Date")
    ax1.tick_params(axis="y")

    # Right axis: Mortgage Rate
    ax2 = ax1.twinx()
    ax2.plot(df["Date"], df["mortgage_rate"], linewidth=1.5, label="Mortgage Rate", linestyle="-")
    ax2.set_ylabel("Mortgage Rate (%)")
    ax2.tick_params(axis="y")

    plt.title("US Housing Market: Prices vs. Mortgage Rates")
    plt.grid(True)

    # Unified legend
    lines = ax1.lines + ax2.lines
    labels = [line.get_label() for line in lines]
    plt.legend(lines, labels, loc="best")

    # Save plot
    out_path1 = os.path.join(out_dir, "HPI_vs_Mortgage.png")
    plt.savefig(out_path1, dpi=300, bbox_inches="tight")
    plt.close()

    # ---------------------------------------------------
    # 4. Plot 2: GDP & Employment (Subplots)
    # ---------------------------------------------------
    plt.figure(figsize=(10, 6))

    # GDP subplot
    plt.subplot(2, 1, 1)
    plt.plot(df["Date"], df["gdp"], linewidth=1.5)
    plt.title("GDP Growth Index")
    plt.ylabel("GDP")
    plt.grid(True)

    # Employment subplot
    plt.subplot(2, 1, 2)
    plt.plot(df["Date"], df["employment_rate"], linewidth=1.5)
    plt.title("Employment Rate (%)")
    plt.ylabel("Employment %")
    plt.xlabel("Date")
    plt.grid(True)

    # Save plot
    out_path2 = os.path.join(out_dir, "Economic_Health.png")
    plt.savefig(out_path2, dpi=300, bbox_inches="tight")
    plt.close()

    print("✅ Analysis complete. Graphs saved in the 'output' folder.")
