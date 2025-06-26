import streamlit as st

st.title("Dependency Test")

# Test 1: Check if we can import basic modules
st.subheader("Testing Basic Imports")

try:
    import sys
    st.success("✅ sys imported")
    st.write(f"Python version: {sys.version}")
except Exception as e:
    st.error(f"❌ sys import failed: {e}")

try:
    import os
    st.success("✅ os imported")
except Exception as e:
    st.error(f"❌ os import failed: {e}")

try:
    import json
    st.success("✅ json imported")
except Exception as e:
    st.error(f"❌ json import failed: {e}")

# Test 2: Check OpenAI specifically
st.subheader("Testing OpenAI Import")

try:
    import openai
    st.success("✅ openai imported successfully!")
    st.write(f"OpenAI version: {openai.__version__}")
except ImportError as e:
    st.error(f"❌ openai import failed: {e}")
    st.error("This means openai is not installed. Check your requirements.txt")
except Exception as e:
    st.error(f"❌ Unexpected error with openai: {e}")

# Test 3: Show current working directory and files
st.subheader("File System Check")
try:
    import os
    st.write(f"Current directory: {os.getcwd()}")
    st.write("Files in current directory:")
    files = os.listdir(".")
    for file in files:
        st.write(f"  - {file}")
except Exception as e:
    st.error(f"Error checking files: {e}")

# Test 4: Check if requirements.txt exists and show contents
st.subheader("Requirements Check")
try:
    with open("requirements.txt", "r") as f:
        requirements_content = f.read()
    st.success("✅ requirements.txt found")
    st.code(requirements_content, language="text")
except FileNotFoundError:
    st.error("❌ requirements.txt not found!")
except Exception as e:
    st.error(f"Error reading requirements.txt: {e}")
