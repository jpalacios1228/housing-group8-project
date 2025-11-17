import streamlit as st
import os
import sys
import traceback

st.set_page_config(layout="wide")
st.title("Housing Market Analysis - Debug Mode")

# Debug: Show current directory structure
st.subheader("📁 Current Directory Structure")
try:
    for root, dirs, files in os.walk("."):
        # Skip hidden directories like .git
        if '/.' in root:
            continue
        level = root.replace(".", "").count(os.sep)
        indent = " " * 2 * level
        st.write(f"{indent}📁 {os.path.basename(root)}/")
        sub_indent = " " * 2 * (level + 1)
        for file in files[:10]:  # Limit to first 10 files per directory
            if file.endswith(('.py', '.txt', '.xlsx', '.csv')):
                st.write(f"{sub_indent}📄 {file}")
except Exception as e:
    st.error(f"Error listing directory: {e}")

# Try to import your modules
st.subheader("🔄 Testing Imports")
try:
    # Add python_files to path
    sys.path.append('python_files')
    
    st.write("✓ Python path updated")
    
    # Try importing
    import python_files.Annual_Macroeconomic_Factors as MacroF
    st.success("✓ Successfully imported Annual_Macroeconomic_Factors")
    
    # If you have other modules, test them too
    try:
        import python_files.HPI_Data as HPI
        st.success("✓ Successfully imported HPI_Data")
    except Exception as e:
        st.warning(f"HPI_Data import: {e}")
        
    try:
        import python_files.US_Housing_Affordability_Index as Affordability
        st.success("✓ Successfully imported US_Housing_Affordability_Index")
    except Exception as e:
        st.warning(f"Affordability import: {e}")
        
except Exception as e:
    st.error(f"❌ Import failed: {e}")
    st.code(traceback.format_exc())

st.success("🔧 Debug complete - check above for issues!")

import python_files.Annual_Macroeconomic_Factors as MacroF
import python_files.Housing as Housing
import python_files.Population_report as Population
import python_files.poverty_report as Poverty
import python_files.Unemployment as Unemployment
