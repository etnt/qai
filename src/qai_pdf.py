import streamlit as st
import os
import PyPDF2
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from io import BytesIO
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama

# Function to split PDF text into chunks
def split_pdf_text(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)
    text_chunks = []
    for page_number in range(num_pages):
        page = pdf_reader.pages[page_number]
        text_chunks.append(page.extract_text())
    return text_chunks

st.set_page_config(page_title="Ask your PDFs")
st.header("Ask your PDFs 💬")

# Check if the session state exists
if 'uploaded_files' not in st.session_state:
    st.session_state['uploaded_files'] = []

if 'splits' not in st.session_state:
    st.session_state['splits'] = []

# If no files have been uploaded yet, show the file uploader
if not st.session_state['uploaded_files']:
    uploaded_files = st.file_uploader("Upload your PDFs", type="pdf", accept_multiple_files=True)

    # If files have been uploaded, add them to the session state
    if uploaded_files:
        st.session_state['uploaded_files'].extend(uploaded_files)
        st.session_state['files_uploaded'] = True

        for uploaded_file in uploaded_files:
            # Read the file contents
            pdf_contents = uploaded_file.read()
            
            # Convert bytes to file-like object
            pdf_file = BytesIO(pdf_contents)

            # Split PDF text into chunks
            text_chunks = split_pdf_text(pdf_file)

            # Add the chunks to the session state
            st.session_state['splits'].extend(text_chunks)

# Load the embeddings
if st.session_state['splits']:
    # Pass the text chunks directly to Chroma
    vectorstore = Chroma.from_texts(
        texts=st.session_state['splits'],
        embedding=OllamaEmbeddings(model="nomic-embed-text")
    )
    retriever = vectorstore.as_retriever()

    # Get the value of the environment variable 'USE_MODEL'
    # If 'USE_MODEL' is not set or is empty, use 'default_value' instead
    model = os.getenv('USE_MODEL', 'mistral')
    model_local = ChatOllama(model=model)

    after_rag_template = """Answer the question based only on the following context:
        {context}
        Question: {question}
        """
    after_rag_prompt = ChatPromptTemplate.from_template(after_rag_template)
    after_rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | after_rag_prompt
        | model_local
        | StrOutputParser()
    )


# If files have been uploaded, remove the file uploader and proceed with the rest of the program
if 'files_uploaded' in st.session_state and st.session_state['files_uploaded']:
    # Get user input
    user_input = st.text_input("Please enter your question")

    # If user_input is not empty
    if user_input:
        stream = after_rag_chain.invoke(user_input)
        st.write(stream)

