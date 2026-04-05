from typing import TypedDict


class RAGASScore(TypedDict):
    faithfulness: float
    relevance: float
    passed: bool
    rerun_flag: bool


def check_faithfulness(question: str, response: str, retrieved_contexts: list[str]) -> RAGASScore:
    try:
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy
        from datasets import Dataset

        data = Dataset.from_dict({
            "question": [question],
            "answer": [response],
            "contexts": [retrieved_contexts],
        })
        scores = evaluate(data, metrics=[faithfulness, answer_relevancy])
        f_score = float(scores.get("faithfulness", 0.0))
        r_score = float(scores.get("answer_relevancy", 0.0))
        
        return {
            "faithfulness": f_score, 
            "relevance": r_score, 
            "passed": f_score >= 0.7,
            "rerun_flag": f_score < 0.7
        }
    except ImportError:
        # Fallback scoring using basic NLI
        try:
            from transformers import pipeline
            nli_model = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
            combined = "\\n".join(retrieved_contexts)
            res = nli_model(response, candidate_labels=[combined], hypothesis_template="This text implies that {}")
            f_score = float(res["scores"][0])
        except ImportError:
            # Basic keyword overlap fallback if NLI model is unavailable
            combined = "\\n".join(retrieved_contexts).lower()
            resp_words = [w for w in response.lower().split() if len(w) > 3]
            if not resp_words:
                f_score = 1.0
            else:
                hits = sum(1 for w in resp_words if w in combined)
                f_score = hits / len(resp_words)
                
        return {
            "faithfulness": f_score,
            "relevance": 1.0,
            "passed": f_score >= 0.7,
            "rerun_flag": f_score < 0.7
        }
