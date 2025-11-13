# Smart Task Executor Command V2

## Execution Model: Sequential Main + Parallel Support with Full Logging

### Core Architecture
```
[GENERATE TASK ID] → [PARALLEL PRE-FLIGHT (30s)] → [TEST FIRST] → [SEQUENTIAL MAIN] → [PARALLEL POST] → [UPDATE SPEC.md ✓]
                                                          ↓                                              (with task_id)
                                              [LOG ALL TO .task_execution.log]
                                                          ↓
                                            [BACKGROUND MONITORING (non-blocking)]
```

### Built-in Task Logger
All operations are logged with unique task IDs to `.task_execution.log`. Task IDs are added to SPEC.md for easy log searching.

---

## Command Usage

```bash
/do-tasks-v2 --step 1         # Execute single step with smart mode
/do-tasks-v2 --step 1-5       # Execute steps 1 through 5
/do-tasks-v2 --continue        # Resume from last completed
/do-tasks-v2 --monitor         # Check all background tasks
```

---

## Task Structure

Each step has **4 execution phases**:

### 1. PRE-FLIGHT PHASE (Parallel, max 30s per task)
Quick checks that run simultaneously before main execution:
- Dependency verification
- File existence checks
- Environment validation
- Resource availability

### 2. MAIN EXECUTION PHASE (Sequential, single subagent)
The primary task that must complete before moving forward:
- Uses tinker-executor agent from `.claude/agents/AGENT.md`
- Leverages skills from `.claude/skills/` (especially tinker-api)
- ONE focused objective
- Clear success criteria
- Timeout protection
- Error recovery

### 3. POST-VALIDATION PHASE (Parallel, max 30s per task)
Verification tasks that run simultaneously after main:
- Output validation
- Success criteria checks
- Metrics collection
- State persistence

### 4. BACKGROUND PHASE (Non-blocking, periodic)
Long-running monitors that don't block progression:
- Training monitoring (check every 60s)
- Log watching
- Resource tracking
- Error detection

### 5. SPEC.md UPDATE PHASE (Always executed)
**CRITICAL**: Update task status in SPEC.md:
- Mark checkbox as complete: `- [ ]` → `- [x]`
- Add completion timestamp
- Note any important outputs or metrics
- This ensures progress is visible to user

---

## Task Definitions

```yaml
# .claude/tasks/step_definitions.yaml

step_1_setup_api:
  pre_flight:
    - task: "verify_env"
      command: "echo $TINKER_API_KEY | head -c 10"
      timeout: 5
      parallel: true
    - task: "check_python"
      command: "python -c 'import sys; print(sys.version)'"
      timeout: 5
      parallel: true
    - task: "test_imports"
      command: "python -c 'import tinker'"
      timeout: 10
      parallel: true

  main:
    agent: "tinker-executor"  # Uses .claude/agents/AGENT.md
    skills: ["tinker-api"]     # Uses .claude/skills/tinker-api/
    objective: "Verify Tinker API authentication"
    script: "01_test_auth.py"
    timeout: 300
    success_criteria:
      - "API key validated"
      - "Authentication successful"

  post_validation:
    - task: "verify_connection"
      command: "python -c 'import tinker; tinker.Client()'"
      timeout: 10
      parallel: true
    - task: "log_completion"
      command: "echo 'Step 1 complete' >> .task_log"
      timeout: 5
      parallel: true

step_13_training:
  pre_flight:
    - task: "check_data"
      command: "ls -lh train.jsonl val.jsonl"
      timeout: 5
      parallel: true
    - task: "check_config"
      command: "cat training_config.yaml | head -20"
      timeout: 5
      parallel: true
    - task: "check_disk"
      command: "df -h . | grep -E '^/'"
      timeout: 5
      parallel: true

  main:
    agent: "tinker-executor"  # Uses .claude/agents/AGENT.md
    skills: ["tinker-api"]     # Uses .claude/skills/tinker-api/
    objective: "Start model training"
    script: "06_train_student_model.py"
    mode: "background"  # Special mode for long-running
    timeout: 300  # Just for startup, not full training
    success_criteria:
      - "Training started"
      - "First checkpoint saved"

  background:
    - task: "monitor_loss"
      command: "tail -n 1 training_logs/loss.txt"
      interval: 60  # Check every minute
      alert_on: "error|failed|nan"
    - task: "watch_checkpoints"
      command: "ls -lht checkpoints/ | head -5"
      interval: 120  # Check every 2 minutes
    - task: "check_memory"
      command: "ps aux | grep train_student | head -1"
      interval: 180
```

---

## Execution Logic

