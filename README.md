# Multi-Agent Debate System with Judge Mediation

A Dockerized multi-agent debate system comparing **Standard Debate** (peer-to-peer) vs. **Mediated Debate** (with judge arbitrator) featuring Olympiad mode using local open-source LLMs via Ollama.

**Course:** COSC3009 - Intelligent Decision Making
**Institution:** RMIT University
**Assessment:** Final Project (50% Weighting)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Research Overview](#research-overview)
3. [System Architecture](#system-architecture)
4. [Debate Mechanisms](#debate-mechanisms)
5. [MMLU Evaluation Pipeline](#mmlu-evaluation-pipeline)
6. [Agent Implementation](#agent-implementation)
7. [Data Flow](#data-flow)
8. [Evaluation Results](#evaluation-results)
9. [Quick Start](#quick-start)
10. [Project Structure](#project-structure)
11. [Configuration](#configuration)
12. [Error Handling](#error-handling)
13. [Theoretical Framework](#theoretical-framework)
14. [Future Enhancements](#future-enhancements)
15. [Demo](#demo)
16. [References](#references)

---

## Executive Summary

This project implements a novel **Judge-Mediated Multi-Agent Debate** architecture that addresses the critical **Social Conformity Bias** (Sycophancy) problem in LLM-based multi-agent systems. By introducing an impartial Judge agent that mediates all communication between debating agents, we structurally eliminate the echo chamber effect that plagues traditional peer-to-peer debate approaches.

### Key Contributions

| Contribution | Description |
|-------------|-------------|
| **Architectural Innovation** | Star-topology debate with centralized Judge arbitration |
| **Sycophancy Prevention** | Structural solution vs. prompting-based mitigation |
| **Olympiad Mode** | Competition-grade reasoning with First-Fatal-Error Rule (FFED) |
| **Hybrid Inference** | OpenAI Cloud with Ollama local fallback, never crashes |
| **Empirical Validation** | MMLU benchmark evaluation across 57 subjects |

### Performance Highlights

```
Standard Debate (Baseline):  91.8% accuracy on MMLU
Mediated Debate (Ours):      94.7% accuracy on MMLU
                             ─────────────────────
Improvement:                 +2.9% absolute gain
```

### Documentation Guide

| Document | Purpose | Key Sections |
|----------|---------|--------------|
| **[README.md](README.md)** | Quick reference & setup guide | Architecture, Quick Start, Evaluation Results |
| **[FINAL_REPORT_WRITING.md](FINAL_REPORT_WRITING.md)** | Comprehensive academic report (17 sections) | Related Work, Evaluation & Discussion, Critical Self-Assessment |
| **[COSC3009_Final_Report.md](COSC3009_Final_Report.md)** | Detailed methodology | Formal definitions, concrete debate examples |
| **[Architecture_Explanation.md](Architecture_Explanation.md)** | Visual architecture guide | Mermaid diagrams, topology comparison |

---

## Research Overview

### Problem Statement: Social Conformity Bias in Multi-Agent Systems

This project addresses the **sycophancy problem** (Social Conformity Bias, Disagreement Collapse) in Large Language Model (LLM) multi-agent debate systems. Based on research by Du et al. (2023) and documented issues from Hu et al. (2025), we implement and evaluate a solution using judge-mediated debate architecture.

```mermaid
flowchart LR
    subgraph Problem["The Sycophancy Problem"]
        A1["Agent A: 2+2=5 - Incorrect but CONFIDENT"] --> A2["Agent B: I agree! - Abandons correct answer"]
        A2 --> Wrong["FALSE CONSENSUS - Both converge on wrong answer"]
    end

    subgraph Solution["Our Solution: Judge Mediation"]
        B1["Agent A: Answer X"] --> Judge["Impartial Judge - Evaluates both independently"]
        B2["Agent B: Answer Y"] --> Judge
        Judge --> |"Critical Feedback"| B1
        Judge --> |"Critical Feedback"| B2
        B1 --> Correct["TRUE CONSENSUS - Converge on correct answer"]
        B2 --> Correct
    end

    Problem -.-> |"Mediated Debate Breaks Echo Chamber"| Solution

    style Wrong fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style Correct fill:#51cf66,stroke:#2f9e44,color:#fff
    style Judge fill:#74c0fc,stroke:#1971c2,color:#000
```

### Why Sycophancy Occurs

| Factor | Explanation |
|--------|-------------|
| **RLHF Training** | LLMs are trained to be "helpful" and "agreeable" which backfires in adversarial settings |
| **Confidence Mimicry** | Models tend to adopt confident-sounding positions from peers |
| **Social Pressure** | Direct peer exposure creates implicit pressure to conform |
| **Asch Effect** | Similar to human conformity bias documented by Asch (1951) |

### Research Contribution Comparison

| Aspect | Baseline (Du et al., 2023) | Our Enhancement |
|--------|---------------------------|-----------------|
| **Architecture** | Peer-to-peer mesh network | Judge-mediated star topology |
| **Sycophancy Prevention** | None (hope for diversity) | Explicit via judge arbitrator |
| **Convergence Criterion** | Answer agreement | Logical correctness verification |
| **Evaluation Mode** | Standard prompts | Olympiad-grade verification (FFED) |
| **Inference** | Cloud API only | Hybrid (Cloud + Local + Simulation fallback) |
| **Error Handling** | Basic retry | Robust never-crash design |

---

## System Architecture

### High-Level Architecture Overview

```mermaid
flowchart TB
    subgraph User["User Interface Layer"]
        UI["Streamlit Web UI - app.py - Port 8501"]
    end

    subgraph Core["Core Debate Engine"]
        SIM["Simulation Logic - simulation.py"]
        AGENTS["Agent Classes - agents.py"]
    end

    subgraph Inference["Hybrid Inference Layer"]
        SC["SmartClient - Auto-failover Logic"]
        OPENAI["OpenAI Cloud - GPT-5-mini - Priority 1"]
        OLLAMA["Local Ollama - qwen2.5:1.5b - Fallback"]
        SIMMODE["Simulation Mode - Never Crashes"]
    end

    subgraph Eval["Evaluation Pipeline"]
        EXTRACT["extract_questions.py - HuggingFace MMLU"]
        GEN32["gen_mmlu_3_2.py - Standard Debate"]
        GEN23["gen_mmlu_2_3.py - Mediated Debate"]
        EVALPY["eval_mmlu.py - Accuracy Metrics"]
    end

    UI --> SIM
    SIM --> AGENTS
    AGENTS --> SC
    SC --> |"Priority 1"| OPENAI
    SC --> |"Fallback 1"| OLLAMA
    SC --> |"Fallback 2"| SIMMODE

    EXTRACT --> GEN32
    EXTRACT --> GEN23
    GEN32 --> EVALPY
    GEN23 --> EVALPY
```

### Docker Container Architecture

```mermaid
flowchart LR
    subgraph Docker["Docker Compose Orchestration"]
        subgraph Ollama["ollama service"]
            OLL["Ollama Server - Port 11434"]
            MODEL[("qwen2.5:1.5b Model Storage")]
        end

        subgraph Webapp["webapp service"]
            STREAM["Streamlit - Port 8501"]
            PY["Python 3.10 Debate Engine"]
        end
    end

    subgraph External["External Services"]
        OPENAIEXT["OpenAI API - Optional"]
        HF["HuggingFace - MMLU Dataset"]
    end

    Webapp --> |"HTTP:11434"| Ollama
    Webapp -.-> |"HTTPS"| OPENAIEXT
    Webapp -.-> |"HTTPS"| HF

    USER["User Browser"] --> |"HTTP:8501"| Webapp

    style Ollama fill:#e7f5ff,stroke:#1971c2
    style Webapp fill:#fff3bf,stroke:#f59f00
```

### Class Hierarchy and Relationships

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

    note for SmartClient "Handles provider switching and failover"
    note for JudgeAgent "Temperature: 0.3 for consistency"
    note for DebateAgent "Temperature: 0.7 for creativity"
```

### Network Topology Comparison

```mermaid
flowchart TB
    subgraph Mesh["MESH TOPOLOGY - Original Du et al."]
        direction LR
        M_A["Agent A"] <--> M_B["Agent B"]
        M_A <--> M_C["Agent C"]
        M_B <--> M_C
    end

    subgraph Star["STAR TOPOLOGY - Our Solution"]
        direction TB
        S_J["JUDGE"]
        S_A["Agent A"] --> S_J
        S_B["Agent B"] --> S_J
        S_J --> S_A
        S_J --> S_B
    end

    Mesh --> |"n*n-1 / 2 connections - High sycophancy risk"| BAD["Vulnerable to Echo Chamber"]
    Star --> |"2n connections - Centralized control"| GOOD["Robust Against Sycophancy"]

    style S_J fill:#74c0fc,stroke:#1971c2,color:#000
    style BAD fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style GOOD fill:#51cf66,stroke:#2f9e44,color:#fff
```

---

## Debate Mechanisms

### Standard Debate (Peer-to-Peer) - Baseline

The original architecture from Du et al. (2023) where agents directly critique each other's answers.

```mermaid
sequenceDiagram
    participant Q as Question
    participant A as Agent A
    participant B as Agent B

    Note over A,B: Round 0 - Initial Answers
    Q->>A: Mathematical Problem
    Q->>B: Mathematical Problem
    A->>A: Generate Initial Answer
    B->>B: Generate Initial Answer

    Note over A,B: Round 1-N - Peer Critique Loop
    loop For each round
        A->>B: Share Answer
        B->>A: Share Answer
        A->>A: Critique B and Revise
        B->>B: Critique A and Revise
    end

    Note over A,B: PROBLEM - Sycophancy Risk - Agents may blindly agree
```

**Network Topology:** Peer-to-Peer (Mesh Network)
```
Agent A <------> Agent B
    (direct critique)
```

**Update Rule:**

$$R_i^{(t+1)} = \text{LLM}_i(q, R_i^{(t)}, \text{Critique}(R_j^{(t)}))$$

**Vulnerability:** Agents see each other's confidence levels, creating social pressure to agree even when the peer's answer is incorrect.

### Mediated Debate (Judge-Arbitrated) - Our Solution

Our enhanced architecture introduces an impartial Judge that mediates all communication.

```mermaid
sequenceDiagram
    participant Q as Question
    participant A as Agent A
    participant B as Agent B
    participant J as Judge

    Note over A,J: Round 0 - Initial Answers
    Q->>A: Mathematical Problem
    Q->>B: Mathematical Problem
    A->>A: Generate Initial Answer
    B->>B: Generate Initial Answer

    Note over A,J: Round 1-N - Judge Mediated Revision
    loop For each round
        A->>J: Submit Answer
        B->>J: Submit Answer
        J->>J: Evaluate Both Solutions
        J->>A: Critical Feedback - No peer answer shown
        J->>B: Critical Feedback - No peer answer shown
        A->>A: Revise based on Judge Feedback
        B->>B: Revise based on Judge Feedback
    end

    Note over A,J: SOLUTION - No Direct Peer Contact - Echo Chamber Broken
```

**Network Topology:** Star Network (Centralized Judge)
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

Where λ > 0 penalizes premature agreement, encouraging truth-seeking over consensus-seeking.

### Temperature Strategy

| Agent Type | Temperature | Purpose |
|-----------|-------------|---------|
| **DebateAgent** | 0.7 (Higher) | Creative diversity, exploration of solution space |
| **JudgeAgent** | 0.3 (Lower) | Deterministic, consistent evaluation |

**Rationale:** This asymmetric temperature follows the exploration-exploitation trade-off. Agents explore diverse solutions while the Judge provides stable, reliable feedback.

### Olympiad Mode

Olympiad Mode introduces competition-grade reasoning constraints inspired by International Mathematical Olympiad (IMO) standards.

```mermaid
flowchart TB
    subgraph Agent["Olympiad Agent Protocol"]
        A1["1. State Problem Domain"]
        A2["2. Apply Object Discipline"]
        A3["3. Justify Every Claim"]
        A4["4. Minimal Generator Check"]
        A5["5. Provide Final Answer"]
        A1 --> A2 --> A3 --> A4 --> A5
    end

    subgraph Judge["Olympiad Judge Protocol"]
        J1["1. Verification Only - No Solving"]
        J2["2. First-Fatal-Error Rule - FFED"]
        J3["3. Check Object Discipline"]
        J4["4. Validate Logical Steps"]
        J5["5. CONSENSUS or REJECTED"]
        J1 --> J2 --> J3 --> J4 --> J5
    end

    Agent --> |"Submit Solution"| Judge
    Judge --> |"Verdict with Feedback"| Agent

    style J2 fill:#ff6b6b,stroke:#c92a2a,color:#fff
```

**Key Constraints:**

| Constraint | Description |
|-----------|-------------|
| **Object Discipline** | Only use objects explicitly given in the problem |
| **Logical Justification** | Every nontrivial claim must be justified |
| **First-Fatal-Error Rule (FFED)** | A single logical flaw is sufficient for rejection |
| **No Repair Policy** | Judge does NOT solve or fix solutions |

**Judge Decision Protocol:**

| Verdict | Condition |
|---------|-----------|
| **CONSENSUS** | Both agents provide logically correct solutions with valid reasoning chains |
| **REJECTED** | At least one agent has a fatal error in reasoning or computation |

---

## MMLU Evaluation Pipeline

### Pipeline Overview

```mermaid
flowchart LR
    subgraph Step1["Step 1: Extract"]
        HF[("HuggingFace cais/mmlu")]
        EXT["extract_questions.py"]
        CSV[("mmlu_questions.csv - 171 questions - 57 subjects")]
        HF --> EXT --> CSV
    end

    subgraph Step2["Step 2: Generate"]
        GEN32["gen_mmlu_3_2.py - 3 agents 2 rounds - Standard Debate"]
        GEN23["gen_mmlu_2_3.py - 2 agents 3 rounds - Mediated + Judge"]
        JSON32[("mmlu_3_2.json")]
        JSON23[("mmlu_2_3.json")]
        CSV --> GEN32 --> JSON32
        CSV --> GEN23 --> JSON23
    end

    subgraph Step3["Step 3: Evaluate"]
        EVALSCRIPT["eval_mmlu.py"]
        CSV32[("eval_by_subject_3_2.csv")]
        CSV23[("eval_by_subject_2_3.csv")]
        JSON32 --> EVALSCRIPT
        JSON23 --> EVALSCRIPT
        EVALSCRIPT --> CSV32
        EVALSCRIPT --> CSV23
    end
```

### Detailed Data Flow

```mermaid
flowchart TB
    subgraph Extract["extract_questions.py"]
        E1["Load MMLU from HuggingFace"]
        E2["Group by 57 Subjects"]
        E3["Sample 3 Questions per Subject"]
        E4["Format: question, A, B, C, D, answer, subject"]
        E1 --> E2 --> E3 --> E4
    end

    subgraph GenStandard["gen_mmlu_3_2.py - Standard Debate"]
        G1["Parse Question + Choices"]
        G2["Initialize 3 Agent Contexts"]
        G3["Round 0: Initial Answers"]
        G4["Round 1: Share Peer Solutions"]
        G5["Aggregate Final Answers"]
        G1 --> G2 --> G3 --> G4 --> G5
    end

    subgraph GenMediated["gen_mmlu_2_3.py - Mediated Debate"]
        M1["Parse Question + Choices"]
        M2["Initialize 2 Agent Contexts"]
        M3["Round 0: Initial Answers"]
        M4["Round 1-3: Judge Evaluates"]
        M5["Agents Revise from Judge Feedback"]
        M1 --> M2 --> M3 --> M4 --> M5
    end

    subgraph Evaluate["eval_mmlu.py"]
        V1["Parse Answer Pattern - Match X in parentheses"]
        V2["Most Frequent Voting"]
        V3["Compare to Ground Truth"]
        V4["Calculate Per-Subject Accuracy"]
        V5["Compute Standard Error"]
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
    INPUT["Agent Response Text"] --> REGEX["Regex Pattern - Find letter in parentheses"]
    REGEX --> MATCHES["Find All Matches"]
    MATCHES --> LAST["Take Last Match - Most likely final answer"]
    LAST --> UPPER["Convert to Uppercase"]
    UPPER --> OUTPUT["A, B, C, or D"]

    MATCHES --> |"No matches"| FALLBACK["solve_math_problems - Extract numbers"]
    FALLBACK --> OUTPUT
```

---

## Agent Implementation

### SmartClient: Hybrid Inference with Auto-Failover

```mermaid
stateDiagram-v2
    [*] --> Initialize
    Initialize --> CheckOpenAI: Check API Key

    CheckOpenAI --> UseOpenAI: Valid key exists
    CheckOpenAI --> UseLocal: No key or FORCE_LOCAL set

    UseOpenAI --> Generate: API Call
    UseLocal --> Generate: API Call

    Generate --> Success: Response OK
    Generate --> AuthError: 401 or 403
    Generate --> RateLimit: 429 Too Many Requests
    Generate --> Timeout: Exceeds 300s
    Generate --> ConnectionError: Network failure

    AuthError --> SwitchLocal: Fallback
    RateLimit --> SwitchLocal: Fallback
    Timeout --> Simulation: All providers failed
    ConnectionError --> SwitchLocal: Try local first

    SwitchLocal --> UseLocal

    Success --> [*]
    Simulation --> [*]
```

### Provider Priority Chain

```mermaid
flowchart TB
    subgraph Priority["Inference Priority Order"]
        P1["1. OpenAI Cloud - GPT-5-mini - Highest accuracy"]
        P2["2. Local Ollama - qwen2.5:1.5b - Offline capability"]
        P3["3. Simulation Mode - Never crashes - Guaranteed response"]
        P1 --> |"Auth or Rate Error"| P2
        P2 --> |"Timeout or Connection Error"| P3
    end

    style P1 fill:#d3f9d8,stroke:#2f9e44
    style P2 fill:#fff3bf,stroke:#f59f00
    style P3 fill:#ffe3e3,stroke:#c92a2a
```

### Simulation Mode Context Detection

```mermaid
flowchart TB
    API["API Call Failed"] --> SIM["Enter Simulation Mode"]

    SIM --> CONTEXT{"Detect Message Context"}

    CONTEXT --> |"Contains 'judge' or 'evaluate'"| JUDGE_RESP["Mock Judge Feedback - CONSENSUS or critique"]
    CONTEXT --> |"Contains 'critique' or 'peer'"| CRITIQUE_RESP["Mock Critique Response"]
    CONTEXT --> |"Math problem detected"| MATH_RESP["Mock Math Solution - Step-by-step"]
    CONTEXT --> |"Default"| DEFAULT_RESP["Generic Response"]

    JUDGE_RESP --> RETURN["Return Response - Never crash"]
    CRITIQUE_RESP --> RETURN
    MATH_RESP --> RETURN
    DEFAULT_RESP --> RETURN

    style SIM fill:#ffe3e3,stroke:#c92a2a
    style RETURN fill:#d3f9d8,stroke:#2f9e44
```

---

## Data Flow

### Interactive Demo Flow

```mermaid
flowchart TB
    subgraph UI["Streamlit UI - app.py"]
        SELECT["Select Problem"]
        BTN1["Start Standard Debate"]
        BTN2["Start Mediated Debate"]
        DISPLAY["Display Results"]
    end

    subgraph Standard["Standard Debate Flow"]
        S1["Initialize Agent A, B"]
        S2["Generate Initial Answers"]
        S3["Peer Critique Loop"]
        S4["Final Answers"]
    end

    subgraph Mediated["Mediated Debate Flow"]
        M1["Initialize Agent A, B, Judge"]
        M2["Generate Initial Answers"]
        M3["Judge Evaluation"]
        M4["Agent Revision"]
        M5["Repeat Rounds"]
        M6["Final Answers"]
    end

    subgraph Storage["Persistence Layer"]
        JSON[("JSON Files - debate_history/")]
        HTML[("HTML Reports")]
    end

    SELECT --> BTN1 --> S1 --> S2 --> S3 --> S4 --> DISPLAY
    SELECT --> BTN2 --> M1 --> M2 --> M3 --> M4 --> M5 --> M6 --> DISPLAY

    S4 --> JSON
    M6 --> JSON
    JSON --> HTML
```

### Message Construction Comparison

```mermaid
flowchart TB
    subgraph Standard["Standard Debate Message Flow"]
        Q1["Question + Choices"]
        A1["Agent 0 Initial"]
        A2["Agent 1 Initial"]
        A3["Agent 2 Initial"]

        COMBINE["Combine: Solutions from other agents..."]

        R1["Agent 0 Revision"]
        R2["Agent 1 Revision"]
        R3["Agent 2 Revision"]

        Q1 --> A1 & A2 & A3
        A1 & A2 & A3 --> COMBINE
        COMBINE --> R1 & R2 & R3
    end

    subgraph Mediated["Mediated Debate Message Flow"]
        Q2["Question + Choices"]
        B1["Agent 0 Initial"]
        B2["Agent 1 Initial"]

        JUDGE["Judge Prompt: Olympiad-level evaluation"]
        FEEDBACK["Judge Feedback - No peer answers shared"]

        REV["Revision Prompt: Revise based on judge feedback"]

        C1["Agent 0 Revised"]
        C2["Agent 1 Revised"]

        Q2 --> B1 & B2
        B1 & B2 --> JUDGE --> FEEDBACK
        FEEDBACK --> REV --> C1 & C2
    end
```

---

## Evaluation Results

### MMLU Dataset Performance Summary

```mermaid
pie title Subject Performance Distribution - Mediated Debate
    "Perfect 100%" : 47
    "Partial 66.7%" : 10
```

### Overall Metrics

| Metric | Standard Debate | Mediated Debate |
|--------|-----------------|-----------------|
| **Total Subjects** | 57 | 57 |
| **Sample Size** | 3 questions/subject | 3 questions/subject |
| **Perfect Accuracy Subjects** | 45/57 (78.9%) | 47/57 (82.5%) |
| **Overall Average Accuracy** | ~91.8% | ~94.7% |
| **Improvement** | - | **+2.9%** |

### Subject-Level Performance

#### Perfect Performance (100% Accuracy)

| Domain | Subjects |
|--------|----------|
| **Mathematics** | Abstract Algebra, Elementary Math, High School Math, College Math |
| **Physics** | Conceptual Physics, High School Physics, College Physics |
| **Computer Science** | High School CS, College CS, Computer Security, Machine Learning |
| **Logic** | Formal Logic, Logical Fallacies |
| **Humanities** | Philosophy, World Religions, All History subjects |

#### Areas Showing Improvement with Mediation

```mermaid
flowchart LR
    subgraph Improved["Subjects with Significant Improvement"]
        I1["High School Macroeconomics: 66.7% -> 100%"]
        I2["Moral Scenarios: 66.7% -> 100%"]
        I3["Professional Law: 66.7% -> 100%"]
        I4["Security Studies: 33.3% -> 66.7%"]
    end

    style I1 fill:#d3f9d8,stroke:#2f9e44
    style I2 fill:#d3f9d8,stroke:#2f9e44
    style I3 fill:#d3f9d8,stroke:#2f9e44
    style I4 fill:#fff3bf,stroke:#f59f00
```

### Comparative Analysis

| Metric | Standard Debate | Mediated Debate | Change |
|--------|-----------------|-----------------|--------|
| **Accuracy** | ~91.8% | ~94.7% | +2.9% |
| **Sycophancy Incidents** | Higher | Lower | Reduced |
| **Consensus Quality** | Agreement-based | Correctness-based | Improved |
| **Average Rounds to Converge** | 1.5 | 2.1 | Slightly more |

### Key Insights from Evaluation

```mermaid
flowchart LR
    subgraph Strengths["Our Approach Strengths"]
        S1["Architectural Simplicity"]
        S2["Scalability"]
        S3["Robustness"]
        S4["Interpretability"]
    end

    subgraph Limitations["Known Limitations"]
        L1["Sample Size (n=3)"]
        L2["Model Dependence"]
        L3["Judge as Single Point"]
    end

    Strengths --> |"Outweighs"| Limitations

    style S1 fill:#d3f9d8,stroke:#2f9e44
    style S2 fill:#d3f9d8,stroke:#2f9e44
    style S3 fill:#d3f9d8,stroke:#2f9e44
    style S4 fill:#d3f9d8,stroke:#2f9e44
```

**For detailed analysis, see [FINAL_REPORT_WRITING.md](FINAL_REPORT_WRITING.md) Section 11: Evaluation & Discussion.**

---

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available for Ollama
- Internet connection (for initial model download and OpenAI API calls)

### Step 1: Clone and Start Services

```bash
git clone <repository-url>
cd Final-Assignment-IDM
docker compose up --build
```

### Step 2: Download the Model or Configure OpenAI

**Option A: Use Local Ollama Model**

Wait for Ollama to start (about 30 seconds), then in a **new terminal**:

```bash
docker exec -it ollama-server ollama pull qwen2.5:1.5b
```

**Option B: Use OpenAI API**

Create a `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

### Step 3: Access the Web UI

Open your browser to: `http://localhost:8501`

### Step 4: Run MMLU Evaluation (Optional)

```bash
cd mmlu

# Extract questions from HuggingFace
python extract_questions.py

# Generate responses for both configurations
python gen_mmlu_3_2.py  # Standard debate (3 agents, 2 rounds)
python gen_mmlu_2_3.py  # Mediated debate (2 agents, 3 rounds + Judge)

# Evaluate accuracy
python eval_mmlu.py
```

---

## Project Structure

```
.
├── docker-compose.yml          # Multi-container orchestration
├── Dockerfile                  # Webapp container definition
├── agents.py                   # SmartClient, DebateAgent, JudgeAgent classes
├── simulation.py               # Debate orchestration logic
├── app.py                      # Streamlit web UI
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create manually)
│
├── mmlu/                       # MMLU Evaluation Pipeline
│   ├── extract_questions.py    # Extract from HuggingFace
│   ├── gen_mmlu_3_2.py         # Standard debate generator
│   ├── gen_mmlu_2_3.py         # Mediated debate generator
│   ├── eval_mmlu.py            # Accuracy evaluation
│   ├── mmlu_questions.csv      # Extracted questions (171 questions)
│   ├── mmlu_3_2.json           # Standard debate responses
│   ├── mmlu_2_3.json           # Mediated debate responses
│   ├── eval_by_subject_3_2.csv # Standard results by subject
│   └── eval_by_subject_2_3.csv # Mediated results by subject
│
├── debate_history/             # Saved debate sessions
│   ├── standard/               # Standard debate logs (JSON)
│   └── mediated/               # Mediated debate logs (JSON)
│
├── COSC3009_Final_Report.md    # Academic report (detailed methodology)
├── Architecture_Explanation.md # Architecture documentation (visual diagrams)
├── FINAL_REPORT_WRITING.md     # Comprehensive final report (17 sections with full analysis)
└── README.md                   # This file (quick reference)
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
| `FORCE_LOCAL` | `false` | Force local inference only |

### Model Selection Strategy

```mermaid
flowchart TB
    START["Application Start"] --> CHECK{"Valid OpenAI Key?"}
    CHECK --> |"Yes"| OPENAI["Use OpenAI Cloud - GPT-5-mini"]
    CHECK --> |"No"| LOCAL["Use Local Ollama - qwen2.5:1.5b"]

    OPENAI --> |"Rate Limit or Auth Error"| LOCAL
    LOCAL --> |"Timeout or Connection Error"| SIM["Simulation Mode"]

    OPENAI --> SUCCESS["Response Returned"]
    LOCAL --> SUCCESS
    SIM --> SUCCESS

    style SUCCESS fill:#d3f9d8,stroke:#2f9e44
```

---

## Error Handling

The system implements **robust fallback mechanisms** ensuring it never crashes:

```mermaid
flowchart TB
    API["API Call"] --> TRY{"Try Provider"}

    TRY --> |"Success"| RETURN["Return Response"]

    TRY --> |"AuthError or RateLimit"| SWITCH["Switch to Local Provider"]
    SWITCH --> TRY

    TRY --> |"Timeout"| SIM["Simulation Mode"]
    TRY --> |"ConnectionError"| SWITCH

    SIM --> CONTEXT{"Detect Context"}
    CONTEXT --> |"Judge context"| JUDGE_RESP["Mock Judge Feedback"]
    CONTEXT --> |"Critique context"| CRITIQUE_RESP["Mock Critique"]
    CONTEXT --> |"Math problem"| MATH_RESP["Mock Math Solution"]

    JUDGE_RESP --> RETURN
    CRITIQUE_RESP --> RETURN
    MATH_RESP --> RETURN

    style RETURN fill:#d3f9d8,stroke:#2f9e44
    style SIM fill:#ffe3e3,stroke:#c92a2a
```

---

## Theoretical Framework

### Social Conformity Bias Definition

Sycophancy occurs when an agent that was **initially correct** becomes **incorrect** after being exposed to a peer's confident-but-wrong answer:

$$\text{Sycophancy}(A_i, t) = \begin{cases} 1 & \text{if } \text{Correct}(A_i, t-1) = \text{True} \land \text{Correct}(A_i, t) = \text{False} \land \text{Agree}(A_i, A_j, t) = \text{True} \\ 0 & \text{otherwise} \end{cases}$$

### Information Flow Comparison

```mermaid
flowchart TB
    subgraph Standard["Standard Debate - Vulnerable"]
        SA["Agent A"] <--> |"Direct Critique + Confidence Signals"| SB["Agent B"]
        SA --> |"Social Pressure"| WRONG["May converge to wrong answer"]
        SB --> WRONG
    end

    subgraph Mediated["Mediated Debate - Protected"]
        MA["Agent A"] --> JUDGE["Judge"]
        MB["Agent B"] --> JUDGE
        JUDGE --> |"Critical Feedback Only - No peer answers"| MA
        JUDGE --> |"Critical Feedback Only - No peer answers"| MB
        MA --> RIGHT["Converge to correct answer"]
        MB --> RIGHT
    end

    style WRONG fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style RIGHT fill:#51cf66,stroke:#2f9e44,color:#fff
    style JUDGE fill:#74c0fc,stroke:#1971c2,color:#000
```

**Key Insight:** In mediated debate, agents never see each other's answers directly. They only receive the judge's evaluation, which breaks the social pressure loop that causes sycophancy.

### Why Our Architecture Works

| Mechanism | Effect |
|-----------|--------|
| **Structural Decoupling** | Agents cannot perceive peer confidence levels |
| **Filtered Feedback** | Judge removes social cues from feedback |
| **Asymmetric Temperature** | Creative agents + consistent judge |
| **Correctness-Based Consensus** | Agreement requires logical validity, not just matching answers |

---

## Future Enhancements

### Planned Improvements

```mermaid
flowchart LR
    subgraph Phase1["Phase 1: ReAct Integration"]
        R1["Add Reasoning Traces"]
        R2["Interleave Thought-Action"]
        R3["Ground in Evidence"]
    end

    subgraph Phase2["Phase 2: Adaptive Stopping"]
        A1["Early Termination on Consensus"]
        A2["Wald Sequential Analysis"]
        A3["Cost-Quality Trade-off"]
    end

    subgraph Phase3["Phase 3: Multi-Modal"]
        M1["Image Reasoning"]
        M2["Code Execution"]
        M3["Web Search Integration"]
    end

    Phase1 --> Phase2 --> Phase3
```

### ReAct Agent Integration (Proposed)

Based on Yao et al. (2022), integrating ReAct (Reasoning + Acting) could enhance agent responses:

```
Thought: I need to calculate the total cost step by step
Action: Calculate 4 × $2.50 = $10.00
Observation: Coffee cost is $10.00
Thought: Now I need to calculate tea cost
Action: Calculate 3 × $1.75 = $5.25
Observation: Tea cost is $5.25
Thought: I can now sum the costs
Action: Calculate $10.00 + $5.25 = $15.25
Final Answer: $15.25
```

---

## Demo




![demo Hybrid Multi Agent Debate System Jan 2026](https://github.com/user-attachments/assets/7686cf67-b5b4-4400-95d1-8f62d72585d8)
[Demo Video](https://youtu.be/90-dHwFYU7s)



---

## References

1. **Du, Y., et al. (2023).** "Improving Factuality and Reasoning in Language Models through Multiagent Debate." *arXiv preprint arXiv:2305.14325*.

2. **Hu, X., et al. (2025).** "Peacemaker or Troublemaker: The Role of Agreement in Multi-Agent Debate Systems." *Proceedings of ICML*.

3. **Yao, S., et al. (2022).** "ReAct: Synergizing Reasoning and Acting in Language Models." *arXiv preprint arXiv:2210.03629*.

4. **Asch, S. E. (1951).** "Effects of group pressure upon the modification and distortion of judgments." *Groups, Leadership, and Men*.

5. **Hendrycks, D., et al. (2021).** "Measuring Massive Multitask Language Understanding." *ICLR 2021*.

6. **Kahneman, D. (2011).** *Thinking, Fast and Slow*. Farrar, Straus and Giroux.

---

## License

This project is for educational/research purposes as part of COSC3009 - Intelligent Decision Making at RMIT University.

## Acknowledgments

- **Ollama Team** - Local LLM inference infrastructure
- **Qwen Team** - Efficient qwen2.5 model family
- **Streamlit** - Interactive web UI framework
- **HuggingFace** - MMLU dataset hosting
- **OpenAI** - Cloud inference API

---

*Document generated for COSC3009 - Intelligent Decision Making, RMIT University*
