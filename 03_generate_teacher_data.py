#!/usr/bin/env python3
"""
STEP 6: Teacher Data Generator (Async - following tinker-cookbook pattern)
Generate responses using Tinker API with full 591-word character prompt
"""

import os
import json
import asyncio
import tinker
from transformers import AutoTokenizer
from character_prompts import get_character_prompt, count_tokens_approximate
import time

# Load .env if exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from tqdm.asyncio import tqdm_asyncio
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

async def generate_teacher_data(num_examples=10, output_file="teacher_data_test.jsonl", checkpoint_every=100):
    """
    Generate teacher responses with full character prompt.
    This demonstrates the baseline (expensive) approach.

    Args:
        num_examples: Number of examples to generate
        output_file: Output JSONL file path
        checkpoint_every: Save progress every N examples (for recovery)
    """
    print("=" * 80)
    print("STEP 6: Generating Teacher Data (Large Scale)")
    print("=" * 80)
    print(f"Target: {num_examples} examples")
    print(f"Checkpoint frequency: every {checkpoint_every} examples")
    print("=" * 80)

    # Verify API key is set
    api_key = os.environ.get("TINKER_API_KEY")
    if not api_key:
        print("✗ Error: TINKER_API_KEY environment variable not set")
        print("  Please run: export TINKER_API_KEY='your-key'")
        return

    print(f"✓ API key found: {api_key[:15]}...")

    # Load tokenizer - using Qwen as fallback since Llama is gated
    print("\nLoading tokenizer...")
    try:
        # Try Llama tokenizer first
        tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-70B-Instruct")
        print("✓ Llama tokenizer loaded")
    except Exception as e:
        # Fallback to Qwen (not gated)
        print("Note: Llama tokenizer unavailable (gated model)")
        print("  Using Qwen/Qwen2.5-7B tokenizer (similar architecture)...")
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B")
        print("✓ Qwen tokenizer loaded")

    # Initialize Tinker client
    print("\nInitializing Tinker ServiceClient...")
    try:
        client = tinker.ServiceClient()
        print("✓ Client initialized")

        print("  Creating async sampling client for Qwen/Qwen3-30B-A3B...")
        sampling_client = client.create_sampling_client(
            base_model="Qwen/Qwen3-30B-A3B"
        )
        print("  ✓ Async sampling client created")

    except Exception as e:
        print(f"✗ Error initializing client: {e}")
        return

    # Get character prompt
    character_prompt = get_character_prompt("Beethoven")
    prompt_tokens = count_tokens_approximate(character_prompt)
    print(f"\n✓ Character prompt loaded: {prompt_tokens} words")

    # Load existing progress if any
    existing_results = []
    if os.path.exists(output_file):
        print(f"\n✓ Found existing file: {output_file}")
        with open(output_file, 'r') as f:
            for line in f:
                existing_results.append(json.loads(line))
        print(f"  Loaded {len(existing_results)} existing examples")
        print(f"  Remaining: {num_examples - len(existing_results)}")

        if len(existing_results) >= num_examples:
            print("✓ Target already reached!")
            return

    # Define diverse question templates for large-scale generation
    question_templates = [
        # Biographical
        "What inspired you to compose the {composition}?",
        "Tell me about your experience creating {composition}.",
        "How did your life circumstances influence {composition}?",
        "What was going through your mind when you wrote {composition}?",

        # Musical Philosophy
        "What role does {concept} play in your compositions?",
        "How do you approach {concept} in your music?",
        "What does {concept} mean to you as a composer?",
        "Can you explain your views on {concept}?",

        # Historical Context
        "What was your relationship with {person}?",
        "How did {person} influence your work?",
        "What do you think about {person}'s music?",
        "Can you describe your interactions with {person}?",

        # Creative Process
        "How did your deafness affect your {aspect}?",
        "Can you describe your {aspect} process?",
        "What role does {aspect} play in your creative work?",

        # Personal
        "How do you feel about {topic}?",
        "What are your thoughts on {topic}?",
        "Can you describe a typical day in {location}?",
        "What advice would you give about {topic}?",
    ]

    # Substitution values for templates
    compositions = [
        "Ninth Symphony", "Eroica Symphony", "Fifth Symphony", "Sixth Symphony (Pastoral)",
        "Moonlight Sonata", "Pathétique Sonata", "Appassionata Sonata", "Waldstein Sonata",
        "Piano Concerto No. 5 (Emperor)", "Violin Concerto", "Missa Solemnis", "Fidelio",
        "String Quartet No. 14", "Hammerklavier Sonata", "Diabelli Variations"
    ]

    concepts = [
        "nature", "emotion", "form", "harmony", "counterpoint", "development",
        "freedom", "heroism", "struggle", "triumph", "improvisation", "variation"
    ]

    people = [
        "Joseph Haydn", "Wolfgang Amadeus Mozart", "Napoleon Bonaparte",
        "Archduke Rudolf", "Prince Lichnowsky", "Count Waldstein", "Goethe",
        "Ferdinand Ries", "Carl Czerny", "Ignaz Schuppanzigh"
    ]

    aspects = [
        "compositional process", "approach to form", "use of orchestration",
        "approach to development", "understanding of harmony"
    ]

    topics = [
        "the aristocratic patronage system", "the French Revolution", "deafness",
        "young composers", "musical education", "the role of art in society",
        "the relationship between nature and music", "improvisation"
    ]

    locations = ["Vienna", "Bonn", "Heiligenstadt", "Baden"]

    # Generate diverse questions
    import random
    random.seed(42)  # For reproducibility

    questions = []
    for template in question_templates:
        if '{composition}' in template:
            for comp in compositions:
                questions.append(template.format(composition=comp))
        elif '{concept}' in template:
            for concept in concepts:
                questions.append(template.format(concept=concept))
        elif '{person}' in template:
            for person in people:
                questions.append(template.format(person=person))
        elif '{aspect}' in template:
            for aspect in aspects:
                questions.append(template.format(aspect=aspect))
        elif '{topic}' in template:
            for topic in topics:
                questions.append(template.format(topic=topic))
        elif '{location}' in template:
            for location in locations:
                questions.append(template.format(location=location))

    # Shuffle and select needed questions
    random.shuffle(questions)

    # If we need more questions, cycle through
    needed = num_examples - len(existing_results)
    selected_questions = []
    while len(selected_questions) < needed:
        selected_questions.extend(questions)
    selected_questions = selected_questions[:needed]

    print(f"\n✓ Generated {len(selected_questions)} unique questions from templates")

    # Generate teacher responses with ASYNC (following cookbook pattern)
    print(f"\nGenerating {len(selected_questions)} teacher responses (async)...")
    print("=" * 80)

    results = existing_results.copy()
    successful = 0
    failed = 0
    start_time = time.time()

    # Define async sample function
    async def sample_one(question):
        full_prompt = f"{character_prompt}\n\nUser: {question}\nBeethoven:"
        input_ids = tokenizer.encode(full_prompt, add_special_tokens=True)
        prompt_input = tinker.types.ModelInput.from_ints(input_ids)

        sampling_params = tinker.types.SamplingParams(
            max_tokens=300,
            temperature=0.7
        )

        result_obj = await sampling_client.sample_async(
            prompt=prompt_input,
            sampling_params=sampling_params,
            num_samples=1
        )

        generated_tokens = result_obj.sequences[0].tokens
        teacher_response = tokenizer.decode(generated_tokens, skip_special_tokens=True)

        return {
            "question": question,
            "full_prompt": full_prompt,
            "teacher_response": teacher_response,
            "prompt_tokens": prompt_tokens,
            "total_prompt_length": count_tokens_approximate(full_prompt)
        }

    # Execute all coroutines concurrently (cookbook pattern)
    tasks = [sample_one(q) for q in selected_questions]

    if HAS_TQDM:
        # Use tqdm_asyncio for progress
        for coro in tqdm_asyncio.as_completed(tasks, total=len(tasks)):
            try:
                result = await coro
                results.append(result)
                successful += 1

                # Checkpoint every N examples
                if len(results) % checkpoint_every == 0:
                    with open(output_file, 'w') as f:
                        for r in results:
                            f.write(json.dumps(r) + '\n')
            except Exception as e:
                failed += 1
                print(f"Error: {e}")
    else:
        # Fallback without tqdm
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in batch_results:
            if isinstance(result, Exception):
                failed += 1
                print(f"Error: {result}")
            else:
                results.append(result)
                successful += 1

    total_time = time.time() - start_time

    # Final save to JSONL file
    print(f"\n{'=' * 80}")
    print(f"Final save: {len(results)} results to {output_file}...")

    with open(output_file, 'w') as f:
        for result in results:
            f.write(json.dumps(result) + '\n')

    print(f"✓ Saved to {output_file}")

    # Summary statistics
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ Total examples: {len(results)}")
    print(f"✓ Successful: {successful}")
    print(f"✓ Failed: {failed}")
    if len(results) > 0:
        print(f"✓ Average prompt length: {sum(r['total_prompt_length'] for r in results) / len(results):.1f} words")
    print(f"✓ Character prompt overhead: {prompt_tokens} words per query")
    print(f"✓ Success rate: {successful/(successful+failed)*100:.1f}%")
    print(f"✓ Total time: {total_time:.1f}s ({total_time/successful:.2f}s/example)")
    print(f"\n✓ Step 6/8 complete! Ready for Step 7/10 (prepare student format)")


if __name__ == "__main__":
    import sys
    # Generate test examples (default 10, or pass number as argument)
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    asyncio.run(generate_teacher_data(num_examples=num))
