#!/usr/bin/env python3
"""Step 19: Export model with download"""

import tinker


def export_model(checkpoint_name, output_file="model-checkpoint.tar.gz"):
    """Download final model checkpoint archive"""

    client = tinker.ServiceClient()

    # Create REST client for downloading
    rest_client = client.create_rest_client()

    # Load the checkpoint to get its path
    training_client = client.create_lora_training_client(
        base_model="Qwen/Qwen3-4B-Instruct-2507",
        rank=32
    )
    training_client.load_state(name=checkpoint_name)

    # Get sampling client to access model path
    sampling_client = training_client.save_weights_and_get_sampling_client(
        name=f"{checkpoint_name}_export"
    )

    # Download checkpoint archive
    print(f"Downloading {sampling_client.model_path}...")
    future = rest_client.download_checkpoint_archive_from_tinker_path(
        sampling_client.model_path
    )

    with open(output_file, "wb") as f:
        f.write(future.result())

    print(f"Model saved to {output_file}")

    # Get file size
    import os
    size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"Size: {size_mb:.1f} MB")


if __name__ == "__main__":
    import sys
    checkpoint = sys.argv[1] if len(sys.argv) > 1 else "beethoven_prompt_distillation_final"
    export_model(checkpoint)
