#!/bin/bash
# Script to sync debate_history from Docker container to local filesystem
# Useful as a backup if volume mount isn't working or to sync existing history

set -e

echo "=========================================="
echo "Syncing Debate History from Docker"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if container is running
if ! docker ps | grep -q "debate-webapp"; then
    echo "ERROR: debate-webapp container is not running."
    echo "Please start the containers first:"
    echo "  docker compose up -d"
    exit 1
fi

# Create local directory if it doesn't exist
mkdir -p debate_history/standard
mkdir -p debate_history/mediated

echo "Step 1: Copying standard debate history..."
if docker exec debate-webapp test -d /app/debate_history/standard 2>/dev/null; then
    docker cp debate-webapp:/app/debate_history/standard/. ./debate_history/standard/ 2>/dev/null || echo "  No standard history found"
    STANDARD_COUNT=$(find debate_history/standard -name "*.json" -not -name "index.json" 2>/dev/null | wc -l | tr -d ' ')
    echo "  ✅ Standard history synced ($STANDARD_COUNT debates)"
else
    echo "  ⚠️  No standard history directory in container"
fi

echo ""
echo "Step 2: Copying mediated debate history..."
if docker exec debate-webapp test -d /app/debate_history/mediated 2>/dev/null; then
    docker cp debate-webapp:/app/debate_history/mediated/. ./debate_history/mediated/ 2>/dev/null || echo "  No mediated history found"
    MEDIATED_COUNT=$(find debate_history/mediated -name "*.json" -not -name "index.json" 2>/dev/null | wc -l | tr -d ' ')
    echo "  ✅ Mediated history synced ($MEDIATED_COUNT debates)"
else
    echo "  ⚠️  No mediated history directory in container"
fi

echo ""
echo "=========================================="
echo "✅ Sync Complete!"
echo "=========================================="
echo ""
echo "History files are now in:"
echo "  - debate_history/standard/"
echo "  - debate_history/mediated/"
echo ""
echo "Note: With volume mount in docker-compose.yml, future debates"
echo "      will automatically sync. This script is for syncing existing history."
echo ""

