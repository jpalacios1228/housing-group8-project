import streamlit as st
import os
import sys
import traceback

# ──────────────────────────────────────────────
# STREAMLIT PAGE SETUP
# ──────────────────────────────────────────────
st.set_page_config(layout="wide")
st.title("📊 Housing Market Analysis — Debug & Run")

# ──────────────────────────────────────────────
# ADD python_files/ TO PATH
# ──────────────────────────────────────────────
sys.path.append("python_files")
st.write("➡️ Added `python_files/` to system path.")


# ──────────────────────────────────────────────
# IMPORT MODULES
# ──────────────────────────────────────────────
st.subheader("🔄 Importing Data Cleaning Modules")

modules = {
    "Macroeconomic Factors":  "Annual_Macroeconomic_Factors",
    "Housing":                "Housing",
    "Population Report":      "Population_report",
    "Homelessness Trend":     "HomelessYears",
    "Housing Macroeconomic Factors": "Housing_Macroeconomic_Factors",
    "Regional Cost of Living": "Regional_Cost_of_Living"
}

loaded_modules = {}

for label, module_name in modules.items():
    try:
        imported = __import__(f"python_files.{module_name}", fromlist=[module_name])
        loaded_modules[label] = imported
        st.success(f"✓ Imported `{module_name}.py` successfully")
    except Exception as e:
        st.error(f"❌ Failed to import `{module_name}.py`")
        st.code(traceback.format_exc())


# ──────────────────────────────────────────────
# CHECK XLSX DATA FILES
# ──────────────────────────────────────────────
st.subheader("📊 Checking Required Excel Data Files")

data_files = [
    "Annual_Macroeconomic_Factors.xlsx",
    "Housing.xlsx",
    "PopulationReport.xlsx",
    "HomelessYears.xlsx",
    "Housing_Macroeconomic_Factors_US(good).xlsx",
    "Regional Cost of Living.xlsx",
]

for file in data_files:
    if os.path.exists(file):
        st.success(f"✓ Found: {file}")
    else:
        st.error(f"❌ Missing: {file}")


# ──────────────────────────────────────────────
# RUN EACH MODULE'S main() FUNCTION
# ──────────────────────────────────────────────
st.subheader("▶️ Running Data Cleaning Scripts")

for label, module in loaded_modules.items():
    st.write(f"### 🔧 Running `{label}`")

    if hasattr(module, "main"):
        try:
            module.main()
            st.success(f"✓ Finished running `{label}`")
        except Exception as e:
            st.error(f"❌ Error in `{label}` during execution")
            st.code(traceback.format_exc())
    else:
        st.warning(f"⚠️ Module `{label}` has no main() function")


st.success("🎉 All Systems Complete — Check output folder for results!")
