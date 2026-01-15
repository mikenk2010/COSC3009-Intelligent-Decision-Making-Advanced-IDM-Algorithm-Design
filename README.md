# Multi-Agent Debate System with Judge Mediation

A Dockerized multi-agent debate system comparing **Standard Debate** (peer-to-peer) vs. **Mediated Debate** (with judge arbitrator) with Olympiad mode using local open-source LLMs via Ollama.

<img width="3446" height="1930" alt="image" src="https://github.com/user-attachments/assets/fdfe1ecf-b64c-4074-8a44-f297c267e44e" />
<img width="3442" height="1934" alt="image" src="https://github.com/user-attachments/assets/26f338f5-5990-42e8-a879-1db28c0cd30c" />



## Screenshots
- Problem: `A coffee shop sells coffee for $2.50 per cup and tea for $1.75 per cup. If a customer buys 4 cups of coffee and 3 cups of tea, how much does the customer pay in total?`
- Expected answer: `Answer: $15.25`
<img width="524" height="646" alt="image" src="https://github.com/user-attachments/assets/9aa08c80-8068-4a17-9185-42489f3d2472" />

- Standard Debate
<img width="1197" height="488" alt="image" src="https://github.com/user-attachments/assets/4507d4cb-725d-4b7d-aadc-45c2f3f51e9a" />

- Mediated Debate (With Judge)
<img width="1170" height="566" alt="image" src="https://github.com/user-attachments/assets/fc05d8b6-22c8-4f6c-bea5-ffdd263c4f95" />

- Olympiad Mode
<img width="3450" height="1928" alt="image" src="https://github.com/user-attachments/assets/89977246-d688-4d0b-8b72-6357bff6bad3" />



## Features

- 🤖 **Local LLM Inference**: Uses Ollama with Qwen 2.5 (1.5B) - optimized for CPU and speed
- ☁️ **OpenAI Cloud Support**: Optional high-accuracy inference using GPT-5 mini, with seamless fallback to local Ollama
- 🐳 **Fully Dockerized**: Run everything with `docker compose up`
- 📊 **Side-by-Side Comparison**: Visual comparison of debate methods
- ⚖️ **Judge-Mediated Architecture**: Breaks echo chamber with impartial arbitrator
- 🏅 **Olympiad Math Mode**: Competition-grade solver and jury agents with strict object discipline and first-fatal-error verification
- 📚 **Expanded Evaluation Dataset**: 57 curated subject areas spanning mathematics, logic, and structured reasoning tasks
- 🔍 **System Status Monitoring**: Real-time Ollama connectivity and model status
- 🛡️ **Robust Error Handling**: Automatic fallback to simulation mode on timeout/errors — **never crashes**


## Architecture

- **Service 1 (ollama)**: Local inference server running open-source models (e.g. Qwen 2.5) for fast, CPU-optimized reasoning
- **Service 2 (webapp)**: Streamlit UI + Python debate engine (agents, judge, Olympiad mode logic)
- **External Service (OpenAI Cloud)**: Optional high-accuracy inference using GPT-5 mini, integrated as a drop-in backend with automatic fallback to local Ollama
<<<<<<< HEAD

=======
>>>>>>> refs/remotes/origin/olympiad-mode

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available for Ollama
- Internet connection (for initial model download and OpenAI API calls)

### Step 1: Start the Services

```bash
docker compose up --build
```

**Note:** Use `docker compose` (with space) for Docker Compose V2, or `docker-compose` (with hyphen) for older versions.

### Step 2: Download the Model or Defined OPENAI_API_KEY 

Wait for Ollama to start (about 30 seconds), then in a **new terminal**, run:

```bash
docker exec -it ollama-server ollama pull qwen2.5:1.5b
```

This will download the Qwen 2.5 model (~1GB). Wait for the download to complete.

### Step 3: Access the UI

Open your browser to: `http://localhost:8501`

- Check the "System Status" section in the sidebar to verify Ollama is connected
- The status should show: `✅ Online | ✅ Model loaded: qwen2.5:1.5b`

### Step 4: Run a Debate

1. Select a math problem from the sidebar
2. Click "Start Standard Debate" to see peer-to-peer debate
3. Click "Start Mediated Debate" to see judge-mediated debate
4. Compare how the Judge prevents sycophancy (false consensus)

## Stopping the Application

```bash
docker compose down
```

To also remove the Ollama data volume (frees up disk space):
```bash
docker compose down -v
```

## Project Structure

