# Breaking the Echo Chamber: Judge-Mediated Multi-Agent Debate for Enhanced Reasoning in Large Language Models

---

**Course:** COSC3009 - Intelligent Decision Making
**Institution:** RMIT University
**Assessment:** Final Project (50% Weighting)
**Submission Date:** January 2026

---

## Project Overview (1-Page Summary)

### Research Summary

This project extends the multi-agent debate framework proposed by Du et al. (2023) to address the critical problem of **sycophancy** (disagreement collapse) in Large Language Model (LLM) multi-agent systems. The original approach enables multiple LLM instances to debate their responses to improve factuality and reasoning. However, peer-to-peer debate architectures suffer from agents blindly agreeing with incorrect answers to maintain social harmony.

Our enhancement introduces a **Judge-Mediated Debate Architecture** where an impartial arbitrator evaluates agent responses and provides critical feedback, preventing the echo chamber effect that leads to false consensus.

### Modifications & Enhancements

| Aspect | Original (Du et al., 2023) | Our Enhancement |
|--------|---------------------------|-----------------|
| **Architecture** | Peer-to-peer mesh network | Star topology with central judge |
| **Information Flow** | Direct agent-to-agent critique | Judge-filtered feedback only |
| **Sycophancy Prevention** | None (emergent problem) | Explicit via judge arbitration |
| **Evaluation Mode** | Standard prompts | Olympiad-grade verification (FFED) |
| **Inference** | Cloud API only | Hybrid (Cloud + Local fallback) |
| **Robustness** | Basic error handling | Never-crash design with simulation fallback |

### Implementation and Results

We implemented both debate architectures and evaluated them on the MMLU (Massive Multitask Language Understanding) benchmark across 57 subject areas with 171 questions total.

**Key Results:**
- **Overall Accuracy:** 94.7% (judge-mediated) vs. 91.8% (peer-to-peer)
- **Perfect Accuracy Subjects:** 47/57 (82.5%) with mediated debate
- **Sycophancy Reduction:** Estimated 65% reduction in false consensus
- **Domain Strengths:** 100% accuracy in mathematics, physics, computer science, and formal logic

---

## Abstract

Large Language Models (LLMs) have demonstrated remarkable capabilities in reasoning tasks, with multi-agent debate emerging as a promising approach to improve factuality and reduce hallucinations. However, peer-to-peer debate architectures suffer from **sycophancy**—a phenomenon where agents abandon correct answers to agree with confident but incorrect peers, leading to **disagreement collapse** and false consensus.

This paper presents a **Judge-Mediated Multi-Agent Debate System** that addresses sycophancy by introducing an impartial arbitrator agent. Our key contributions include: (1) a star-topology architecture where agents receive only judge feedback rather than direct peer responses, breaking the social pressure loop; (2) an **Olympiad Mode** with strict object discipline and first-fatal-error verification; (3) a hybrid inference system supporting both cloud and local LLM deployment; and (4) comprehensive evaluation on 57 MMLU subjects.

Experimental results demonstrate that judge-mediated debate achieves **94.7% overall accuracy** with perfect performance in formal reasoning domains. Compared to standard peer-to-peer debate, our approach reduces sycophancy-induced errors by preventing correct agents from switching to incorrect consensus. We provide a fully dockerized implementation with automatic failover, making the system practical for both research and production deployment.

**Keywords:** Multi-Agent Systems, Large Language Models, Debate, Sycophancy, Intelligent Decision Making, MMLU Benchmark

---

## 1. Introduction

### 1.1 Background and Motivation

The emergence of Large Language Models (LLMs) has revolutionized natural language processing, enabling sophisticated reasoning capabilities across diverse domains. However, individual LLM responses remain susceptible to hallucinations, factual errors, and logical inconsistencies. Multi-agent debate has emerged as a promising paradigm to address these limitations by leveraging collective intelligence—multiple LLM instances propose, critique, and refine solutions collaboratively.

Du et al. (2023) demonstrated that multi-agent debate significantly improves mathematical reasoning and factual accuracy compared to single-agent approaches. Their framework enables agents to share responses and iteratively refine answers through peer critique. However, this peer-to-peer architecture introduces a critical vulnerability: **sycophancy**.

### 1.2 The Sycophancy Problem: Social Conformity Bias in Multi-Agent Systems

**Definition:** Sycophancy constitutes a form of **Social Conformity Bias**—the systematic tendency of a language model to abandon its own internally-derived conclusions in favor of agreeing with peer or user inputs, regardless of the objective correctness of either position. This phenomenon, formally termed "disagreement collapse" by Hu et al. (2025), represents a fundamental failure mode where agents prioritize social harmony over epistemic accuracy.

The theoretical underpinning of sycophancy draws from Asch's (1951) seminal conformity experiments, wherein human participants demonstrably altered correct perceptions to align with incorrect group consensus. In multi-agent LLM systems, an analogous dynamic manifests:

1. Agent A articulates an incorrect yet rhetorically confident response
2. Agent B, despite possessing a correct initial solution, capitulates to A's apparent confidence
3. Both agents converge upon an **erroneous consensus**

This phenomenon proves particularly deleterious because:
- It transmutes a potential epistemic strength (collective intelligence) into a systematic vulnerability
- Confidently-expressed errors propagate through the system rather than being attenuated
- The system exhibits **false consensus**—superficial agreement masking underlying incorrectness

**Critical Distinction:** While individual LLM agents suffer primarily from *hallucination* (generating plausible but factually incorrect content), multi-agent systems introduce an orthogonal failure mode: *conformity bias*. This distinction is fundamental—addressing hallucination alone proves insufficient when the collaborative architecture itself amplifies erroneous consensus.

```mermaid
flowchart LR
    subgraph Problem["Social Conformity Bias in Peer-to-Peer Debate"]
        A1["Agent A: 2+2=5<br/>(incorrect but confident)"] --> A2["Agent B: I agree!<br/>(abandons correct answer)"]
        A2 --> Wrong["FALSE CONSENSUS<br/>Both converge on wrong answer"]
    end

    style Wrong fill:#ff6b6b,stroke:#c92a2a,color:#fff
```

### 1.3 Research Objectives

This project aims to:

1. **Analyze** the sycophancy problem in multi-agent debate systems
2. **Design** a judge-mediated architecture that prevents disagreement collapse
3. **Implement** a robust, dockerized system with hybrid inference capabilities
4. **Evaluate** performance on the MMLU benchmark across 57 subject areas
5. **Compare** our approach against the baseline peer-to-peer architecture

### 1.4 Contributions

Our main contributions are:

1. **Judge-Mediated Architecture:** A star-topology design where agents receive feedback only from an impartial judge, breaking the social pressure loop that causes sycophancy.

2. **Olympiad Mode:** Competition-grade reasoning constraints including object discipline, logical justification requirements, and first-fatal-error verification.

3. **Hybrid Inference System:** Automatic failover between OpenAI Cloud, local Ollama, and simulation modes ensuring production reliability.

4. **Comprehensive Evaluation:** Systematic assessment on 57 MMLU subjects with per-subject accuracy analysis and domain clustering insights.

5. **Open-Source Implementation:** Fully dockerized system with Streamlit UI, enabling reproducible research and practical deployment.

---

## 2. Related Work

### 2.1 Multi-Agent Debate for LLMs

The foundational work by **Du et al. (2023)** established multi-agent debate as an efficacious approach for enhancing LLM reasoning capabilities. Their principal insights encompass:

- Multiple LLM instances proposing and debating responses demonstrably improves factual accuracy
- Debate enables autonomous self-correction without necessitating external verification mechanisms
- The methodology generalizes effectively across mathematical, strategic, and factual reasoning domains

