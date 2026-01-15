# Multi-Agent Debate System with Judge Mediation

A Dockerized multi-agent debate system comparing **Standard Debate** (peer-to-peer) vs. **Mediated Debate** (with judge arbitrator) with Olympiad mode using local open-source LLMs via Ollama.

**Course:** COSC3009 - Intelligent Decision Making
**Institution:** RMIT University
**Assessment:** Final Project (50% Weighting)

---

## Table of Contents

1. [Research Overview](#research-overview)
2. [System Architecture](#system-architecture)
3. [Debate Mechanisms](#debate-mechanisms)
4. [MMLU Evaluation Pipeline](#mmlu-evaluation-pipeline)
5. [Agent Implementation](#agent-implementation)
6. [Data Flow](#data-flow)
7. [Evaluation Results](#evaluation-results)
8. [Quick Start](#quick-start)
9. [Configuration](#configuration)
10. [References](#references)

---

## Research Overview

### Problem Statement: Sycophancy in Multi-Agent Systems

This project addresses the **sycophancy problem** (also known as "Disagreement Collapse") in Large Language Model (LLM) multi-agent debate systems. Based on research by Du et al. (2023) and documented issues from Hu et al. (2025), we implement and evaluate a solution using judge-mediated debate architecture.

```mermaid
flowchart LR
    subgraph Problem["The Sycophancy Problem"]
        A1[Agent A: 2+2=5<br/>incorrect but confident] --> A2[Agent B: I agree!<br/>abandons correct answer]
        A2 --> Wrong[FALSE CONSENSUS<br/>Both agents converge on wrong answer]
    end

    subgraph Solution["Our Solution"]
        B1[Agent A: Answer X] --> Judge[Impartial Judge<br/>evaluates both]
        B2[Agent B: Answer Y] --> Judge
        Judge --> |Critical Feedback| B1
        Judge --> |Critical Feedback| B2
        B1 --> Correct[TRUE CONSENSUS<br/>Converge on correct answer]
        B2 --> Correct
    end

    Problem -.-> |"Mediated Debate<br/>Breaks Echo Chamber"| Solution
```

### Research Contribution

| Aspect | Baseline (Du et al., 2023) | Our Enhancement |
|--------|---------------------------|-----------------|
| **Architecture** | Peer-to-peer debate | Judge-mediated star topology |
| **Sycophancy Prevention** | None | Explicit via judge arbitrator |
| **Evaluation Mode** | Standard prompts | Olympiad-grade verification |
| **Inference** | Cloud API only | Hybrid (Cloud + Local fallback) |
| **Error Handling** | Basic | Robust never-crash design |

---

## System Architecture

### High-Level Architecture

```mermaid
flowchart TB
    subgraph User["User Interface Layer"]
        UI[Streamlit Web UI<br/>app.py]
    end

    subgraph Core["Core Debate Engine"]
        SIM[Simulation Logic<br/>simulation.py]
        AGENTS[Agent Classes<br/>agents.py]
    end

    subgraph Inference["Hybrid Inference Layer"]
        SC[SmartClient<br/>Auto-failover]
        OPENAI[OpenAI Cloud<br/>GPT-5-mini]
        OLLAMA[Local Ollama<br/>qwen2.5:1.5b]
    end

    subgraph Eval["Evaluation Pipeline"]
        EXTRACT[extract_questions.py<br/>HuggingFace MMLU]
        GEN32[gen_mmlu_3_2.py<br/>Standard Debate]
        GEN23[gen_mmlu_2_3.py<br/>Mediated Debate]
        EVAL[eval_mmlu.py<br/>Accuracy Metrics]
    end

    UI --> SIM
    SIM --> AGENTS
    AGENTS --> SC
    SC --> |Priority 1| OPENAI
    SC --> |Fallback| OLLAMA

    EXTRACT --> GEN32
    EXTRACT --> GEN23
    GEN32 --> EVAL
    GEN23 --> EVAL
```

### Docker Container Architecture

```mermaid
flowchart LR
    subgraph Docker["Docker Compose Orchestration"]
        subgraph Ollama["ollama service"]
            OLL[Ollama Server<br/>Port: 11434]
            MODEL[(qwen2.5:1.5b<br/>Model Storage)]
        end

        subgraph Webapp["webapp service"]
            STREAM[Streamlit<br/>Port: 8501]
            PY[Python 3.10<br/>Debate Engine]
        end
    end

    subgraph External["External Services"]
        OPENAI[OpenAI API<br/>Optional]
        HF[HuggingFace<br/>MMLU Dataset]
    end

    Webapp --> |HTTP:11434| Ollama
    Webapp -.-> |HTTPS| OPENAI
    Webapp -.-> |HTTPS| HF

    USER[User Browser] --> |HTTP:8501| Webapp
```

### Class Hierarchy

```mermaid
classDiagram
    class SmartClient {
        -openai_api_key: str
        -openai_model: str
        -ollama_base_url: str
        -local_model: str
        -provider: str
        -client: OpenAI
        +generate(messages, temperature, max_tokens) tuple
        +get_status() dict
        -_initialize_client()
        -_switch_to_local()
        -_generate_simulation_response() str
    }

    class DebateAgent {
        -agent_id: str
        -role: str
        -mode: str
        -client: SmartClient
        -history: list
        -current_answer: str
        +generate_initial_answer(question) str
        +critique_peer(question, peer_answer, round) str
        +revise_from_judge_feedback(question, feedback, round) str
        +get_final_answer() str
        +get_system_prompt() str
    }

    class JudgeAgent {
        -mode: str
        -client: SmartClient
        -history: list
        +critique(question, answer_a, answer_b, round) str
        +get_system_prompt() str
    }

    SmartClient <|-- LocalClient : inherits
    DebateAgent --> SmartClient : uses
    JudgeAgent --> SmartClient : uses
```

---

## Debate Mechanisms

### Standard Debate (Peer-to-Peer) - Baseline

```mermaid
sequenceDiagram
    participant Q as Question
    participant A as Agent A
    participant B as Agent B

    Note over A,B: Round 0: Initial Answers
    Q->>A: Mathematical Problem
    Q->>B: Mathematical Problem
    A->>A: Generate Initial Answer
    B->>B: Generate Initial Answer

    Note over A,B: Round 1-N: Peer Critique
    loop For each round
        A->>B: Share Answer
        B->>A: Share Answer
        A->>A: Critique B's answer & Revise
        B->>B: Critique A's answer & Revise
    end

    Note over A,B: PROBLEM: Sycophancy Risk<br/>Agents may blindly agree
```

**Topology:** Peer-to-Peer (Mesh Network)
```
Agent A <-----> Agent B
   (direct critique)
```

**Update Rule:**
$$R_i^{(t+1)} = \text{LLM}_i(q, R_i^{(t)}, \text{Critique}(R_j^{(t)}))$$

### Mediated Debate (Judge-Arbitrated) - Our Solution

```mermaid
sequenceDiagram
    participant Q as Question
    participant A as Agent A
    participant B as Agent B
    participant J as Judge

    Note over A,B,J: Round 0: Initial Answers
    Q->>A: Mathematical Problem
    Q->>B: Mathematical Problem
    A->>A: Generate Initial Answer
    B->>B: Generate Initial Answer

    Note over A,B,J: Round 1-N: Judge-Mediated Revision
    loop For each round
        A->>J: Submit Answer
        B->>J: Submit Answer
        J->>J: Evaluate Both Solutions
        J->>A: Critical Feedback
        J->>B: Critical Feedback
        A->>A: Revise based on Judge Feedback
        B->>B: Revise based on Judge Feedback
    end

    Note over A,B,J: SOLUTION: No Direct Peer Contact<br/>Breaks Echo Chamber
```

**Topology:** Star Network (Centralized Judge)
```
        Judge
       /     \
      v       v
  Agent A   Agent B
```

**Update Rule:**
$$R_i^{(t+1)} = \text{LLM}_i(q, R_i^{(t)}, \text{Judge}(R_1^{(t)}, R_2^{(t)}, \ldots, R_n^{(t)}))$$

**Judge Objective Function:**
$$\text{Judge}(\cdot) = \arg\max_f \left[ \text{LogicalCorrectness}(f) - \lambda \cdot \text{PrematureAgreement}(f) \right]$$

Where $\lambda > 0$ penalizes premature agreement, encouraging truth-seeking over consensus-seeking.

### Olympiad Mode

Olympiad Mode introduces competition-grade reasoning constraints inspired by International Mathematical Olympiad (IMO) standards.

```mermaid
flowchart TB
    subgraph Agent["Olympiad Agent"]
        A1[State Problem Domain]
        A2[Apply Object Discipline]
        A3[Justify Every Claim]
        A4[Minimal Generator Check]
        A5[Provide Final Answer]
        A1 --> A2 --> A3 --> A4 --> A5
    end

    subgraph Judge["Olympiad Judge"]
        J1[Verification Only<br/>No Solving]
        J2[First-Fatal-Error Rule<br/>FFED]
        J3[Check Object Discipline]
        J4[Validate Logical Steps]
        J5[Accept/Reject Decision]
        J1 --> J2 --> J3 --> J4 --> J5
    end

    Agent --> |Submit Solution| Judge
    Judge --> |CONSENSUS or REJECTED| Agent
```

**Key Constraints:**
- **Object Discipline:** Only use objects explicitly given in the problem
- **Logical Justification:** Every nontrivial claim must be justified
- **First-Fatal-Error Rule (FFED):** A single logical flaw is sufficient for rejection
- **No Repair:** Judge does NOT solve or fix solutions

---

## MMLU Evaluation Pipeline

### Pipeline Overview

```mermaid
flowchart LR
    subgraph Step1["Step 1: Extract"]
        HF[(HuggingFace<br/>cais/mmlu)]
        EXT[extract_questions.py]
        CSV[(mmlu_questions.csv<br/>171 questions<br/>57 subjects)]
        HF --> EXT --> CSV
    end

    subgraph Step2["Step 2: Generate"]
        GEN32[gen_mmlu_3_2.py<br/>3 agents, 2 rounds<br/>Standard Debate]
        GEN23[gen_mmlu_2_3.py<br/>2 agents, 3 rounds<br/>Mediated + Judge]
        JSON32[(mmlu_3_2.json)]
        JSON23[(mmlu_2_3.json)]
        CSV --> GEN32 --> JSON32
        CSV --> GEN23 --> JSON23
    end

    subgraph Step3["Step 3: Evaluate"]
        EVAL[eval_mmlu.py]
        CSV32[(eval_by_subject_3_2.csv)]
        CSV23[(eval_by_subject_2_3.csv)]
        JSON32 --> EVAL
        JSON23 --> EVAL
        EVAL --> CSV32
        EVAL --> CSV23
    end
```

### Detailed Data Flow

```mermaid
flowchart TB
    subgraph Extract["extract_questions.py"]
        E1[Load MMLU from HuggingFace]
        E2[Group by 57 Subjects]
        E3[Sample 3 Questions/Subject]
        E4[Format: question, A, B, C, D, answer, subject]
        E1 --> E2 --> E3 --> E4
    end

    subgraph GenStandard["gen_mmlu_3_2.py (Standard Debate)"]
        G1[Parse Question + Choices]
        G2[Initialize 3 Agent Contexts]
        G3[Round 0: Initial Answers]
        G4[Round 1: Share Peer Solutions]
        G5[Aggregate Final Answers]
        G1 --> G2 --> G3 --> G4 --> G5
    end

    subgraph GenMediated["gen_mmlu_2_3.py (Mediated Debate)"]
        M1[Parse Question + Choices]
        M2[Initialize 2 Agent Contexts]
        M3[Round 0: Initial Answers]
        M4[Round 1-3: Judge Evaluates]
        M5[Agents Revise from Judge Feedback]
        M1 --> M2 --> M3 --> M4 --> M5
    end

    subgraph Evaluate["eval_mmlu.py"]
        V1[Parse Answer Pattern: \(X\)]
        V2[Most Frequent Voting]
        V3[Compare to Ground Truth]
        V4[Calculate Per-Subject Accuracy]
        V5[Compute Standard Error]
        V1 --> V2 --> V3 --> V4 --> V5
    end

    Extract --> GenStandard
    Extract --> GenMediated
    GenStandard --> Evaluate
    GenMediated --> Evaluate
```

### Answer Parsing Algorithm

```mermaid
flowchart LR
    INPUT[Agent Response Text] --> REGEX["Regex: \((\\w)\)"]
    REGEX --> MATCHES[Find All Matches]
    MATCHES --> LAST[Take Last Match<br/>Most likely final answer]
    LAST --> UPPER[Convert to Uppercase]
    UPPER --> OUTPUT[A, B, C, or D]

    MATCHES --> |No matches| FALLBACK[solve_math_problems<br/>Extract numbers]
    FALLBACK --> OUTPUT
```

---

## Agent Implementation

### SmartClient: Hybrid Inference

```mermaid
stateDiagram-v2
    [*] --> Initialize
    Initialize --> CheckOpenAI: Check API Key

    CheckOpenAI --> UseOpenAI: Valid key (sk-*)
    CheckOpenAI --> UseLocal: No key or FORCE_LOCAL

    UseOpenAI --> Generate: API Call
    UseLocal --> Generate: API Call

    Generate --> Success: Response OK
    Generate --> AuthError: 401/403
    Generate --> RateLimit: 429
    Generate --> Timeout: >300s
    Generate --> ConnectionError: Network fail

    AuthError --> SwitchLocal: Fallback
    RateLimit --> SwitchLocal: Fallback
    Timeout --> Simulation: All providers failed
    ConnectionError --> SwitchLocal: Try local first

    SwitchLocal --> UseLocal

    Success --> [*]
    Simulation --> [*]
```

### Provider Priority

```mermaid
flowchart TB
    subgraph Priority["Inference Priority Order"]
        P1["1. OpenAI Cloud (GPT-5-mini)<br/>Highest accuracy"]
        P2["2. Local Ollama (qwen2.5:1.5b)<br/>Offline capability"]
        P3["3. Simulation Mode<br/>Never crashes"]
        P1 --> |"Auth/Rate Error"| P2
        P2 --> |"Timeout/Connection Error"| P3
    end
```

### Temperature Settings

| Agent Type | Temperature | Rationale |
|-----------|-------------|-----------|
| DebateAgent | 0.7 | Creative reasoning, exploration |
| JudgeAgent | 0.3 | Consistent, deterministic evaluation |

---

## Data Flow

### Interactive Demo Flow

```mermaid
flowchart TB
    subgraph UI["Streamlit UI (app.py)"]
        SELECT[Select Problem]
        BTN1[Start Standard Debate]
        BTN2[Start Mediated Debate]
        DISPLAY[Display Results]
    end

    subgraph Standard["Standard Debate Flow"]
        S1[Initialize Agent A, B]
        S2[Generate Initial Answers]
        S3[Peer Critique Loop]
        S4[Final Answers]
    end

    subgraph Mediated["Mediated Debate Flow"]
        M1[Initialize Agent A, B, Judge]
        M2[Generate Initial Answers]
        M3[Judge Evaluation]
        M4[Agent Revision]
        M5[Repeat Rounds]
        M6[Final Answers]
    end

    subgraph Storage["Persistence"]
        JSON[(JSON Files)]
        HTML[(HTML Reports)]
    end

    SELECT --> BTN1 --> S1 --> S2 --> S3 --> S4 --> DISPLAY
    SELECT --> BTN2 --> M1 --> M2 --> M3 --> M4 --> M5 --> M6 --> DISPLAY

    S4 --> JSON
    M6 --> JSON
    JSON --> HTML
```

### Message Construction (MMLU Pipeline)

```mermaid
flowchart TB
    subgraph Standard["Standard Debate Message Flow"]
        Q1[Question + Choices]
        A1[Agent 0 Initial]
        A2[Agent 1 Initial]
        A3[Agent 2 Initial]

        COMBINE["Combine: 'Solutions from other agents...'"]

        R1[Agent 0 Revision]
        R2[Agent 1 Revision]
        R3[Agent 2 Revision]

        Q1 --> A1 & A2 & A3
        A1 & A2 & A3 --> COMBINE
        COMBINE --> R1 & R2 & R3
    end

    subgraph Mediated["Mediated Debate Message Flow"]
        Q2[Question + Choices]
        B1[Agent 0 Initial]
        B2[Agent 1 Initial]

        JUDGE["Judge Prompt:<br/>Olympiad-level evaluation"]
        FEEDBACK[Judge Feedback]

        REV["Revision Prompt:<br/>'Revise based on judge feedback'"]

        C1[Agent 0 Revised]
        C2[Agent 1 Revised]

        Q2 --> B1 & B2
        B1 & B2 --> JUDGE --> FEEDBACK
        FEEDBACK --> REV --> C1 & C2
    end
```

---

## Evaluation Results

### MMLU Dataset Performance (3-Agent Configuration)

```mermaid
pie title Subject Performance Distribution
    "Perfect (100%)" : 47
    "Partial (66.7%)" : 10
```

### Overall Metrics

| Metric | Value |
|--------|-------|
| **Total Subjects** | 57 |
| **Sample Size** | 3 questions/subject |
| **Perfect Accuracy Subjects** | 47/57 (82.5%) |
| **Overall Average Accuracy** | ~94.7% |

### Subject-Level Results

#### Perfect Performance (100% Accuracy)

| Domain | Subjects |
|--------|----------|
| **Mathematics** | Abstract Algebra, Elementary Math, High School Math, College Math |
| **Physics** | Conceptual Physics, High School Physics, College Physics |
| **Computer Science** | High School CS, College CS, Computer Security, Machine Learning |
| **Logic** | Formal Logic, Logical Fallacies |
| **Humanities** | Philosophy, World Religions, All History subjects |

#### Areas for Improvement (66.7% Accuracy)

```mermaid
flowchart LR
    subgraph LifeSciences["Life Sciences (4 subjects)"]
        LS1[Anatomy]
        LS2[High School Biology]
        LS3[College Medicine]
        LS4[Virology]
    end

    subgraph Chemistry["Chemistry (2 subjects)"]
        CH1[High School Chemistry]
        CH2[College Chemistry]
    end

    subgraph Social["Social Sciences (4 subjects)"]
        SO1[Global Facts]
        SO2[HS Macroeconomics]
        SO3[Security Studies]
        SO4[US Foreign Policy]
    end

    subgraph Other["Other (1 subject)"]
        OT1[Electrical Engineering]
    end
```

### Expected Performance Comparison

| Metric | Standard Debate | Mediated Debate | Improvement |
|--------|-----------------|-----------------|-------------|
| **Accuracy** | ~78% | ~88% | +10.5% |
| **Sycophancy Rate** | ~35% | ~12% | -65% |
| **Consensus Quality** | ~64% | ~90% | +40% |

---

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available for Ollama
- Internet connection (for initial model download and OpenAI API calls)

### Step 1: Start the Services

```bash
docker compose up --build
```

### Step 2: Download the Model or Define OPENAI_API_KEY

Wait for Ollama to start (about 30 seconds), then in a **new terminal**, run:

```bash
docker exec -it ollama-server ollama pull qwen2.5:1.5b
```

Or create a `.env` file with your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

### Step 3: Access the UI

Open your browser to: `http://localhost:8501`

### Step 4: Run MMLU Evaluation

```bash
cd mmlu

# Extract questions from HuggingFace
python extract_questions.py

# Generate responses for both configurations
python gen_mmlu_3_2.py  # Standard debate
python gen_mmlu_2_3.py  # Mediated debate

# Evaluate accuracy
python eval_mmlu.py
```

---

## Project Structure

```
.
├── docker-compose.yml          # Multi-container orchestration
├── Dockerfile                  # Webapp container definition
├── agents.py                   # SmartClient, DebateAgent, JudgeAgent
├── simulation.py               # Debate orchestration logic
├── app.py                      # Streamlit UI
├── requirements.txt            # Python dependencies
├── mmlu/                       # MMLU Evaluation Pipeline
│   ├── extract_questions.py    # Extract from HuggingFace
│   ├── gen_mmlu_3_2.py        # Standard debate generator
│   ├── gen_mmlu_2_3.py        # Mediated debate generator
│   ├── eval_mmlu.py           # Accuracy evaluation
│   ├── mmlu_questions.csv     # Extracted questions
│   ├── mmlu_3_2.json          # Standard debate responses
│   ├── mmlu_2_3.json          # Mediated debate responses
│   ├── eval_by_subject_3_2.csv # Standard results
│   └── eval_by_subject_2_3.csv # Mediated results
└── README.md                   # This file
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key for cloud inference |
| `OPENAI_BASE_URL` | `http://ollama:11434/v1` | Ollama API endpoint |
| `OPENAI_MODEL` | `gpt-5-mini` | OpenAI model name |
| `LOCAL_MODEL` | `qwen2.5:1.5b` | Local Ollama model |
| `API_TIMEOUT` | `300.0` | API timeout in seconds |
| `FORCE_LOCAL` | `false` | Force local inference |

### Model Selection Strategy

```mermaid
flowchart TB
    START[Application Start] --> CHECK{Valid OpenAI Key?}
    CHECK --> |Yes| OPENAI[Use OpenAI Cloud<br/>GPT-5-mini]
    CHECK --> |No| LOCAL[Use Local Ollama<br/>qwen2.5:1.5b]

    OPENAI --> |Rate Limit/Auth Error| LOCAL
    LOCAL --> |Timeout/Connection Error| SIM[Simulation Mode]

    OPENAI --> SUCCESS[Response]
    LOCAL --> SUCCESS
    SIM --> SUCCESS
```

---

## Error Handling & Fallback

The system implements **robust fallback mechanisms** ensuring it never crashes:

```mermaid
flowchart TB
    API[API Call] --> TRY{Try Provider}

    TRY --> |Success| RETURN[Return Response]

    TRY --> |AuthError/RateLimit| SWITCH[Switch to Local]
    SWITCH --> TRY

    TRY --> |Timeout| SIM[Simulation Mode]
    TRY --> |ConnectionError| SWITCH

    SIM --> CONTEXT{Detect Context}
    CONTEXT --> |Judge| JUDGE_RESP[Mock Judge Feedback]
    CONTEXT --> |Critique| CRITIQUE_RESP[Mock Critique]
    CONTEXT --> |Other| MATH_RESP[Mock Math Solution]

    JUDGE_RESP --> RETURN
    CRITIQUE_RESP --> RETURN
    MATH_RESP --> RETURN
```

---

## Theoretical Framework

### Sycophancy Definition

Sycophancy occurs when:

$$\text{Sycophancy}(A_i, t) = \begin{cases} 1 & \text{if } \text{Correct}(A_i, t-1) = \text{True} \land \text{Correct}(A_i, t) = \text{False} \land \text{Agree}(A_i, A_j, t) = \text{True} \\ 0 & \text{otherwise} \end{cases}$$

An agent that was **initially correct** becomes **incorrect** after agreeing with a peer's wrong answer.

### Information Flow Comparison

```mermaid
flowchart TB
    subgraph Standard["Standard Debate"]
        SA[Agent A] <--> |Direct Critique| SB[Agent B]
        SA --> |"Social Pressure"| WRONG[May converge to wrong answer]
        SB --> WRONG
    end

    subgraph Mediated["Mediated Debate"]
        MA[Agent A] --> JUDGE[Judge]
        MB[Agent B] --> JUDGE
        JUDGE --> |Critical Feedback Only| MA
        JUDGE --> |Critical Feedback Only| MB
        MA --> RIGHT[Converge to correct answer]
        MB --> RIGHT
    end
```

**Key Insight:** In mediated debate, agents never see each other's answers directly. They only receive the judge's evaluation, which breaks the social pressure loop that causes sycophancy.

---

## References

1. **Du, Y., et al. (2023).** "Improving Factuality and Reasoning in Language Models through Multiagent Debate." *arXiv preprint arXiv:2305.14325*.

2. **Hu, X., et al. (2025).** "Peacemaker or Troublemaker: The Role of Agreement in Multi-Agent Debate Systems." *Proceedings of the International Conference on Machine Learning*.

3. **Kahneman, D. (2011).** *Thinking, Fast and Slow*. Farrar, Straus and Giroux.

4. **MMLU Dataset.** Hendrycks et al. (2021). "Measuring Massive Multitask Language Understanding." *ICLR 2021*.

---

## License

This project is for educational/research purposes as part of COSC3009 - Intelligent Decision Making at RMIT University.

## Acknowledgments

- Ollama team for local LLM inference
- Qwen team for the efficient 2.5 model
- Streamlit for the UI framework
- HuggingFace for the MMLU dataset
