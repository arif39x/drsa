import ctypes  # Deep codebase analyser using LlamaIndex and Tree-Sitter."
import os
import shutil
import subprocess
import sys

from git import Repo
from tree_sitter import Language, Parser

try:
    from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
    from llama_index.vector_stores.lancedb import LanceDBVectorStore

    LLAMA_INDEX_AVAIL = True
except ImportError:
    LLAMA_INDEX_AVAIL = False

import lancedb

_GRAMMAR_LIB = "./grammars/languages.so"
_GRAMMAR_SETUP = "setup_grammars.py"


def _ensure_grammars() -> None:

    if os.path.exists(_GRAMMAR_LIB):
        return

    result = subprocess.run(
        [sys.executable, _GRAMMAR_SETUP],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0 or not os.path.exists(_GRAMMAR_LIB):
        raise RuntimeError(
            f"Tree-Sitter grammar build failed.\n"
            f"Run manually: python {_GRAMMAR_SETUP}\n\n"
            f"Error output:\n{result.stderr.strip()}"
        )


class DeepCodeAnalyzer:
    def __init__(self, db_uri: str = "./lancedb_vault") -> None:

        self.db_uri = db_uri
        self.db = lancedb.connect(db_uri)

        _ensure_grammars()

        lib = ctypes.cdll.LoadLibrary(_GRAMMAR_LIB)
        lib.tree_sitter_python.restype = ctypes.c_void_p
        lang_ptr = lib.tree_sitter_python()
        self.py_language = Language(lang_ptr)
        self.parser = Parser(self.py_language)

    def clone_and_index(self, repo_url: str, target_dir: str = "./temp_repos") -> str:

        if not LLAMA_INDEX_AVAIL:
            return "[LlamaIndex not available. Run: pip install llama-index-core]"

        # Check if it's a local directory
        if os.path.isdir(repo_url):
            dest = os.path.abspath(repo_url)
            repo_name = os.path.basename(dest)
            is_local = True
        else:
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            dest = os.path.join(target_dir, repo_name)
            if os.path.exists(dest):
                shutil.rmtree(dest)
            Repo.clone_from(repo_url, dest)
            is_local = False

        documents = SimpleDirectoryReader(dest, recursive=True).load_data()
        vector_store = LanceDBVectorStore(uri=self.db_uri, table_name="code_index")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        VectorStoreIndex.from_documents(documents, storage_context=storage_context)

        source_type = "local directory" if is_local else "remote repository"
        return f"Successfully indexed {len(documents)} files from {source_type} '{repo_name}'."

    def analyze_structure(self, file_path: str) -> list:

        with open(file_path, "rb") as f:
            tree = self.parser.parse(f.read())
            return self._walk_tree(tree.root_node)

    def _walk_tree(self, node) -> list:
        results = []

        def traverse(n):
            if n.type == "function_definition":
                name_idx = n.child_by_field_name("name")
                params_idx = n.child_by_field_name("parameters")
                name = name_idx.text.decode("utf-8") if name_idx else "unknown"
                params = params_idx.text.decode("utf-8") if params_idx else ""
                results.append({"type": "function", "name": name, "parameters": params})
            elif n.type == "class_definition":
                name_idx = n.child_by_field_name("name")
                super_classes_idx = n.child_by_field_name("superclasses")
                name = name_idx.text.decode("utf-8") if name_idx else "unknown"
                supers = (
                    super_classes_idx.text.decode("utf-8") if super_classes_idx else ""
                )
                results.append({"type": "class", "name": name, "inheritance": supers})
            elif n.type == "import_statement":
                results.append({"type": "import", "statement": n.text.decode("utf-8")})
            elif n.type == "import_from_statement":
                results.append(
                    {"type": "import_from", "statement": n.text.decode("utf-8")}
                )

            for child in n.children:
                traverse(child)

        traverse(node)
        return results

    def query(self, query_text: str) -> str:

        if not LLAMA_INDEX_AVAIL:
            return "[LlamaIndex not available. Run: pip install llama-index-core]"

        vector_store = LanceDBVectorStore(uri=self.db_uri, table_name="code_index")
        index = VectorStoreIndex.from_vector_store(vector_store)
        query_engine = index.as_query_engine()
        response = query_engine.query(query_text)
        return str(response)
