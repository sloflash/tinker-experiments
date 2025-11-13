# Prompt Distillation Research: 85% Token Reduction with Tinker API

## Overview

This research demonstrates **prompt distillation** - internalizing a 591-token Beethoven character prompt into model weights through supervised fine-tuning. We achieved:

- **85.5% token reduction** (691 → 100 tokens per query) 
- **98.3% cost savings** ($3,093 → $53.25 per 1M queries)
- **31x speedup** in data generation (async optimization)
- **99.88% loss reduction** in just 100 training steps

The cost difference reflects using a smaller distilled model (4B vs 30B) plus eliminating the 591-token
  system prompt. The pricing appears to be from Tinker API's tiered pricing for different model sizes

## Project Structure

```
tinker-experiments/
├── src/                              # Original implementation scripts
│   ├── 01_explore_dataset.py        # Dataset exploration
│   ├── 02_validate_character_data.py # Character validation
│   ├── 03_generate_teacher_data.py  # Teacher data generation (async)
│   ├── 06_train_student_model.py    # Student model training
│   ├── 07_evaluate_models.py        # Model evaluation
│   ├── 08_calculate_metrics.py      # Metrics calculation
│   ├── 09_interactive_demo.py       # Interactive testing
│   └── 11_export_model.py           # Model export
│
├── data/                            # Generated datasets
│   ├── teacher_data_test.jsonl     # 5000 examples from teacher
│   ├── train.jsonl                 # 4500 training examples
│   └── val.jsonl                   # 500 validation examples
│
├── config/
│   └── training_config.yaml        # Training hyperparameters
│
├── reports/                         # Comprehensive research documentation
│   ├── 1_METHODOLOGY.md             # Research approach
│   ├── 2_ASYNC_OPTIMIZATION.md      # 31x speedup details
│   ├── 3_TRAINING_RESULTS.md        # Training logs & metrics
│   ├── 4_COST_ANALYSIS.md           # Economic analysis
│   └── 5_LESSONS_LEARNED.md         # Key insights
│
└── deprecated/                      # Previous refactored versions
    ├── 1_generate_teacher_data.py
    ├── 2_train_student_model.py
    ├── 3_evaluate_models.py
    └── 4_calculate_metrics.py
```

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API key
export TINKER_API_KEY="your-api-key-here"
```

### Reproduction Steps

#### 1. Generate Teacher Data (15 minutes)
```bash
python src/03_generate_teacher_data.py
# Generates 5000 examples using async pattern (31x speedup)
```

#### 2. Train Student Model (3 minutes)
```bash
python src/06_train_student_model.py
# LoRA fine-tuning with Tinker API
# Loss: 2.38 → 0.0029 (99.88% reduction)
```

#### 3. Evaluate Models
```bash
python src/07_evaluate_models.py
# Compare student (no prompt) vs teacher (with prompt)
```

#### 4. Calculate Metrics
```bash
python src/08_calculate_metrics.py
# Analyze cost savings and token reduction
```

## Key Results

### Training Performance
- **Model**: Qwen3-4B with LoRA (rank 32)
- **Training time**: 2.97 minutes (100 steps)
- **Loss reduction**: 99.88% (2.38 → 0.0029)
- **Data generation**: 15 minutes for 5000 examples

### Economic Impact
| Metric | Teacher (w/ prompt) | Student (no prompt) | Savings |
|--------|-------------------|-------------------|---------|
| Tokens/query | 691 | 100 | 85.5% |
| Cost/1M queries | $3,093 | $53.25 | 98.3% |
| ROI at 1M queries | - | 3,040x | - |

### Technical Achievements
- **Async optimization**: 31x speedup (7.8 hours → 15 minutes)
- **Quality retention**: 89% semantic similarity
- **Character consistency**: 92% accuracy
- **Break-even point**: ~329 queries (or ~50K with infrastructure costs)

## Key Insights

1. **Async is Critical**: Using `sample_async()` + `asyncio.gather()` achieved 31x speedup
2. **Small Models Work**: 4B parameters sufficient for character behavior
3. **Hard Labels Sufficient**: No soft probabilities needed for distillation
4. **Fast Convergence**: 100 training steps achieved 99.88% loss reduction

## Technical Notes

### Tinker API Best Practices
- Always use async for data generation
- Pipeline training operations (forward_backward + optim_step)
- Use string dtypes ('float32', 'int64') not enums
- Loss masking critical for training on responses only

### Data Format Requirements
```python
types.Datum(
    model_input=types.ModelInput.from_ints(input_tokens),
    loss_fn_inputs={
        'weights': types.TensorData(
            data=weights_list,  # List, not array
            dtype='float32',    # String, not enum
            shape=[len(weights)]
        ),
        'target_tokens': types.TensorData(
            data=target_tokens_list,
            dtype='int64',
            shape=[len(targets)]
        )
    }
)
```

## Resources

- [Tinker API Documentation](https://tinker-docs.thinkingmachines.ai/)
- [Tinker Cookbook](https://github.com/thinking-machines-lab/tinker-cookbook)
- [Character-LLM Dataset](https://huggingface.co/datasets/fnlp/character-llm-data)

## License

MIT