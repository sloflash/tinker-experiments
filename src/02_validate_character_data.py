#!/usr/bin/env python3
"""
STEP 4: Validate Character Data Quality
Filter dataset to Beethoven and validate completeness, count examples
"""

from datasets import load_dataset
import json

def validate_character_data():
    print("=" * 80)
    print("STEP 4: Validating Character Data Quality")
    print("=" * 80)

    # Load the Beethoven dataset
    print("\nLoading Beethoven data from fnlp/character-llm-data...")
    dataset = load_dataset("fnlp/character-llm-data", data_files="prompted/prompted_agent_dialogue_*.jsonl")
    data = dataset['train']

    print(f"✓ Dataset loaded: {len(data)} total examples")

    # Filter to Beethoven (all examples are Beethoven in this specific file)
    beethoven_examples = []
    for example in data:
        example_text = json.dumps(example).lower()
        if 'beethoven' in example_text:
            beethoven_examples.append(example)

    print(f"\n✓ Beethoven examples found: {len(beethoven_examples)}")

    # Check for completeness (no empty fields)
    print("\n" + "=" * 80)
    print("DATA QUALITY CHECKS")
    print("=" * 80)

    empty_prompts = 0
    empty_outputs = 0
    for example in beethoven_examples:
        if not example.get('prompt') or len(example['prompt'].strip()) == 0:
            empty_prompts += 1
        if not example.get('output') or len(example['output'].strip()) == 0:
            empty_outputs += 1

    print(f"\n✓ Empty prompts: {empty_prompts}")
    print(f"✓ Empty outputs: {empty_outputs}")
    print(f"✓ Complete examples: {len(beethoven_examples) - max(empty_prompts, empty_outputs)}")

    # Calculate statistics
    print("\n" + "=" * 80)
    print("STATISTICS")
    print("=" * 80)

    prompt_lengths = [len(ex['prompt'].split()) for ex in beethoven_examples]
    output_lengths = [len(ex['output'].split()) for ex in beethoven_examples]

    print(f"\nPrompt statistics:")
    print(f"  Average length: {sum(prompt_lengths) / len(prompt_lengths):.1f} words")
    print(f"  Min length: {min(prompt_lengths)} words")
    print(f"  Max length: {max(prompt_lengths)} words")

    print(f"\nOutput statistics:")
    print(f"  Average length: {sum(output_lengths) / len(output_lengths):.1f} words")
    print(f"  Min length: {min(output_lengths)} words")
    print(f"  Max length: {max(output_lengths)} words")

    # Check for unique sources
    sources = [ex.get('source', 'unknown') for ex in beethoven_examples]
    unique_sources = set(sources)
    print(f"\nUnique sources: {len(unique_sources)}")
    print(f"Source distribution (top 10):")
    from collections import Counter
    source_counts = Counter(sources)
    for source, count in source_counts.most_common(10):
        print(f"  {source}: {count}")

    # Check for character-specific keywords
    print("\n" + "=" * 80)
    print("CHARACTER CONSISTENCY CHECK")
    print("=" * 80)

    keywords = ['music', 'symphony', 'compose', 'deaf', 'vienna', 'haydn', 'piano', 'sonata']
    keyword_counts = {kw: 0 for kw in keywords}

    for example in beethoven_examples:
        output_lower = example['output'].lower()
        for keyword in keywords:
            if keyword in output_lower:
                keyword_counts[keyword] += 1

    print(f"\nKeyword presence in outputs:")
    for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(beethoven_examples)) * 100
        print(f"  '{keyword}': {count} examples ({percentage:.1f}%)")

    overall_keyword_presence = sum(1 for ex in beethoven_examples if any(kw in ex['output'].lower() for kw in keywords))
    overall_percentage = (overall_keyword_presence / len(beethoven_examples)) * 100
    print(f"\n✓ Examples with at least one character keyword: {overall_keyword_presence} ({overall_percentage:.1f}%)")

    # Final summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ Total Beethoven examples: {len(beethoven_examples)}")
    print(f"✓ Data quality: {'PASS' if empty_prompts == 0 and empty_outputs == 0 else 'NEEDS REVIEW'}")
    print(f"✓ Character consistency: {'EXCELLENT' if overall_percentage > 80 else 'GOOD' if overall_percentage > 60 else 'NEEDS IMPROVEMENT'}")
    print(f"\n✓ Step 4 complete! Ready for Step 5 (design character system prompt)")

if __name__ == "__main__":
    validate_character_data()
