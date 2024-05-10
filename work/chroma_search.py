import chromadb
import os
from dotenv import load_dotenv
from typing import Optional, Union, List
import chromadb.utils.embedding_functions as embedding_functions
load_dotenv()
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("OPENAI_API_KEY"),
                model_name="text-embedding-3-small",
                api_base=os.getenv("OPENAI_BASE_URL")
            )
client = chromadb.HttpClient(
    host = os.getenv("CHROMA_HOST"),
    port = 8888,
    ssl=False
)



def search_chroma(
        query_texts : Union[List, str, None] = None,
        n_results: int = 6,
        where: Optional[dict] = None,
        where_document: Optional[dict] = None,
        include = ["documents",]):
    

    collection = client.get_collection(
        name="law_data",
        embedding_function=openai_ef    
    )
    try:
        res = collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where,
            where_document=where_document,
            include=include
            )
        return res["documents"][0]
    except Exception as e:
        print(e)
        return []
    
# tes = search_chroma(query_texts="如何支付加班费")
# print(tes)

