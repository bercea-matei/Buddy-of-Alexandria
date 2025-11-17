from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    load_index_from_storage,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
import chromadb

import os

PERSIST_DIR = "./llama_storage"
DB_DIR = "chroma_db"
CHROMA_DB_PATH = os.path.join(PERSIST_DIR, DB_DIR)
CHROMA_DB_COLLECTION = "quickstart"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class IndexManager:
    def __init__(self, docs_dir):
        self.docs_dir = docs_dir
        self.db_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.chroma_collection = self.db_client.get_or_create_collection(
            CHROMA_DB_COLLECTION
        )

        # Now, check if the LlamaIndex parts of the index exist
        docstore_path = os.path.join(PERSIST_DIR, "docstore.json")
        if not os.path.exists(docstore_path):
            self.re_build_all()
        else:
            self._load_existing_index()

    def re_build_all(self):
        """Re-embedds ALL the files"""
        existing_ids = self.chroma_collection.get()["ids"]
        if existing_ids:
            print(
                f"Clearing {len(existing_ids)} old entries from ChromaDB collection..."
            )
            self.chroma_collection.delete(ids=existing_ids)

        Settings.embed_model = HuggingFaceEmbedding(EMBEDDING_MODEL)

        documents = SimpleDirectoryReader(
            self.docs_dir, required_exts=[".md"]
        ).load_data()

        # Use the connection that __init__ created (self.chroma_collection)
        vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            transformations=[SentenceSplitter(chunk_size=512, chunk_overlap=120)],
        )
        index.storage_context.persist(persist_dir=PERSIST_DIR)

        return index

    def _load_existing_index(self):
        Settings.embed_model = HuggingFaceEmbedding(EMBEDDING_MODEL)
        vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store, persist_dir=PERSIST_DIR
        )
        self.index = load_index_from_storage(storage_context=storage_context)

    def query_question(self, query_msg: str) -> str:
        """Query a question with answer from DB"""
        if not os.path.exists(PERSIST_DIR):
            # TODO - Throw an exception
            # print(f"CromaDB not found at {CHROMA_DB_PATH}.")
            pass
        else:
            # print(f"Loading CromaDB from {CHROMA_DB_PATH}...")
            Settings.embed_model = HuggingFaceEmbedding(EMBEDDING_MODEL)

            db2 = chromadb.PersistentClient(path=CHROMA_DB_PATH)
            chroma_collection = db2.get_or_create_collection(CHROMA_DB_COLLECTION)
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

            storage_context = StorageContext.from_defaults(
                vector_store=vector_store, persist_dir=PERSIST_DIR
            )

            index = load_index_from_storage(storage_context=storage_context)

            retriever_engine = index.as_retriever()
            response = retriever_engine.retrieve(query_msg)

            return sorted(response, key=lambda x: x.score, reverse=True)[0].text

    def delete_file_node(self, file):
        delete_file_path = os.path.join(self.docs_dir, file)
        self.chroma_collection.delete(where={"file_path": delete_file_path})

    def update_file_node(self, filepath):
        # delete_file_path = os.path.join(self.docs_dir, file)
        if not os.path.exists(PERSIST_DIR):
            # print(f"CromaDB not found at {CHROMA_DB_PATH}. Please run build_index.py first.")
            pass
        else:
            # print(f"Loading CromaDB from {CHROMA_DB_PATH}...")

            self.index.delete_ref_doc(ref_doc_id=filepath, delete_from_docstore=True)
            reader = SimpleDirectoryReader(
                input_dir=self.docs_dir,
                input_files=[filepath],
            )

            documents = reader.load_data()

            node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=120)
            new_nodes = node_parser.get_nodes_from_documents(documents)
            self.index.insert_nodes(new_nodes)
