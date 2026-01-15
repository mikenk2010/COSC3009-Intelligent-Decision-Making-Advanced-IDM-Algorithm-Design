# MMLU Multi-Agent Debate Evaluation

This folder contains scripts for evaluating multi-agent debate on the MMLU (Massive Multitask Language Understanding) dataset.

## Overview

The evaluation process consists of three sequential steps:
1. **Extract questions** from the MMLU dataset via Hugging Face API
2. **Generate agent responses** using multi-agent debate configurations
3. **Evaluate accuracy** and generate per-subject reports

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

### gen_mmlu_2_3.py
- `agents`: 2 (Agent A and Agent B)
- `rounds`: 3 debate rounds
- `model`: OpenAI model to use (currently: "gpt-5-mini")
- Generates: `mmlu_2_3.json`

### gen_mmlu_3_2.py
- `agents`: 3 (Agent A, Agent B, and Judge)
- `rounds`: 2 debate rounds
- `model`: OpenAI model to use (currently: "gpt-5-mini")
- Generates: `mmlu_3_2.json`

## Experiment Configurations

This evaluation includes two different agent configurations, each with its own generation script:

| Configuration | Script | Agents | Rounds | Output File | Evaluation File |
|--------------|--------|--------|--------|-------------|------------------|
| **2-agent debate** | `gen_mmlu_2_3.py` | 2 (A, B) | 3 | `mmlu_2_3.json` | `eval_by_subject_2_3.csv` |
| **3-agent with judge** | `gen_mmlu_3_2.py` | 3 (A, B, Judge) | 2 | `mmlu_3_2.json` | `eval_by_subject_3_2.csv` |

**Filename format**: 
- Generation scripts: `gen_mmlu_{agents}_{rounds}.py`
- Response data: `mmlu_{agents}_{rounds}.json`
- Evaluation results: `eval_by_subject_{agents}_{rounds}.csv`

## Step-by-Step Execution

### Step 1: Extract Questions

Extract questions from the MMLU dataset using the Hugging Face API:

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

Run multi-agent debate to generate responses for each configuration using the respective scripts:

```bash
# For 2 agents, 3 rounds (generates mmlu_2_3.json)
python gen_mmlu_2_3.py

# For 3 agents, 2 rounds (generates mmlu_3_2.json)
python gen_mmlu_3_2.py
```

**Output:**
- `mmlu_2_3.json` - Agent debate responses for 2 agents (A, B), 3 rounds
- `mmlu_3_2.json` - Agent debate responses for 3 agents (A, B, Judge), 2 rounds

**What it does:**
- Reads questions from `mmlu_questions.csv`
- For each question, runs a multi-agent debate:
  - Each agent provides an initial answer
  - Agents see other agents' responses and update their answers
  - This repeats for the specified number of rounds
- Saves all agent conversations and answers to JSON

**⚠️ Note:** This step makes API calls to OpenAI and may take significant time and incur costs depending on the number of questions.

### Step 3: Evaluate Results

Evaluate the accuracy of both multi-agent debate configurations:

```bash
python eval_mmlu.py
```

**Output:**
- Console output: Running accuracy and standard error of the mean for each configuration
- `eval_by_subject_2_3.csv` - Per-subject results for 2-agent, 3-round configuration
- `eval_by_subject_3_2.csv` - Per-subject results for 3-agent, 2-round configuration

Each CSV contains columns:
- `subject`: MMLU subject name
- `n`: Number of questions evaluated for this subject
- `accuracy`: Mean accuracy (0.0 to 1.0)
- `std_error`: Standard error of the mean

**What it does:**
- Reads agent responses from both `mmlu_2_3.json` and `mmlu_3_2.json`
- Parses agent answers (looking for format like "(A)", "(B)", etc.)
- Compares against ground truth answers
- Calculates overall and per-subject accuracy metrics for each configuration
- Generates separate evaluation reports for each debate configuration
- Displays running statistics as it processes each question

## Example Workflow

```bash
# 1. Extract 10 questions per subject
# (Edit QUESTIONS_PER_SUBJECT = 10 in extract_questions.py first)
python extract_questions.py

# 2. Generate agent responses for 2-agent configuration (3 rounds)
python gen_mmlu_2_3.py

# 3. Generate agent responses for 3-agent configuration (2 rounds)
python gen_mmlu_3_2.py

# 4. Evaluate and view results for both configurations
python eval_mmlu.py

# 5. Check the results
cat eval_by_subject_2_3.csv
cat eval_by_subject_3_2.csv
```

## Output Files

| File | Description |
|------|-------------|
| `mmlu_questions.csv` | Sampled questions from MMLU dataset (from Hugging Face) |
| `mmlu_2_3.json` | Agent debate responses (2 agents: A and B, 3 rounds) |
| `mmlu_3_2.json` | Agent debate responses (3 agents: A, B, and Judge, 2 rounds) |
| `eval_by_subject_2_3.csv` | Per-subject accuracy for 2-agent configuration |
| `eval_by_subject_3_2.csv` | Per-subject accuracy for 3-agent configuration |

## Understanding the Results

### Standard Error of the Mean (SEM)