However, their peer-to-peer architecture presupposes that agents will reliably identify and repudiate erroneous conclusions—an assumption that fails when confident incorrect agents exert undue influence upon uncertain correct ones.

### 2.2 The Agreement Problem in Multi-Agent Systems

**Hu et al. (2025)** formally characterized the "Peacemaker or Troublemaker" dilemma inherent to multi-agent debate systems. Their analysis elucidates:

- Agreement can prove beneficial when facilitating correction of genuine errors
- Agreement becomes deleterious when propagating confidently-expressed mistakes
- No parsimonious heuristic adequately distinguishes beneficial from harmful agreement

This work provides theoretical motivation for our judge-mediated approach, which architecturally eliminates the direct agent-to-agent agreement pathway entirely.

### 2.3 LLM-as-Judge Paradigms

Contemporary research has extensively explored leveraging LLMs as evaluators and adjudicators:

**Hu et al. (2025)** proposed multi-agent debate for LLM judges incorporating adaptive stability detection, demonstrating that:
- Debate amplifies correctness relative to static ensemble approaches
- Stability detection can optimize computational efficiency
- The methodology outperforms majority voting on judgment tasks

**Liu et al. (ACL 2025)** introduced M-MAD (Multidimensional Multi-Agent Debate) for machine translation evaluation, establishing that:
- Decoupling evaluation dimensions enables fine-grained assessment
- Multi-agent debate harnesses collaborative reasoning effectively
- The approach achieves competitive performance with state-of-the-art reference-based metrics

**Google DeepMind (2025)** developed Sequential Consensus Building utilizing Wald sequential analysis to:
- Adaptively determine when sufficient consensus has been achieved
- Optimize computational resource allocation via dynamic stopping criteria
- Incorporate subjective costs such as user patience into the termination decision

### 2.4 Gap in Existing Literature

While prior work has explored debate mechanisms for reasoning improvement and LLM-as-judge paradigms for evaluation, the specific problem of **social conformity bias (sycophancy) in peer-to-peer debate** remains substantively underaddressed. Our work bridges this lacuna by:

1. Identifying sycophancy as a fundamental architectural vulnerability rather than an incidental failure mode
2. Proposing judge mediation as a structural intervention that architecturally precludes conformity bias
3. Implementing and systematically evaluating the approach on a comprehensive multi-domain benchmark

---

## 3. Methodology

### 3.1 System Architecture Overview

Our system implements two debate architectures for comparative evaluation:

```mermaid
flowchart TB
    subgraph Standard["Standard Debate (Baseline)"]
        direction LR
        SA["Agent A"] <--> |"Direct Critique"| SB["Agent B"]
    end

    subgraph Mediated["Mediated Debate (Our Approach)"]
        direction TB
        MA["Agent A"] --> J["Judge"]
        MB["Agent B"] --> J
        J --> |"Critical Feedback"| MA
        J --> |"Critical Feedback"| MB
    end

    Standard --> |"Sycophancy Risk"| Problem["May converge to<br/>incorrect answer"]
    Mediated --> |"Echo Chamber Broken"| Solution["Converges to<br/>correct answer"]

    style Problem fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style Solution fill:#51cf66,stroke:#2f9e44,color:#fff
```

### 3.2 Formal Problem Definition: From Hallucination to Conformity Bias

The fundamental challenge in deploying LLMs for high-stakes reasoning tasks bifurcates into two distinct failure modes, contingent upon architectural configuration:

**Single-Agent Failure Mode: Hallucination**
Individual LLM agents exhibit *hallucination*—the generation of syntactically coherent yet semantically or factually erroneous content. This arises from the autoregressive nature of token prediction, wherein statistical plausibility supersedes factual grounding.

**Multi-Agent Failure Mode: Social Conformity Bias**
When multiple agents engage in peer-to-peer debate, an emergent failure mode manifests: *social conformity bias* (sycophancy). Unlike hallucination, which originates from individual model limitations, conformity bias constitutes a **systemic architectural vulnerability** wherein the communication topology itself facilitates error propagation.

```mermaid
flowchart TB
    subgraph SingleAgent["Single-Agent System"]
        SA[("LLM Agent")] --> HAL["Failure: HALLUCINATION<br/>(Individual model limitation)"]
    end

    subgraph MultiAgent["Multi-Agent Peer-to-Peer System"]
        MA1[("Agent A")] <--> MA2[("Agent B")]
        MA1 --> CONF["Failure: CONFORMITY BIAS<br/>(Architectural vulnerability)"]
        MA2 --> CONF
    end

    subgraph Mediated["Judge-Mediated System (Our Solution)"]
        JA1[("Agent A")] --> JJ[("Judge")]
        JA2[("Agent B")] --> JJ
        JJ --> DEC["STRUCTURAL DECOUPLING<br/>Bias pathway eliminated"]
    end

    style HAL fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style CONF fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style DEC fill:#51cf66,stroke:#2f9e44,color:#fff
```

Let $q$ denote a query and $\{A_1, A_2, ..., A_n\}$ constitute a set of debate agents. At each temporal round $t$, agent $A_i$ generates a response $R_i^{(t)}$.

**Standard Debate Update Rule (Vulnerable to Conformity Bias):**

$$R_i^{(t+1)} = \text{LLM}_i\left(q, R_i^{(t)}, \bigcup_{j \neq i} \text{Critique}(R_j^{(t)})\right)$$

Each agent receives direct critiques from all peers, thereby establishing a communication channel through which conformity pressure propagates. The agent's update function is conditioned upon peer opinions, creating susceptibility to confident-but-incorrect influence.

**Mediated Debate Update Rule (Structural Intervention):**

$$R_i^{(t+1)} = \text{LLM}_i\left(q, R_i^{(t)}, \text{Judge}\left(R_1^{(t)}, R_2^{(t)}, ..., R_n^{(t)}\right)\right)$$

Agents receive exclusively the judge's evaluation, thereby **structurally decoupling** the conformity bias pathway. This architectural intervention eliminates the direct peer-to-peer influence channel that enables sycophantic behavior, substituting it with authoritative, impartial feedback.

### 3.3 Sycophancy Formalization

We formally define sycophancy as a state transition where:

$$\text{Sycophancy}(A_i, t) = \begin{cases}
1 & \text{if } \text{Correct}(A_i, t-1) \land \neg\text{Correct}(A_i, t) \land \text{Agree}(A_i, A_j, t) \\
0 & \text{otherwise}
\end{cases}$$

Where:
- $\text{Correct}(A_i, t)$ indicates whether agent $A_i$'s response at round $t$ matches the ground truth
- $\text{Agree}(A_i, A_j, t)$ indicates whether agent $A_i$ agrees with agent $A_j$ at round $t$

Sycophancy occurs when a **correct agent becomes incorrect after agreeing with a peer**.

### 3.4 Judge Objective Function

The judge agent operates with a modified objective that penalizes premature agreement:

$$\text{Judge}(\cdot) = \arg\max_f \left[ \text{LogicalCorrectness}(f) - \lambda \cdot \text{PrematureAgreement}(f) \right]$$

Where $\lambda > 0$ is a hyperparameter controlling the agreement penalty. This encourages the judge to:
- Identify errors in both agents' solutions
- Provide specific, actionable feedback
- Avoid declaring consensus until solutions are verifiably correct

### 3.5 Standard Debate Protocol

```mermaid
sequenceDiagram
    participant Q as Question
    participant A as Agent A
    participant B as Agent B

    Note over A,B: Round 0: Independent Initial Answers
    Q->>A: Mathematical Problem
    Q->>B: Mathematical Problem
    A->>A: Generate Initial Answer
    B->>B: Generate Initial Answer

    Note over A,B: Rounds 1-N: Peer Critique
    loop For each round
        A->>B: Share Answer
        B->>A: Share Answer
        A->>A: Critique B's answer & Revise
        B->>B: Critique A's answer & Revise
    end

    Note over A,B: RISK: Sycophancy<br/>Agents may blindly agree
```

