# MMLU Multi-Agent Debate Evaluation

This folder contains scripts for evaluating multi-agent debate on the MMLU (Massive Multitask Language Understanding) dataset.

## Overview

The evaluation process consists of three sequential steps:
1. **Extract questions** from the MMLU dataset
2. **Generate agent responses** using multi-agent debate
3. **Evaluate accuracy** and generate reports

## Prerequisites

Install required dependencies:
```bash
pip install pandas numpy datasets openai python-dotenv
```

Set up your OpenAI API key in a `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

## Configuration

Before running, you can adjust these settings:

### extract_questions.py
- `QUESTIONS_PER_SUBJECT`: Number of questions to sample per subject (default: 3)
  - Line 14: Change this to extract more questions per subject for better statistics

### gen_mmlu.py
- `agents`: Number of agents in the debate (default: 3)
- `rounds`: Number of debate rounds (default: 2)
- `model`: OpenAI model to use (currently: "gpt-5-mini")

## Step-by-Step Execution

### Step 1: Extract Questions

Extract questions from the MMLU dataset (fetched from Hugging Face):

```bash
python extract_questions.py
```

**Output:**
- `mmlu_questions.csv` - Contains sampled questions from all MMLU subjects

**What it does:**
- Loads the MMLU dataset from Hugging Face (`cais/mmlu`)
- Samples N questions per subject (configurable via `QUESTIONS_PER_SUBJECT`)
- Uses deterministic sampling based on a random seed for reproducibility
- Generates a CSV with columns: question, A, B, C, D, answer, subject

### Step 2: Generate Agent Responses

Run multi-agent debate to generate responses:

```bash
python gen_mmlu.py
```

**Output:**
- `mmlu_3_2.json` - Contains agent debate responses for each question
  - Filename format: `mmlu_{agents}_{rounds}.json`

**What it does:**
- Reads questions from `mmlu_questions.csv`
- For each question, runs a multi-agent debate:
  - Each agent provides an initial answer
  - Agents see other agents' responses and update their answers
  - This repeats for the specified number of rounds
- Saves all agent conversations and answers to JSON

**⚠️ Note:** This step makes API calls to OpenAI and may take significant time and incur costs depending on the number of questions.

### Step 3: Evaluate Results

Evaluate the accuracy of the multi-agent debate:

```bash
python eval_mmlu.py
```

**Output:**
- Console output: Running accuracy and standard error of the mean
- `eval_by_subject.csv` - Per-subject accuracy report with columns:
  - `subject`: MMLU subject name
  - `n`: Number of questions evaluated for this subject
  - `accuracy`: Mean accuracy (0.0 to 1.0)
  - `std_error`: Standard error of the mean

**What it does:**
- Reads agent responses from `mmlu_3_2.json`
- Parses agent answers (looking for format like "(A)", "(B)", etc.)
- Compares against ground truth answers
- Calculates overall and per-subject accuracy metrics
- Displays running statistics as it processes each question

## Example Workflow

```bash
# 1. Extract 10 questions per subject
# (Edit QUESTIONS_PER_SUBJECT = 10 in extract_questions.py first)
python extract_questions.py

# 2. Generate agent responses (this will take time!)
python gen_mmlu.py

# 3. Evaluate and view results
python eval_mmlu.py

# 4. Check the results
cat eval_by_subject.csv
```

## Output Files

| File | Description |
|------|-------------|
| `mmlu_questions.csv` | Sampled questions from MMLU dataset |
| `mmlu_3_2.json` | Agent debate responses (3 agents, 2 rounds) |
| `eval_by_subject.csv` | Per-subject accuracy evaluation results |

## Understanding the Results

### Standard Error of the Mean (SEM)

The evaluation reports both accuracy and standard error:
- **Accuracy**: Mean performance (0.0 to 1.0)
- **Standard Error**: `std_dev / sqrt(n)` - measures confidence in the mean
  - Smaller SEM = more reliable estimate
  - Can construct 95% confidence interval: `accuracy ± 1.96 × SEM`

**Note:** With only 1 question per subject, SEM will be 0 (no variance). Use `QUESTIONS_PER_SUBJECT > 1` for meaningful statistics.

## Troubleshooting

### Missing subjects in evaluation
If `eval_mmlu.py` shows fewer subjects than expected, regenerate `mmlu_3_2.json` with the fixed `gen_mmlu.py` that iterates sequentially through all CSV rows.

### API Rate Limits
If you encounter OpenAI rate limits, the script includes retry logic with 20-second delays. You may need to reduce the number of questions or upgrade your API plan.

### Different random questions each run
The script uses a random seed in `extract_questions.py`. To get consistent questions across runs, replace the random seed with a fixed value (e.g., `random_seed = 42`).
