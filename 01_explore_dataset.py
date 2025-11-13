#!/usr/bin/env python3
"""
STEP 3: Explore Character LLM Dataset
Load fnlp/character-llm-data from HuggingFace and inspect schema
"""

from datasets import load_dataset
import json

def explore_dataset():
    print("=" * 80)
    print("STEP 3: Exploring Character LLM Dataset")
    print("=" * 80)

    # Load the dataset - try different configs
    print("\nLoading fnlp/character-llm-data from HuggingFace...")
    print("Note: This dataset has mixed schemas, trying 'prompted' subfolder...")
    try:
        # Load the prompted/agent dialogue format (prompt/output schema)
        from datasets import load_dataset
        import os

        # Try loading specific file patterns
        dataset = load_dataset("fnlp/character-llm-data", data_files="prompted/prompted_agent_dialogue_*.jsonl")
        print(f"✓ Dataset loaded successfully (prompted format)!")
    except Exception as e:
        print(f"Error with prompted format: {e}")
        print("\nTrying to load all files from 'prompted' directory...")
        try:
            dataset = load_dataset("fnlp/character-llm-data", data_dir="prompted")
            print(f"✓ Dataset loaded successfully!")
        except Exception as e2:
            print(f"✗ Error loading dataset: {e2}")
            return

    # Inspect structure
    print(f"\nDataset splits available: {list(dataset.keys())}")

    # Get the first split (usually 'train')
    split_name = list(dataset.keys())[0]
    data = dataset[split_name]

    print(f"\nUsing split: '{split_name}'")
    print(f"Total examples: {len(data)}")
    print(f"Column names: {data.column_names}")

    # Print first 5 Beethoven examples
    print("\n" + "=" * 80)
    print("SAMPLE BEETHOVEN EXAMPLES (First 5)")
    print("=" * 80)

    beethoven_count = 0
    for idx, example in enumerate(data):
        # Check if this example is about Beethoven
        example_text = json.dumps(example).lower()
        if 'beethoven' in example_text:
            beethoven_count += 1
            print(f"\n--- Beethoven Example #{beethoven_count} (Index {idx}) ---")
            for key, value in example.items():
                print(f"{key}: {value[:200] if isinstance(value, str) and len(value) > 200 else value}")

            if beethoven_count >= 5:
                break

    # Identify schema format
    print("\n" + "=" * 80)
    print("SCHEMA ANALYSIS")
    print("=" * 80)

    if 'dialogue' in data.column_names and 'setting' in data.column_names:
        print("✓ Schema type: DIALOGUE-BASED (setting/dialogue/background)")
    elif 'prompt' in data.column_names and 'output' in data.column_names:
        print("✓ Schema type: PROMPT-BASED (prompt/output)")
    else:
        print(f"✓ Schema type: CUSTOM ({data.column_names})")

    # Count available characters
    print("\n" + "=" * 80)
    print("AVAILABLE CHARACTERS")
    print("=" * 80)

    characters = set()
    for example in data.select(range(min(1000, len(data)))):  # Sample first 1000
        example_text = json.dumps(example).lower()
        if 'beethoven' in example_text:
            characters.add('Beethoven')
        if 'newton' in example_text:
            characters.add('Newton')
        if 'caesar' in example_text:
            characters.add('Caesar')
        if 'socrates' in example_text:
            characters.add('Socrates')
        if 'cleopatra' in example_text:
            characters.add('Cleopatra')

    print(f"Characters found in first 1000 examples: {sorted(characters)}")
    print(f"\n✓ Step 3 complete! Ready for Step 4 (character data validation)")

if __name__ == "__main__":
    explore_dataset()
