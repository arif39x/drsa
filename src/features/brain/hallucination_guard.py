from typing import TypedDict


class RAGASScore(TypedDict):
    faithfulness: float
    relevance: float
    passed: bool


def score_response(question: str, answer: str, context: str) -> RAGASScore:

    try:
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy
        from datasets import Dataset

        data = Dataset.from_dict({
            "question": [question],
            "answer": [answer],
            "contexts": [[context]],
        })
        scores = evaluate(data, metrics=[faithfulness, answer_relevancy])
        f_score = float(scores["faithfulness"])
        r_score = float(scores["answer_relevancy"])
        return {"faithfulness": f_score, "relevance": r_score, "passed": f_score > 0.6 and r_score > 0.6}
    except ImportError:
        return {"faithfulness": -1.0, "relevance": -1.0, "passed": True}


def is_hallucinated(question: str, answer: str, context: str, threshold: float = 0.6) -> bool:
    # Return True if the answer is likely hallucinated (faithfulness below threshold).
    score = score_response(question, answer, context)
    if score["faithfulness"] < 0:
        return False
    return score["faithfulness"] < threshold