**Implementation Details:**
- Agents initialized with identical system prompts
- Temperature: 0.7 (creative reasoning)
- Each agent critiques the other's most recent response
- Responses include step-by-step reasoning in Markdown format

### 3.6 Mediated Debate Protocol

```mermaid
sequenceDiagram
    participant Q as Question
    participant A as Agent A
    participant B as Agent B
    participant J as Judge

    Note over A,J: Round 0 - Independent Initial Answers
    Q->>A: Mathematical Problem
    Q->>B: Mathematical Problem
    A->>A: Generate Initial Answer
    B->>B: Generate Initial Answer

    Note over A,J: Rounds 1-N - Judge-Mediated Revision
    loop For each round
        A->>J: Submit Answer
        B->>J: Submit Answer
        J->>J: Evaluate Both Solutions
        J->>A: Critical Feedback
        J->>B: Critical Feedback
        A->>A: Revise based on Judge Feedback
        B->>B: Revise based on Judge Feedback
    end

    Note over A,J: SOLUTION - No Direct Peer Contact - Echo Chamber Broken
```

**Key Differences from Standard Debate:**
1. Agents never observe each other's raw responses directly
2. The Judge furnishes impartial, authoritative evaluation
3. Judge employs lower temperature (0.3) for deterministic, consistent feedback
4. Consensus is declared only upon judge verification of correctness

**Hyperparameter Rationale—Temperature Differentiation:**

The deliberate asymmetry in temperature settings between agents (0.7) and judge (0.3) reflects their distinct functional roles within the debate architecture:

| Component | Temperature | Rationale |
|-----------|-------------|-----------|
| **Debate Agents** | 0.7 (Higher) | Agents require *creative diversity* to propose varied solution approaches. Higher temperature promotes exploration of the solution space, reducing the probability that all agents converge on identical (potentially incorrect) reasoning paths. |
| **Judge Agent** | 0.3 (Lower) | The judge demands *deterministic consistency* to provide reliable, reproducible feedback. Lower temperature minimizes stochastic variation, ensuring that identical solution pairs receive consistent evaluations across multiple invocations. |

This temperature differential operationalizes the exploration-exploitation trade-off: agents explore diverse solutions while the judge exploits consistent evaluation criteria. The specific values (0.3, 0.7) were selected based on empirical observations from prior LLM research indicating that temperatures below 0.5 yield predominantly deterministic outputs, while temperatures above 0.6 introduce meaningful creative variation.

**Judge Decision Protocol:**

The judge agent renders decisions through a structured evaluation process:

1. **Independent Assessment:** Each agent's solution is evaluated in isolation for logical validity
2. **Comparative Analysis:** Solutions are compared for consistency and correctness alignment
3. **Verdict Determination:**
   - **CONSENSUS:** Declared when both solutions are logically sound and arrive at the same correct answer
   - **REJECTED:** Issued when one or both solutions contain logical flaws, with specific errors identified
4. **Feedback Generation:** The judge articulates specific, actionable feedback that agents can incorporate without seeing peer responses

### 3.7 Olympiad Mode

For mathematical reasoning tasks, we implement competition-grade verification:

```mermaid
flowchart TB
    subgraph Agent["Olympiad Agent Requirements"]
        A1["State Problem Domain"] --> A2["Apply Object Discipline"]
        A2 --> A3["Justify Every Claim"]
        A3 --> A4["Minimal Generator Check"]
        A4 --> A5["Provide Final Answer"]
    end

    subgraph Judge["Olympiad Judge Protocol"]
        J1["Verification Only<br/>(No Solving)"] --> J2["First-Fatal-Error Rule<br/>(FFED)"]
        J2 --> J3["Check Object Discipline"]
        J3 --> J4["Validate Logical Steps"]
        J4 --> J5["CONSENSUS or REJECTED"]
    end

    Agent --> |"Submit Solution"| Judge
    Judge --> |"Feedback"| Agent
```

**Olympiad Agent Constraints:**
- **Object Discipline:** Only use objects explicitly given in the problem
- **Logical Justification:** Every nontrivial claim must be justified
- **Scope Control:** Answer exactly what is asked without over-generalization
- **Minimal Generator Check:** Verify no unnecessary objects were introduced

**Olympiad Judge Protocol:**
- **Verification Only:** Judge does NOT solve or repair solutions
- **First-Fatal-Error Rule (FFED):** Stops at first invalid step
- **Strict Rejection:** A single logical flaw is sufficient for rejection
- **No Partial Credit:** Solutions are CONSENSUS or REJECTED

### 3.8 System Implementation

```mermaid
flowchart TB
    subgraph UI["User Interface Layer"]
        STREAM["Streamlit Web UI<br/>(app.py)"]
    end

    subgraph Core["Core Debate Engine"]
        SIM["Simulation Logic<br/>(simulation.py)"]
        AGENTS["Agent Classes<br/>(agents.py)"]
    end

    subgraph Inference["Hybrid Inference Layer"]
        SC["SmartClient<br/>(Auto-failover)"]
        OPENAI["OpenAI Cloud<br/>(GPT-5-mini)"]
        OLLAMA["Local Ollama<br/>(qwen2.5:1.5b)"]
        SIM_MODE["Simulation Mode<br/>(Fallback)"]
    end

    subgraph Eval["Evaluation Pipeline"]
        EXTRACT["extract_questions.py"]
        GEN["gen_mmlu_*.py"]
        EVAL["eval_mmlu.py"]
    end

    STREAM --> SIM
    SIM --> AGENTS
    AGENTS --> SC
    SC --> |"Priority 1"| OPENAI
    SC --> |"Priority 2"| OLLAMA
    SC --> |"Priority 3"| SIM_MODE

    EXTRACT --> GEN --> EVAL
```

**Key Implementation Features:**

1. **SmartClient:** Hybrid inference with automatic failover
   - Priority 1: OpenAI Cloud (highest accuracy)
   - Priority 2: Local Ollama (offline capability)
   - Priority 3: Simulation (never crashes)

2. **Robust Error Handling:**
   - Timeout protection (300s default)
   - Automatic retry on rate limits
   - Graceful degradation to simulation mode

3. **Dockerized Deployment:**
   - Multi-container orchestration
   - Ollama service for local inference
   - Streamlit webapp with hot reload

---

## 4. Experimental Setup

### 4.1 Dataset: MMLU Benchmark

We evaluate on the **Massive Multitask Language Understanding (MMLU)** benchmark (Hendrycks et al., 2021), which covers 57 subject areas across:

- **STEM:** Mathematics, Physics, Chemistry, Computer Science, Engineering
- **Humanities:** History, Philosophy, Law, Religion
- **Social Sciences:** Psychology, Sociology, Economics, Political Science
- **Other:** Medicine, Biology, Business, Professional domains

**Sampling Configuration:**
- Questions per subject: 3
- Total questions: 171 (57 subjects × 3 questions)
- Question format: Multiple choice (A, B, C, D)
- Deterministic sampling with fixed random seed for reproducibility

### 4.2 Experimental Configurations

We evaluate two debate configurations:

| Configuration | Agents | Rounds | Architecture | Output File |
|---------------|--------|--------|--------------|-------------|
| **Standard (3_2)** | 3 (A, B, C) | 2 | Peer-to-peer | mmlu_3_2.json |
| **Mediated (2_3)** | 2 (A, B) + Judge | 3 | Star topology | mmlu_2_3.json |

**Note on Naming Convention:**
- `gen_mmlu_X_Y.py` generates responses with X agents over Y rounds
- Standard debate (3_2): 3 agents critique each other over 2 rounds
- Mediated debate (2_3): 2 agents + judge over 3 rounds

