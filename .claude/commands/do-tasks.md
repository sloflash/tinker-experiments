---
allowed-tools: Read
argument-hint: "[optional-limit]"
description: Read tasks.md and execute remaining tasks sequentially using the execution agent
---

# Do Tasks Command

This command orchestrates automated task execution from a `tasks.md` file. It reads your task list and executes remaining items one-by-one through the specialized execution agent.

## How It Works

1. **Reads tasks.md** - Parses all tasks marked as pending or in-progress
2. **Task Filtering** - Respects optional limit ($1) if provided
3. **Delegates to Agent** - Uses `.claude/agents/AGENT.md` (your tinker-executor) for implementation
4. **Tracks Progress** - Updates task statuses in real-time
5. **Sequential Execution** - Waits for each task to complete before proceeding

## Usage

```bash
# Run all remaining tasks
/do-tasks

# Run only the next 3 tasks
/do-tasks 3

# Run next 5 tasks
/do-tasks 5
```

## Task File Format

Create a `tasks.md` in your project root following this format:

```markdown
# Task List

## Task 1: Your First Task
- **Status**: [ ] Pending | [x] Completed | [~] In Progress
- **Description**: What needs to be done
- **Expected Output**: What the result should be

## Task 2: Your Second Task
- **Status**: [ ] Pending
- **Description**: Another task description
- **Expected Output**: Expected result

...
```

## What the Agent Does

When invoked, the execution agent will:

1. Parse all pending/in-progress tasks from `tasks.md`
2. Execute each task step-by-step
3. Update task status on completion
4. Handle errors and provide recovery steps
5. Report progress and final summary

**Note**: The agent uses your existing `AGENT.md` configuration. For non-Tinker tasks, the agent will adapt its approach while maintaining comprehensive validation and error handling standards.
