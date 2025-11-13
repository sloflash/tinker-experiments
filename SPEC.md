# CHARACTER PROMPT DISTILLATION SPEC
## 20-Step Implementation Using Tinker API + Character LLM Dataset

---

## QUICK TASK LIST (for /do-tasks execution)

This task list is automatically parsed by the `/do-tasks` command. Each task corresponds to a step in the full specification below. The **tinker-executor** agent (configured in `.claude/agents/AGENT.md`) will execute these sequentially, validating outputs and handling errors.

### Task Tracking

- [ ] **STEP 1**: Setup Tinker API Access - Create account, obtain API key, set environment variable
- [ ] **STEP 2**: Install Core Dependencies - Create requirements.txt, install packages, verify imports
- [ ] **STEP 3**: Explore Character LLM Dataset - Load fnlp/character-llm-data, inspect schema, print samples
- [ ] **STEP 4**: Validate Character Data Quality - Filter to Beethoven, count examples, check completeness
- [ ] **STEP 5**: Design Character System Prompt - Write 450+ token prompt for Beethoven personality/history
- [ ] **STEP 6**: Create Teacher Data Generator - Build Tinker API script to generate 10 test examples
- [ ] **STEP 7**: Create Student Format Converter - Strip long prompts, convert to student training format
- [ ] **STEP 8**: Generate Full Training Dataset - Run teacher generator for 5000 diverse questions
- [ ] **STEP 9**: Audit Dataset Quality - Validate character consistency, duplicates, diversity metrics
- [ ] **STEP 10**: Prepare Student Training Data - Convert to train/val split (4500/500), output train.jsonl + val.jsonl
- [ ] **STEP 11**: Configure Training Hyperparameters - Create training_config.yaml with LoRA params
- [ ] **STEP 12**: Write Tinker Training Script - Implement 06_train_student_model.py with forward_backward() loop
- [ ] **STEP 13**: Execute Student Model Training - Run training for 1000 steps, save 5 checkpoints, monitor loss
- [ ] **STEP 14**: Create Evaluation Script - Build 07_evaluate_models.py comparing student vs teacher
- [ ] **STEP 15**: Run Evaluation on Best Checkpoint - Execute evaluation, target 85-95% similarity scores
- [ ] **STEP 16**: Calculate Cost Savings Metrics - Analyze token reduction (95%), cost savings (30-40x)
- [ ] **STEP 17**: Test Interactive Inference - Create 09_interactive_demo.py CLI for real-time conversations
- [ ] **STEP 18**: Validate Character Consistency - Manual review of 50 responses for character traits
- [ ] **STEP 19**: Export Model for Production - Export to HuggingFace format (adapter_model.bin + config)
- [ ] **STEP 20**: Document Results and Deployment - Create RESULTS_REPORT.md + DEPLOYMENT.md

---

## AGENT CONFIGURATION

**Executor**: tinker-executor (configured in `.claude/agents/AGENT.md`)
**Execution Pattern**: Sequential, with validation after each step
**Skill Integration**: Uses tinker-api skill for all Tinker-specific questions
**Error Handling**: Graceful recovery with clear guidance

---

## FULL SPECIFICATION (Steps 1-20 with detailed instructions)

## STEP 1: Setup Tinker API Access

**What to Accomplish:**
Create Tinker account and obtain API key from console for authentication

**Files:**
None → Set environment variable `export TINKER_API_KEY="your-key"`

**Success Outcome:**
`echo $TINKER_API_KEY` prints your key; authentication works when calling Tinker API

**Instructions:**
1. Visit https://thinkingmachines.ai/tinker and join waitlist
2. Once approved, login to https://tinker-console.thinkingmachines.ai
3. Navigate to API Keys section and generate new key
4. Add to shell profile: `echo 'export TINKER_API_KEY="sk-..."' >> ~/.bashrc`
5. Verify with `source ~/.bashrc && echo $TINKER_API_KEY`

---

## STEP 2: Install Core Dependencies

