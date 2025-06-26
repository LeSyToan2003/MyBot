import os
import json
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

class EmbedStore:
    def __init__(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.data_path = os.path.join(self.root_dir, "data", "qa_rag", "qa")
        self.persist_dir = os.path.join(self.root_dir, "ai", "rag", "chroma_db")
        self.model_folder = os.path.join(os.path.dirname(__file__), "vietnamese-bi-encoder")
        
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=self.model_folder
        )

    def load_data(self):
        documents = []
        for filename in os.listdir(self.data_path):
            if filename.endswith(".json"):
                file_path = os.path.join(self.data_path, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        question = item.get("question", "").strip()
                        answer = item.get("answer", "").strip()
                        content = f"Hỏi: {question}\nĐáp: {answer}"
                        doc = Document(page_content=content, metadata={"source": filename})
                        documents.append(doc)

        return documents

    def build_vectorstore(self):
        docs = self.load_data()
        
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=self.embedding_model,
            persist_directory=self.persist_dir
        )