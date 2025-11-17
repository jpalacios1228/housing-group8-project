import streamlit as st

st.set_page_config(layout="wide")
st.title("Debug - App is loading")

try:
    st.write("✓ Streamlit is working")
    import pandas as pd
    st.write("✓ Pandas imported")
    import openpyxl
    st.write("✓ Openpyxl imported")
    
    # Test your imports one by one
    from python_files.Annual_Macroeconomic_Factors import *
    st.write("✓ Custom modules imported")
    
    st.success("All imports successful!")
    
except Exception as e:
    st.error(f"Error at: {str(e)}")
    import traceback
    st.code(traceback.format_exc())

import python_files.Annual_Macroeconomic_Factors as MacroF
import python_files.Housing as Housing
import python_files.Population_report as Population
import python_files.poverty_report as Poverty
import python_files.Unemployment as Unemployment