```python
# Pseudo-code for the executor

def execute_step(step_number):
    step_def = load_step_definition(step_number)

    # PHASE 0: Generate unique task ID and start logging
    task_id = f"task_{step_number}_{uuid.uuid4().hex[:8]}"
    log_entry = {
        "task_id": task_id,
        "step": step_number,
        "timestamp": datetime.now().isoformat(),
        "status": "STARTED"
    }
    with open(".task_execution.log", 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

    # PHASE 1: Pre-flight checks (parallel) - ALL LOGGED
    pre_results = run_parallel_tasks(
        tasks=step_def.pre_flight,
        timeout=30,
        fail_fast=True,
        task_id=task_id  # Pass task_id for logging
    )

    # Log pre-flight results
    log_phase(task_id, "PRE-FLIGHT", pre_results)

    if not all_success(pre_results):
        return handle_pre_flight_failure(pre_results, task_id)

    # PHASE 2: Main execution WITH TESTING FIRST
    # IMPORTANT: Test before assuming success!
    test_prompt = f"{step_def.main.objective}. FIRST run a test with minimal data to ensure the script works!"

    if step_def.main.mode == "background":
        # Test first with small sample
        test_result = test_script_minimal(step_def.main.script, task_id)

        if test_result.success:
            # Start in background for long-running tasks
            process_id = start_background_task_with_agent(
                agent="tinker-executor",  # From .claude/agents/AGENT.md
                skills=step_def.main.skills,  # From .claude/skills/
                task=step_def.main,
                task_id=task_id  # Pass for logging
            )
            register_background_monitor(process_id, step_def.background, task_id)
        else:
            log_error(task_id, "Test failed, not starting main task")
            return handle_test_failure(test_result, task_id)
    else:
        # Block until complete for normal tasks
        main_result = execute_main_task_with_agent(
            agent="tinker-executor",  # From .claude/agents/AGENT.md
            skills=step_def.main.skills or ["tinker-api"],
            task=step_def.main,
            timeout=step_def.main.timeout,
            test_first=True,  # Always test first!
            task_id=task_id  # Pass for logging
        )

        # Log main execution results
        log_phase(task_id, "MAIN", main_result)

        if not main_result.success:
            return handle_main_failure(main_result, task_id)

    # PHASE 3: Post-validation (parallel)
    post_results = run_parallel_tasks(
        tasks=step_def.post_validation,
        timeout=30,
        fail_fast=False  # Try all validations
    )

    # PHASE 4: Register any background monitors
    if step_def.background:
        for monitor in step_def.background:
            schedule_periodic_check(monitor)

    # PHASE 5: Update SPEC.md with task ID for searching
    update_spec_md(step_number, task_id=task_id, status="complete")

    # Log completion
    log_phase(task_id, "COMPLETED", {"step": step_number, "success": True})

    return StepResult(success=True, task_id=task_id, next_step=step_number + 1)
```

---

## Parallel Execution Patterns

### Pattern 1: Fast Exploration (max 30s)
```bash
# Run these in parallel before Step 3
parallel --timeout 30 ::: \
  "grep -r 'character-llm' --include='*.py'" \
  "find . -name '*.jsonl' -type f" \
  "ls -la datasets/"
```

### Pattern 2: Dependency Validation (max 10s each)
```bash
# Quick parallel checks
(python -c "import tinker" &)
(python -c "import datasets" &)
(python -c "import transformers" &)
wait  # Wait max 10s for all
```

### Pattern 3: Background Monitoring
```bash
# Start monitor in background
nohup watch -n 60 'tail training_logs/loss.txt' &
MONITOR_PID=$!

# Continue with next steps...
execute_step_14

# Later, check monitor
kill -0 $MONITOR_PID && echo "Still monitoring"
```

---

## Time Management Strategy

### Quick Operations (< 30s)
- File checks: `ls`, `cat`, `head`, `wc -l`
- Import tests: `python -c "import X"`
- API pings: `curl -I endpoint`
- Git status: `git status --short`

### Medium Operations (30s - 5min)
- Data generation for small samples
- Quick evaluations (10-50 examples)
- Model loading and single inference
- Dataset filtering/preparation

### Long Operations (> 5min)
- Full training runs → Run in background
- 5000 example generation → Chunk and monitor
- Full evaluation (1000+ examples) → Stream results
- Model export → Background with progress

---

## Benefits of This Architecture

1. **Non-blocking Progress**: Long tasks don't stop pipeline
2. **Early Failure Detection**: Pre-flight catches issues fast
3. **Parallel Exploration**: Learn about environment quickly
4. **Focused Execution**: One main task at a time for clarity
5. **Continuous Monitoring**: Background checks for long tasks
6. **Time-boxed Operations**: Nothing blocks indefinitely

