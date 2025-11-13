#!/usr/bin/env python3
"""
STEP 6: Teacher Data Generator
Generate responses using Tinker API with full 591-word character prompt
"""

import os
import json
import tinker
from transformers import AutoTokenizer
from character_prompts import get_character_prompt, count_tokens_approximate

def generate_teacher_data(num_examples=10, output_file="teacher_data_test.jsonl"):
    """
    Generate teacher responses with full character prompt.
    This demonstrates the baseline (expensive) approach.
    """
    print("=" * 80)
    print("STEP 6: Generating Teacher Data")
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
        # Initialize service client
        client = tinker.ServiceClient()
        print("✓ Tinker client initialized")

        # Create sampling client for the teacher model
        # Note: Using Qwen2.5-7B for teacher (larger models don't support sampling in Tinker)
        # For production, you'd train from better teacher, but this demonstrates the technique
        print("  Creating sampling client for Qwen/Qwen2.5-7B...")
        sampling_client = client.create_sampling_client(
            base_model="Qwen/Qwen2.5-7B"
        )
        print("  ✓ Sampling client created")

    except Exception as e:
        print(f"✗ Error initializing client: {e}")
        return

    # Get character prompt
    character_prompt = get_character_prompt("Beethoven")
    prompt_tokens = count_tokens_approximate(character_prompt)
    print(f"\n✓ Character prompt loaded: {prompt_tokens} words")

    # Define diverse test questions
    test_questions = [
        "What inspired you to compose the Ninth Symphony?",
        "How did your deafness affect your compositional process?",
        "What was your relationship with your teacher Joseph Haydn?",
        "Why did you dedicate and then un-dedicate the Eroica Symphony to Napoleon?",
        "What do you think about Mozart's music?",
        "Can you describe a typical day in Vienna?",
        "What role does nature play in your compositions?",
        "How do you feel about the aristocratic patronage system?",
        "What emotions were you trying to convey in the Moonlight Sonata?",
        "What advice would you give to young composers?"
    ][:num_examples]

    # Generate teacher responses
    print(f"\nGenerating {len(test_questions)} teacher responses...")
    print("=" * 80)

    results = []
    for idx, question in enumerate(test_questions, 1):
        print(f"\n[{idx}/{len(test_questions)}] Question: {question}")

        # Construct full prompt (system prompt + user question)
        full_prompt = f"{character_prompt}\n\nUser: {question}\nBeethoven:"

        try:
            # Generate response using Tinker API
            print("  Generating response...")

            # Tokenize the prompt
            input_ids = tokenizer.encode(full_prompt, add_special_tokens=True)

            # Convert to ModelInput
            prompt_input = tinker.types.ModelInput.from_ints(input_ids)

            # Sample from the model
            sampling_params = tinker.types.SamplingParams(
                max_tokens=300,
                temperature=0.7
            )

            future = sampling_client.sample(
                prompt=prompt_input,
                sampling_params=sampling_params,
                num_samples=1
            )

            # Get result
            result_obj = future.result()
            # Decode the generated tokens
            generated_tokens = result_obj.sequences[0].tokens
            teacher_response = tokenizer.decode(generated_tokens, skip_special_tokens=True)

            # Save result
            result = {
                "question": question,
                "full_prompt": full_prompt,
                "teacher_response": teacher_response,
                "prompt_tokens": prompt_tokens,
                "total_prompt_length": count_tokens_approximate(full_prompt)
            }
            results.append(result)

            print(f"  ✓ Response: {teacher_response[:100]}...")
            print(f"  ✓ Prompt tokens: {result['total_prompt_length']} words")

        except Exception as e:
            print(f"  ✗ Error generating response: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Save to JSONL file
    print(f"\n{'=' * 80}")
    print(f"Saving {len(results)} results to {output_file}...")

    with open(output_file, 'w') as f:
        for result in results:
            f.write(json.dumps(result) + '\n')

    print(f"✓ Saved to {output_file}")

    # Summary statistics
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ Examples generated: {len(results)}")
    print(f"✓ Average prompt length: {sum(r['total_prompt_length'] for r in results) / len(results):.1f} words")
    print(f"✓ Character prompt overhead: {prompt_tokens} words per query")
    print(f"\n✓ Step 6 complete! Ready for Step 7 (create student format converter)")


if __name__ == "__main__":
    import sys
    # Generate test examples (default 10, or pass number as argument)
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    generate_teacher_data(num_examples=num)
