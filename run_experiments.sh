#!/bin/bash
# Script to run experimental data collection inside Docker

set -e

echo "=========================================="
echo "Running Experimental Data Collection"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if containers are running
if ! docker ps | grep -q "debate-webapp"; then
    echo "ERROR: debate-webapp container is not running."
    echo "Please start the containers first:"
    echo "  docker compose up -d"
    exit 1
fi

echo "Step 1: Copying experimental script to container..."
docker cp collect_experimental_data.py debate-webapp:/app/collect_experimental_data.py

echo ""
echo "Step 2: Running experiments (this will take 10-20 minutes)..."
echo ""

# Run the experiment inside the container
docker exec -it debate-webapp python collect_experimental_data.py

echo ""
echo "Step 3: Copying results back..."
docker cp debate-webapp:/app/experimental_results.json ./experimental_results.json

echo ""
echo "=========================================="
echo "✅ Experiments Complete!"
echo "=========================================="
echo ""
echo "Results saved to: experimental_results.json"
echo ""
echo "Next step: Update Assignment_Report.md with these results"
echo ""

