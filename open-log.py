import streamlit as st
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import FAISS
import openai
import os
import re
from htmlTemplates import css, bot_template, user_template
from collections import Counter

openai.api_key = "your api key open ai"

MAX_FILE_SIZE_MB = 100 

def split_text_into_chunks(text, chunk_size=1000):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks

def get_log_text(log_files):
    text = ""
    total_size_mb = 0
    for log_file in log_files:
        total_size_mb += log_file.size / (1024 * 1024)  
        if total_size_mb > MAX_FILE_SIZE_MB:
            st.warning(f"The total size of uploaded files exceeds the maximum allowed size of {MAX_FILE_SIZE_MB}MB.")
            return ""
        if not log_file.name.endswith('.log'):
            st.error(f"Upload only valid file formats. '{log_file.name}' is not a valid format.")
            return ""
        with log_file as file:
            text += file.read().decode("utf-8")  
    return text

def preprocess_text(text):
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

    
def handle_user_input(user_input, log_text):
        log_text = preprocess_text(log_text)
        prompt = f"User: {user_input}\nLogs: {log_text}\nBot: "
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=150
        )
        generated_text = response.choices[0].text.strip()
        if user_input:
            st.write(user_template.replace("{{MSG}}", user_input), unsafe_allow_html=True)
        st.write(bot_template.replace("{{MSG}}", generated_text), unsafe_allow_html=True)

   
def count_issues(log_text):
    error_count = log_text.lower().count("error")
    errors = re.findall(r'error.*?(?=(?:error|\Z))', log_text.lower())
    return {"error": error_count, "errors": errors}

def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with your GPT")
    st.write(css, unsafe_allow_html=True)

    st.header("Nova Bot")
    user_input = st.text_input("Ask a question or type 'count [word]' to count occurrences of a word in the log files:")
    
    st.subheader("Your log files")
    log_files = st.file_uploader(
        "Upload your log files here and click on 'Process'",
        accept_multiple_files=True,
        type=["txt", "log"]  
    )
    if st.button("Process"):
        with st.spinner("Processing"):
            if log_files:
                raw_text = get_log_text(log_files)
                if raw_text:
                    if user_input:
                        handle_user_input(user_input, raw_text) 
                        
if __name__ == '__main__':
    main()