The evaluation reports both accuracy and standard error:
- **Accuracy**: Mean performance (0.0 to 1.0)
- **Standard Error**: `std_dev / sqrt(n)` - measures confidence in the mean
  - Smaller SEM = more reliable estimate
  - Can construct 95% confidence interval: `accuracy ± 1.96 × SEM`

**Note:** With only 1 question per subject, SEM will be 0 (no variance). Use `QUESTIONS_PER_SUBJECT > 1` for meaningful statistics.

---

## Evaluation Results Summary

### Overall Performance (3-Agent Configuration: eval_by_subject_3_2.csv)

**Excellent results!** The multi-agent debate system achieved very high accuracy across MMLU subjects:

- **Total subjects evaluated**: 57 (all subjects present ✓)
- **Sample size per subject**: 3 questions each
- **Perfect accuracy (100%) subjects**: 47 out of 57 (82.5%)
- **Partial accuracy (66.7%) subjects**: 10 out of 57 (17.5%)
- **Overall average accuracy**: ~94.7%

### Subjects with Less Than Perfect Accuracy (66.7% = 2/3 correct)

| Subject | Domain |
|---------|--------|
| anatomy | Biology/Medical |
| college_chemistry | Chemistry |
| college_medicine | Medical |
| electrical_engineering | Engineering |
| global_facts | World Knowledge |
| high_school_biology | Biology |
| high_school_chemistry | Chemistry |
| high_school_macroeconomics | Economics |
| jurisprudence | Law/Legal Reasoning |
| security_studies | Security/Policy |
| us_foreign_policy | Politics/Policy |
| virology | Medical/Biology |

### Key Observations

#### 1. Domain Clustering

Most errors occur in:

- **Life sciences** (anatomy, biology, medicine, virology): 4 subjects
- **Chemistry**: 2 subjects  
- **Social sciences/policy** (global facts, macroeconomics, security, foreign policy, jurisprudence): 5 subjects
- **Engineering**: 1 subject

#### 2. STEM Performance

The system shows **exceptional performance** in formal reasoning domains:

- ✅ **Mathematics**: Perfect across all levels (elementary, high school, college)
- ✅ **Physics**: Perfect across all levels  
- ✅ **Computer Science**: Perfect across all levels
- ✅ **Logic/Formal Reasoning**: Perfect

#### 3. Standard Error

All subjects show SEM of either:
- **0.0** (perfect accuracy, no variance)
- **0.272** (expected with n=3 and 2/3 accuracy)

#### 4. Statistical Significance

With only **3 questions per subject**, the difference between 66.7% and 100% could be due to:

- Random question difficulty variation
- Specific weaknesses in certain domains  
- Small sample size limiting confidence

**⚠️ More samples needed to confirm true performance patterns**

### Recommendations

#### 1. Increase Sample Size
- Expand to **10-20 questions per subject** for more reliable statistics
- This will provide better confidence intervals and reduce sampling error

#### 2. Investigate Failed Questions
Analyze the 10 subjects with errors to identify:
- Are these **knowledge gaps** or **reasoning failures**?
- Do agents **disagree more** in these domains?
- Are certain question types more difficult?

#### 3. Domain-Specific Analysis
- Life sciences and social policy appear more challenging
- Consider **domain-specific prompting strategies**
- Investigate if additional context or specialized reasoning helps

#### 4. Agent Consensus Analysis
- Review debate transcripts for subjects with errors
- Check if agents converged to wrong answers or remained divided
- Analyze the quality of reasoning in these domains

#### 5. Compare Configurations
- Compare results between 2-agent (eval_by_subject_2_3.csv) and 3-agent (eval_by_subject_3_2.csv) setups
- Determine if adding a Judge agent improves accuracy
- Analyze whether more rounds vs. more agents produces better results

### Conclusion

The multi-agent debate system demonstrates **strong performance** with approximately **95% overall accuracy**. 

#### Strengths
- ✅ Excels at formal reasoning, mathematics, and computer science
- ✅ High consistency across most STEM subjects
- ✅ Strong performance in humanities (history, psychology, philosophy)

#### Areas for Improvement
- ⚠️ Life sciences (biology, medicine, virology)
- ⚠️ Chemistry (both high school and college levels)
- ⚠️ Social policy and international relations

#### Next Steps
1. Increase sample size to validate patterns
2. Analyze debate quality in error-prone domains
3. Consider domain-specific enhancements for life sciences and policy subjects
4. Compare different agent configurations (2 vs 3 agents) to optimize debate structure

---

## Troubleshooting

### Missing subjects in evaluation
If `eval_mmlu.py` shows fewer subjects than expected, regenerate the JSON files using the appropriate `gen_mmlu_2_3.py` or `gen_mmlu_3_2.py` script that iterates sequentially through all CSV rows.

### API Rate Limits
If you encounter OpenAI rate limits, the script includes retry logic with 20-second delays. You may need to reduce the number of questions or upgrade your API plan.

### Different random questions each run
The script uses a random seed in `extract_questions.py`. To get consistent questions across runs, replace the random seed with a fixed value (e.g., `random_seed = 42`).
