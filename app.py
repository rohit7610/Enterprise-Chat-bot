from dotenv import load_dotenv
import os

load_dotenv() # env values retrival

from langchain_community.document_loaders import PyPDFLoader # pdf file ke data ko read karne ke liye
from langchain_text_splitters import RecursiveCharacterTextSplitter # pdf ke data ko size me split karega,,chunks me
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import InMemoryVectorStore
import streamlit as st
from time import sleep

llm = ChatOllama(
    model="qwen2.5:7b",
    temperature=0
)

if "vector_db" not in st.session_state:
    st.session_state.vector_db = None

if "messages" not in st.session_state:
    st.session_state.messages = [] # ek blank bana denge, dono ke message store karane ke liye

def document_process(path):
#document loading 
    loader = PyPDFLoader(path)
    docs = loader.load()


    #splitting
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    #chunk overlap ka kam first chunk aur dusre chaunk ke bich relation bethane ka 200 esse words jo milte julte hai,helps to build
    docs = splitter.split_documents(docs)


#embedding and vector stores
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector_db = InMemoryVectorStore.from_documents(
        documents=docs,
        embedding=embeddings
    )

    vector_db.similarity_search
    st.session_state.vector_db = vector_db # ek seession me es vector_db ko access kar painge
    st.session_state.document_uploaded = True

#user query
#query = "What is the name of the project"
#documents = vector_db.similarity_search(query=query, k=1) #vector embedding karega aur vector databse se fetch karega similarity and context dega,k= 1 matlab kitne similar chunks chahaeye

#doc me jitne document honge unka context genrate
#context = ""
#for doc in documents:
    #context = context + doc.page_content + "\n\n"


#prompt = f"""
#    You are a helpful assistant and provide answer based in the provided context: {context}, question:{query}
#"""

#answer = llm.invoke(prompt)

st.subheader("Document Q&A ChatBot - Ask Anything")

if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False # ek page jo open kiya hai wo session


## document uplaod
if not st.session_state.document_uploaded:
    file = st.file_uploader(label="Select Your Pdf File", type="pdf")
    if file:
        with open("uploaded_document.pdf", "wb") as f:
            f.write(file.getvalue())

        with st.spinner("Processing Document"): #spinner ,ek loader dikhaiga
           document_process("./uploaded_document.pdf")

        st.markdown("Document Process successfully.")
        sleep(2)
        st.rerun() # session same rahega bs code rerun hoga


if st.session_state.document_uploaded and st.session_state.vector_db:
    for onemessage in st.session_state.messages: # message ko print karane ke liye
        role = onemessage["roles"]
        content = onemessage["content"]

        st.chat_message(role).markdown(content)

    query = st.chat_input("Ask Anything...")
    if query:

        st.session_state.messages.append({"roles":"user","content":query})

        st.chat_message("user").markdown(query) # application me chat dikhane ke liye

        documents = st.session_state.vector_db.similarity_search(query, k=2)
        context = ""

        for doc in documents:
            context += doc.page_content + "\n\n"

        prompt = f"""You are a helpful assistant and you provide answers for user questions based on provided context. context: {context} nad question:{query}"""
        result = llm.invoke(prompt)

        
        st.session_state.messages.append({
         "roles": "assistant",
         "content": result.content
        })

        st.chat_message("ai").markdown(result.content) # ai ka message app me display karne ke liye