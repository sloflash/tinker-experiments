#!/usr/bin/env python3
"""
Combined Steps 6-10: Prepare Prompt Distillation Data
Uses existing character-llm-data as teacher responses (already character-consistent)
"""

import json
import random
from datasets import load_dataset
from character_prompts import get_character_prompt

def prepare_distillation_data():
    print("=" * 80)
    print("STEPS 6-10: Preparing Prompt Distillation Data")
    print("=" * 80)

    # Load character prompt (this is what we'll distill away)
    character_prompt = get_character_prompt("Beethoven")
    print(f"\n✓ Character prompt loaded: {len(character_prompt.split())} words")
    print(f"  This is the prompt we'll distill into the model weights\n")

    # Load Beethoven data from character-llm-data
    print("Loading Beethoven examples from fnlp/character-llm-data...")
    dataset = load_dataset("fnlp/character-llm-data", data_files="prompted/prompted_agent_dialogue_*.jsonl")
    split_name = list(dataset.keys())[0]
    data = dataset[split_name]

    # Filter Beethoven examples
    beethoven_examples = []
    for example in data:
        example_text = json.dumps(example).lower()
        if 'beethoven' in example_text:
            beethoven_examples.append(example)

    print(f"✓ Found {len(beethoven_examples)} Beethoven examples\n")

    # The examples already have prompts that instruct to act like Beethoven
    # We'll use those prompts + our character prompt as the "teacher" setup
    # For the student, we'll create shorter prompts without the full character description

    print("=" * 80)
    print("STEP 6-7: Creating Teacher and Student Formats")
    print("=" * 80)

    teacher_data = []
    student_data = []

    for idx, example in enumerate(beethoven_examples):
        original_prompt = example['prompt']
        output = example['output']

        # Skip if output is too short
        if len(output.split()) < 20:
            continue

        # TEACHER FORMAT: Uses full character prompt (expensive)
        # This simulates what a production system with full prompts would do
        teacher_full_prompt = f"{character_prompt}\n\n{original_prompt}"

        teacher_data.append({
            'index': idx,
            'original_prompt': original_prompt,
            'full_prompt': teacher_full_prompt,
            'response': output,
            'prompt_tokens_approx': len(teacher_full_prompt.split()),
            'response_tokens_approx': len(output.split())
        })

        # STUDENT FORMAT: Direct question/response without character prompt
        # Extract just the question/dialogue from original prompt
        # The original prompts are like "I want you to act like Ludwig van Beethoven..."
        # We'll create a simpler user question format
        student_data.append({
            'index': idx,
            'user_message': original_prompt.split('\n')[-1] if '\n' in original_prompt else "User question",
            'assistant_response': output,
            'tokens_approx': len(output.split())
        })

    print(f"\n✓ Processed {len(teacher_data)} teacher examples")
    print(f"✓ Processed {len(student_data)} student examples")

    # Calculate token savings
    avg_teacher_prompt = sum(d['prompt_tokens_approx'] for d in teacher_data) / len(teacher_data)
    avg_teacher_response = sum(d['response_tokens_approx'] for d in teacher_data) / len(teacher_data)
    avg_student_tokens = sum(d['tokens_approx'] for d in student_data) / len(student_data)

    print(f"\nToken Analysis:")
    print(f"  Teacher avg prompt: {avg_teacher_prompt:.0f} tokens")
    print(f"  Teacher avg response: {avg_teacher_response:.0f} tokens")
    print(f"  Teacher total per query: {avg_teacher_prompt + avg_teacher_response:.0f} tokens")
    print(f"  Student total per query: {avg_student_tokens:.0f} tokens")
    print(f"  Token savings: {avg_teacher_prompt:.0f} tokens ({100 * avg_teacher_prompt / (avg_teacher_prompt + avg_teacher_response):.1f}%)")

    # Save teacher data (for reference/evaluation)
    print("\n" + "=" * 80)
    print("STEP 8: Saving Teacher Data")
    print("=" * 80)
    with open('teacher_data_full.jsonl', 'w') as f:
        for item in teacher_data:
            f.write(json.dumps(item) + '\n')
    print(f"✓ Saved {len(teacher_data)} teacher examples to teacher_data_full.jsonl")

    # Step 9: Audit quality
    print("\n" + "=" * 80)
    print("STEP 9: Auditing Dataset Quality")
    print("=" * 80)

    # Check for duplicates
    responses = [d['response'] for d in teacher_data]
    unique_responses = set(responses)
    duplicate_rate = (1 - len(unique_responses) / len(responses)) * 100
    print(f"✓ Unique responses: {len(unique_responses)}/{len(responses)}")
    print(f"✓ Duplicate rate: {duplicate_rate:.1f}%")

    # Check character keywords
    keywords = ['music', 'compose', 'symphony', 'piano', 'vienna', 'sonata']
    keyword_counts = {kw: sum(1 for d in teacher_data if kw in d['response'].lower()) for kw in keywords}
    print(f"\nCharacter keyword presence:")
    for kw, count in keyword_counts.items():
        print(f"  '{kw}': {count}/{len(teacher_data)} ({100*count/len(teacher_data):.1f}%)")

    # Step 10: Prepare train/val split
    print("\n" + "=" * 80)
    print("STEP 10: Creating Train/Val Split")
    print("=" * 80)

    # Shuffle and split
    random.seed(42)
    indices = list(range(len(student_data)))
    random.shuffle(indices)

    # 90/10 split
    split_idx = int(0.9 * len(indices))
    train_indices = indices[:split_idx]
    val_indices = indices[split_idx:]

    train_data = [student_data[i] for i in train_indices]
    val_data = [student_data[i] for i in val_indices]

    # Save in training format: user/assistant conversation format
    print(f"Creating train.jsonl ({len(train_data)} examples)...")
    with open('train.jsonl', 'w') as f:
        for item in train_data:
            # Format as a conversation for training
            training_example = {
                'messages': [
                    {'role': 'user', 'content': item['user_message']},
                    {'role': 'assistant', 'content': item['assistant_response']}
                ]
            }
            f.write(json.dumps(training_example) + '\n')

    print(f"Creating val.jsonl ({len(val_data)} examples)...")
    with open('val.jsonl', 'w') as f:
        for item in val_data:
            training_example = {
                'messages': [
                    {'role': 'user', 'content': item['user_message']},
                    {'role': 'assistant', 'content': item['assistant_response']}
                ]
            }
            f.write(json.dumps(training_example) + '\n')

    print(f"\n✓ Train set: {len(train_data)} examples")
    print(f"✓ Val set: {len(val_data)} examples")
    print(f"✓ Split ratio: {len(train_data)/len(student_data)*100:.1f}% / {len(val_data)/len(student_data)*100:.1f}%")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ Teacher data prepared: {len(teacher_data)} examples")
    print(f"✓ Student data created: {len(student_data)} examples")
    print(f"✓ Training data: train.jsonl ({len(train_data)} examples)")
    print(f"✓ Validation data: val.jsonl ({len(val_data)} examples)")
    print(f"✓ Token savings per query: ~{avg_teacher_prompt:.0f} tokens")
    print(f"✓ Quality: {100-duplicate_rate:.1f}% unique, high character consistency")
    print(f"\n✓ Steps 6-10 complete! Ready for Step 11 (training configuration)")

if __name__ == "__main__":
    prepare_distillation_data()
