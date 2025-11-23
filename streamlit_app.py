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
# DIRECTORY STRUCTURE VIEW
# ──────────────────────────────────────────────
st.subheader("📁 Current Directory Structure")

try:
    for root, dirs, files in os.walk("."):
        if "/." in root:
            continue  # skip hidden directories
        indent = " " * (root.count(os.sep) * 2)
        st.write(f"{indent}📁 {root}/")

        for file in files:
            if file.endswith((".py", ".xlsx", ".csv")):
                st.write(f"{indent} 📄 {file}")
except Exception as e:
    st.error(f"Error scanning directory: {e}")


# ──────────────────────────────────────────────
# ADD python_files/ TO SYSTEM PATH
# ──────────────────────────────────────────────
sys.path.append("python_files")
st.write("➡️ Added `python_files/` to system path.")


# ──────────────────────────────────────────────
# IMPORT MODULES (UPDATED — CORRECT FILENAMES)
# ──────────────────────────────────────────────
st.subheader("🔄 Importing Python Data Modules")

modules = {
    "Macroeconomic Factors":           "Annual_Macroeconomic_Factors",
    "Housing Data":                    "Housing",
    "Population Report":               "Population_report",
    "Homelessness Trend":              "HomelessYears",
    "Housing & Macroeconomic Factors": "Housing_Macroeconomic_Factors",
    "Regional Cost of Living":         "Regional_Cost_of_Living"
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
# CHECK THAT ALL REQUIRED EXCEL FILES EXIST
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
# RUN main() FOR EACH PYTHON SCRIPT
# ──────────────────────────────────────────────
st.subheader("▶️ Running Data Cleaning Scripts")

for label, module in loaded_modules.items():
    st.write(f"### 🔧 Running `{label}`")

    if hasattr(module, "main"):
        try:
            # Redirect script print() output to Streamlit
            with st.capture_output() as captured:
                module.main()

            st.success(f"✓ Finished running `{label}`")

            # Display the captured print() output
            if captured:
                st.code(str(captured))

        except Exception as e:
            st.error(f"❌ Error while running `{label}`")
            st.code(traceback.format_exc())

    else:
        st.warning(f"⚠️ `{label}` has no main() function")


st.success("🎉 All Systems Complete — Check output folder for results!")