```
.
├── docker-compose.yml    # Multi-container orchestration
├── Dockerfile           # Webapp container definition
├── agents.py           # DebateAgent and JudgeAgent classes
├── simulation.py       # Debate simulation logic
├── app.py             # Streamlit UI
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## How It Works

### Standard Debate (Baseline)
- **Topology**: Peer-to-Peer (Agent A ↔ Agent B)
- **Process**: Agents directly critique each other's answers
- **Problem**: Agents may blindly agree (sycophancy/disagreement collapse)

### Mediated Debate (Improved)
- **Topology**: Star Topology (Agent A + Agent B → Judge)
- **Process**:
  1. Agents generate independent answers
  2. Judge evaluates both and provides critical feedback
  3. Agents revise based on judge's feedback
- **Benefit**: Breaks echo chamber, forces error correction

### Olympiad Mode (Improved)

Olympiad Mode introduces **competition-grade reasoning constraints** inspired by
International Mathematical Olympiad (IMO) standards.

It replaces conversational debate behavior with **formal mathematical roles**:

#### Olympiad Agent
- Acts as an Olympiad-level problem solver
- States the problem domain explicitly
- Uses strict object discipline (no invented assumptions)
- Justifies every nontrivial claim
- Focuses on correctness over verbosity

#### Olympiad Judge
- Acts as an Olympiad jury member
- Does **not** solve or repair solutions
- Enforces definitions, assumptions, and logical completeness
- Applies a **first-fatal-error rule**: a single logical flaw is sufficient for rejection
- Declares consensus only if solutions are fully correct

<<<<<<< HEAD
=======
**Purpose**:  
To evaluate mathematical reasoning at a competition standard rather than conversational plausibility.

>>>>>>> refs/remotes/origin/olympiad-mode
## Dataset Coverage & Evaluation

The system is evaluated on an expanded benchmark covering **57 subject areas**, designed to test
reasoning accuracy, domain discipline, and judge strictness across both technical and non-technical domains.

Each subject contains 3 representative questions, with accuracy measured under the
judge-mediated evaluation pipeline.

### Subject-Level Results

| Subject                      |  N | Accuracy | Std. Error |
| ---------------------------- | -: | -------: | ---------: |
| Abstract Algebra             |  3 |     1.00 |      0.000 |
| Anatomy                      |  3 |     0.67 |      0.272 |
| Astronomy                    |  3 |     1.00 |      0.000 |
| Business Ethics              |  3 |     1.00 |      0.000 |
| Clinical Knowledge           |  3 |     1.00 |      0.000 |
| College Biology              |  3 |     1.00 |      0.000 |
| College Chemistry            |  3 |     0.67 |      0.272 |
| College Computer Science     |  3 |     1.00 |      0.000 |
| College Mathematics          |  3 |     1.00 |      0.000 |
| College Medicine             |  3 |     0.67 |      0.272 |
| College Physics              |  3 |     1.00 |      0.000 |
| Computer Security            |  3 |     1.00 |      0.000 |
| Conceptual Physics           |  3 |     1.00 |      0.000 |
| Econometrics                 |  3 |     1.00 |      0.000 |
| Electrical Engineering       |  3 |     0.67 |      0.272 |
| Elementary Mathematics       |  3 |     1.00 |      0.000 |
| Formal Logic                 |  3 |     1.00 |      0.000 |
| Global Facts                 |  3 |     0.67 |      0.272 |
| High School Biology          |  3 |     0.67 |      0.272 |
| High School Chemistry        |  3 |     0.67 |      0.272 |
| High School Computer Science |  3 |     1.00 |      0.000 |
| High School European History |  3 |     1.00 |      0.000 |
| High School Geography        |  3 |     1.00 |      0.000 |
| High School Gov & Politics   |  3 |     1.00 |      0.000 |
| High School Macroeconomics   |  3 |     0.67 |      0.272 |
| High School Mathematics      |  3 |     1.00 |      0.000 |
| High School Microeconomics   |  3 |     1.00 |      0.000 |
| High School Physics          |  3 |     1.00 |      0.000 |
| High School Psychology       |  3 |     1.00 |      0.000 |
| High School Statistics       |  3 |     1.00 |      0.000 |
| High School US History       |  3 |     1.00 |      0.000 |
| High School World History    |  3 |     1.00 |      0.000 |
| Human Aging                  |  3 |     1.00 |      0.000 |
| Human Sexuality              |  3 |     1.00 |      0.000 |
| International Law            |  3 |     1.00 |      0.000 |
| Jurisprudence                |  3 |     0.67 |      0.272 |
| Logical Fallacies            |  3 |     1.00 |      0.000 |
| Machine Learning             |  3 |     1.00 |      0.000 |
| Management                   |  3 |     1.00 |      0.000 |
| Marketing                    |  3 |     1.00 |      0.000 |
| Medical Genetics             |  3 |     1.00 |      0.000 |
| Miscellaneous                |  3 |     1.00 |      0.000 |
| Moral Disputes               |  3 |     1.00 |      0.000 |
| Moral Scenarios              |  3 |     1.00 |      0.000 |
| Nutrition                    |  3 |     1.00 |      0.000 |
| Philosophy                   |  3 |     1.00 |      0.000 |
| Prehistory                   |  3 |     1.00 |      0.000 |
| Professional Accounting      |  3 |     1.00 |      0.000 |
| Professional Law             |  3 |     1.00 |      0.000 |
| Professional Medicine        |  3 |     1.00 |      0.000 |
| Professional Psychology      |  3 |     1.00 |      0.000 |
| Public Relations             |  3 |     1.00 |      0.000 |
| Security Studies             |  3 |     0.67 |      0.272 |
| Sociology                    |  3 |     1.00 |      0.000 |
| US Foreign Policy            |  3 |     0.67 |      0.272 |
| Virology                     |  3 |     0.67 |      0.272 |
| World Religions              |  3 |     1.00 |      0.000 |

**Notes:**
- Accuracy reflects judge-validated correctness, not self-reported confidence.
- Lower scores typically correspond to ambiguity, missing justification, or assumption violations.
- Olympiad Mode applies stricter rejection criteria than standard debate.

<<<<<<< HEAD
**Purpose**:  
To evaluate mathematical reasoning at a competition standard rather than conversational plausibility.

=======
>>>>>>> refs/remotes/origin/olympiad-mode

## Configuration

### Environment Variables

The application uses these environment variables (set in `docker-compose.yml`):

- `OPENAI_BASE_URL`: Ollama API endpoint (default: `http://ollama:11434/v1`)
- `OPENAI_API_KEY`: API key (set to `ollama` for local use)
- `OLLAMA_HOST`: Ollama server host (default: `http://ollama:11434`)
- `MODEL_NAME`: Model to use (default: `qwen2.5:1.5b`)
- `OLLAMA_TIMEOUT`: API timeout in seconds (default: `120.0`)

