# Tinker Experiments - Execution Guide

## Overview

This project implements **character prompt distillation** using the Tinker API to create efficient, low-token student models that replicate teacher model behavior without expensive system prompts.

## Quick Start

### 1. Review the Task Structure

Your project has:
- **tasks.md** - Master file with quick task list + full specification
- **.claude/agents/AGENT.md** - Tinker executor agent configuration
- **tinker-api skill** - Expert guidance for Tinker API usage

### 2. Execute Tasks

```bash
# Run the first 5 steps
/do-tasks 5

# Run specific number of remaining tasks
/do-tasks 10

# Run all remaining tasks
/do-tasks
```

### 3. What the Agent Does

The **tinker-executor** agent will:
1. ✓ Validate environment setup (API key, virtual environment, dependencies)
2. ✓ Execute each step sequentially
3. ✓ Validate outputs after each step
4. ✓ Invoke tinker-api skill when needed for expertise
5. ✓ Track progress and report results
6. ✓ Handle errors with recovery strategies

## Task Checklist

All 20 steps are defined in `tasks.md`:

**Setup (Steps 1-2)**
- [ ] Tinker API account & key
- [ ] Install dependencies

**Dataset (Steps 3-5)**
- [ ] Explore dataset structure
- [ ] Validate character data
- [ ] Design system prompt

**Data Generation (Steps 6-10)**
- [ ] Teacher data generator
- [ ] Student format converter
- [ ] Generate 5000 examples
- [ ] Audit quality
- [ ] Train/val split

**Training (Steps 11-13)**
- [ ] Configure hyperparameters
- [ ] Write training script
- [ ] Execute training (1000 steps)

**Evaluation (Steps 14-16)**
- [ ] Create evaluation script
- [ ] Run evaluation
- [ ] Calculate metrics

**Finalization (Steps 17-20)**
- [ ] Interactive demo
- [ ] Manual review
- [ ] Export model
- [ ] Document results

## Key Features

### Environment Management
The agent automatically:
- Creates virtual environment
- Installs requirements.txt
- Verifies Tinker API connectivity
- Sets up logging directories

### Progress Tracking
Each step validates:
- Input files exist
- Expected outputs are created
- Metrics are within acceptable ranges
- No errors occurred

### Expert Integration
The agent consults the **tinker-api skill** for:
- Training loop best practices
- LoRA configuration guidance
- Error debugging
- Performance optimization

## Expected Timeline

| Phase | Steps | Duration | Cost |
|-------|-------|----------|------|
| Setup | 1-2 | 15 min | $0 |
| Dataset | 3-5 | 30 min | $0 |
| Data Gen | 6-10 | 2-3 hours | $75 |
| Training | 11-13 | 2-4 hours | $300-500 |
| Evaluation | 14-16 | 30 min | $25 |
| Finalization | 17-20 | 1 hour | $0 |
| **TOTAL** | **1-20** | **5-8 hours** | **$400-600** |

## Success Metrics

The project succeeds when:
- ✓ All 20 steps complete without errors
- ✓ Training loss decreases from ~3.5 to ~0.8
- ✓ 5 checkpoints saved at steps 200, 400, 600, 800, 1000
- ✓ Evaluation shows 85-95% similarity scores
- ✓ Student model achieves 95% token reduction
- ✓ Final model exports to HuggingFace format
- ✓ Cost savings documented (30-40x improvement)

## Troubleshooting

### "TINKER_API_KEY not set"
```bash
export TINKER_API_KEY="your_key_here"
source ~/.bashrc
```

### "ModuleNotFoundError: No module named 'tinker'"
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### "Training loss is NaN"
- Reduce learning rate (1e-4 → 1e-5)
- Check data quality (Step 9 validation)
- Resume from previous checkpoint

### Training interrupted?
The agent can resume from the last checkpoint. Just run `/do-tasks` again.

## File Structure

```
tinker-experiments/
├── tasks.md                      # Master spec + task list
├── EXECUTION_GUIDE.md            # This file
├── .claude/
│   ├── agents/AGENT.md           # Tinker executor configuration
│   └── skills/                   # Available skills
├── requirements.txt              # Python dependencies
├── character_prompts.py          # Character definitions
├── 01_explore_dataset.py         # Step 3
├── 02_validate_character_data.py # Step 4
├── 03_generate_teacher_data.py   # Step 6
├── 04_prepare_student_data.py    # Step 7
├── 05_audit_dataset.py           # Step 9
├── 06_train_student_model.py     # Step 12
├── 07_evaluate_models.py         # Step 14
├── 08_calculate_metrics.py       # Step 16
├── 09_interactive_demo.py        # Step 17
├── 10_manual_review.py           # Step 18
├── 11_export_model.py            # Step 19
├── training_config.yaml          # Step 11
├── data_generation_config.yaml   # Step 8
└── [Generated during execution]
    ├── teacher_data_5000.jsonl
    ├── train.jsonl
    ├── val.jsonl
    ├── checkpoints/
    ├── training_logs/
    ├── evaluation_results.json
    ├── models/beethoven_distilled/
    ├── RESULTS_REPORT.md
    └── DEPLOYMENT.md
```

## Next Steps

1. **Set up environment**: Ensure TINKER_API_KEY is set
2. **Review tasks.md**: Understand the full workflow
3. **Run `/do-tasks 5`**: Start with first 5 steps
4. **Monitor progress**: Check agent output and logs
5. **Deploy when complete**: Follow DEPLOYMENT.md

---

**Questions?** Consult the comprehensive AGENT.md for agent-specific guidance, or run `/do-tasks` to begin the automated workflow.