**What to Accomplish:**
Install tinker SDK and HuggingFace libraries for dataset access and model training

**Files:**
Create `requirements.txt` → Run `pip install -r requirements.txt`

**Success Outcome:**
`python -c "import tinker; import datasets; import transformers"` executes without import errors

**Instructions:**
1. Create requirements.txt with: tinker>=0.1.0, datasets>=2.14.0, transformers>=4.35.0, torch>=2.0.0, pyyaml, pandas, tqdm
2. Run `pip install -r requirements.txt`
3. Test imports: `python -c "import tinker"`
4. Verify Tinker client initializes: `python -c "import tinker; tinker.Client()"`
5. Check version: `pip show tinker`

---

## STEP 3: Explore Character LLM Dataset

**What to Accomplish:**
Load fnlp/character-llm-data from HuggingFace and inspect schema, columns, available characters

**Files:**
Create new `01_explore_dataset.py` → Prints dataset structure and 5 sample Beethoven entries

**Success Outcome:**
Script outputs column names (setting/dialogue/background OR prompt/output) and shows complete example entries

**Instructions:**
1. Use `from datasets import load_dataset` to load "fnlp/character-llm-data"
2. Print dataset.keys() to see splits, print column_names to see schema
3. Iterate through first 5 examples and pretty-print all fields
4. Identify which format: dialogue-based (setting/dialogue/background) vs. prompt-based (prompt/output)
5. Note available characters (Beethoven, Newton, Caesar, etc.) for Step 4

---

## STEP 4: Validate Character Data Quality

**What to Accomplish:**
Filter dataset to one character (Beethoven) and validate completeness, count examples

**Files:**
Create new `02_validate_character_data.py` using dataset from Step 3

**Success Outcome:**
Confirms 500+ Beethoven examples exist, no empty fields, prints count and statistics

**Instructions:**
1. Load dataset and filter rows containing character name (case-insensitive search)
2. Count total examples, check for null/empty values in all columns
3. Calculate avg dialogue length, count unique settings/scenarios
4. Print distribution of data (conversations, monologues, actions, etc.)
5. Save filtered character data for later use if needed

---

## STEP 5: Design Character System Prompt

**What to Accomplish:**
Write 450+ token system prompt describing Beethoven's personality, background, speech patterns, era

**Files:**
Create new `character_prompts.py` with function `get_character_prompt("Beethoven")`

**Success Outcome:**
Function returns 450+ word prompt covering biography, temperament, speech style, historical context

