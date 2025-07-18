### AGENT THAT CAN ANSWER QUESTIONS ABOUT THE DATA ###

import os
from dotenv import load_dotenv
from videoInfoExtractor import VideoInfoExtractor

### LANGGRAPH LIBRARY IMPORTS ###
from langgraph.graph import START, END, StateGraph, MessagesState



from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import WikipediaLoader
from langchain_community.document_loaders import ArxivLoader


load_dotenv()

youtube_extractor = VideoInfoExtractor()

### TOOLS ###

@tool
def wikipedia_search(query:str) -> str:
    """Tool to search wikipedia for information to answer the query"""
    loader = WikipediaLoader(query=query).load()
    return loader.page_content

# Pending extraction of youtube url from query
@tool
def youtube_search(query:str) -> str:
    """Tool to extract info from youtube video to answer the query"""
    youtube_url = query
    video_id = youtube_extractor.extact_video_id(youtube_url)
    transcript = youtube_extractor.extract_transcript(video_id)
    metadata = youtube_extractor.extract_metadata(youtube_url)
    if not transcript:
        return None
    return extract_info(transcript, metadata)

@tool
def arxiv_search(query:str) -> str:
    """Tool to search articles and papers on arxiv"""
    search_docs = ArxivLoader(query=query).load()
    return search_docs

@tool
def web_search(query:str) -> str:
    """Tool to search the web for information to answer the query"""
    search_results = TavilySearchResults().invoke(query)
    return search_results

    

tools = [
    wikipedia_search,
    youtube_search,
    arxiv_search,
    web_search,
]

### BUILD GRAPH FUNCTION ###

def build_graph(provider: str = "groq"):
    if provider == "groq":
        llm = ChatGroq(model="qwen/qwen3-32b", temperature=0)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    
    llm_with_tools = llm.bind_tools(tools)

    




