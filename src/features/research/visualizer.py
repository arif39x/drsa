import os
import subprocess
import networkx as nx
try:
    from pylatexenc.latex2text import LatexNodes2Text
except ImportError:
    LatexNodes2Text = None

class ResearchVisualizer:
    # Visualization engine for the TUI (diagrams, math, graphs).

    def __init__(self):
        self.latex_p = LatexNodes2Text() if LatexNodes2Text else None

    def render_mermaid_to_ansi(self, mermaid_code):
        # Generate Mermaid diagram and render to ANSI via Chafa.
        with open("temp.mmd", "w") as f:
            f.write(mermaid_code)

        subprocess.run(["mmdc", "-i", "temp.mmd", "-o", "temp.png"], capture_output=True)

        result = subprocess.run(["chafa", "temp.png"], capture_output=True, text=True)
        return result.stdout

    def render_graph_ascii(self, g: nx.Graph):
        # Render a NetworkX graph as ASCII/Braille (logic stub).
        return nx.to_dict_of_lists(g)

    def render_latex(self, latex_str):
        # Convert LaTeX math to terminal-readable text.
        if self.latex_p:
            return self.latex_p.latex_to_text(latex_str)
        return latex_str
