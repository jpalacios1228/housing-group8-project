import streamlit as st
import os

st.title("File Path Debugger")

# Show current working directory
st.write("Current working directory:", os.getcwd())

# List all files in current directory
st.write("Files in current directory:")
for file in os.listdir("."):
    st.write(f"- {file}")

# List files in python_files directory
if os.path.exists("python_files"):
    st.write("Files in python_files directory:")
    for file in os.listdir("python_files"):
        st.write(f"- {file}")

# Now try your imports with error handling
try:
    import python_files.Annual_Macroeconomic_Factors as MacroF
    st.success("✓ Successfully imported MacroF")
except Exception as e:
    st.error(f"Import failed: {e}")

import python_files.Annual_Macroeconomic_Factors as MacroF
import python_files.Housing as Housing
import python_files.Population_report as Population
import python_files.poverty_report as Poverty
import python_files.Unemployment as Unemployment
