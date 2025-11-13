#!/usr/bin/env python3
"""
STEP 12: Train Student Model with Tinker API
Implements supervised fine-tuning using forward_backward() and optim_step()
Based on tinker-api skill examples
"""

import os
import json
import yaml
import numpy as np
import time
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass
from transformers import AutoTokenizer
import tinker
from tinker import types

# Load .env if exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class TrainingExample:
    """Simple training example structure for Tinker API"""
    model_input: any
    loss_fn_inputs: dict

@contextmanager
def timed(name, metrics=None):
    """Context manager for timing operations"""
    start = time.time()
    yield
    duration = time.time() - start
    if metrics is not None:
        metrics[name] = duration
    print(f"  ⏱️  {name}: {duration:.2f}s")

def load_config(config_path="training_config.yaml"):
    """Load training configuration"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def load_jsonl_data(file_path):
    """Load JSONL training data"""
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def prepare_training_examples(data, tokenizer, max_length=2048):
    """
    Prepare examples for Tinker API training following tinker-cookbook format.
    Format: user/assistant messages with loss weights and target tokens
    """
    processed = []

    for example in data:
        messages = example['messages']

        # Format as conversation
        conversation = ""
        for msg in messages:
            role = msg['role']
            content = msg['content']
            conversation += f"<|{role}|>\n{content}\n"

        # Tokenize
        tokens = tokenizer.encode(conversation, max_length=max_length, truncation=True)

        # Find where assistant response starts (to mask prompt in loss)
        # We want to train on assistant responses, not user prompts
        prompt_text = f"<|user|>\n{messages[0]['content']}\n<|assistant|>\n"
        prompt_tokens = tokenizer.encode(prompt_text)
        prompt_len = len(prompt_tokens)

        # Create loss weights (0 for prompt, 1 for response)
        # This ensures we only train on the assistant's response
        weights = [0.0] * prompt_len + [1.0] * (len(tokens) - prompt_len)

        # Following tinker-cookbook format from datum_from_tokens_weights:
        # - model_input uses tokens[:-1] (all except last)
        # - target_tokens uses tokens[1:] (all except first)
        # - weights uses weights[1:] (shifted to match target_tokens)
        # - loss_fn_inputs must include BOTH weights and target_tokens

        input_tokens = tokens[:-1]
        target_tokens = tokens[1:]
        shifted_weights = weights[1:]

        model_input = types.ModelInput.from_ints(input_tokens)
        training_example = types.Datum(
            model_input=model_input,
            loss_fn_inputs={
                'weights': types.TensorData(
                    data=shifted_weights,
                    dtype='float32',
                    shape=[len(shifted_weights)]
                ),
                'target_tokens': types.TensorData(
                    data=target_tokens,
                    dtype='int64',
                    shape=[len(target_tokens)]
                )
            }
        )
        processed.append(training_example)

    return processed

def calculate_loss(fwdbwd_result, processed_examples):
    """
    Calculate weighted mean negative log likelihood.
    Based on tinker_cookbook.supervised.common.compute_mean_nll
    """
    total_weighted_logprobs = 0.0
    total_weights = 0.0

    # Iterate over each example in the batch
    for output, example in zip(fwdbwd_result.loss_fn_outputs, processed_examples):
        # Extract logprobs and weights from TensorData objects
        logprobs = np.array(output['logprobs'].data)
        weights = np.array(example.loss_fn_inputs['weights'].data)

        # Accumulate weighted logprobs and total weights
        total_weighted_logprobs += np.dot(logprobs, weights)
        total_weights += np.sum(weights)

    # Compute mean negative log likelihood
    if total_weights == 0:
        return float('nan')

    return float(-total_weighted_logprobs / total_weights)

def train_student_model(config_path="training_config.yaml"):
    """Main training function"""
    print("=" * 80)
    print("STEP 12-13: Training Student Model with Tinker API")
    print("=" * 80)

    # Load configuration
    print("\nLoading configuration...")
    config = load_config(config_path)
    print(f"✓ Config loaded from {config_path}")

    # Extract config values
    base_model = config['model']['base_model']
    lora_rank = config['model']['lora_rank']
    lora_alpha = config['model'].get('lora_alpha', lora_rank * 2)
    learning_rate = config['training']['learning_rate']
    num_steps = config['training']['num_steps']
    batch_size = config['training']['batch_size']
    save_every = config['checkpointing']['save_every']
    log_every = config['logging']['log_every']

    print(f"  Model: {base_model}")
    print(f"  LoRA rank: {lora_rank}, alpha: {lora_alpha}")
    print(f"  Learning rate: {learning_rate}")
    print(f"  Training steps: {num_steps}")

    # Create output directories
    checkpoint_dir = Path(config['checkpointing']['output_dir'])
    log_dir = Path(config['logging']['log_dir'])
    checkpoint_dir.mkdir(exist_ok=True)
    log_dir.mkdir(exist_ok=True)
    print(f"✓ Output directories created")

    # Initialize Tinker client
    print("\nInitializing Tinker client...")
    api_key = os.environ.get("TINKER_API_KEY")
    if not api_key:
        raise ValueError("TINKER_API_KEY environment variable not set")

    service_client = tinker.ServiceClient()
    print("✓ Service client initialized")

    # Create LoRA training client
    print(f"Creating LoRA training client for {base_model}...")
    training_client = service_client.create_lora_training_client(
        base_model=base_model,
        rank=lora_rank
    )
    print("✓ Training client created")

    # Load tokenizer
    print(f"\nLoading tokenizer...")
    try:
        # Try to load model's own tokenizer
        tokenizer = AutoTokenizer.from_pretrained(base_model)
        print(f"✓ Tokenizer loaded for {base_model}")
    except:
        # Fallback to Qwen (not gated) as it's compatible
        print(f"Note: {base_model} tokenizer unavailable (gated), using Qwen/Qwen2.5-7B tokenizer")
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B")
        print("✓ Qwen tokenizer loaded")

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load training data
    print("\nLoading training data...")
    train_data = load_jsonl_data(config['data']['train_file'])
    val_data = load_jsonl_data(config['data']['val_file'])
    print(f"✓ Train examples: {len(train_data)}")
    print(f"✓ Val examples: {len(val_data)}")

    # Prepare training examples
    print("\nPreparing training examples...")
    train_examples = prepare_training_examples(
        train_data,
        tokenizer,
        max_length=config['data']['max_seq_length']
    )
    print(f"✓ Prepared {len(train_examples)} training examples")

    # Training loop with timing and pipelining
    print("\n" + "=" * 80)
    print("STARTING TRAINING")
    print("=" * 80)

    loss_history = []
    step_times = []
    total_start = time.time()

    for step in range(num_steps):
        step_start = time.time()
        step_metrics = {}

        # Get batch (cycle through data if needed)
        with timed("batch_prep", step_metrics):
            batch_idx = step % len(train_examples)
            batch = [train_examples[batch_idx]]  # Single example per step for small dataset

        # Submit forward-backward pass and optimizer step together (per tinker-api best practice)
        # This enables request pipelining for better throughput
        with timed("submit_ops", step_metrics):
            fwdbwd_future = training_client.forward_backward(batch, "cross_entropy")
            optim_future = training_client.optim_step(
                types.AdamParams(
                    learning_rate=learning_rate,
                    beta1=config['training']['beta1'],
                    beta2=config['training']['beta2'],
                    eps=config['training']['eps']
                )
            )

        # Wait for results (async clock)
        with timed("fwd_bwd_wait", step_metrics):
            fwdbwd_result = fwdbwd_future.result()

        with timed("optim_wait", step_metrics):
            optim_result = optim_future.result()

        # Calculate loss
        with timed("loss_calc", step_metrics):
            loss = calculate_loss(fwdbwd_result, batch)
            loss_history.append(loss)

        step_duration = time.time() - step_start
        step_times.append(step_duration)
        step_metrics['total_step'] = step_duration

        # Log progress
        if step % log_every == 0 or step == num_steps - 1:
            avg_loss = np.mean(loss_history[-log_every:]) if len(loss_history) >= log_every else np.mean(loss_history)
            avg_time = np.mean(step_times[-log_every:]) if len(step_times) >= log_every else np.mean(step_times)
            print(f"Step {step:4d}/{num_steps}: loss={loss:.4f}, avg_loss={avg_loss:.4f}, step_time={step_duration:.2f}s")

            # Write to log file
            with open(log_dir / "loss.txt", 'a') as f:
                f.write(f"{step},{loss:.6f},{avg_loss:.6f},{step_duration:.4f}\n")

        # Save checkpoint
        if step % save_every == 0 and step > 0:
            print(f"  → Saving checkpoint at step {step}...")
            checkpoint_name = f"beethoven_step_{step}"
            training_client.save_state(name=checkpoint_name)
            print(f"  ✓ Checkpoint saved as '{checkpoint_name}'")

    # Save final checkpoint and weights for sampling
    print(f"\nSaving final checkpoint...")
    final_checkpoint_name = f"{config['metadata']['experiment_name']}_final_checkpoint"
    training_client.save_state(name=final_checkpoint_name)
    print(f"✓ Final checkpoint saved as '{final_checkpoint_name}'")

    print(f"\nSaving final model weights for sampling...")
    final_model_name = f"{config['metadata']['experiment_name']}_final"
    sampling_client = training_client.save_weights_and_get_sampling_client(name=final_model_name)
    print(f"✓ Final model saved as '{final_model_name}'")

    # Training summary
    total_duration = time.time() - total_start
    print("\n" + "=" * 80)
    print("TRAINING COMPLETE")
    print("=" * 80)
    print(f"✓ Total steps: {num_steps}")
    print(f"✓ Final loss: {loss_history[-1]:.4f}")
    print(f"✓ Average loss (last 10): {np.mean(loss_history[-10:]):.4f}")
    print(f"✓ Total training time: {total_duration:.2f}s ({total_duration/60:.2f}min)")
    print(f"✓ Average time/step: {np.mean(step_times):.2f}s")
    print(f"✓ Checkpoints saved to: {checkpoint_dir}")
    print(f"✓ Logs saved to: {log_dir}")
    print(f"\n✓ Step 12-13 complete! Ready for Step 14 (evaluation)")

if __name__ == "__main__":
    train_student_model()