---

## Example: Step 8 (Generate 5000 Examples)

```yaml
step_8_generate_data:
  pre_flight:
    - explore: "Check existing JSONL files"  # 10s
    - verify: "Test teacher model access"    # 10s
    - estimate: "Calculate time/cost"        # 5s

  main:
    mode: "chunked"  # Special handling
    chunks:
      - size: 100   # Generate 100, check quality
      - size: 900   # If good, generate 900 more
      - size: 4000  # If still good, complete
    checkpoint_every: 500

  background:
    - monitor: "wc -l teacher_data_*.jsonl"
    - check: "tail -1 generation.log"
    - alert: "grep ERROR generation.log"
```

---

## Integration with Agents & Skills

### Agent Usage
All main tasks use the **tinker-executor** agent from `.claude/agents/AGENT.md`:
- Configured specifically for Tinker API operations
- Has knowledge of prompt distillation workflows
- Handles errors specific to training/generation tasks

### Skills Integration (CRITICAL)

**The project MUST always rely on `.claude/skills/tinker-api/` to avoid going off track!**

Tasks leverage skills from `.claude/skills/`:

**PRIMARY (Required for ALL steps):**
- `tinker-api`: **MANDATORY** - Contains correct Tinker API usage patterns, examples, and error handling
  - Location: `.claude/skills/tinker-api/`
  - Files: `SKILL.md`, `examples.md`, `quick-reference.md`
  - Use for: ALL Tinker operations (training, sampling, evaluation, data generation)

**Supporting (Optional):**
- `document-skills`: For creating documentation and reports
- Other skills only when explicitly needed

**IMPORTANT:** Every main task execution MUST include the tinker-api skill to ensure correct API usage!

### Execution Pattern

```markdown
When executing tasks:

1. **Before each step**, run MAX 3 parallel pre-checks (30s timeout each)
2. **For main execution**, use tinker-executor agent with relevant skills
3. **After completion**, run MAX 3 parallel validations (30s timeout each)
4. **For long tasks** (training, generation), start in background and monitor
5. **Always update SPEC.md** to mark tasks complete

Agent/Skills example:
```python
Task(
    subagent_type="tinker-executor",
    skills=["tinker-api", "document-skills"],
    prompt="Execute Step 8: Generate 5000 training examples"
)
```

This ensures forward progress while maintaining quality.
```

---

## Command Integration with Testing & Logging

```bash
# In your current terminal
/do-tasks-v2 --step 1

# Output:
[TASK ID] Generated: task_1_a2b3c4d5

[PRE] ✓ Environment verified (3s) - logged
[PRE] ✓ Python 3.11 found (2s) - logged
[PRE] ✓ Tinker imported (4s) - logged

[TEST] Running minimal test first...
[TEST] ✓ Test passed with 2 examples

[MAIN] Executing: Verify Tinker API authentication...
[MAIN] Using: tinker-api skill (MANDATORY)
[MAIN] ✓ Authentication successful (12s)
[MAIN] All outputs logged with ID: task_1_a2b3c4d5

[POST] ✓ Connection test passed (5s) - logged
[POST] ✓ Results validated (1s) - logged

[SPEC] ✓ Updated SPEC.md - Step 1 marked complete
       Added task_id: task_1_a2b3c4d5 for log searching

Step 1 complete in 27s. Ready for step 2.

To view logs: grep "task_1_a2b3c4d5" .task_execution.log
```

## SPEC.md Update Mechanism

**Every successful step completion MUST update SPEC.md:**

```python
def update_spec_md(step_number, status="complete"):
    """
    Updates the task checkbox in SPEC.md to mark completion.
    This is CRITICAL for progress tracking!
    """
    # Read SPEC.md
    spec_content = read_file("SPEC.md")

    # Find the step line
    pattern = f"- \[ \] \*\*STEP {step_number}\*\*:"
    replacement = f"- [x] **STEP {step_number}**: ✓ [{datetime.now()}]"

    # Update the checkbox
    updated_content = spec_content.replace(pattern, replacement)

    # Write back to SPEC.md
    write_file("SPEC.md", updated_content)

    print(f"[SPEC] ✓ Step {step_number} marked complete in SPEC.md")
```

**Why this matters:**
- User can see progress at a glance in SPEC.md
- Provides audit trail with timestamps
- Enables resume from interruption
- Shows which steps succeeded/failed

This architecture gives you the best of both worlds: sequential reliability with parallel efficiency!