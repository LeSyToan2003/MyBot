import os
import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

class Retriever:
    def __init__(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.context_file = os.path.join(self.root_dir, "data", "qa_rag", "logs", "context.json")
        self.persist_dir = os.path.join(self.root_dir, "ai", "rag", "chroma_db")
        self.model_folder = os.path.join(self.root_dir, "ai", "rag", "vietnamese-bi-encoder")

        with open(self.context_file, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=self.model_folder
        )

        self.vectorstore = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embedding_model
        )

    def save_context(self, query: str, context: str):
        with open(self.context_file, "r", encoding="utf-8") as f:
            logs = json.load(f)

        logs.append({
            "query": query,
            "context": context
        })

        with open(self.context_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def retrieve_docs(self, query: str, top_k: int = 10):
        return self.vectorstore.similarity_search(query, k=top_k)

    def retrieve(self, query: str) -> str:
        docs = self.retrieve_docs(query)

        output = "\n\n".join([doc.page_content for doc in docs])

        self.save_context(query, output)

        return output