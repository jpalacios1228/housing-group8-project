import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import os
import streamlit as st  


def main():
    """Streamlit version — cleans and plots Homelessness Trends (2007–2024)."""

    st.header("🏠 Homelessness Trends in the US (2007–2024)")

    # ---------------------------------------------
    # 1. Load Data
    # ---------------------------------------------
    in_file = "HomelessYears.xlsx"
    out_dir = "output"

    Path(out_dir).mkdir(exist_ok=True)

    st.subheader("📂 Loading & Previewing Data")

    if not os.path.exists(in_file):
        st.error(f'❌ File "{in_file}" not found in working directory.')
        return

    try:
        df = pd.read_excel(in_file)
        st.success("Data loaded successfully.")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return

    # Show sample of the data
    st.write("### 🔎 Preview of Dataset")
    st.dataframe(df.head())

    # ---------------------------------------------
    # 2. Extract variables
    # ---------------------------------------------
    years = df["year"]
    counts = df["Overall Homeless"]

    # ---------------------------------------------
    # 3. Create Plot
    # ---------------------------------------------
    st.subheader("📈 Homelessness Trend Over Time")

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(years, counts, "-o", linewidth=2.5, markersize=8)

    # Styling
    ax.grid(True)
    ax.set_title("Overall Homelessness in the US (2007–2024)", fontsize=14)
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Total Homeless Count", fontsize=12)

    # Format y-axis commas
    ax.ticklabel_format(style="plain", axis="y")
    ax.get_yaxis().set_major_formatter(
        plt.matplotlib.ticker.FuncFormatter(lambda x, p: f"{int(x):,}")
    )

    # Year ticks
    ax.set_xlim(min(years) - 1, max(years) + 1)
    ax.set_xticks(range(min(years), max(years) + 1))

    # Annotate 2021 dip
    if 2021 in years.values:
        idx = years[years == 2021].index[0]
        ax.text(
            2021, counts[idx],
            "  2021 Dip (Pandemic Data Issues)",
            fontsize=10,
            va="bottom"
        )

    # Display figure in Streamlit
    st.pyplot(fig)

    # ---------------------------------------------
    # 4. Save output image
    # ---------------------------------------------
    out_path = os.path.join(out_dir, "Homelessness_Trend_Graph.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")

    st.success(f"📁 Graph saved to: {out_path}")

    return fig
