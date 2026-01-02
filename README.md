# Multi-Agent Debate System with Judge Mediation

A Dockerized multi-agent debate system comparing **Standard Debate** (peer-to-peer) vs. **Mediated Debate** (with judge arbitrator) using local open-source LLMs via Ollama.

## Features

- 🤖 **Local LLM Inference**: Uses Ollama with Qwen 2.5 (1.5B) - optimized for CPU and speed
- 🐳 **Fully Dockerized**: Run everything with `docker compose up`
- 📊 **Side-by-Side Comparison**: Visual comparison of debate methods
- ⚖️ **Judge-Mediated Architecture**: Breaks echo chamber with impartial arbitrator
- 🔍 **System Status Monitoring**: Real-time Ollama connectivity and model status
- 🛡️ **Robust Error Handling**: Automatic fallback to simulation mode on timeout/errors - **never crashes**

## Architecture

- **Service 1 (ollama)**: Runs Ollama inference server with Qwen 2.5 model
- **Service 2 (webapp)**: Streamlit UI + Python debate logic

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available for Ollama
- Internet connection (for initial model download)

### Step 1: Start the Services

```bash
docker compose up --build
```

**Note:** Use `docker compose` (with space) for Docker Compose V2, or `docker-compose` (with hyphen) for older versions.

### Step 2: Download the Model

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

## Configuration

### Environment Variables

The application uses these environment variables (set in `docker-compose.yml`):

- `OPENAI_BASE_URL`: Ollama API endpoint (default: `http://ollama:11434/v1`)
- `OPENAI_API_KEY`: API key (set to `ollama` for local use)
- `OLLAMA_HOST`: Ollama server host (default: `http://ollama:11434`)
- `MODEL_NAME`: Model to use (default: `qwen2.5:1.5b`)
- `OLLAMA_TIMEOUT`: API timeout in seconds (default: `120.0`)

### Model Selection

The system uses `qwen2.5:1.5b` by default. This model is:
- **Fast**: Optimized for CPU inference
- **Lightweight**: Only 1.5B parameters
- **Reliable**: Better timeout handling than larger models

To use a different model:
1. Edit `docker-compose.yml` and change `MODEL_NAME`
2. Pull the new model: `docker exec -it ollama-server ollama pull <model-name>`

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
./update_code.sh
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
