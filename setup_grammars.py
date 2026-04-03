import os
import subprocess
import shutil

def main():
    grammars_dir = "./grammars"
    repo_url = "https://github.com/tree-sitter/tree-sitter-python"
    repo_dir = os.path.join(grammars_dir, "tree-sitter-python")
    lib_path = os.path.join(grammars_dir, "languages.so")

    if not os.path.exists(grammars_dir):
        os.makedirs(grammars_dir)

    if not os.path.exists(repo_dir):
        print(f"Cloning {repo_url}...")
        subprocess.run(["git", "clone", repo_url, repo_dir], check=True)
    else:
        print(f"Repo {repo_dir} already exists. Pulling latest...")
        subprocess.run(["git", "-C", repo_dir, "pull"], check=True)

    print("Building languages.so...")
    src_dir = os.path.join(repo_dir, "src")
    parser_c = os.path.join(src_dir, "parser.c")
    scanner_c = os.path.join(src_dir, "scanner.c")
    
    # Run the C compiler to create a shared library
    compile_cmd = [
        "cc", "-fPIC", "-shared",
        f"-I{src_dir}",
        parser_c,
        scanner_c,
        "-o", lib_path
    ]
    
    # We might need gcc or clang
    print("Running command:", " ".join(compile_cmd))
    try:
        subprocess.run(compile_cmd, check=True)
        print("Successfully built grammars/languages.so")
    except subprocess.CalledProcessError as e:
        print(f"Failed to build: {e}")
        exit(1)

if __name__ == "__main__":
    main()
