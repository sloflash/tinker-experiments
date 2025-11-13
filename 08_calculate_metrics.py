#!/usr/bin/env python3
"""Step 16: Calculate cost savings metrics"""

import json


def calculate_metrics():
    """Analyze evaluation results for cost/quality metrics"""

    with open('evaluation_results.json', 'r') as f:
        results = json.loads(f.read())

    # Quality metrics
    similarities = [r['similarity'] for r in results]
    avg_sim = sum(similarities) / len(similarities)
    min_sim = min(similarities)

    # Token savings
    token_savings = results[0]['teacher_tokens'] - results[0]['student_tokens']
    reduction_pct = token_savings / results[0]['teacher_tokens'] * 100

    # Cost calculation (Qwen pricing: $0.06/1M input tokens)
    teacher_cost_per_1m = (results[0]['teacher_tokens'] / 1000) * 0.06
    student_cost_per_1m = (results[0]['student_tokens'] / 1000) * 0.06
    savings_per_1m = teacher_cost_per_1m - student_cost_per_1m
    cost_multiplier = teacher_cost_per_1m / student_cost_per_1m if student_cost_per_1m > 0 else float('inf')

    metrics = {
        "quality_retention": f"{avg_sim:.1%}",
        "min_similarity": f"{min_sim:.1%}",
        "tokens_saved_per_query": token_savings,
        "token_reduction": f"{reduction_pct:.1f}%",
        "cost_savings_per_1m_queries": f"${savings_per_1m:.2f}",
        "cost_multiplier": f"{cost_multiplier:.1f}x cheaper"
    }

    with open('metrics_report.json', 'w') as f:
        json.dump(metrics, f, indent=2)

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    calculate_metrics()
