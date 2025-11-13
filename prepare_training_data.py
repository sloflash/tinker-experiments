#!/usr/bin/env python3
"""Prepare training data: convert teacher→student format, split train/val"""

import json
import random
from pathlib import Path


def prepare_training_data(
    teacher_file="teacher_data_5000.jsonl",
    train_file="train.jsonl",
    val_file="val.jsonl",
    train_ratio=0.9,
    seed=42
):
    if not Path(teacher_file).exists():
        print(f"Error: {teacher_file} not found")
        return

    # Load and convert
    with open(teacher_file, 'r') as f:
        teacher_data = [json.loads(line) for line in f]

    student_data = [{
        "messages": [
            {"role": "user", "content": ex["question"]},
            {"role": "assistant", "content": ex["teacher_response"]}
        ]
    } for ex in teacher_data]

    # Split
    random.seed(seed)
    random.shuffle(student_data)
    split_idx = int(len(student_data) * train_ratio)
    train = student_data[:split_idx]
    val = student_data[split_idx:]

    # Save
    with open(train_file, 'w') as f:
        for ex in train:
            f.write(json.dumps(ex) + '\n')

    with open(val_file, 'w') as f:
        for ex in val:
            f.write(json.dumps(ex) + '\n')

    print(f"Prepared {len(train)} train, {len(val)} val examples")


if __name__ == "__main__":
    import sys
    teacher_file = sys.argv[1] if len(sys.argv) > 1 else "teacher_data_5000.jsonl"
    prepare_training_data(teacher_file=teacher_file)
