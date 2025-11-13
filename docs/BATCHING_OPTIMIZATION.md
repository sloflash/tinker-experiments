# Async Optimization for Tinker API Data Generation

## Performance Improvement: 31x Speedup

### Problem
Sequential API calls for generating teacher data were extremely slow, processing one example at a time with ~5.6s per example. For 5000 examples, this would take **~7.8 hours**.

### Solution: Async Pattern (Tinker Cookbook)
We optimized the data generation using the official tinker-cookbook async pattern with `sample_async()` and `asyncio.gather()`, allowing true concurrent request processing.

### Implementation

**Before (Sequential)**:
```python
for question in questions:
    future = sampling_client.sample(prompt, params)
    result = future.result()  # Block and wait
    results.append(result)
```
Time: 5.6s/example ❌

**Failed Attempt (Manual Batching)**:
```python
# Submitted futures but used sync sample() - still blocked
futures = [sampling_client.sample(prompt, params) for prompt in batch]
for future in futures:
    result = future.result()  # Still blocking!
```
Time: 0.45s/example ⚠️ (Better but not optimal)

**Correct Solution (Async - Cookbook Pattern)**:
```python
async def sample_one(question):
    prompt = create_prompt(question)
    # KEY: Use sample_async(), not sample()
    result = await sampling_client.sample_async(
        prompt=prompt,
        sampling_params=params,
        num_samples=1
    )
    return process_result(result)

# Create all coroutines
tasks = [sample_one(q) for q in questions]

# Execute concurrently with asyncio.gather
results = await asyncio.gather(*tasks, return_exceptions=True)
```
Time: 0.18s/example ✓

### Key Insight
The critical difference is `sample_async()` vs `sample()`:
- `sample()` returns a future that blocks on `.result()`
- `sample_async()` returns an awaitable coroutine for true async concurrency
- Must use `asyncio.gather()` or similar to execute concurrently

### Results (100 examples benchmark)
- **Sequential**: 5.6s/example (560s total)
- **Manual batching**: 0.45s/example (45s total) - 12.4x speedup
- **Async (cookbook)**: 0.18s/example (18s total) - **31x speedup** ✓
- **5000 examples**: ~7.8 hours → **~15 minutes**

### Complete Working Code Pattern
```python
import asyncio
import tinker
from transformers import AutoTokenizer

async def generate_data(questions, output_file):
    # Initialize client
    client = tinker.ServiceClient()
    sampling_client = client.create_sampling_client(
        base_model="Qwen/Qwen3-30B-A3B"
    )
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B")

    # Define async sample function
    async def sample_one(question):
        prompt = f"System prompt\n\nUser: {question}\nAssistant:"
        input_ids = tokenizer.encode(prompt)
        prompt_input = tinker.types.ModelInput.from_ints(input_ids)

        # CRITICAL: Use sample_async()
        result = await sampling_client.sample_async(
            prompt=prompt_input,
            sampling_params=tinker.types.SamplingParams(
                max_tokens=300,
                temperature=0.7
            ),
            num_samples=1
        )

        response = tokenizer.decode(result.sequences[0].tokens)
        return {"question": question, "response": response}

    # Create all coroutines
    tasks = [sample_one(q) for q in questions]

    # Execute concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Save results
    with open(output_file, 'w') as f:
        for result in results:
            if not isinstance(result, Exception):
                f.write(json.dumps(result) + '\n')

# Run with asyncio
asyncio.run(generate_data(questions, "output.jsonl"))
```

### Impact
- **Data generation time**: 7.8 hours → 15 minutes (31x speedup)
- **Total pipeline time**: Reduced by ~7.5 hours
- **Scalability**: Can now generate 5000+ examples in minutes, not hours

### Lessons Learned
1. **Always use `sample_async()` for concurrent requests** - not `sample()`
2. **Follow official cookbook patterns** - they're optimized and tested
3. **Use `asyncio.gather()`** - properly handles concurrent coroutines
4. **Manual batching with sync futures doesn't work** - you still block on `.result()`

### Reference
Based on: [tinker-cookbook/prompt_distillation/create_data.py](https://github.com/thinking-machines-lab/tinker-cookbook/blob/main/tinker_cookbook/recipes/prompt_distillation/create_data.py)

This optimization makes large-scale prompt distillation experiments practical and cost-effective.
