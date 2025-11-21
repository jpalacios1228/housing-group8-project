import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import os

def main():
    st.header("🏡 Housing Dataset Analysis")

    # ---------------------------------------------------------
    # 1) Load dataset
    # ---------------------------------------------------------
    file = "Housing.xlsx"
    sheet = "in"

    st.subheader("📂 Loading Dataset")
    try:
        T = pd.read_excel(file, sheet_name=sheet)
        st.success(f"Loaded: {file}")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return

    # ---------------------------------------------------------
    # 2) Handle missing or invalid values
    # ---------------------------------------------------------
    st.subheader("🔍 Missing Value Analysis")
    st.write(T.isna().sum())

    # Convert numeric columns to floats
    numVars = ['price','area','bedrooms','bathrooms','stories','parking']

    for col in numVars:
        if T[col].dtype == object:  # convert string-like columns
            T[col] = pd.to_numeric(T[col], errors='coerce')

    # Drop rows missing key data
    Tclean = T.dropna(subset=['price', 'area'])
    st.success(f"Cleaned dataset: {len(Tclean)} rows remaining.")

    # ---------------------------------------------------------
    # 3) Summary statistics for Price
    # ---------------------------------------------------------
    st.subheader("📊 Summary Statistics — Price")
    x = Tclean['price']

    st.write({
        "Count": int(x.count()),
        "Mean": float(x.mean()),
        "Std": float(x.std()),
        "Min": float(x.min()),
        "Median": float(x.median()),
        "Max": float(x.max()),
        "Sum": float(x.sum())
    })

    # ---------------------------------------------------------
    # 4) Most common categorical features
    # ---------------------------------------------------------
    st.subheader("🏷 Most Common Features")

    st.write("**Most common furnishing status:**", Tclean["furnishingstatus"].mode()[0])
    st.write("**Most common air conditioning:**", Tclean["airconditioning"].mode()[0])
    st.write("**Most common basement presence:**", Tclean["basement"].mode()[0])

    # ---------------------------------------------------------
    # 5) Visualizations
    # ---------------------------------------------------------
    st.subheader("📈 Visualizations")

    # --- Histogram: Price ---
    fig, ax = plt.subplots(figsize=(7,5))
    ax.hist(Tclean["price"], bins=20)
    ax.set_xlabel("Price")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of House Prices")
    ax.grid(True)
    st.pyplot(fig)

    # --- Scatter: Area vs Price ---
    fig, ax = plt.subplots(figsize=(7,5))
    ax.scatter(Tclean["area"], Tclean["price"])
    ax.set_xlabel("Area")
    ax.set_ylabel("Price")
    ax.set_title("House Price vs Area")
    ax.grid(True)
    st.pyplot(fig)

    # --- Boxplot: Price by Furnishing ---
    fig, ax = plt.subplots(figsize=(7,5))
    Tclean.boxplot(column="price", by="furnishingstatus", ax=ax)
    ax.set_title("Price by Furnishing Status")
    ax.set_xlabel("Furnishing Status")
    ax.set_ylabel("Price")
    plt.suptitle("")  # remove default pandas title
    ax.grid(True)
    st.pyplot(fig)

    # --- Bar chart: Bedrooms ---
    bedStats = Tclean.groupby("bedrooms")["price"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(7,5))
    ax.bar(bedStats["bedrooms"], bedStats["price"])
    ax.set_xlabel("Bedrooms")
    ax.set_ylabel("Average Price")
    ax.set_title("Average Price by Number of Bedrooms")
    ax.grid(True)
    st.pyplot(fig)

    # --- Pie chart: Furnishing ---
    furn_counts = Tclean["furnishingstatus"].value_counts()

    fig, ax = plt.subplots(figsize=(6,6))
    ax.pie(furn_counts, labels=furn_counts.index, autopct="%1.1f%%")
    ax.set_title("Furnishing Status Distribution")
    st.pyplot(fig)

    # --- Bar chart: Parking Spots ---
    parkStats = Tclean.groupby("parking")["price"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(7,5))
    ax.bar(parkStats["parking"], parkStats["price"])
    ax.set_xlabel("Parking Spots")
    ax.set_ylabel("Average Price")
    ax.set_title("Average Price by Number of Parking Spots")
    ax.grid(True)
    st.pyplot(fig)

    # ---------------------------------------------------------
    # 6) Save output
    # ---------------------------------------------------------
    st.subheader("💾 Saving Output")

    os.makedirs("output", exist_ok=True)
    Tclean.to_csv("output/Housing_Clean.csv", index=False)

    st.success("Cleaned dataset saved to output/Housing_Clean.csv")

    st.success("🏁 Housing analysis complete!")

if __name__ == "__main__":
    main()
