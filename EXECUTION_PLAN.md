# Execution Plan: Large-Scale Prompt Distillation

## What's Been Prepared

### ✓ Scripts Updated for Scale
- **03_generate_teacher_data.py**: Scaled to 5000 examples with:
  - Template-based question generation (60+ templates)
  - Progress checkpointing every 100 examples
  - Error recovery
  - Diverse question types (biographical, musical, philosophical)

- **prepare_training_data.py**: Converts teacher→student format, 90/10 split

- **06_train_student_model.py**: Ready for 1000-step training with:
  - Request pipelining (fwd_bwd + optim together)
  - Proper loss weighting
  - Checkpoints every 200 steps

- **training_config.yaml**: Updated for large-scale:
  - 1000 steps
  - Qwen 4B Instruct student model
  - LoRA rank 32

### ✓ Evaluation Scripts Created
- **07_evaluate_models.py**: Compare student vs teacher (Step 14-15)
- **08_calculate_metrics.py**: Cost/quality analysis (Step 16)
- **09_interactive_demo.py**: CLI chat interface (Step 17)
- **11_export_model.py**: Download checkpoint with rest_client (Step 19)

### ✓ Orchestration
- **run_full_pipeline.py**: Master script running all steps sequentially

## Execution Steps

### 1. Set API Key
```bash
export TINKER_API_KEY="your-key-here"
```

### 2. Generate Data (5000 examples, ~2-3 hours)
```bash
.venv/bin/python3 03_generate_teacher_data.py 5000
```

### 3. Prepare Training Data
```bash
.venv/bin/python3 prepare_training_data.py
# Creates train.jsonl (4500) + val.jsonl (500)
```

### 4. Train Model (1000 steps, ~3-5 hours)
```bash
.venv/bin/python3 06_train_student_model.py
# Saves checkpoints every 200 steps
# Logs to training_logs/loss.txt
```

### 5. Evaluate
```bash
.venv/bin/python3 07_evaluate_models.py
.venv/bin/python3 08_calculate_metrics.py
```

### 6. Test Interactively
```bash
.venv/bin/python3 09_interactive_demo.py
```

### 7. Export Model
```bash
.venv/bin/python3 11_export_model.py
# Downloads model-checkpoint.tar.gz
```

## OR: Run Full Pipeline
```bash
.venv/bin/python3 run_full_pipeline.py
```

## Key Improvements

1. **Data Generation**: 5000 diverse examples vs 10 test examples
2. **Training Scale**: 1000 steps vs 100 steps
3. **Model Size**: Qwen 4B (production-ready)
4. **Checkpointing**: Every 200 steps (5 checkpoints total)
5. **Export**: Automatic checkpoint download via REST API

## Expected Outcomes

| Metric | Target |
|--------|--------|
| Training time | 3-5 hours |
| Data generation | 2-3 hours |
| Quality retention | 85-95% similarity |
| Token savings | ~591 tokens/query |
| Cost reduction | 30-40x cheaper |

## Next: Set API Key

The only blocker is `TINKER_API_KEY`. Once set, run:
```bash
.venv/bin/python3 run_full_pipeline.py
```

Or run steps individually as shown above.