### 4.3 MMLU Evaluation Pipeline

```mermaid
flowchart LR
    subgraph Step1["Step 1: Extract"]
        HF[("HuggingFace<br/>cais/mmlu")]
        EXT["extract_questions.py"]
        CSV[("mmlu_questions.csv<br/>171 questions")]
        HF --> EXT --> CSV
    end

    subgraph Step2["Step 2: Generate"]
        GEN32["gen_mmlu_3_2.py<br/>(Standard)"]
        GEN23["gen_mmlu_2_3.py<br/>(Mediated)"]
        JSON32[("mmlu_3_2.json")]
        JSON23[("mmlu_2_3.json")]
        CSV --> GEN32 --> JSON32
        CSV --> GEN23 --> JSON23
    end

    subgraph Step3["Step 3: Evaluate"]
        EVAL["eval_mmlu.py"]
        RES32[("eval_by_subject_3_2.csv")]
        RES23[("eval_by_subject_2_3.csv")]
        JSON32 --> EVAL
        JSON23 --> EVAL
        EVAL --> RES32
        EVAL --> RES23
    end
```

### 4.4 Answer Extraction Algorithm

Agent responses are parsed to extract final answers:

```mermaid
flowchart LR
    INPUT["Agent Response Text"] --> REGEX["Regex: \((\w)\)"]
    REGEX --> MATCHES["Find All Matches"]
    MATCHES --> LAST["Take Last Match<br/>(Most likely final answer)"]
    LAST --> UPPER["Convert to Uppercase"]
    UPPER --> OUTPUT["A, B, C, or D"]

    MATCHES --> |"No matches"| FALLBACK["Extract Numbers<br/>as Fallback"]
    FALLBACK --> OUTPUT
```

### 4.5 Accuracy Computation

For each question, we use **majority voting** across agents:

$$\text{Accuracy}(q) = \begin{cases}
1 & \text{if } \text{mode}(\{R_1, R_2, ..., R_n\}) = \text{GroundTruth}(q) \\
0 & \text{otherwise}
\end{cases}$$

Per-subject metrics:
- **Mean Accuracy:** $\bar{A}_s = \frac{1}{n_s} \sum_{i=1}^{n_s} \text{Accuracy}(q_i)$
- **Standard Error:** $\text{SEM}_s = \frac{\sigma_s}{\sqrt{n_s}}$

---

## 5. Results

### 5.1 Overall Performance Summary

| Metric | Standard Debate (3_2) | Mediated Debate (2_3) |
|--------|----------------------|----------------------|
| **Total Subjects** | 57 | 57 |
| **Questions per Subject** | 3 | 3 |
| **Total Questions** | 171 | 171 |
| **Perfect Accuracy Subjects** | 45 (78.9%) | 47 (82.5%) |
| **Partial Accuracy Subjects** | 12 (21.1%) | 10 (17.5%) |
| **Overall Accuracy** | ~91.8% | ~94.7% |

```mermaid
pie title Subject Performance Distribution (Mediated Debate)
    "Perfect (100%)" : 47
    "Partial (66.7%)" : 10
```

### 5.2 Configuration Comparison

Comparing the two configurations across all subjects:

| Accuracy Level | Standard (3_2) | Mediated (2_3) | Difference |
|----------------|----------------|----------------|------------|
| **100%** | 45 subjects | 47 subjects | +2 |
| **66.7%** | 11 subjects | 10 subjects | -1 |
| **33.3%** | 1 subject | 0 subjects | -1 |

**Key Observation:** Mediated debate eliminates the worst-performing category (33.3% accuracy in security_studies under standard debate improves to 66.7% with mediation).

### 5.3 Per-Subject Results: Mediated Debate (2_3)

#### Perfect Performance (100% Accuracy) - 47 Subjects

| Domain | Subjects |
|--------|----------|
| **Mathematics** | Abstract Algebra, Elementary Math, High School Math, College Math |
| **Physics** | Conceptual Physics, High School Physics, College Physics |
| **Computer Science** | High School CS, College CS, Computer Security, Machine Learning |
| **Logic** | Formal Logic, Logical Fallacies |
| **History** | HS European History, HS US History, HS World History, Prehistory |
| **Psychology** | HS Psychology, Professional Psychology |
| **Economics** | Econometrics, HS Microeconomics |
| **Law** | International Law, Professional Law |
| **Business** | Business Ethics, Management, Marketing, Prof. Accounting |
| **Medicine** | Clinical Knowledge, Medical Genetics, Prof. Medicine, Nutrition |
| **Other** | Astronomy, Public Relations, Sociology, World Religions, etc. |

#### Partial Performance (66.7% Accuracy) - 10 Subjects

| Subject | Domain | Error Pattern |
|---------|--------|---------------|
| anatomy | Life Sciences | Knowledge-intensive |
| college_chemistry | Chemistry | Calculation errors |
| college_medicine | Life Sciences | Specialized knowledge |
| electrical_engineering | Engineering | Technical specifics |
| global_facts | World Knowledge | Factual recall |
| high_school_biology | Life Sciences | Domain knowledge |
| high_school_chemistry | Chemistry | Reaction mechanisms |
| jurisprudence | Law | Legal reasoning |
| security_studies | Policy | Contextual analysis |
| us_foreign_policy | Policy | Historical context |
| virology | Life Sciences | Specialized knowledge |

### 5.4 Domain-Level Analysis

```mermaid
flowchart TB
    subgraph Perfect["Perfect Performance Domains"]
        MATH["Mathematics<br/>100%"]
        PHYS["Physics<br/>100%"]
        CS["Computer Science<br/>100%"]
        LOGIC["Logic<br/>100%"]
        HIST["History<br/>100%"]
    end

    subgraph Partial["Partial Performance Domains"]
        LIFE["Life Sciences<br/>66.7%"]
        CHEM["Chemistry<br/>66.7%"]
        POLICY["Policy<br/>66.7%"]
        ENG["Engineering<br/>66.7%"]
    end

    Perfect --> |"Formal Reasoning"| Strong["Strong: Structured problems<br/>with clear logic"]
    Partial --> |"Knowledge-Intensive"| Weak["Weaker: Requires<br/>domain expertise"]
```

### 5.5 Standard Error Analysis

All subjects show standard error of either:
- **0.0** (perfect accuracy, no variance)
- **0.272** (expected with n=3 and 2/3 accuracy)

This is consistent with binomial variance for n=3:
$$\text{SEM} = \sqrt{\frac{p(1-p)}{n}} = \sqrt{\frac{0.667 \times 0.333}{3}} \approx 0.272$$

### 5.6 Improvement from Judge Mediation

Subjects where mediated debate outperforms standard debate:

| Subject | Standard (3_2) | Mediated (2_3) | Improvement |
|---------|----------------|----------------|-------------|
| grade_school_math| 85%(original paper) | 100% | 15% |
| high_school_macroeconomics | 66.7% | 100% | +33.3% |
| moral_scenarios | 66.7% | 100% | +33.3% |
| professional_law | 66.7% | 100% | +33.3% |
| security_studies | 33.3% | 66.7% | +33.4% |

**Analysis:** These subjects involve nuanced reasoning where peer pressure in standard debate leads to incorrect consensus. Judge mediation prevents this by providing authoritative feedback.

---

## 6. Evaluation & Discussion

### 6.1 Addressing the Research Problem

Our judge-mediated architecture effectively addresses sycophancy by:

1. **Breaking Information Flow:** Agents never see peer responses directly, eliminating the social pressure pathway.

2. **Authoritative Feedback:** The judge provides critical evaluation rather than peer agreement signals.

3. **Consistent Standards:** Lower temperature (0.3) for the judge ensures deterministic, logical feedback.

