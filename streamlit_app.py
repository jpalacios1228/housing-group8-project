import streamlit as st
import os
import sys
import traceback

st.set_page_config(layout="wide")
st.title("📊 Housing Market Analysis — Debug & Run")

st.subheader("📁 Current Directory Structure")

try:
    for root, dirs, files in os.walk("."):
        if "/." in root:
            continue  
        indent = " " * (root.count(os.sep) * 2)
        st.write(f"{indent}📁 {root}/")

        for file in files:
            if file.endswith((".py", ".xlsx", ".csv")):
                st.write(f"{indent} 📄 {file}")
except Exception as e:
    st.error(f"Error scanning directory: {e}")

sys.path.append("python_files")
st.write("➡️ Added `python_files/` to system path.")

st.subheader("🔄 Importing Data Cleaning Modules")

modules = {
    "Macroeconomic Factors":  "Annual_Macroeconomic_Factors",
    "Housing":                "Housing",
    "Population Report":      "Population_report",
    "Poverty Report":         "poverty_report",
    "Unemployment Report":    "Unemployment"
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


st.subheader("📊 Checking Required Excel Data Files")

data_files = [
    "Annual_Macroeconomic_Factors.xlsx",
    "Housing.xlsx",
    "PopulationReport.xlsx",
    "PovertyReport.xlsx",
    "UnemploymentReport.xlsx"
]

for file in data_files:
    if os.path.exists(file):
        st.success(f"✓ Found: {file}")
    else:
        st.error(f"❌ Missing: {file}")

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
