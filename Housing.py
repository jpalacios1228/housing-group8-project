import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------
# 1) Load dataset
# ---------------------------------------------------------
file = "Housing.xlsx"
sheet = "in"

T = pd.read_excel(file, sheet_name=sheet)

# ---------------------------------------------------------
# 2) Handle missing or invalid values
# ---------------------------------------------------------
print("Missing values per column:")
print(T.isna().sum())

# Convert numeric columns to float if they came in as strings
numVars = ['price','area','bedrooms','bathrooms','stories','parking']

for col in numVars:
    if T[col].dtype == object:     # string-like
        T[col] = pd.to_numeric(T[col], errors='coerce')

# Drop rows missing key variables
Tclean = T.dropna(subset=['price', 'area'])
print(f"✅ Cleaned dataset: {len(Tclean)} rows remaining.")

# ---------------------------------------------------------
# 3) Summary statistics for Price
# ---------------------------------------------------------
x = Tclean['price']

print("\n=== Summary Statistics for Price ===")
print(f"Count: {x.count()}")
print(f"Mean: {x.mean():.2f}")
print(f"Std: {x.std():.2f}")
print(f"Min: {x.min():.2f}")
print(f"Median: {x.median():.2f}")
print(f"Max: {x.max():.2f}")
print(f"Sum: {x.sum():.2f}")

# ---------------------------------------------------------
# 4) Most common features
# ---------------------------------------------------------
print("\n=== Most Common Features ===")
print("Most common furnishing status:", Tclean["furnishingstatus"].mode()[0])
print("Most common air conditioning:", Tclean["airconditioning"].mode()[0])
print("Most common basement presence:", Tclean["basement"].mode()[0])

# ---------------------------------------------------------
# 5) Visualizations
# ---------------------------------------------------------
plt.figure(figsize=(7,5))
plt.hist(Tclean["price"], bins=20)
plt.xlabel("Price")
plt.ylabel("Count")
plt.title("Distribution of House Prices")
plt.grid(True)
plt.show()

# Scatter: Area vs Price
plt.figure(figsize=(7,5))
plt.scatter(Tclean["area"], Tclean["price"])
plt.xlabel("Area")
plt.ylabel("Price")
plt.title("House Price vs Area")
plt.grid(True)
plt.show()

# Boxplot: Price by Furnishing
plt.figure(figsize=(7,5))
Tclean.boxplot(column="price", by="furnishingstatus")
plt.title("Price by Furnishing Status")
plt.suptitle("")  # remove default pandas title
plt.xlabel("Furnishing Status")
plt.ylabel("Price")
plt.grid(True)
plt.show()

# Bar chart: Average Price by Bedrooms
bedStats = Tclean.groupby("bedrooms")["price"].mean().reset_index()

plt.figure(figsize=(7,5))
plt.bar(bedStats["bedrooms"], bedStats["price"])
plt.xlabel("Bedrooms")
plt.ylabel("Average Price")
plt.title("Average Price by Number of Bedrooms")
plt.grid(True)
plt.show()

# Pie chart: Furnishing Status
furn_counts = Tclean["furnishingstatus"].value_counts()

plt.figure(figsize=(6,6))
plt.pie(furn_counts, labels=furn_counts.index, autopct="%1.1f%%")
plt.title("Furnishing Status Distribution")
plt.show()

# Bar chart: Parking vs Avg Price
parkStats = Tclean.groupby("parking")["price"].mean().reset_index()

plt.figure(figsize=(7,5))
plt.bar(parkStats["parking"], parkStats["price"])
plt.xlabel("Parking Spots")
plt.ylabel("Average Price")
plt.title("Average Price by Number of Parking Spots")
plt.grid(True)
plt.show()

# ---------------------------------------------------------
# 6) Save output
# ---------------------------------------------------------
os.makedirs("output", exist_ok=True)
Tclean.to_csv("output/Housing_Clean.csv", index=False)

print("Clean dataset saved to output/Housing_Clean.csv")
