#!/usr/bin/env python3
"""Step 17: Interactive inference demo"""

import tinker
from transformers import AutoTokenizer


def interactive_demo(checkpoint_name):
    """CLI for chatting with distilled student model"""

    client = tinker.ServiceClient()
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B")

    # Load student
    training_client = client.create_lora_training_client(
        base_model="Qwen/Qwen3-4B-Instruct-2507",
        rank=32
    )
    training_client.load_state(name=checkpoint_name)
    student_client = training_client.save_weights_and_get_sampling_client(
        name=f"{checkpoint_name}_demo"
    )

    print("Interactive Beethoven Demo (Ctrl+C to exit)")
    print("=" * 60)

    while True:
        try:
            question = input("\nYou: ")
            if not question.strip():
                continue

            prompt = f"<|user|>\n{question}\n<|assistant|>\n"
            tokens = tokenizer.encode(prompt)
            model_input = tinker.types.ModelInput.from_ints(tokens)

            result = student_client.sample(
                prompt=model_input,
                sampling_params=tinker.types.SamplingParams(max_tokens=200, temperature=0.7),
                num_samples=1
            ).result()

            response = tokenizer.decode(result.sequences[0].tokens, skip_special_tokens=True)
            print(f"Beethoven: {response}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    import sys
    checkpoint = sys.argv[1] if len(sys.argv) > 1 else "beethoven_prompt_distillation_final_checkpoint"
    interactive_demo(checkpoint)
