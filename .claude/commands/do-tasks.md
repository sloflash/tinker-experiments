---
allowed-tools: Read, Edit, Task, Bash, Write
argument-hint: "[step-number or range]"
description: Execute Tinker implementation steps from SPEC.md with smart parallel/sequential orchestration
---

# Do Tasks Command

Executes the 20-step implementation plan from `SPEC.md` using intelligent parallel pre-flight checks, sequential main execution, and parallel post-validation.

## Built-in Task Logger

This command includes integrated logging with unique task IDs. All outputs are logged to `.task_execution.log` with searchable IDs that are added to SPEC.md upon completion.

### Logging Functions (used internally)

```python
import uuid
import json
from datetime import datetime

def generate_task_id(step_number):
    """Generate unique ID for this task execution"""
    return f"task_{step_number}_{uuid.uuid4().hex[:8]}"

def log_to_file(message, task_id=None, file=".task_execution.log"):
    """Log message with timestamp and task ID"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "task_id": task_id,
        "message": message
    }
    with open(file, 'a') as f:
        f.write(json.dumps(entry) + '\n')

def update_spec_with_id(step_number, task_id, success=True):
    """Update SPEC.md with task ID for log searching"""
    # Read SPEC.md
    spec_content = read_file("SPEC.md")

    # Find and update the checkbox
    old_pattern = f"- [ ] **STEP {step_number}**:"
    new_pattern = f"- [x] **STEP {step_number}**: ✓ [task_id: {task_id}] [{datetime.now().isoformat()}]"

    if not success:
        new_pattern = f"- [ ] **STEP {step_number}**: ✗ Failed [task_id: {task_id}] [{datetime.now().isoformat()}]"

    # Update and save
    updated_content = spec_content.replace(old_pattern, new_pattern)
    write_file("SPEC.md", updated_content)
```

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
Execute ONE focused task using the tinker-executor agent with TESTING:
```python
# Use the configured agent from .claude/agents/AGENT.md
# IMPORTANT: Test before assuming success!

# Log task start
task_id = generate_task_id(step_number)
log_to_file(f"[{task_id}] Starting Step {step_number}")

try:
    if step.requires_long_running:
        # For training, large data generation
        result = Task(
            subagent_type="tinker-executor",  # Uses .claude/agents/AGENT.md
            prompt=f"{step_objective}. TEST the script before assuming it works!",
            skills=["tinker-api"]  # Uses .claude/skills/tinker-api
        )

        # Log agent output
        log_to_file(f"[{task_id}] Agent output: {result}")

        # Only start background if test succeeded
        if result.success:
            start_background_task()
            register_monitors()
    else:
        # For setup, config, small operations
        result = Task(
            subagent_type="tinker-executor",
            prompt=f"{step_objective}. TEST the script before assuming it works!",
            skills=["tinker-api"]
        )

        # Log all outputs
        log_to_file(f"[{task_id}] Result: {result}")

except Exception as e:
    log_to_file(f"[{task_id}] ERROR: {str(e)}")
    # Handle error gracefully
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

### 4. Update SPEC.md with Task ID
**CRITICAL**: Mark task complete in SPEC.md with unique ID for log searching:
```python
from task_logger import TaskLogger

# Start task with unique ID
logger = TaskLogger(".task_execution.log")
task_id = logger.start_task(step_number, description)

# ... execute task phases ...

# Update SPEC.md with task ID for easy log searching
- [ ] **STEP N**: Description...
# becomes
- [x] **STEP N**: Description... ✓ [task_id: task_1_a3b4c5d6] [2024-11-13 10:30]
```

Users can search logs with: `grep "task_1_a3b4c5d6" .task_execution.log`

## Step-by-Step Execution with Logging

When you run `/do-tasks N`:

1. **Initialize Logging** - Create unique task ID for this execution
2. **Read SPEC.md** to get step N details
3. **Pre-Flight** (parallel, 30s each):
   - Log each check to `.task_execution.log` with task ID
   - Check if step N-1 outputs exist
   - Verify environment ready
   - Test required connections
4. **Main Task** (sequential):
   - Use Task tool with subagent_type="tinker-executor" (from .claude/agents/AGENT.md)
   - Log all agent outputs with task ID
   - Single focused objective from SPEC.md
   - Leverage relevant skills from .claude/skills/ (especially tinker-api)
   - For long tasks, start in background
5. **Post-Validation** (parallel, 30s each):
   - Log validation results with task ID
   - Verify success criteria from SPEC.md
   - Quick quality check
6. **Update SPEC.md**:
   - Mark checkbox as complete: `- [x]`
   - **Add task ID for log searching**: `[task_id: task_N_xxxxx]`
   - Add timestamp: `[2024-11-13 10:30]`
   - Save the file

All outputs logged to `.task_execution.log` with task ID for easy searching!

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

## Example Output with Testing & Logging

```
/do-tasks 8

[TASK ID: task_8_3fa2b8c1] Generated for this execution

[STEP 8: Generate Full Training Dataset]

[PRE-FLIGHT] Parallel checks (3)...
  ✓ Teacher model accessible [3s]
  ✓ character_prompts.py exists [1s]
  ✓ Config file valid [2s]

[MAIN] Executing with tinker-executor agent...
  → Testing script first...
  → Test run with 2 examples: SUCCESS
  → Now generating 5000 examples
  → All outputs logged to .task_execution.log with ID: task_8_3fa2b8c1
  → Progress: 500/5000 [10%]
  → Using background generation...
  → Monitor started (PID: 45678)

[POST] Parallel validations (3)...
  ✓ Output file created [1s]
  ✓ Valid JSONL format [3s]
  ✓ Character consistency: 97% [5s]

[UPDATE] Marking complete in SPEC.md...
  ✓ Step 8 marked complete with task_id: task_8_3fa2b8c1

Step 8 completed successfully. Ready for Step 9.
Background monitor active for data generation.

To view logs: grep "task_8_3fa2b8c1" .task_execution.log
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

**Agent & Skills Integration (CRITICAL):**
```python
# For main execution phase
# MUST ALWAYS include tinker-api skill to avoid going off track!
Task(
    subagent_type="tinker-executor",  # From .claude/agents/AGENT.md
    prompt=f"Execute Step {N}: {step_description}. Use tinker-api skill for all API operations!",
    skills=["tinker-api"],  # MANDATORY - from .claude/skills/tinker-api/
    model="haiku"  # Use fast model for quick tasks
)

# The tinker-api skill contains:
# - Correct API usage patterns
# - Working examples
# - Error handling guidance
# Without it, scripts may fail with API errors!
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