import os
import subprocess
import tempfile

import networkx as nx

try:
    from pylatexenc.latex2text import LatexNodes2Text
except ImportError:
    LatexNodes2Text = None


class ResearchVisualizer:


    def __init__(self) -> None:
        self.latex_parser = LatexNodes2Text() if LatexNodes2Text else None

    def render_mermaid_to_ansi(self, mermaid_code: str) -> str:

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                mmd_path = os.path.join(tmpdir, "diagram.mmd")
                png_path = os.path.join(tmpdir, "diagram.png")

                with open(mmd_path, "w") as f:
                    f.write(mermaid_code)

                mmdc_result = subprocess.run(
                    ["mmdc", "-i", mmd_path, "-o", png_path],
                    capture_output=True,
                    text=True,
                )
                if mmdc_result.returncode != 0 or not os.path.exists(png_path):
                    return self._fallback_mermaid(mermaid_code, "mmdc unavailable")

                chafa_result = subprocess.run(
                    ["chafa", png_path],
                    capture_output=True,
                    text=True,
                )
                if chafa_result.returncode != 0:
                    return self._fallback_mermaid(mermaid_code, "chafa unavailable")

                return chafa_result.stdout
        except FileNotFoundError as exc:
            return self._fallback_mermaid(mermaid_code, str(exc))
        except Exception as exc:
            return self._fallback_mermaid(mermaid_code, str(exc))

    def render_knowledge_graph(self, graph_dict: dict) -> str:

        mermaid_str = graph_dict.get("mermaid", "")
        if not mermaid_str:
            from src.features.studio.knowledge_graph import build_mermaid

            mermaid_str = build_mermaid(graph_dict)
        return self.render_mermaid_to_ansi(mermaid_str)

    def render_graph_ascii(self, g: nx.Graph) -> dict:

        return nx.to_dict_of_lists(g)

    def render_latex(self, latex_str: str) -> str:

        if self.latex_parser:
            return self.latex_parser.latex_to_text(latex_str)
        return latex_str

    @staticmethod
    def _fallback_mermaid(mermaid_code: str, reason: str) -> str:
        return f"[Render unavailable: {reason}]\n\n{mermaid_code}"