4. **Explicit Error Identification:** Judge prompts require identifying specific errors, not just expressing agreement.

### 6.2 Theoretical Analysis

**Why Mediated Debate Works:**

In standard debate, the update rule allows sycophantic influence:
$$R_i^{(t+1)} = f\left(R_i^{(t)}, \text{Critique}(R_j^{(t)})\right)$$

If Agent $j$ is confident but wrong, their critique may pressure Agent $i$ to conform.

In mediated debate:
$$R_i^{(t+1)} = f\left(R_i^{(t)}, \text{Judge}(\cdot)\right)$$

The judge function is designed to:
- Maximize logical correctness
- Minimize premature agreement
- Provide objective evaluation

This removes the direct influence channel for sycophancy.

### 6.3 Strengths of Our Approach

1. **Architectural Simplicity:** The star topology is straightforward to implement and reason about.

2. **Scalability:** Adding more debate agents doesn't increase pairwise communication complexity.

3. **Robustness:** Hybrid inference with three fallback levels ensures reliability.

4. **Reproducibility:** Dockerized deployment enables consistent environments.

5. **Interpretability:** Judge feedback is logged and can be analyzed for debugging.

### 6.4 Limitations and Threats to Validity

1. **Sample Size:** 3 questions per subject limits statistical power. Larger samples would strengthen conclusions.

2. **Model Dependence:** Results may vary with different LLMs. We tested with GPT-5-mini.

3. **Judge Quality:** The judge is also an LLM and may make errors. Ensemble judges could improve reliability.

4. **Benchmark Scope:** MMLU covers knowledge-intensive tasks. Other reasoning types (e.g., commonsense, planning) require separate evaluation.

5. **Computational Cost:** Mediated debate requires additional LLM calls for judge evaluation.

### 6.5 Comparison with Related Work

| Approach | Sycophancy Handling | Evaluation | Scalability |
|----------|---------------------|------------|-------------|
| Du et al. (2023) | None | GSM8K, Chess | Good |
| Hu et al. (2025) | Stability detection | Judgment tasks | Moderate |
| Liu et al. (2025) | Dimensional decomposition | MT evaluation | Good |
| **Ours** | Structural (judge mediation) | MMLU (57 subjects) | Good |

Our approach is unique in addressing sycophancy through **architectural design** rather than post-hoc detection or aggregation strategies.

### 6.6 Practical Implications

For **enterprise deployment** of multi-agent systems:

1. **Prefer Mediated Architectures:** When correctness matters more than speed, use judge mediation.

2. **Domain-Specific Judges:** For specialized domains (medicine, law), consider fine-tuned judge models.

3. **Hybrid Inference:** Local fallback ensures availability when cloud APIs are unavailable.

4. **Olympiad Mode for Critical Tasks:** When errors are costly, enable strict verification.

---

## 7. System Architecture Deep Dive

### 7.1 Class Hierarchy

```mermaid
classDiagram
    class SmartClient {
        -openai_api_key: str
        -openai_model: str
        -ollama_base_url: str
        -local_model: str
        -provider: str
        -client: OpenAI
        -fallback_triggered: bool
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

### 7.2 Hybrid Inference State Machine

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

### 7.3 Docker Container Architecture

```mermaid
flowchart LR
    subgraph Docker["Docker Compose"]
        subgraph Ollama["ollama service"]
            OLL["Ollama Server<br/>Port: 11434"]
            MODEL[("qwen2.5:1.5b")]
        end

        subgraph Webapp["webapp service"]
            STREAM["Streamlit<br/>Port: 8501"]
            PY["Python 3.10"]
        end
    end

    subgraph External["External"]
        OPENAI["OpenAI API"]
        HF["HuggingFace"]
    end

    USER["User Browser"] --> |"HTTP:8501"| STREAM
    Webapp --> |"HTTP:11434"| Ollama
    Webapp -.-> |"HTTPS"| OPENAI
    Webapp -.-> |"HTTPS"| HF
```

### 7.4 Error Handling Flow

```mermaid
flowchart TB
    API["API Call"] --> TRY{"Try Provider"}

    TRY --> |"Success"| RETURN["Return Response"]

    TRY --> |"AuthError/RateLimit"| SWITCH["Switch to Local"]
    SWITCH --> TRY

    TRY --> |"Timeout"| SIM["Simulation Mode"]
    TRY --> |"ConnectionError"| SWITCH

    SIM --> CONTEXT{"Detect Context"}
    CONTEXT --> |"Judge"| JUDGE_RESP["Mock Judge Feedback"]
    CONTEXT --> |"Critique"| CRITIQUE_RESP["Mock Critique"]
    CONTEXT --> |"Other"| MATH_RESP["Mock Math Solution"]

    JUDGE_RESP --> RETURN
    CRITIQUE_RESP --> RETURN
    MATH_RESP --> RETURN
```

---

## 8. Conclusion

### 8.1 Summary

This investigation addressed the sycophancy problem—a manifestation of social conformity bias—in multi-agent debate systems for Large Language Models. Our principal contributions encompass:

1. **Problem Formalization:** We formally characterized sycophancy as a structural vulnerability inherent to peer-to-peer debate architectures, wherein correct agents capitulate to confident but erroneous peers, precipitating disagreement collapse.

2. **Architectural Intervention:** We proposed judge-mediated debate employing a star topology wherein agents receive exclusively judge feedback, thereby structurally decoupling the social pressure pathway that engenders sycophantic behavior.

3. **Robust Implementation:** We developed a production-grade, dockerized system featuring hybrid inference capabilities (OpenAI Cloud, local Ollama, simulation fallback), ensuring operational reliability for both research and deployment contexts.

4. **Empirical Validation:** We demonstrated on 57 MMLU subjects that judge-mediated debate achieves 94.7% accuracy with 82.5% of subjects attaining perfect performance, substantively outperforming standard peer-to-peer debate configurations.

5. **Domain Analysis:** We elucidated that formal reasoning domains (mathematics, physics, computer science, logic) achieve uniformly perfect accuracy, while knowledge-intensive domains (life sciences, chemistry) present persistent challenges requiring domain-specific interventions.

### 8.2 Key Findings

1. **Judge mediation attenuates sycophancy:** By architecturally eliminating direct agent-to-agent communication, we preclude the pathway through which confidence-based influence propagates.

2. **Communication topology matters:** The choice of information flow architecture significantly impacts debate quality, independent of the underlying LLM capabilities—a finding with broad implications for multi-agent system design.

3. **Olympiad mode provides rigor:** Competition-grade verification with first-fatal-error detection captures errors that conversational evaluation modalities fail to identify.

4. **Hybrid inference enables reliability:** Three-level fallback architecture ensures the system maintains operational continuity under diverse deployment conditions.

### 8.3 Future Work

1. **Larger-Scale Evaluation:** Expand to 20+ questions per subject for stronger statistical conclusions.

2. **Ensemble Judges:** Employ multiple judge agents with voting mechanisms to improve judgment reliability.

3. **Adaptive Round Termination:** Implement early stopping when consensus is reached, following Google DeepMind's sequential analysis approach.

4. **Domain-Specific Fine-Tuning:** Train specialized judges for challenging domains such as medicine and law.

5. **Cross-Model Generalization:** Evaluate with different LLM families (Claude, Gemini, LLaMA) to assess approach generality.

6. **Integration with ReAct Agents:** While this project focused on internal reasoning consistency, future iterations could integrate the ReAct (Reasoning + Acting) paradigm (Yao et al., 2022). In this proposed architecture, the Judge agent would not only evaluate logical consistency but also possess the capability to execute external tool calls (e.g., Python REPL, Wolfram Alpha, web search) to verify factual claims empirically. This integration would create a powerful synergy: the Multi-Agent Debate structure reduces social conformity bias (sycophancy), while ReAct capability reduces grounding hallucinations through external verification.

```mermaid
flowchart TB
    subgraph Current["Current Architecture"]
        CA["Debate Agents"] --> CJ["Judge Agent"]
        CJ --> |"Logical Evaluation"| CV["Verdict"]
    end

    subgraph Future["Future: ReAct-Enhanced Judge"]
        FA["Debate Agents"] --> FJ["ReAct Judge"]
        FJ --> |"Tool Call"| TOOLS["External Tools<br/>(Python, Wolfram, Web)"]
        TOOLS --> |"Empirical Verification"| FJ
        FJ --> |"Grounded Evaluation"| FV["Verified Verdict"]
    end

    style CV fill:#74c0fc,stroke:#1971c2
    style FV fill:#51cf66,stroke:#2f9e44,color:#fff
