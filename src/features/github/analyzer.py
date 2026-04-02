import os
import shutil
from git import Repo
import tree_sitter
from tree_sitter import Language, Parser
try:
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
    from llama_index.vector_stores.lancedb import LanceDBVectorStore
    LLAMA_INDEX_AVAIL = True
except ImportError:
    LLAMA_INDEX_AVAIL = False
import lancedb
import ctypes

class DeepCodeAnalyzer:
    # codebase analyzer using LlamaIndex and Tree-Sitter.

    def __init__(self, db_uri="./lancedb_vault"):
        self.db_uri = db_uri
        self.db = lancedb.connect(db_uri)

        grammar_path = "./grammars/tree-sitter-python"
        lib_path = "./grammars/languages.so"

        if not os.path.exists(lib_path):
            # This should have been handled by setup or manual build
            pass

        lib = ctypes.cdll.LoadLibrary(lib_path)
        lib.tree_sitter_python.restype = ctypes.c_void_p
        lang_ptr = lib.tree_sitter_python()
        self.PY_LANGUAGE = Language(int(lang_ptr))
        self.parser = Parser(self.PY_LANGUAGE)

    def clone_and_index(self, repo_url, target_dir="./temp_repos"):
        """Clone and hierarchically index a repository."""
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        dest = os.path.join(target_dir, repo_name)

        if os.path.exists(dest):
            shutil.rmtree(dest)

        Repo.clone_from(repo_url, dest)

        documents = SimpleDirectoryReader(dest, recursive=True).load_data()

        vector_store = LanceDBVectorStore(uri=self.db_uri, table_name="code_index")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context
        )
        return f"Successfully indexed {len(documents)} files from {repo_name}."

    def analyze_structure(self, file_path):
        # Analyze code structure (classes/functions) using Tree-Sitter.
        with open(file_path, "rb") as f:
            tree = self.parser.parse(f.read())
            return self._walk_tree(tree.root_node)

    def _walk_tree(self, node):
        return []

    def query(self, query_text):
        # Query the indexed codebase.
        vector_store = LanceDBVectorStore(uri=self.db_uri, table_name="code_index")
        index = VectorStoreIndex.from_vector_store(vector_store)
        query_engine = index.as_query_engine()
        response = query_engine.query(query_text)
        return str(response)
