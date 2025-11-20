import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import streamlit as st

# =========================================================
# 1) Function: Load and clean dataset
# =========================================================
def load_data():
    file = "Annual_Macroeconomic_Factors.xlsx"
    sheet = "in"

    # Load excel file
    T = pd.read_excel(file, sheet_name=sheet)

    # Ensure Date is datetime
    if not np.issubdtype(T["Date"].dtype, np.datetime64):
        try:
            T["Date"] = pd.to_datetime(T["Date"])
        except:
            T["Date"] = pd.to_datetime(T["Date"], format="%Y-%m-%d")

    # Clean numeric variables
    numVars = [c for c in T.columns if c != "Date"]
    for col in numVars:
        if T[col].dtype == object:
            T[col] = pd.to_numeric(T[col], errors="coerce")

    # Remove rows where all numeric values are missing
    allNumMissing = T[numVars].isna().all(axis=1)
    Tclean = T[~allNumMissing].copy()

    # Add decade column
    Tclean["Decade"] = (Tclean["Date"].dt.year // 10) * 10

    # Save cleaned data
    os.makedirs("output", exist_ok=True)
    Tclean.to_csv("output/Annual_Macro_Clean.csv", index=False)

    return Tclean


# =========================================================
# 2) Function: Make Streamlit plots
# =========================================================
def make_plots(Tclean):
    st.subheader("📈 Annual Macroeconomic Trends")

    # --- House Price Index ---
    fig, ax = plt.subplots(figsize=(7,4))
    ax.plot(Tclean["Date"], Tclean["House_Price_Index"])
    ax.set_xlabel("Year")
    ax.set_ylabel("Index")
    ax.set_title("House Price Index")
    ax.grid(True)
    st.pyplot(fig)

    # --- Mortgage Rate ---
    fig, ax = plt.subplots(figsize=(7,4))
    ax.plot(Tclean["Date"], Tclean["Mortgage_Rate"])
    ax.set_xlabel("Year")
    ax.set_ylabel("Percent")
    ax.set_title("Mortgage Rate")
    ax.grid(True)
    st.pyplot(fig)

    # --- Unemployment Rate ---
    fig, ax = plt.subplots(figsize=(7,4))
    ax.plot(Tclean["Date"], Tclean["Unemployment_Rate"])
    ax.set_xlabel("Year")
    ax.set_ylabel("Percent")
    ax.set_title("Unemployment Rate")
    ax.grid(True)
    st.pyplot(fig)

    # --- Real Disposable Income ---
    fig, ax = plt.subplots(figsize=(7,4))
    ax.plot(Tclean["Date"], Tclean["Real_Disposable_Income"])
    ax.set_xlabel("Year")
    ax.set_ylabel("Real $")
    ax.set_title("Real Disposable Income")
    ax.grid(True)
    st.pyplot(fig)

    # --- Histogram ---
    fig, ax = plt.subplots(figsize=(7,4))
    ax.hist(Tclean["Mortgage_Rate"], bins=15)
    ax.set_xlabel("Mortgage Rate (%)")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Mortgage Rates")
    ax.grid(True)
    st.pyplot(fig)

    # --- Decadal Summary ---
    decTbl = (
        Tclean.groupby("Decade")[["Mortgage_Rate", "Unemployment_Rate"]]
        .mean()
        .reset_index()
        .rename(columns={
            "Mortgage_Rate": "Avg_Mortgage_Rate",
            "Unemployment_Rate": "Avg_Unemployment_Rate"
        })
    )

    # Bar charts
    fig, ax = plt.subplots(figsize=(7,4))
    ax.bar(decTbl["Decade"], decTbl["Avg_Mortgage_Rate"])
    ax.set_xlabel("Decade")
    ax.set_ylabel("Avg Mortgage Rate (%)")
    ax.set_title("Avg Mortgage Rate by Decade")
    ax.grid(True)
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(7,4))
    ax.bar(decTbl["Decade"], decTbl["Avg_Unemployment_Rate"])
    ax.set_xlabel("Decade")
    ax.set_ylabel("Avg Unemployment (%)")
    ax.set_title("Avg Unemployment Rate by Decade")
    ax.grid(True)
    st.pyplot(fig)

    return decTbl