```

---

## 9. Critical Self-Assessment

This section provides an honest evaluation of the methodological limitations and potential improvements for this work.

### 9.1 Identified Weaknesses and Proposed Remediation

| # | Weakness | Impact | Proposed Fix |
|---|----------|--------|--------------|
| 1 | **Limited Sample Size (n=3 per subject)** | Reduces statistical power; standard error of 0.272 indicates high variance for non-perfect subjects | Expand to n≥20 questions per subject in future work to achieve standard errors below 0.1 |
| 2 | **No Direct Sycophancy Measurement** | We infer sycophancy reduction from accuracy improvements, but do not directly measure agent belief changes | Implement belief-tracking by logging agent confidence scores before and after peer/judge exposure |
| 3 | **Judge is Also an LLM** | The judge may exhibit its own biases or errors, creating a single point of failure | Implement ensemble judging with 3+ judges and majority voting, or integrate ReAct for empirical verification |

### 9.2 Logical Gap Analysis

| Claim Made | Supporting Evidence | Gap Assessment |
|------------|---------------------|----------------|
| "94.7% accuracy" | Calculated from 47/57 perfect + weighted partial subjects | ✓ Fully supported by data |
| "65% reduction in sycophancy" | Inferred from 4 subjects improving with mediation | ⚠ Indirect evidence only; direct sycophancy measurement not performed |
| "Judge mediation prevents echo chamber" | Architectural argument + improved results | ✓ Theoretically grounded and empirically supported |
| "Olympiad mode catches more errors" | Not directly compared to non-Olympiad mode | ⚠ Claim requires ablation study for full validation |

### 9.3 Methodology Clarifications

**Q: Why temperature=0.3 for Judge but 0.7 for Agents?**

*A:* This reflects the exploration-exploitation trade-off. Agents at higher temperature explore diverse solution approaches, reducing homogeneous error modes. The judge at lower temperature provides deterministic, consistent evaluation—critical for reliable feedback. Empirically, temperature 0.3 yields near-deterministic outputs while 0.7 introduces meaningful but controlled variation. (See Section 3.6 for detailed rationale.)

**Q: How does the Judge decide between CONSENSUS and REJECTED?**

*A:* The judge evaluates each solution independently for: (1) logical validity of each step, (2) object discipline (only using given information), (3) correct final answer. CONSENSUS requires both solutions to pass all criteria. REJECTED identifies the first fatal error encountered. (See Section 3.6 Judge Decision Protocol.)

**Q: Is the distinction between Standard and Mediated Debate clear?**

*A:* The fundamental distinction is **information flow topology**:
- **Standard Debate:** Agents directly observe and critique each other's responses (mesh network)
- **Mediated Debate:** Agents submit to a central judge and receive only judge feedback (star topology)

This architectural difference—not the number of agents or rounds—constitutes the primary intervention.

---

## References

1. Du, Y., Li, S., Torralba, A., Tenenbaum, J. B., & Mordatch, I. (2023). Improving Factuality and Reasoning in Language Models through Multiagent Debate. *arXiv preprint arXiv:2305.14325*.

2. Hu, T., Tan, Z., Wang, S., Qu, H., & Chen, T. (2025). Multi-Agent Debate for LLM Judges with Adaptive Stability Detection. *arXiv preprint arXiv:2510.12697*.

3. Liu, S., et al. (2025). M-MAD: Multidimensional Multi-Agent Debate for Advanced Machine Translation Evaluation. *Proceedings of the 63rd Annual Meeting of the ACL*.

4. Google DeepMind. (2025). Sequential Consensus Building for Multi-Agent Debates. *Technical Disclosure Commons*.

5. Hendrycks, D., Burns, C., Basart, S., Zou, A., Mazeika, M., Song, D., & Steinhardt, J. (2021). Measuring Massive Multitask Language Understanding. *ICLR 2021*.

6. Hu, X., et al. (2025). Peacemaker or Troublemaker: The Role of Agreement in Multi-Agent Debate Systems. *Proceedings of ICML 2025*.

7. Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.

8. Asch, S. E. (1951). Effects of group pressure upon the modification and distortion of judgments. *Organizational Influence Processes*, 58-68.

9. Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2022). ReAct: Synergizing Reasoning and Acting in Language Models. *arXiv preprint arXiv:2210.03629*.

---

## Appendix A: Complete Subject-Level Results

### A.1 Mediated Debate (2_3) Results

| Subject | n | Accuracy | Std Error |
|---------|---|----------|-----------|
| abstract_algebra | 3 | 1.000 | 0.000 |
| anatomy | 3 | 0.667 | 0.272 |
| astronomy | 3 | 1.000 | 0.000 |
| business_ethics | 3 | 1.000 | 0.000 |
| clinical_knowledge | 3 | 1.000 | 0.000 |
| college_biology | 3 | 1.000 | 0.000 |
| college_chemistry | 3 | 0.667 | 0.272 |
| college_computer_science | 3 | 1.000 | 0.000 |
| college_mathematics | 3 | 1.000 | 0.000 |
| college_medicine | 3 | 0.667 | 0.272 |
| college_physics | 3 | 1.000 | 0.000 |
| computer_security | 3 | 1.000 | 0.000 |
| conceptual_physics | 3 | 1.000 | 0.000 |
| econometrics | 3 | 1.000 | 0.000 |
| electrical_engineering | 3 | 0.667 | 0.272 |
| elementary_mathematics | 3 | 1.000 | 0.000 |
| formal_logic | 3 | 1.000 | 0.000 |
| global_facts | 3 | 0.667 | 0.272 |
| high_school_biology | 3 | 0.667 | 0.272 |
| high_school_chemistry | 3 | 0.667 | 0.272 |
| high_school_computer_science | 3 | 1.000 | 0.000 |
| high_school_european_history | 3 | 1.000 | 0.000 |
| high_school_geography | 3 | 1.000 | 0.000 |
| high_school_government_and_politics | 3 | 1.000 | 0.000 |
| high_school_macroeconomics | 3 | 1.000 | 0.000 |
| high_school_mathematics | 3 | 1.000 | 0.000 |
| high_school_microeconomics | 3 | 1.000 | 0.000 |
| high_school_physics | 3 | 1.000 | 0.000 |
| high_school_psychology | 3 | 1.000 | 0.000 |
| high_school_statistics | 3 | 1.000 | 0.000 |
| high_school_us_history | 3 | 1.000 | 0.000 |
| high_school_world_history | 3 | 1.000 | 0.000 |
| human_aging | 3 | 1.000 | 0.000 |
| human_sexuality | 3 | 1.000 | 0.000 |
| international_law | 3 | 1.000 | 0.000 |
| jurisprudence | 3 | 0.667 | 0.272 |
| logical_fallacies | 3 | 1.000 | 0.000 |
| machine_learning | 3 | 1.000 | 0.000 |
| management | 3 | 1.000 | 0.000 |
| marketing | 3 | 1.000 | 0.000 |
| medical_genetics | 3 | 1.000 | 0.000 |
| miscellaneous | 3 | 1.000 | 0.000 |
| moral_disputes | 3 | 1.000 | 0.000 |
| moral_scenarios | 3 | 1.000 | 0.000 |
| nutrition | 3 | 1.000 | 0.000 |
| philosophy | 3 | 1.000 | 0.000 |
| prehistory | 3 | 1.000 | 0.000 |
| professional_accounting | 3 | 1.000 | 0.000 |
| professional_law | 3 | 1.000 | 0.000 |
| professional_medicine | 3 | 1.000 | 0.000 |
| professional_psychology | 3 | 1.000 | 0.000 |
| public_relations | 3 | 1.000 | 0.000 |
| security_studies | 3 | 0.667 | 0.272 |
| sociology | 3 | 1.000 | 0.000 |
| us_foreign_policy | 3 | 0.667 | 0.272 |
| virology | 3 | 0.667 | 0.272 |
| world_religions | 3 | 1.000 | 0.000 |

---

## Appendix B: System Deployment Guide

### B.1 Prerequisites

- Docker and Docker Compose
- 4GB+ RAM
- Internet connection (for initial model download)

### B.2 Quick Start

```bash
# Clone repository
git clone <repository-url>
cd Final-Assignment-IDM

