# Multi-Agent Debate System

A Dockerized multi-agent debate system comparing **Standard Debate** (peer-to-peer) vs. **Mediated Debate** (with judge arbitrator) using local open-source LLMs via Ollama.

## Features

- 🤖 **Local LLM Inference**: Uses Ollama with DeepSeek R1 (1.5B) reasoning model
- 🐳 **Fully Dockerized**: Run everything with `docker compose up`
- 📊 **Side-by-Side Comparison**: Visual comparison of debate methods
- ⚖️ **Judge-Mediated Architecture**: Breaks echo chamber with impartial arbitrator
- 🔍 **System Status Monitoring**: Real-time Ollama connectivity and model status

## Architecture

- **Service 1 (ollama)**: Runs Ollama inference server with DeepSeek R1 model
- **Service 2 (webapp)**: Streamlit UI + Python debate logic

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available for Ollama

### Running the Application

1. **Clone or navigate to the project directory**

2. **Start the services:**
   ```bash
   docker compose up --build
   ```
   
   **Note:** Use `docker compose` (with space) for Docker Compose V2, or `docker-compose` (with hyphen) for older versions.

3. **Wait for initialization:**
   - Ollama will start and pull the `deepseek-r1:1.5b` model (first run only, ~1GB download)
   - This may take 2-5 minutes on first startup

4. **Access the UI:**
   - Open your browser to: `http://localhost:8501`
   - Check the "System Status" section to verify Ollama is connected

5. **Run a debate:**
   - Select a math problem from the sidebar
   - Click "Start Standard Debate" and "Start Mediated Debate" to compare
   - Observe how the Judge intervenes in mediated debates

### Stopping the Application

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

### Model Selection

The system uses `deepseek-r1:1.5b` by default. To use a different model:

1. Edit `docker-compose.yml` and change `deepseek-r1:1.5b` to your preferred model
2. Edit `agents.py` and update the `get_model_name()` function

Available DeepSeek models:
- `deepseek-r1:1.5b` (smaller, faster)
- `deepseek-r1:7b` (larger, more capable)

## Troubleshooting

### Volume Mount Permission Error

If you see: `error while creating mount source path: operation not permitted`

**Fix Docker Desktop File Sharing:**
1. Open Docker Desktop → Settings → Resources → File Sharing
2. Add: `/Users/baonguyen/Documents/Study/RMIT`
3. Click Apply & Restart

**Alternative (No Volume Mounts):**
```bash
docker compose -f docker-compose.no-volumes.yml up -d --build
```

### Ollama Not Connecting

1. Check if the container is running: `docker ps`
2. Check logs: `docker compose logs ollama`
3. Verify port 11434 is not in use: `lsof -i :11434`
4. Manually pull the model: `docker exec -it ollama-server ollama pull deepseek-r1:1.5b`

### Model Not Loading

1. Check Ollama logs: `docker compose logs ollama`
2. Manually pull the model: `docker exec -it ollama-server ollama pull deepseek-r1:1.5b`
3. Verify model exists: `docker exec -it ollama-server ollama list`

### Slow Performance

- The 1.5B model is optimized for speed. For better quality, use `deepseek-r1:7b`
- Ensure sufficient RAM (4GB+ recommended)
- Close other resource-intensive applications

### Docker Not Running

- **macOS/Windows:** Open Docker Desktop application
- **Linux:** `sudo systemctl start docker`
- Verify: `docker info`

## Development

### Updating Code Changes in Docker

**Important:** The code is copied into the Docker image during build (not mounted as a volume), so you need to **rebuild the image** to see code changes.

#### Quick Update (Recommended)

Use the provided update script:
```bash
./update_code.sh
```

This script will:
1. Rebuild the webapp image with latest code
2. Stop and remove the old container
3. Start a new container with the updated image

#### Manual Update

If you prefer to do it manually:
```bash
# Rebuild the webapp image (forces rebuild without cache)
docker compose build --no-cache webapp

# Stop and remove the old container
docker compose stop webapp
docker compose rm -f webapp

# Start with the new image
docker compose up -d webapp

# View logs to verify
docker compose logs -f webapp
```

#### Quick Restart (Only if no code changes)

If you only changed environment variables or want to restart without code changes:
```bash
docker compose restart webapp
```

**Note:** This will NOT pick up code changes - use the update script or manual rebuild instead.

### Running Locally (Without Docker)

1. Install dependencies: `pip install -r requirements.txt`
2. Start Ollama locally: `ollama serve`
3. Pull model: `ollama pull deepseek-r1:1.5b`
4. Set environment: `export OPENAI_BASE_URL=http://localhost:11434/v1`
5. Run app: `streamlit run app.py`

### Mock Mode

Enable mock mode in the UI sidebar to test without API calls. Useful for:
- UI development
- Testing without model inference
- Demonstrations without GPU/API access

## Research Background

This implementation is based on:
- **Du et al. (2023)**: "Improving Factuality and Reasoning in Language Models through Multiagent Debate"
- **Problem Addressed**: Sycophancy and disagreement collapse in peer-to-peer debates
- **Solution**: Mediated debate with impartial judge arbitrator

## License

This project is for educational/research purposes.

## Acknowledgments

- Ollama team for local LLM inference
- DeepSeek for the reasoning model
- Streamlit for the UI framework

