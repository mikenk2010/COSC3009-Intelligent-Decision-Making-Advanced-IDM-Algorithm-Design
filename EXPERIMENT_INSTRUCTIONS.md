# Instructions for Collecting Real Experimental Data

## Overview

To replace the synthetic results in `Assignment_Report.md` with actual experimental data, you need to run the debate system and collect real metrics.

## Prerequisites

1. Docker and Docker Compose installed and running
2. Ollama container running
3. Qwen 2.5:1.5b model loaded in Ollama

## Step-by-Step Instructions

### Step 1: Start Docker Containers

```bash
docker compose up -d
```

Wait for containers to start (about 30 seconds).

### Step 2: Load the Model

```bash
docker exec -it ollama-server ollama pull qwen2.5:1.5b
```

Wait for the model to download (~1GB, may take a few minutes).

### Step 3: Verify Model is Loaded

```bash
docker exec -it ollama-server ollama list
```

You should see `qwen2.5:1.5b` in the list.

### Step 4: Run the Experiment

**Option A: Using the convenience script (recommended)**

```bash
./run_experiments.sh
```

**Option B: Manual execution**

```bash
# Copy script to container
docker cp collect_experimental_data.py debate-webapp:/app/

# Run experiment (takes 10-20 minutes)
docker exec -it debate-webapp python collect_experimental_data.py

# Copy results back
docker cp debate-webapp:/app/experimental_results.json ./
```

### Step 5: Update the Report

After the experiment completes, update the report with real results:

```bash
python update_report_with_results.py
```

This will automatically update `Assignment_Report.md` with the actual experimental data.

## What the Experiment Does

1. **Runs 3 test problems** through both Standard and Mediated debate
2. **Collects metrics** for each debate:
   - Accuracy (correctness of final answers)
   - Sycophancy rate (agents switching from correct to incorrect)
   - False consensus rate
   - True consensus rate
   - Consensus quality

3. **Calculates aggregate statistics** across all problems
4. **Saves results** to `experimental_results.json`

## Expected Duration

- **Per problem:** ~3-5 minutes (9 LLM calls × ~20-30s each)
- **Total time:** ~10-20 minutes for 3 problems

## Troubleshooting

### "Cannot connect to Ollama"
- Check if containers are running: `docker compose ps`
- Check Ollama logs: `docker compose logs ollama`
- Restart Ollama: `docker compose restart ollama`

### "Model not found"
- Pull the model: `docker exec -it ollama-server ollama pull qwen2.5:1.5b`
- Verify: `docker exec -it ollama-server ollama list`

### Timeout Errors
- The system will automatically use simulation mode on timeout
- Results will be marked as mock/simulation
- Check system resources (CPU, RAM)
- Consider increasing timeout in `docker-compose.yml`

## Understanding the Results

The results file (`experimental_results.json`) contains:
- **Aggregate metrics**: Overall statistics
- **Raw results**: Individual problem results with detailed analysis

The update script will automatically:
- Replace synthetic numbers in the report
- Calculate improvements and percentages
- Update all relevant sections

## Next Steps

After updating the report:
1. Review the results in `experimental_results.json`
2. Check that the updated report makes sense
3. If needed, run more problems to get better statistics
4. Consider running on a larger dataset for more robust results

