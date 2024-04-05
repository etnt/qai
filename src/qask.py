from langchain.llms import Ollama
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

# Load the Ollama model
ollama = Ollama(model="mistral")

# Get the URL from the user
url = input("Enter a URL: ")

# Load the data from the URL
loader = WebBaseLoader(url)
data = loader.load()

# We need to split it up into smaller pieces
text_splitter=RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
all_splits = text_splitter.split_documents(data)

# Load the embeddings
oembed = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = Chroma.from_documents(documents=all_splits, embedding=oembed)

# Get the question from the user
question = input("Enter a Question: ")

# Get the most similar documents
docs = vectorstore.similarity_search(question)

# Get a good answer from the model
qachain=RetrievalQA.from_chain_type(ollama, retriever=vectorstore.as_retriever())
answer = qachain.invoke({"query": question})

print("")
print(answer['result'])
