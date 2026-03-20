import bs4
import os
from dotenv import load_dotenv

from fastapi import FastAPI
from pydantic import BaseModel

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

# INIT
load_dotenv()
app = FastAPI()

# MODEL
model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# EMBEDDINGS
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = InMemoryVectorStore(embeddings)

# LOAD + SPLIT
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    ),
)

docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

all_splits = text_splitter.split_documents(docs)
vector_store.add_documents(all_splits)

# TOOL
@tool
def retrieve_context(query: str):
    docs = vector_store.similarity_search(query, k=2)
    return "\n\n".join(doc.page_content for doc in docs)

tools = [retrieve_context]

agent = create_agent(
    model,
    tools,
    system_prompt="Use the tool to answer questions."
)

# REQUEST MODEL
class Question(BaseModel):
    query: str

# API ROUTE
@app.post("/ask")
def ask_question(q: Question):
    response_text = ""

    for step in agent.stream(
        {"messages": [{"role": "user", "content": q.query}]},
        stream_mode="values",
    ):
        response_text = step["messages"][-1].content

    return {"response": response_text}

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)