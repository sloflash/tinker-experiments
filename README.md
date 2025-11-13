# Tinker Experiments: Character Prompt Distillation

Implementation of character prompt distillation using [Tinker API](https://tinker-docs.thinkingmachines.ai/) and the [Character-LLM dataset](https://huggingface.co/datasets/fnlp/character-llm-data).

## Overview

This project demonstrates **prompt distillation** - internalizing a 450+ token character system prompt into an 8B student model to achieve:
- **95% token reduction** (450 → 0 prompt tokens)
- **30-40x cost savings** ($165 → $5 per 1M queries)
- **10x faster inference** (5s → 0.5s per query)
- **85-95% quality retention** compared to teacher model

## Quick Start

See **[SPEC.md](./SPEC.md)** for the complete 20-step implementation guide.

## Project Structure

```
tinker-experiments/
├── SPEC.md                          # Complete 20-step implementation spec
├── .gitignore                       # Ignore training artifacts and API keys
└── README.md                        # This file
```

## Implementation Steps

1. **Setup** (Steps 1-2): API key + dependencies
2. **Dataset** (Steps 3-5): Explore Character-LLM data, design character prompt
3. **Data Generation** (Steps 6-10): Generate 5000 training examples with teacher model
4. **Training** (Steps 11-13): Train student model with Tinker API
5. **Evaluation** (Steps 14-16): Measure quality, cost savings, latency
6. **Testing** (Steps 17-18): Interactive demo + manual validation
7. **Deployment** (Steps 19-20): Export model + documentation

## Requirements

- Tinker API key (get at [thinkingmachines.ai/tinker](https://thinkingmachines.ai/tinker))
- Python 3.8+
- Dependencies: `tinker`, `datasets`, `transformers`, `torch`

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/sloflash/tinker-experiments.git
   cd tinker-experiments
   ```

2. **Configure API key**
   ```bash
   cp .env.example .env
   # Edit .env and add your Tinker API key
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Follow the implementation**
   - See [SPEC.md](./SPEC.md) for the complete 20-step guide

## Expected Results

| Metric | Target |
|--------|--------|
| Training time | 8-13 hours |
| Data generation cost | $50-100 |
| Training cost | $300-500 |
| Quality retention | 85-95% |
| Token reduction | 95% |
| Cost savings | 30-40x |
| Latency improvement | 10x |

## License

MIT

## Resources

- [Tinker API Documentation](https://tinker-docs.thinkingmachines.ai/)
- [Tinker Cookbook (GitHub)](https://github.com/thinking-machines-lab/tinker-cookbook)
- [Character-LLM Dataset](https://huggingface.co/datasets/fnlp/character-llm-data)
