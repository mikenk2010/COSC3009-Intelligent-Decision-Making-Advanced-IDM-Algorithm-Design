#!/bin/bash
# Simple startup script - runs everything step by step

set -e

echo "=========================================="
echo "Starting Multi-Agent Debate System"
echo "=========================================="
echo ""

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "Step 1: Cleaning up..."
docker compose down -v 2>/dev/null || true
docker rm -f ollama-server debate-webapp 2>/dev/null || true
echo "✓ Cleanup done"
echo ""

echo "Step 2: Starting Ollama..."
docker compose up -d ollama
echo "✓ Ollama started"
echo ""

echo "Step 3: Waiting for Ollama to be ready (30 seconds)..."
sleep 30

echo "Step 4: Testing Ollama..."
if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✓ Ollama is ready!"
else
    echo "⚠ Ollama not ready yet, but continuing..."
fi
echo ""

echo "Step 5: Pulling model (this takes 2-5 minutes)..."
echo "You can watch progress with: docker compose logs -f ollama"
docker exec ollama-server ollama pull deepseek-r1:1.5b || {
    echo "⚠ Model pull had issues, but continuing..."
}
echo ""

echo "Step 6: Starting webapp..."
docker compose up -d --build webapp
echo "✓ Webapp started"
echo ""

echo "Step 7: Waiting for webapp (10 seconds)..."
sleep 10
echo ""

echo "=========================================="
echo "STATUS"
echo "=========================================="
docker compose ps
echo ""

echo "=========================================="
echo "SUCCESS!"
echo "=========================================="
echo ""
echo "Access the UI at: http://localhost:8501"
echo ""
echo "View logs:"
echo "  docker compose logs -f ollama"
echo "  docker compose logs -f webapp"
echo ""

