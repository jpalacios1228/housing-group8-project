import streamlit as st
import os
import sys
import traceback

st.set_page_config(layout="wide")
st.title("Housing Market Analysis - Debug Mode")

# Make sure python_files is importable
sys.path.append("python_files")

# Debug: Show directory structure
st.subheader("📁 Current Directory Structure")
try:
    for root, dirs, files in os.walk("."):
        if "/." in root:
            continue
        st.write(f"📁 {root}")
        for file in files:
            st.write(f" - {file}")
except Exception as e:
    st.error(f"Error listing directory: {e}")

# Test imports
st.subheader("🔄 Testing Imports")
try:
    import python_files.Annual_Macroeconomic_Factors as MacroF
    st.success("Imported Annual_Macroeconomic_Factors")

    import python_files.Housing as Housing
    st.success("Imported Housing")

    import python_files.Population_report as Population
    st.success("Imported Population_report")

    import python_files.poverty_report as Poverty
    st.success("Imported poverty_report")

    import python_files.Unemployment as Unemployment
    st.success("Imported Unemployment")

except Exception as e:
    st.error("❌ Import failed")
    st.code(traceback.format_exc())

# Test data files
st.subheader("📊 Testing Data File Access")
data_files = [
    "Annual_Macroeconomic_Factors.xlsx",
    "Housing.xlsx",
    "PopulationReport.xlsx",
    "PovertyReport.xlsx",
    "UnemploymentReport.xlsx",
]

for file in data_files:
    if os.path.exists(file):
        st.success(f"Found: {file}")
    else:
        st.error(f"Missing: {file}")

# RUN MODULE FUNCTIONS (if available)
st.subheader("🚀 Running Module Functions")

def try_run(name, module, func):
    """Helper to safely run a module function"""
    if hasattr(module, func):
        try:
            st.write(f"Running `{name}.{func}()`...")
            result = getattr(module, func)()
            st.success(f"✔ {name}.{func}() ran successfully")
            return result
        except Exception as e:
            st.error(f"❌ Error running {name}.{func}()")
            st.code(traceback.format_exc())
    else:
        st.warning(f"⚠ {name} has no function named `{func}`")

# Run load_data() if exists
macro_df = try_run("MacroF", MacroF, "load_data")
housing_df = try_run("Housing", Housing, "load_data")
population_df = try_run("Population", Population, "load_data")
poverty_df = try_run("Poverty", Poverty, "load_data")
unemp_df = try_run("Unemployment", Unemployment, "load_data")

st.success("🔧 Debug complete!")
