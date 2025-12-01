# IndexManager.py

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
CHUNK_SIZE = 384
CHUNK_OVERLAP = 52


class IndexManager:
    def __init__(self, docs_dir) -> None:
        self.docs_dir = docs_dir
        self.db_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.chroma_collection = self.db_client.get_or_create_collection(
            CHROMA_DB_COLLECTION
        )
        Settings.embed_model = HuggingFaceEmbedding(EMBEDDING_MODEL)
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)

        docstore_path = os.path.join(PERSIST_DIR, "docstore.json")
        if not os.path.exists(docstore_path):
            self.index = self.re_build_all()
        else:
            self.index = self._load_existing_index()

    def re_build_all(self) -> VectorStoreIndex:
        """Re-embedds ALL the files and creates a new index"""
        print("Setting up the db")
        existing_ids = self.chroma_collection.get()["ids"]
        if existing_ids:
            print(
                f"Clearing {len(existing_ids)} old entries from ChromaDB collection..."
            )
            self.chroma_collection.delete(ids=existing_ids)
        print("Searching for the documents")
        try:
            documents = SimpleDirectoryReader(
                self.docs_dir, required_exts=[".md"], recursive=True
            ).load_data()
        except ValueError:
            documents = []

        if not documents:
            print("no ducuments were found")
            return None

        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        print("building the index")
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            transformations=[
                SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
            ],
        )
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        print("index built successfully")
        return index

    def _load_existing_index(self) -> VectorStoreIndex:
        """Loads the existing index into memory"""
        storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store, persist_dir=PERSIST_DIR
        )
        index = load_index_from_storage(storage_context=storage_context)
        return index

    def delete_file_node(self, filepath: str) -> None:
        """Deletes all nodes associated with the provided file"""
        if not os.path.exists(PERSIST_DIR):
            print(f"CromaDB not found at {CHROMA_DB_PATH}.")
            # should never really happen
            # we are creating a db at startup if not found
        else:
            self.chroma_collection.delete(where={"file_path": filepath})

    def update_file_node(self, filepath: str) -> None:
        """
        Deletes all nodes associated with the provided file
        Then re-embedds the file.
        """
        if not os.path.exists(PERSIST_DIR):
            print(f"No Index found at not found at {PERSIST_DIR}.")
            pass
        else:
            # self.index.delete_ref_doc(ref_doc_id=filepath, delete_from_docstore=True)
            self.chroma_collection.delete(where={"file_path": filepath})
            reader = SimpleDirectoryReader(
                input_dir=self.docs_dir,
                input_files=[filepath],
            )

            documents = reader.load_data()

            node_parser = SentenceSplitter(
                chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
            )
            new_nodes = node_parser.get_nodes_from_documents(documents)

            if not self.index:
                self.re_build_all()
            self.index.insert_nodes(new_nodes)

    def query_question(self, query_msg: str) -> str:
        """Returns the most relevant answer to the query"""
        if not os.path.exists(PERSIST_DIR):
            print(f"CromaDB not found at {CHROMA_DB_PATH}.")
            # should never really happen
            # we are creating a db at startup if not found
        else:
            if not self.index:
                self.re_build_all()
            if not self.index:
                return "There is no info that can be used. Please create/add a note."
            retriever_engine = self.index.as_retriever()
            response = retriever_engine.retrieve(query_msg)

            return sorted(response, key=lambda x: x.score, reverse=True)[0].text