### Model Selection

The system uses a **hybrid inference strategy** with automatic fallback.

#### Inference Priority

1. **OpenAI Cloud (GPT-5 mini)** — if a valid API key is available  
2. **Local Ollama (Qwen 2.5:1.5B)** — automatic fallback if cloud inference is unavailable

This ensures **maximum accuracy when possible** and **full offline reliability** when needed.

---

#### OpenAI Cloud (Primary)

When an OpenAI API key is present, the system prioritizes **GPT-5 mini**:
- **Higher reasoning accuracy** for complex logic and mathematics
- **Stronger consistency** in multi-agent debate and judging
- **No code changes required** — drop-in backend

To enable:
1. Get API key from [OpenAI](https://platform.openai.com/api-keys)
2. Create `.env` file:
```
OPENAI_API_KEY=sk-your-key
```
3. Restart: `docker compose down && docker compose up -d`

## Error Handling & Fallback

The system implements **robust fallback mechanisms**:

1. **Timeout Protection**: If API calls exceed 120 seconds, automatically switches to simulation mode
2. **Connection Error Handling**: If Ollama is unreachable, uses simulated responses
3. **Graceful Degradation**: The UI always shows something - never crashes
4. **Simulation Mode**: Provides contextually appropriate mock responses when the model is unavailable

**Result**: The demo can run even on slow hardware or when the model is not loaded.

## Troubleshooting

### Ollama Not Connecting

1. Check if the container is running: `docker compose ps`
2. Check logs: `docker compose logs ollama`
3. Verify port 11434 is not in use: `lsof -i :11434`
4. Restart Ollama: `docker compose restart ollama`

### Model Not Loading

1. Check Ollama logs: `docker compose logs ollama`
2. Manually pull the model: `docker exec -it ollama-server ollama pull qwen2.5:1.5b`
3. Verify model exists: `docker exec -it ollama-server ollama list`

### Timeout Errors

If you see timeout errors:
1. The system will automatically use simulation mode (you'll see `[SIMULATION]` in responses)
2. To increase timeout, edit `docker-compose.yml` and change `OLLAMA_TIMEOUT=300.0` (5 minutes)
3. Check system resources (CPU, RAM) - Qwen 2.5 needs adequate resources

### Slow Performance

- Qwen 2.5 is optimized for speed, but still requires sufficient CPU/RAM
- Close other resource-intensive applications
- Consider using simulation mode for demos if hardware is limited

### Docker Not Running

- **macOS/Windows:** Open Docker Desktop application
- **Linux:** `sudo systemctl start docker`
- Verify: `docker info`

## Development

### Updating Code Changes in Docker

**Important:** The code is copied into the Docker image during build, so you need to **rebuild the image** to see code changes.

#### Quick Update (Recommended)

Use the provided update script:
```bash
./scripts/update_code.sh
```

#### Manual Update

```bash
# Rebuild the webapp image
docker compose build --no-cache webapp

# Stop and remove the old container
docker compose stop webapp
docker compose rm -f webapp

# Start with the new image
docker compose up -d webapp
```

### Running Locally (Without Docker)

1. Install dependencies: `pip install -r requirements.txt`
2. Start Ollama locally: `ollama serve`
3. Pull model: `ollama pull qwen2.5:1.5b`
4. Set environment: `export OPENAI_BASE_URL=http://localhost:11434/v1`
5. Run app: `streamlit run app.py`

## Research Background

This implementation is based on:
- **Du et al. (2023)**: "Improving Factuality and Reasoning in Language Models through Multiagent Debate"
- **Problem Addressed**: Sycophancy and disagreement collapse in peer-to-peer debates
- **Solution**: Mediated debate with impartial judge arbitrator

## License

This project is for educational/research purposes.

## Acknowledgments

- Ollama team for local LLM inference
- Qwen team for the efficient 2.5 model
- Streamlit for the UI framework