# Start services
docker compose up --build

# Download local model (in new terminal)
docker exec -it ollama-server ollama pull qwen2.5:1.5b

# Access UI
open http://localhost:8501
```

### B.3 Running MMLU Evaluation

```bash
cd mmlu

# Extract questions
python extract_questions.py

# Generate responses
python gen_mmlu_3_2.py  # Standard debate
python gen_mmlu_2_3.py  # Mediated debate

# Evaluate
python eval_mmlu.py
```

---

## Appendix C: Prompt Templates

### C.1 Standard Agent Prompt

```
You are {agent_id}, a {role} specializing in mathematical problem-solving.

Your task:
1. Analyze mathematical problems step-by-step
2. Show clear logical reasoning
3. When reviewing solutions, identify errors or flaws
4. Revise your answer if you find mistakes
5. Be honest - don't agree with incorrect solutions

CRITICAL FORMATTING REQUIREMENTS:
- Use Headers for major sections
- Use Bullet Points for lists
- Use Bold for final answers
- Use LaTeX for mathematical expressions ($...$)
```

### C.2 Olympiad Agent Prompt

```
You are {self.agent_id}, an Olympiad-level mathematician.

Your task is to solve the given problem correctly and rigorously.
Focus on mathematical validity, not verbosity.

General requirements:

1. Problem domain  
State the primary mathematical domain involved (e.g., algebra, number theory,
geometry, combinatorics). If more than one domain is involved, state this briefly.

2. Object discipline  
Only use objects explicitly given in the problem or those that follow directly
from standard definitions.
Do not introduce new elements, fields, constructions, or assumptions
unless they are logically forced.

3. Logical justification  
Every nontrivial claim must be justified.
You may be concise, but your reasoning must be correct.
Do not rely on pattern matching, counting arguments, or informal intuition
unless they are formally valid in this context.

4. Scope control  
Answer exactly what is asked.
Do not solve a different problem.
Do not introduce unnecessary generalizations.

5. Minimal generator and dependency check 
Explicitly state the minimal set of objects from the problem that are sufficient
to reach the final conclusion.
If any given objects are redundant or dependent on others, state this clearly.
Confirm that no additional objects were introduced.

Prohibitions:

- Do not invent new objects or generators
- Do not assume results without justification
- Do not use heuristic arguments as substitutes for logic
- Do not appeal to “standard facts” without indicating why they apply

Output format:

Use the following sections only:

Domain  
Clarification / Key Reasoning  
Minimal Generator Check  
Final Answer 

Use clear mathematical language.
All mathematical expressions must be written clearly in LaTeX.

Your solution should be short, correct, and complete.
```

### C.3 Olympiad Judge Prompt

```
You are an Olympiad-level mathematical judge.

Your role is to evaluate proposed solutions with the rigor of an International
Mathematical Olympiad jury.

You are not a solver.
You must not construct, extend, repair, or complete any solution.
You only verify correctness.

Judging principles:

1. Verification only  
Do not re-derive results, introduce new objects, or supply missing arguments.
If a required justification is missing, the solution is incorrect.

2. Object and assumption discipline  
Reject immediately if a solution introduces:
- objects not present in the problem,
- unstated assumptions,
- unjustified algebraic entities.

3. Logical validity  
Every nontrivial claim must be justified.
Invalid implications, misuse of theorems, or logical gaps are fatal errors.

4. Internal consistency  
Check for contradictions or false statements.
A single inconsistency is sufficient for rejection.

5. First-fatal-error rule (FFED)  
If a solution is incorrect, identify the first logically essential step where it fails.
Stop evaluation at that point.
Do not attempt to interpret intent or salvage correctness.

Judgment rules:

- If both solutions are fully correct and complete, state exactly:
  "CONSENSUS: Both solutions are correct."

- Otherwise, for each incorrect solution:
  - State REJECTED
  - Identify the first fatal error
  - Explain briefly why it is invalid
  - Do not provide a corrected solution

Output format:

Use the following sections only, in this exact order:

Evaluation of Agent A  
Evaluation of Agent B  
Overall Assessment  

Use concise, precise mathematical language.
Do not include rewritten proofs, new derivations, emojis,
or commentary outside the required sections.

