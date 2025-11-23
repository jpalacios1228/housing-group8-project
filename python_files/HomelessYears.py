import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import os

def main():
    """Cleans and plots Homelessness Trends (2007–2024)"""

    # ---------------------------------------------
    # 1. Load Data
    # ---------------------------------------------
    in_file = "HomelessYears.xlsx"
    out_dir = "output"

    Path(out_dir).mkdir(exist_ok=True)

    if not os.path.exists(in_file):
        raise FileNotFoundError(f'File "{in_file}" not found in working directory.')

    # Read table exactly as-is
    df = pd.read_excel(in_file)

    # Preview
    print("Data Preview:")
    print(df.head())

    # ---------------------------------------------
    # 2. Extract variables
    # ---------------------------------------------
    years = df["year"]
    counts = df["Overall Homeless"]

    # ---------------------------------------------
    # 3. Create Plot
    # ---------------------------------------------
    plt.figure(figsize=(10, 6))

    # Line with markers
    plt.plot(
        years, counts, "-o",
        linewidth=2.5,
        markersize=8,
    )

    # ---------------------------------------------
    # 4. Format Graph
    # ---------------------------------------------
    plt.grid(True)
    plt.title("Overall Homelessness in the US (2007–2024)", fontsize=14)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Total Homeless Count", fontsize=12)

    # Format y-axis with commas
    plt.ticklabel_format(style="plain", axis="y")
    plt.gca().get_yaxis().set_major_formatter(
        plt.matplotlib.ticker.FuncFormatter(lambda x, p: f"{int(x):,}")
    )

    # X-axis ticks for every year
    plt.xlim(min(years)-1, max(years)+1)
    plt.xticks(range(min(years), max(years) + 1))

    # Add annotation for 2021 dip
    if 2021 in years.values:
        idx = years[years == 2021].index[0]
        plt.text(
            2021, counts[idx],
            "  2021 Dip (Pandemic Data Issues)",
            fontsize=10,
            va="bottom"
        )

    # ---------------------------------------------
    # 5. Save Output
    # ---------------------------------------------
    out_path = os.path.join(out_dir, "Homelessness_Trend_Graph.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Graph created: {out_path}")
