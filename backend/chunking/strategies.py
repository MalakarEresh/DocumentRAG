from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_chunks(text: str, strategy: str = "recursive"):
    if strategy == "recursive":
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return splitter.split_text(text)
    
    elif strategy == "semantic":
        semantic_chunker = SemanticChunker(embeddings, breakpoint_threshold_type="percentile")
        return semantic_chunker.split_text(text)
    
    elif strategy == "token":
        splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=100)
        return splitter.split_text(text)
    
    else:
        raise ValueError("Invalid chunking strategy")