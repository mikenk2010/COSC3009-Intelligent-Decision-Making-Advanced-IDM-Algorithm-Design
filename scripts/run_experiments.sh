#!/bin/bash
# Script to run experimental data collection inside Docker

set -e

echo "=========================================="
echo "Running Experimental Data Collection"
echo "=========================================="
echo ""

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker command not found. Please install Docker."
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Please start Docker Desktop."
    echo ""
    echo "On macOS:"
    echo "  1. Open Docker Desktop application"
    echo "  2. Wait for Docker to start (whale icon in menu bar should be steady)"
    echo "  3. Run this script again"
    exit 1
fi

# Check if containers are running
CONTAINER_RUNNING=$(docker ps --format '{{.Names}}' | grep -q "debate-webapp" && echo "yes" || echo "no")

if [ "$CONTAINER_RUNNING" != "yes" ]; then
    echo "ERROR: debate-webapp container is not running."
    echo ""
    echo "Please start the containers first:"
    echo "  cd $(pwd)"
    echo "  docker compose up -d"
    echo ""
    echo "Or if using docker-compose (older version):"
    echo "  docker-compose up -d"
    echo ""
    echo "To check container status:"
    echo "  docker ps -a | grep debate-webapp"
    exit 1
fi

echo "✅ Docker is running"
echo "✅ Container 'debate-webapp' is running"
echo ""

# Check if the experimental script exists
if [ ! -f "collect_experimental_data.py" ]; then
    echo "ERROR: collect_experimental_data.py not found in current directory."
    echo "Current directory: $(pwd)"
    exit 1
fi

# Check if file is already mounted as volume (docker-compose.yml mounts it)
# If mounted, we don't need to copy it
echo "Step 1: Checking if script is available in container..."
if docker exec debate-webapp test -f /app/collect_experimental_data.py 2>/dev/null; then
    echo "✅ Script already available in container (via volume mount)"
    echo "   No need to copy - file is mounted from docker-compose.yml"
else
    echo "⚠️  Script not found in container, attempting to copy..."
    docker cp collect_experimental_data.py debate-webapp:/app/collect_experimental_data.py
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to copy script to container."
        echo "Make sure the file is mounted in docker-compose.yml or copy it manually."
        exit 1
    fi
    echo "✅ Script copied successfully"
fi

echo ""
echo "Step 2: Running experiments (this will take 10-20 minutes)..."
echo ""

# Run the experiment inside the container
# Use -T instead of -it to avoid TTY allocation issues
if [ -t 0 ]; then
    # Interactive terminal available
    docker exec -it debate-webapp python collect_experimental_data.py
else
    # Non-interactive (e.g., from cron or script)
    docker exec debate-webapp python collect_experimental_data.py
fi

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Experiment script failed. Check the output above for details."
    exit 1
fi

echo ""
echo "Step 3: Copying results back..."
docker cp debate-webapp:/app/experimental_results.json ./experimental_results.json

if [ $? -ne 0 ]; then
    echo "WARNING: Failed to copy results file. It may not have been generated."
    echo "Check the container logs: docker logs debate-webapp"
    exit 1
fi

echo "✅ Results copied successfully"
echo ""
echo "=========================================="
echo "✅ Experiments Complete!"
echo "=========================================="
echo ""
echo "Results saved to: experimental_results.json"
echo ""
echo "Next step: Update Assignment_Report.md with these results"
echo ""

