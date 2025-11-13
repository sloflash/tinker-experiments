#!/usr/bin/env python3
"""Step 14: Evaluate student vs teacher on held-out set"""

import json
import tinker
from transformers import AutoTokenizer
from character_prompts import get_character_prompt
from difflib import SequenceMatcher


def evaluate_models(checkpoint_name, num_samples=100):
    """Compare student (no prompt) vs teacher (with prompt)"""

    # Setup
    client = tinker.ServiceClient()
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B")

    # Load student model from checkpoint
    training_client = client.create_lora_training_client(
        base_model="Qwen/Qwen3-4B-Instruct-2507",
        rank=32
    )
    training_client.load_state(name=checkpoint_name)
    student_client = training_client.save_weights_and_get_sampling_client(
        name=f"{checkpoint_name}_eval"
    )

    # Load teacher model
    teacher_client = client.create_sampling_client(base_model="Qwen/Qwen3-30B-A3B")

    # Load eval questions
    with open('val.jsonl', 'r') as f:
        eval_data = [json.loads(line) for line in f][:num_samples]

    character_prompt = get_character_prompt("Beethoven")
    results = []

    for i, example in enumerate(eval_data):
        question = example['messages'][0]['content']

        # Student (no prompt)
        student_prompt = f"<|user|>\n{question}\n<|assistant|>\n"
        student_tokens = tokenizer.encode(student_prompt)
        student_input = tinker.types.ModelInput.from_ints(student_tokens)
        student_result = student_client.sample(
            prompt=student_input,
            sampling_params=tinker.types.SamplingParams(max_tokens=300, temperature=0.7),
            num_samples=1
        ).result()
        student_response = tokenizer.decode(student_result.sequences[0].tokens, skip_special_tokens=True)

        # Teacher (with prompt)
        teacher_prompt = f"{character_prompt}\n\nUser: {question}\nBeethoven:"
        teacher_tokens = tokenizer.encode(teacher_prompt)
        teacher_input = tinker.types.ModelInput.from_ints(teacher_tokens)
        teacher_result = teacher_client.sample(
            prompt=teacher_input,
            sampling_params=tinker.types.SamplingParams(max_tokens=300, temperature=0.7),
            num_samples=1
        ).result()
        teacher_response = tokenizer.decode(teacher_result.sequences[0].tokens, skip_special_tokens=True)

        # Calculate similarity
        similarity = SequenceMatcher(None, student_response, teacher_response).ratio()

        results.append({
            "question": question,
            "student_response": student_response,
            "teacher_response": teacher_response,
            "similarity": similarity,
            "student_tokens": len(student_tokens),
            "teacher_tokens": len(teacher_tokens)
        })

        if (i + 1) % 10 == 0:
            print(f"Evaluated {i+1}/{num_samples}")

    # Save results
    with open('evaluation_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    avg_similarity = sum(r['similarity'] for r in results) / len(results)
    print(f"Avg similarity: {avg_similarity:.2%}")
    print(f"Token savings: {results[0]['teacher_tokens'] - results[0]['student_tokens']} per query")


if __name__ == "__main__":
    import sys
    checkpoint = sys.argv[1] if len(sys.argv) > 1 else "beethoven_prompt_distillation_final_checkpoint"
    evaluate_models(checkpoint)
