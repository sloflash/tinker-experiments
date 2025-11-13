---
allowed-tools: Read, Edit, Task, Bash, Write
argument-hint: "[step-number or range]"
description: Execute Tinker implementation steps from SPEC.md with smart parallel/sequential orchestration
---

# Do Tasks Command

Executes the 20-step implementation plan from `SPEC.md` using intelligent parallel pre-flight checks, sequential main execution, and parallel post-validation.

## Usage

```bash
# Execute specific step
/do-tasks 1

# Execute range of steps
/do-tasks 1-5

# Continue from last completed
/do-tasks continue

# Execute all remaining
/do-tasks all
```

## Execution Model

```
[PARALLEL PRE-FLIGHT] → [SEQUENTIAL MAIN] → [PARALLEL POST] → [UPDATE SPEC.md]
         (30s)              (variable)          (30s)           (mark complete)
                                ↓
                    [BACKGROUND MONITORING]
                        (non-blocking)
```

## Implementation Logic

For each step from SPEC.md:

### 1. Pre-Flight Phase (Parallel, 30s max)
Run up to 3 simultaneous checks:
```python
parallel_tasks = [
    check_dependencies(),    # Verify packages/imports
    validate_inputs(),       # Check required files
    test_environment()       # API keys, connections
]
# Execute all in parallel with 30s timeout
```

### 2. Main Execution Phase (Sequential)
Execute ONE focused task using the tinker-executor agent:
```python
# Use the configured agent from .claude/agents/AGENT.md
if step.requires_long_running:
    # For training, large data generation
    Task(subagent_type="tinker-executor",  # Uses .claude/agents/AGENT.md
         prompt=step_objective,
         skills=["tinker-api"])  # Uses .claude/skills/tinker-api
    start_background_task()
    register_monitors()
else:
    # For setup, config, small operations
    Task(subagent_type="tinker-executor",
         prompt=step_objective,
         skills=["tinker-api"])
```

### 3. Post-Validation Phase (Parallel, 30s max)
Run up to 3 simultaneous validations:
```python
parallel_validations = [
    verify_outputs(),        # Check files created
    test_functionality(),    # Quick smoke test
    collect_metrics()        # Performance stats
]
```

### 4. Update SPEC.md
**CRITICAL**: Mark task complete in SPEC.md:
```python
# Update the task checkbox
- [ ] **STEP N**: Description...
# becomes
- [x] **STEP N**: Description... ✓ [timestamp]
```

## Step-by-Step Execution

When you run `/do-tasks N`:

1. **Read SPEC.md** to get step N details
2. **Pre-Flight** (parallel, 30s each):
   - Check if step N-1 outputs exist
   - Verify environment ready
   - Test required connections
3. **Main Task** (sequential):
   - Use Task tool with subagent_type="tinker-executor" (from .claude/agents/AGENT.md)
   - Single focused objective from SPEC.md
   - Leverage relevant skills from .claude/skills/ (especially tinker-api)
   - For long tasks, start in background
4. **Post-Validation** (parallel, 30s each):
   - Verify success criteria from SPEC.md
   - Quick quality check
   - Log completion
5. **Update SPEC.md**:
   - Mark checkbox as complete: `- [x]`
   - Add timestamp and status
   - Save the file

## Special Handling by Step Type

### Quick Steps (1-2, 4-7, 11-12, 14, 16-20)
- Full blocking execution
- Complete before moving to next
- 5-15 minutes typical

### Data Generation (3, 8-10)
```python
# Chunk large operations
for chunk in chunks:
    generate_data(chunk)
    if check_quality():
        continue
    else:
        fix_and_retry()
```

### Training (Step 13)
```python
# Start in background
process = start_training()
register_monitor(process, check_every=60)
# Immediately continue to step 14
```

### Evaluation (Step 15)
```python
# Stream results for large sets
for batch in evaluation_batches:
    results = evaluate(batch)
    stream_to_file(results)
    if sufficient_samples():
        break
```

## Error Recovery

- **Pre-flight fails**: Fix issue, retry step
- **Main fails**: Log error, attempt recovery, or skip with warning
- **Post fails**: Note issue but continue (unless critical)
- **Background fails**: Alert user, continue pipeline

## Progress Tracking

The command will:
1. Show real-time status for each phase
2. Update SPEC.md checkboxes immediately
3. Log all operations to `.task_log`
4. Report summary after each step

## Example Output

```
/do-tasks 8

[STEP 8: Generate Full Training Dataset]

[PRE-FLIGHT] Parallel checks (3)...
  ✓ Teacher model accessible [3s]
  ✓ character_prompts.py exists [1s]
  ✓ Config file valid [2s]

[MAIN] Executing data generation...
  → Generating 5000 examples
  → Progress: 500/5000 [10%]
  → Using background generation...
  → Monitor started (PID: 45678)

[POST] Parallel validations (3)...
  ✓ Output file created [1s]
  ✓ Valid JSONL format [3s]
  ✓ Character consistency: 97% [5s]

[UPDATE] Marking complete in SPEC.md...
  ✓ Step 8 marked complete

Step 8 completed successfully. Ready for Step 9.
Background monitor active for data generation.
```

## Implementation

Use these tools in combination:
1. **Read**: Get step details from SPEC.md
2. **Task**: Execute main operations with tinker-executor agent
   - Agent location: `.claude/agents/AGENT.md`
   - Skills to use: `.claude/skills/tinker-api/` (for all Tinker-specific tasks)
   - Other skills: Use as needed (document-skills, skill-creator, etc.)
3. **Bash**: Run parallel pre-flight/post checks
4. **Edit**: Update SPEC.md checkboxes to mark complete
5. **Write**: Log progress to `.task_log`

**Agent & Skills Integration:**
```python
# For main execution phase
Task(
    subagent_type="tinker-executor",  # From .claude/agents/AGENT.md
    prompt=f"Execute Step {N}: {step_description}",
    skills=["tinker-api", "document-skills"],  # From .claude/skills/
    model="haiku"  # Use fast model for quick tasks
)
```

**IMPORTANT**: Always update SPEC.md after completing each step so progress is visible!

## Parallel Execution Examples

### Pre-flight checks (run simultaneously):
```bash
(python -c "import tinker" && echo "✓ Tinker ready") &
(test -f train.jsonl && echo "✓ Training data ready") &
(test -f config.yaml && echo "✓ Config ready") &
wait  # Wait max 30s for all
```

### Background monitoring:
```bash
nohup bash -c 'while true; do tail -1 training_logs/loss.txt >> monitor.log; sleep 60; done' &
```

This ensures efficient execution while maintaining clear progress tracking in SPEC.md.