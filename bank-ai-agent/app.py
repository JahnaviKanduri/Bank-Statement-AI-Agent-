import streamlit as st
import pandas as pd
import pdfplumber
from openai import OpenAI

# -----------------------------
# 🔑 SET YOUR OPENROUTER API KEY HERE
# -----------------------------
API_KEY = "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"  # 👈 paste your key

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
    default_headers={
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Bank AI Agent"
    }
)

# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="Bank AI Agent", page_icon="💰")
st.title("💰 Bank Statement AI Agent")

st.write("Upload your bank statement (CSV or PDF) and ask questions.")

# -----------------------------
# File Upload
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload File",
    type=["csv", "pdf"]
)

df = None
text_data = ""

# -----------------------------
# Handle CSV
# -----------------------------
if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        try:
            df = pd.read_csv(uploaded_file)
            st.success("✅ CSV Loaded Successfully")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

# -----------------------------
# Handle PDF
# -----------------------------
    elif uploaded_file.name.endswith(".pdf"):
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_data += extracted + "\n"

            st.success("✅ PDF Loaded Successfully")
            st.text_area("Extracted Text Preview", text_data[:1500], height=200)

        except Exception as e:
            st.error(f"Error reading PDF: {e}")

# -----------------------------
# Ask Question
# -----------------------------
question = st.text_input("💬 Ask a question about your bank data:")

if question:

    if df is not None:
        data_context = df.to_string()
    elif text_data:
        data_context = text_data
    else:
        st.warning("⚠️ Please upload a file first.")
        st.stop()

    prompt = f"""
You are a financial assistant.

Analyze the bank statement data below and answer the question.

DATA:
{data_context}

QUESTION:
{question}

Give a clear, short, and correct answer.
"""

    # -----------------------------
    # Call OpenRouter
    # -----------------------------
    try:
        with st.spinner("🤔 Analyzing..."):
            response = client.chat.completions.create(
                model="deepseek/deepseek-r1",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            answer = response.choices[0].message.content

        st.subheader("🧠 Answer:")
        st.write(answer)

    except Exception as e:
        st.error(f"❌ Error: {e}")