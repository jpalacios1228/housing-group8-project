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

    import python_files.Housing as Housing
    st.success("✓ Successfully imported Housing")

    import python_files.Population_report as Population
    st.success("✓ Successfully imported Population_report")

    import python_files.poverty_report as Poverty
    st.success("✓ Successfully imported poverty_report")

    import python_files.Unemployment as Unemployment
    st.success("✓ Successfully imported Unemployment")

# Test data file access
st.subheader("📊 Testing Data File Access")
try:
    # Check if data files exist
    data_files = [
        "Annual_Macroeconomic_Factors.xlsx",
        "Housing.xlsx",
        "PopulationReport.xlsx",
        "PovertyReport.xlsx",
        "UnemploymentReport.xlsx",
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            st.success(f"✓ Found: {file_path}")
        else:
            st.error(f"❌ Missing: {file_path}")
            
except Exception as e:
    st.error(f"Error checking data files: {e}")

st.success("🔧 Debug complete - check above for issues!")

#import python_files.Annual_Macroeconomic_Factors as MacroF
#import python_files.Housing as Housing
#import python_files.Population_report as Population
#import python_files.poverty_report as Poverty
#import python_files.Unemployment as Unemployment