**Instructions:**
1. Research Beethoven: personality traits (volatile, passionate), key life events (deafness, patrons, compositions)
2. Include speech patterns (direct, emotional, references to music/philosophy), historical context (1770-1827, French Revolution)
3. Structure: Personality & Temperament, Speech Patterns, Historical Context, Musical Philosophy, Response Guidelines
4. Aim for 450-600 words total (this is the prompt we'll distill away)
5. Test token count: `len(get_character_prompt("Beethoven").split())` should be 450+

---

## STEP 6: Create Teacher Data Generator

**What to Accomplish:**
Build script calling Tinker API to generate responses using teacher model WITH full 450-token character prompt

**Files:**
Create new `03_generate_teacher_data.py` using prompts from Step 5

**Success Outcome:**
Generates 10 test examples in JSONL format: {question, full_prompt, teacher_response, prompt_tokens}

**Instructions:**
1. Import tinker and character_prompts, initialize `client = tinker.Client()`
2. For each test question, construct full_prompt = character_prompt + "\n\nUser: {question}\nBeethoven:"
3. Call `client.sample(model="meta-llama/Llama-3.1-70B-Instruct", prompt=full_prompt, max_tokens=300)`
4. Save results as JSONL with fields: question, full_prompt, teacher_response, prompt_tokens (count from split)
5. Test with 10 diverse questions (biographical, musical, philosophical, historical, emotional)

---

## STEP 7: Create Student Format Converter

**What to Accomplish:**
Build converter that strips long character prompts to create student training format

**Files:**
Create new `04_prepare_student_data.py` processing output JSONL from Step 6

**Success Outcome:**
Converts teacher JSONL to student format: {question, response} with character voice but NO prompt tokens

**Instructions:**
1. Read teacher_data_test.jsonl line by line (JSON lines format)
2. For each example, extract only question and teacher_response fields
3. Discard full_prompt field (this is key: student never sees the 450-token character description)
4. Write new JSONL with simplified schema: {"question": ..., "response": ...}
5. Verify token reduction: original has 450+ prompt tokens, student has 0

---

## STEP 8: Generate Full Training Dataset

**What to Accomplish:**
Run teacher generator for 5000 diverse questions spanning Beethoven's life, work, era, philosophy

**Files:**
Use `03_generate_teacher_data.py` + create new `data_generation_config.yaml` → Outputs `teacher_data_5000.jsonl`

**Success Outcome:**
Produces 20MB+ JSONL file with 5000 character-consistent Q&A pairs in 1-2 hours

**Instructions:**
1. Create YAML config with: character="Beethoven", teacher_model="meta-llama/Llama-3.1-70B-Instruct", num_examples=5000
2. Define question templates covering: compositions, biographical events, relationships, philosophy, historical context
3. Modify Step 6 script to read config and loop through 5000 questions (use tqdm for progress)
4. Use diverse question types: factual, hypothetical, emotional, technical musical analysis
5. Estimate cost: ~5000 queries × 500 tokens avg × $0.03/1K = ~$75 for data generation

---

## STEP 9: Audit Dataset Quality

**What to Accomplish:**
Validate training data for character consistency (95%+ keyword presence), diversity, duplicates (<5%)

**Files:**
Create new `05_audit_dataset.py` analyzing `teacher_data_5000.jsonl` from Step 8

**Success Outcome:**
Report shows 95%+ character-specific phrases, <5% duplicates, balanced question type distribution

**Instructions:**
1. Load all 5000 examples and calculate response length distribution (mean, median, std dev)
2. Check character keyword presence: count responses containing ['music', 'symphony', 'compose', 'deaf', 'Vienna', 'Haydn']
3. Detect duplicates: convert responses to set and compare length (duplicates = total - unique)
4. Analyze question diversity: categorize by type (biographical, musical, emotional, etc.) and check balance
5. Flag quality issues: empty responses, very short (<20 words), very long (>400 words), off-topic

---

## STEP 10: Prepare Student Training Data

**What to Accomplish:**
Convert validated teacher data to student format and split into train (4500) / validation (500) sets

**Files:**
Execute `04_prepare_student_data.py` on validated data → Outputs `train.jsonl` + `val.jsonl`

**Success Outcome:**
Two files created with no system prompts, 90/10 train/val split, student format confirmed

**Instructions:**
1. Load validated teacher_data_5000.jsonl that passed quality audit in Step 9
2. Shuffle data with random seed for reproducibility
3. Split: first 4500 examples → train.jsonl, remaining 500 → val.jsonl
4. For each file, convert to student format (question + response only, no prompts)
5. Validate output: read back files, confirm no 'full_prompt' field exists, verify counts

---

## STEP 11: Configure Training Hyperparameters

**What to Accomplish:**
Define LoRA training config following Tinker distillation best practices: lr=1e-4, rank=128, 1000 steps

**Files:**
Create new `training_config.yaml` with model, training, data, checkpointing sections

**Success Outcome:**
YAML contains all required fields (model_name, lora params, learning rate, batch size, checkpoint intervals)

**Instructions:**
1. Model section: name="meta-llama/Llama-3.1-8B-Instruct" (student, smaller than 70B teacher), lora_rank=128, lora_alpha=256, lora_dropout=0.05
2. Training section: learning_rate=1e-4, batch_size=64, max_steps=1000, warmup_steps=100, gradient_accumulation_steps=8
3. Data section: train_file="train.jsonl", val_file="val.jsonl", max_seq_length=2048
4. Checkpointing: save_every=200, output_dir="checkpoints/", eval_every=100
5. Logging: log_every=10, log_dir="training_logs/"

---

## STEP 12: Write Tinker Training Script

**What to Accomplish:**
Implement supervised training loop using Tinker `forward_backward()` and `optim_step()` APIs

**Files:**
Create new `06_train_student_model.py` reading config from Step 11, logs to `training_logs/`

**Success Outcome:**
Script initializes without errors, creates training client, loads datasets, prints "Starting training..."

**Instructions:**
1. Load config with PyYAML, initialize `client = tinker.TrainingClient()`
2. Call `model_id = client.load_model(model_name, lora_rank, lora_alpha)` to get model handle
3. Load train.jsonl and val.jsonl into memory (list of dicts)
4. Implement training loop: for step in range(max_steps), get batch, format as "User: {q}\nAssistant: {r}"
5. Call `loss = client.forward_backward(model_id, text=prompt, lr=lr)` then `client.optim_step(model_id)` every N accumulation steps
6. Save checkpoints every 200 steps with `client.save_state(model_id, path)`, log loss to file

---

## STEP 13: Execute Student Model Training

**What to Accomplish:**
Run training script for 1000 steps, monitoring loss curve, saving 5 checkpoints every 200 steps

**Files:**
Execute `python 06_train_student_model.py --config training_config.yaml`

**Success Outcome:**
Training completes in 2-4 hours, 5 checkpoints saved to checkpoints/, loss decreases from ~3.5 → ~0.8

**Instructions:**
1. Run script in terminal: `python 06_train_student_model.py --config training_config.yaml`
2. Monitor progress: `tail -f training_logs/loss.txt` to watch loss decrease
3. Check GPU utilization if applicable: `nvidia-smi` (optional, Tinker handles this remotely)
4. Verify checkpoints: `ls -lh checkpoints/` should show step_200.pt, step_400.pt, ..., step_1000.pt
5. Expected timeline: ~2-4 hours total, ~1.5 min/step for 8B model with LoRA rank 128

---

## STEP 14: Create Evaluation Script

**What to Accomplish:**
Build harness comparing student (no prompt) vs teacher (with prompt) responses on 100 held-out questions

**Files:**
Create new `07_evaluate_models.py` with side-by-side comparison and similarity scoring

**Success Outcome:**
Script loads both models, generates 100 response pairs, saves to `evaluation_results.json`

**Instructions:**
1. Load student checkpoint with `client.load_checkpoint(checkpoint_path)` and teacher model "meta-llama/Llama-3.1-70B-Instruct"
2. For each question in val.jsonl (first 100): generate student response (no prompt) and teacher response (with 450-token prompt)
3. Calculate similarity with SequenceMatcher from difflib: `SequenceMatcher(None, student, teacher).ratio()`
4. Save results: {question, student_response, teacher_response, similarity_score, token_counts}
5. Print progress and avg similarity after completion

---

## STEP 15: Run Evaluation on Best Checkpoint

**What to Accomplish:**
Execute evaluation script using checkpoint with lowest validation loss (typically step_1000.pt)

**Files:**
Run `python 07_evaluate_models.py --checkpoint checkpoints/step_1000.pt --test_data val.jsonl`

**Success Outcome:**
Generates `evaluation_results.json` showing student achieves 85-95% similarity scores to teacher

**Instructions:**
1. Identify best checkpoint by reviewing training logs (usually final step_1000.pt)
2. Run evaluation: `python 07_evaluate_models.py --checkpoint checkpoints/step_1000.pt --character Beethoven --num_samples 100`
3. Wait ~15-20 minutes for 100 generations (both student and teacher)
4. Review evaluation_results.json: check similarity_score distribution
5. Target: avg similarity 85-95%, individual scores mostly 80%+

---

## STEP 16: Calculate Cost Savings Metrics

**What to Accomplish:**
Compute token reduction (95%), cost savings (30-40x), latency improvement (10x) from prompt distillation

**Files:**
Create new `08_calculate_metrics.py` analyzing `evaluation_results.json` from Step 15

**Success Outcome:**
Report shows 450 tokens saved/query, 30-40x cost reduction, 10x faster inference, 85-95% quality retention

**Instructions:**
1. Load evaluation_results.json and extract prompt_tokens_saved (should be ~450) and avg_similarity
2. Calculate costs: teacher = (450 prompt + 100 response) × $0.03/1K, student = (0 + 100) × $0.03/1K
3. Compute monthly savings for 1M queries: (teacher_cost - student_cost) × 1M
4. Calculate latency: assume 50ms per token generation, teacher ~5s vs student ~0.5s
5. Output formatted report with tables: quality (similarity %), tokens (reduction %), cost (savings $), latency (speedup factor)

---

## STEP 17: Test Interactive Inference

**What to Accomplish:**
Create CLI demo for real-time character conversations using student model with sample() API

**Files:**
Create new `09_interactive_demo.py` loading checkpoint from Step 13

**Success Outcome:**
CLI accepts user questions, student model responds in-character in <1 second without system prompt

**Instructions:**
1. Load checkpoint with `client.load_checkpoint()`, create interactive input loop
2. For each user input, format as "User: {input}\nAssistant:" (no character prompt!)
3. Call `client.sample(model, prompt, max_tokens=200, temperature=0.7)` for generation
4. Print response with character name prefix: "Beethoven: {response}"
5. Test with diverse questions: biographical, musical, emotional, philosophical

---

## STEP 18: Validate Character Consistency

**What to Accomplish:**
Manual review of 50 diverse responses to ensure Beethoven traits preserved without long prompt

**Files:**
Create new `10_manual_review.py` generating test cases → Saves to `manual_review.txt`

**Success Outcome:**
45+ of 50 responses (90%) maintain character voice, historical accuracy, personality quirks

**Instructions:**
1. Define 5 question categories: biographical, musical, philosophical, historical, emotional
2. Sample 10 questions per category (50 total) covering diverse scenarios
3. Generate responses using student model, format as review sheet with rating scales
4. Output to manual_review.txt with space for ratings (1-5) and notes
5. Manually review each response, check for: character consistency, historical accuracy, emotional authenticity, speech patterns

---

## STEP 19: Export Model for Production

**What to Accomplish:**
Download trained LoRA weights using save_state() and convert to HuggingFace PEFT format

**Files:**
Create new `11_export_model.py` → Saves to `models/beethoven_distilled/` directory

**Success Outcome:**
Directory contains `adapter_model.bin` and `adapter_config.json` ready for HuggingFace PEFT deployment

**Instructions:**
1. Load best checkpoint, call `client.save_state(model_id, "models/beethoven_distilled/adapter_model.bin")`
2. Create adapter_config.json with PEFT format: base_model, lora_alpha=256, r=128, target_modules, task_type="CAUSAL_LM"
3. Write deploy_example.py showing how to load with `from peft import PeftModel; PeftModel.from_pretrained(base, adapter_path)`
4. Verify model size: adapter should be ~45MB (LoRA weights only, not full 8B model)
5. Test loading: `from peft import PeftModel; model = PeftModel.from_pretrained(base_model, "models/beethoven_distilled")`

---

## STEP 20: Document Results and Deployment

**What to Accomplish:**
Write final report with all metrics, before/after examples, deployment guide, multi-character strategy

**Files:**
Create new `RESULTS_REPORT.md` (metrics from Steps 15-16) + `DEPLOYMENT.md` (instructions)

**Success Outcome:**
Documentation includes comparison table, cost analysis, inference code, troubleshooting, scaling strategy

**Instructions:**
1. RESULTS_REPORT.md: Executive summary, metrics table (quality/cost/latency), example comparisons (teacher vs student), cost-benefit analysis, limitations, recommendations
2. DEPLOYMENT.md: Quick start code (HuggingFace PEFT, vLLM, Tinker API), multi-character scaling pattern, performance optimization tips, monitoring metrics, troubleshooting guide
3. Include before/after example: same question, teacher response (with prompt) vs student (without), highlight similarity and token savings
4. Add ROI calculation: development cost (~$500) vs monthly savings ($160) = 3-month payback
5. Document next steps: deploy to staging, A/B test, collect feedback, scale to 9 more characters (Newton, Caesar, etc.)

---

## COMPLETION CHECKLIST

- [ ] **Steps 1-2:** Environment setup (API key, dependencies)
- [ ] **Steps 3-5:** Dataset explored, character selected, 450+ word prompt created
- [ ] **Steps 6-10:** 5000 training examples generated, validated, split into train/val
- [ ] **Steps 11-13:** Training config created, script written, 1000 steps completed
- [ ] **Steps 14-16:** Evaluation run, 85-95% similarity achieved, metrics calculated
- [ ] **Steps 17-18:** Interactive demo working, 90%+ manual review quality
- [ ] **Steps 19-20:** Model exported, documentation complete

---

## EXPECTED OUTCOMES

| Metric | Target |
|--------|--------|
| Training time | 8-13 hours total |
| Data generation cost | $50-100 |
| Training cost | $300-500 |
| Quality retention | 85-95% similarity |
| Token reduction | 95% (450 → 0) |
| Cost savings | 30-40x cheaper |
| Latency improvement | 10x faster |
| ROI timeline | 3-4 months |

---

## FILE STRUCTURE (15 files created)

```
tinker-experiments/
├── requirements.txt                    # Step 2
├── 01_explore_dataset.py              # Step 3
├── 02_validate_character_data.py      # Step 4
├── character_prompts.py               # Step 5
├── 03_generate_teacher_data.py        # Step 6
├── 04_prepare_student_data.py         # Step 7
├── data_generation_config.yaml        # Step 8
├── 05_audit_dataset.py                # Step 9
├── training_config.yaml               # Step 11
├── 06_train_student_model.py          # Step 12
├── 07_evaluate_models.py              # Step 14
├── 08_calculate_metrics.py            # Step 16
├── 09_interactive_demo.py             # Step 17
├── 10_manual_review.py                # Step 18
├── 11_export_model.py                 # Step 19
├── RESULTS_REPORT.md                  # Step 20
└── DEPLOYMENT.md                      # Step 20

Generated artifacts:
├── teacher_data_5000.jsonl            # Step 8 output
├── train.jsonl                        # Step 10 output
├── val.jsonl                          # Step 10 output
├── checkpoints/                       # Step 13 output
│   ├── step_200.pt
│   ├── step_400.pt
│   ├── step_600.pt
│   ├── step_800.pt
│   └── step_1000.pt
├── training_logs/                     # Step 13 output
│   └── loss.txt
├── evaluation_results.json            # Step 15 output
├── metrics_report.json                # Step 16 output
├── manual_review.txt                  # Step 18 output
└── models/beethoven_distilled/        # Step 19 output
    ├── adapter_model.bin
    ├── adapter_config.json
    └── deploy_example.py
```

---

## TECHNICAL NOTES

**Tinker API Key Concepts:**
- `forward_backward()`: Computes loss and accumulates gradients
- `optim_step()`: Updates model weights using accumulated gradients
- `sample()`: Generates text from model
- `save_state()`: Saves model checkpoint
- `TrainingClient()`: Training-specific client with distributed compute

**Character LLM Dataset:**
- Two schemas: dialogue-based (setting/dialogue/background) or prompt-based (prompt/output)
- Characters: Beethoven, Newton, Caesar, Socrates, Cleopatra, etc.
- ~500-1000 examples per character
- Use prompted/ subfolder for direct SFT data

**Prompt Distillation Principle:**
1. Teacher uses long prompt (450 tokens) → high-quality character responses
2. Student learns question → response mapping WITHOUT seeing prompt
3. Character knowledge internalized into model weights
4. Result: Same quality, zero prompt tokens, 30-40x cost savings

---

**END OF SPEC**
