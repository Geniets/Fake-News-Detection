import streamlit as st

st.title("Debug App Imports")

try:
    st.write("1. Testing basic imports...")
    import pandas as pd
    import numpy as np
    import joblib
    import json
    import os
    from PIL import Image
    import io
    st.success("✓ Basic imports successful")
except Exception as e:
    st.error(f"✗ Basic imports failed: {e}")

try:
    st.write("2. Testing google.genai...")
    import google.genai as genai
    st.success("✓ google.genai imported")
except Exception as e:
    st.error(f"✗ google.genai failed: {e}")

try:
    st.write("3. Testing utils.webscraper...")
    from utils.webscraper import scrape_website_metadata, format_metadata_for_display
    st.success("✓ utils.webscraper imported")
except Exception as e:
    st.error(f"✗ utils.webscraper failed: {e}")
    import traceback
    st.code(traceback.format_exc())

st.write("All imports completed!")
