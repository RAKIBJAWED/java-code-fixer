import streamlit as st
from runner import run_java
from java_code_fixer import JavaCodeFixer
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

st.title("Java Code Runner")

# Initialize session state
if "execution_result" not in st.session_state:
    st.session_state.execution_result = ""
if "reset_clicked" not in st.session_state:
    st.session_state.reset_clicked = False
if "corrected_code" not in st.session_state:
    st.session_state.corrected_code = ""

# Handle reset before creating widgets
if st.session_state.reset_clicked:
    st.session_state.execution_result = ""
    st.session_state.java_input = ""
    st.session_state.reset_clicked = False

# Create two columns for input and corrected code
col1, col2 = st.columns(2)

with col1:
    st.subheader("Java Code Input")
    java_code_input = st.text_area("Enter Java code:", height=300, key="java_input")

with col2:
    st.subheader("Corrected Java Code")
    corrected_code_output = st.text_area("Corrected code will appear here:", value=st.session_state.corrected_code, height=300, disabled=True)

# Dropdown selections
col3, col4 = st.columns(2)

with col3:
    java_version = st.selectbox("Java Version:", ["8", "11", "17", "21"], key="java_version")

with col4:
    llm_model = st.selectbox("LLM Model:", ["ANTHROPIC ✅ Working", "OPEN_AI ❌ Not Working"], key="llm_model")

# Output box for execution results
st.subheader("Java Code Output")

execution_output = st.text_area("Execution output will appear here:", value=st.session_state.execution_result, height=200, disabled=True)

# Buttons
col5, col6, col7 = st.columns(3)

with col5:
    run_button = st.button("Run Java Code", key="run_button")

with col6:
    reset_button = st.button("Reset", key="reset_button")

with col7:
    generate_button = st.button("Generate Updated Code", key="generate_button")

# Run Java code functionality
if run_button and java_code_input.strip():
    try:
        result = run_java(java_version, java_code_input)
        if result["success"]:
            print("Success!")
            st.session_state.execution_result = f"✅ Execution successful:\n{result['stdout']}"
        else:
            print("Failed!")
            st.session_state.execution_result = f"❌ Execution failed (Exit code: {result['exit_code']}):\n{result['stderr']}"
        st.rerun()
    except Exception as e:
        print("Failed with exception:", e)
        st.session_state.execution_result = f"❌ Error: {str(e)}"
        st.rerun()

# Reset functionality
if reset_button:
    st.session_state.reset_clicked = True
    st.rerun()

# Generate Updated Code functionality
if generate_button:
    if not java_code_input.strip():
        st.error("Java code input is empty!")
    elif not st.session_state.execution_result.strip():
        st.error("Java code output is empty! Please run the code first.")
    else:
        try:
            if "ANTHROPIC" in llm_model:
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    st.error("ANTHROPIC_API_KEY environment variable not set!")
                    st.stop()
            else:  # OPEN_AI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    st.error("OPENAI_API_KEY environment variable not set!")
                    st.stop()
            
            fixer = JavaCodeFixer(api_key)
            st.session_state.corrected_code = fixer.fix_code(
                java_code_input, 
                st.session_state.execution_result, 
                java_version
            )
            st.rerun()
        except Exception as e:
            st.error(f"Error generating updated code: {str(e)}")
