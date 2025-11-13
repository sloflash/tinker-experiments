#!/usr/bin/env python3
"""
Steps 7-10: Prepare Student Training Data
- Convert teacher data to student format (no long prompts)
- Create train/val splits
- Validate quality
"""

import json
import random

def prepare_training_data():
    print("=" * 80)
    print("STEPS 7-10: Preparing Student Training Data")
    print("=" * 80)

    # Step 7: Load teacher data and convert to student format
    print("\nSTEP 7: Converting to Student Format")
    print("-" * 80)

    print("Loading teacher data from teacher_data_test.jsonl...")
    with open('teacher_data_test.jsonl', 'r') as f:
        teacher_data = [json.loads(line) for line in f]

    print(f"✓ Loaded {len(teacher_data)} teacher examples")

    # Convert to student format: just question + response, NO character prompt
    student_data = []
    for item in teacher_data:
        student_example = {
            'messages': [
                {'role': 'user', 'content': item['question']},
                {'role': 'assistant', 'content': item['teacher_response']}
            ]
        }
        student_data.append(student_example)

    print(f"✓ Converted {len(student_data)} examples to student format")
    print(f"  (Removed {teacher_data[0]['prompt_tokens']} word character prompt)")

    # Step 9: Audit quality
    print("\nSTEP 9: Auditing Quality")
    print("-" * 80)

    # Check for empty responses
    empty_count = sum(1 for item in student_data if not item['messages'][1]['content'].strip())
    print(f"✓ Empty responses: {empty_count}/{len(student_data)}")

    # Check response lengths
    response_lengths = [len(item['messages'][1]['content'].split()) for item in student_data]
    avg_length = sum(response_lengths) / len(response_lengths)
    print(f"✓ Average response length: {avg_length:.1f} words")
    print(f"  Min: {min(response_lengths)} words, Max: {max(response_lengths)} words")

    # Check for duplicate responses
    responses = [item['messages'][1]['content'] for item in student_data]
    unique_responses = len(set(responses))
    print(f"✓ Unique responses: {unique_responses}/{len(responses)}")

    # Step 10: Create train/val split
    print("\nSTEP 10: Creating Train/Val Split")
    print("-" * 80)

    # Shuffle data
    random.seed(42)
    indices = list(range(len(student_data)))
    random.shuffle(indices)

    # Since we only have 10 examples, use 8 for train, 2 for val
    split_idx = int(0.8 * len(indices))
    train_indices = indices[:split_idx]
    val_indices = indices[split_idx:]

    train_data = [student_data[i] for i in train_indices]
    val_data = [student_data[i] for i in val_indices]

    # Save train.jsonl
    print(f"Saving train.jsonl ({len(train_data)} examples)...")
    with open('train.jsonl', 'w') as f:
        for item in train_data:
            f.write(json.dumps(item) + '\n')

    # Save val.jsonl
    print(f"Saving val.jsonl ({len(val_data)} examples)...")
    with open('val.jsonl', 'w') as f:
        for item in val_data:
            f.write(json.dumps(item) + '\n')

    print(f"\n✓ Training set: {len(train_data)} examples")
    print(f"✓ Validation set: {len(val_data)} examples")
    print(f"✓ Split ratio: {100*len(train_data)/len(student_data):.0f}% / {100*len(val_data)/len(student_data):.0f}%")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ Student format created: question + response (NO {teacher_data[0]['prompt_tokens']}-word prompt)")
    print(f"✓ Training data: train.jsonl ({len(train_data)} examples)")
    print(f"✓ Validation data: val.jsonl ({len(val_data)} examples)")
    print(f"✓ Quality: {unique_responses}/{len(responses)} unique responses, avg {avg_length:.0f} words")
    print(f"\n✓ Steps 7-10 complete! Ready for Step 11 (training configuration)")
    print(f"\nNOTE: This is a test run with 10 examples.")
    print(f"      For production, generate 5000+ examples using Step 8 script.")

if __name__ == "__main__":
    prepare_training_data()