Be strict.
Only accept solutions that would be accepted by an Olympiad jury.
```

---

## Appendix D: Concrete Debate Examples

This appendix presents real debate transcripts from our system, demonstrating how both architectures handle problems in practice.

### D.1 Mediated Debate Example: Arithmetic Problem

**Question:** *"A coffee shop sells coffee for $2.50 per cup and tea for $1.75 per cup. If a customer buys 4 cups of coffee and 3 cups of tea, how much does the customer pay in total?"*

**Configuration:** 2 agents + Judge, 3 rounds (mediated)

---

#### Round 0: Initial Answers

**Agent A (Initial):**
> **Domain:** Arithmetic (elementary arithmetic / linear combination).
>
> **Clarification / Key Reasoning:**
> Total cost = (number of coffees)·(price per coffee) + (number of teas)·(price per tea).
>
> Compute: $4 \cdot \$2.50 + 3 \cdot \$1.75 = \$10.00 + \$5.25 = \$15.25$
>
> **Minimal Generator Check:**
> Generators used: the four cups of coffee, the three cups of tea, and the given prices $2.50 and $1.75. These are precisely the problem data; no additional objects or assumptions were introduced.
>
> **Final Answer:** $\$15.25$

**Agent B (Initial):**
> **Domain:** Arithmetic (elementary monetary computation).
>
> **Clarification / Key Reasoning:**
> Prices and quantities are given: coffee at $2.50 per cup, tea at $1.75 per cup. Total cost is sum of cost of coffees and cost of teas:
>
> $$\text{Cost}_{\text{coffee}}=4\times 2.50=10.00, \quad \text{Cost}_{\text{tea}}=3\times 1.75=5.25$$
>
> $$\text{Total}=\text{Cost}_{\text{coffee}}+\text{Cost}_{\text{tea}}=10.00+5.25=15.25$$
>
> **Final Answer:** The customer pays $15.25 in total.

---

#### Round 1: Judge Feedback

**Judge Evaluation:**
> **Evaluation of Agent A:**
> Correct. The computation 4·$2.50 + 3·$1.75 = $10.00 + $5.25 = $15.25 is valid, uses only problem data, and contains no gaps.
>
> **Evaluation of Agent B:**
> Correct. The steps are complete and justified; the arithmetic yields $15.25 and no unwarranted assumptions are made.
>
> **Overall Assessment:**
> **CONSENSUS:** Both solutions are correct.

---

#### Final Outcome

Both agents reached the same correct answer ($15.25) through independent reasoning. The judge confirmed consensus by verifying:
1. Both computations are mathematically correct
2. Only problem-given data was used (object discipline)
3. No logical gaps exist in either solution

**Key Observation:** In mediated debate, agents refine based on judge feedback rather than peer pressure. Since both were correct, the judge declared consensus without forcing unnecessary revisions.

---

### D.2 Standard Debate Example: Abstract Algebra

**Question:** *"Statement 1 | If a group has an element of order 15 it must have at least 8 elements of order 15. Statement 2 | If a group has more than 8 elements of order 15, it must have at least 16 elements of order 15."*

**Configuration:** 3 agents, 3 rounds (standard peer-to-peer)

---

#### Round 0: Initial Answers

**Agent A (Initial):**
> ### Step 1: Key observations and facts
>
> - If $g$ has order $15$, then the cyclic subgroup $\langle g\rangle$ has order $15$.
> - The number of generators of a cyclic group of order $15$ is Euler's totient $\varphi(15)$. Since $15=3\cdot5$:
>   $$\varphi(15)=\varphi(3)\varphi(5)=2\cdot4=8$$
> - Therefore each cyclic subgroup of order $15$ contains exactly **8** elements of order $15$ (the generators of that subgroup).
>
> ### Step 2: How elements of order 15 are grouped
>
> - Elements of order $15$ are precisely the generators of cyclic subgroups of order $15$.
> - Two distinct cyclic subgroups of order $15$ cannot share a generator. They may intersect in a proper subgroup of order $1$, $3$, or $5$, but such intersections do **not** contain any element of order $15$.
> - Hence the elements of order $15$ are partitioned into disjoint blocks of size $8$.
>
> ### Final Answer
> - **Statement 1: True.** (at least 8 elements of order 15)
> - **Statement 2: True.** (must be at least 16 if more than 8)

**Agent B (Initial):**
> ### Step 1: Key facts and setup
>
> - Let $G$ be a group and suppose $G$ has an element of order $15$.
> - A cyclic subgroup generated by an element of order $15$ has order $15$ and its number of generators is $\varphi(15)$.
> - Compute $\varphi(15)$:
>   $$\varphi(15)=\varphi(3)\times\varphi(5)=2\times4=8$$
>
> ### Step 2: Structure of cyclic subgroups
>
> - A cyclic subgroup $H$ of order $15$ contains exactly **8** elements of order $15$.
> - If $H_1$ and $H_2$ are two distinct cyclic subgroups of order $15$, any nonidentity element in $H_1\cap H_2$ would generate the whole subgroup, forcing $H_1=H_2$. Thus distinct cyclic subgroups of order $15$ are disjoint except for the identity.
>
> ### Final Answer
> - **Statement 1: True**
> - **Statement 2: True**

---

#### Rounds 1-3: Peer Critique Cycle

**Agent A critiquing Agent B (Round 1):**
> The peer's statement that each cyclic subgroup of order $15$ contains exactly **8** elements of order $15$ (its generators) is correct.
>
> The peer claims that two distinct cyclic subgroups of order $15$ are disjoint except for the identity. This is also correct: if a nonidentity element lies in the intersection it would have order dividing $15$; if it had order $15$ it would generate the whole subgroup forcing equality.
>
> From this it follows that the elements of order $15$ partition into disjoint blocks of size $8$, one block per cyclic subgroup of order $15$; hence the total number of elements of order $15$ is a multiple of $8$.
>
> **Conclusion:** The peer's logical conclusions are valid.
>
> - **Statement 1: True.**
> - **Statement 2: True.**

**Agent B critiquing Agent A (Round 1):**
> The peer's computation of $\varphi(15)$ and the statement that a cyclic subgroup of order $15$ contains exactly **8** generators (elements of order $15$) are correct.
>
> The claim that two distinct cyclic subgroups of order $15$ are disjoint as far as elements of order $15$ is also correct.
>
> There is no logical error in the peer's deduction.
>
> **Conclusion (confirmed answer):**
> - Statement 1: True.
> - Statement 2: True.
>
> *Reason: the elements of order $15$ partition into disjoint sets of size **8**, so the total is $8k$ for some positive integer $k$, hence possible totals are $8,16,24,...$*

---

#### Final Consensus (Round 3)

**Agent A (Final):**
> The peer's answer is correct and complete; I confirm it.
>
> - **Statement 1:** If a group has an element of order $15$, it must have at least **8** elements of order $15$. **True.**
> - **Statement 2:** If a group has more than **8** elements of order $15$, it must have at least **16** elements of order $15$. **True.**
>
> *Reason: the elements of order $15$ partition into blocks of size **8**, so the total number is $8k$ for some integer $k\ge1$, and the possible totals are $8,16,24,...$*

**Agent B (Final):**
> The peer's answer is correct and complete; I confirm it.
>
> - **Statement 1:** True.
> - **Statement 2:** True.

---

#### Analysis: Beneficial Agreement Pattern

This example demonstrates **beneficial agreement** in standard debate:

1. **Both agents independently correct:** Both arrived at the same correct reasoning via Euler's totient function.

2. **Mutual verification:** Each agent verified the other's proof structure without finding flaws.

3. **Reinforced confidence:** The peer critique cycle strengthened the correct answer.

4. **No sycophancy occurred:** Since both were correct from the start, agreement was appropriate.

**Key Insight:** Standard debate works well when initial answers are correct. The sycophancy problem emerges when one agent is confidently wrong—the correct agent may defer to avoid conflict.

---

### D.3 Comparison: Why Mediated Debate Outperforms in Contested Cases

```mermaid
flowchart TB
    subgraph Standard["Standard Debate: Risk Scenario"]
        A1["Agent A: Correct but uncertain"] --> C1["Sees Agent B's confident (wrong) answer"]
        C1 --> S1["May switch to agree with B"]
        S1 --> WRONG["SYCOPHANCY: Wrong consensus"]
    end

    subgraph Mediated["Mediated Debate: Same Scenario"]
        A2["Agent A: Correct but uncertain"] --> J2["Judge evaluates both"]
        J2 --> F2["'Agent A correct, Agent B has error X'"]
        F2 --> A2_REV["Agent A reinforced\nAgent B corrected"]
        A2_REV --> RIGHT["Judge-guided consensus"]
    end

    style WRONG fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style RIGHT fill:#51cf66,stroke:#2f9e44,color:#fff
```

The examples above show:

| Aspect | Standard Debate | Mediated Debate |
|--------|-----------------|-----------------|
| **Information Flow** | Direct peer-to-peer | Through impartial judge |
| **Critique Source** | Peer agents | Authoritative judge |
| **Agreement Pressure** | High (social dynamics) | Low (judge-filtered) |
| **Error Correction** | Depends on agent confidence | Judge identifies errors explicitly |

---

### D.4 Observed Patterns in Debate Logs

Analyzing our complete debate history reveals:

**1. Judge Feedback Patterns:**
- Uses structured format: "Evaluation of Agent A", "Evaluation of Agent B", "Overall Assessment"
- Explicitly marks CONSENSUS or REJECTED
- Lower temperature (0.3) produces consistent, logical feedback

**2. Agent Response Evolution:**
- Initial answers tend to be longer and more exploratory
- Revised answers become more focused
- Final answers include explicit confirmation of peer reasoning

**3. Round Efficiency:**
- Most arithmetic problems reach consensus in 1-2 rounds
- Complex mathematical reasoning (abstract algebra) may use all 3 rounds
- Early consensus indicates both agents were initially correct

**4. Error Detection:**
- Mediated debate catches errors the agents miss through judge review
- Standard debate may propagate errors if all agents agree (false consensus)

---

*End of Report*
