#!/bin/bash
# Startup and Debug Script for Multi-Agent Debate System

set -e

echo "=========================================="
echo "Multi-Agent Debate System - Startup & Debug"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check if Docker is running
echo -e "${YELLOW}[1/5] Checking Docker status...${NC}"
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker is running${NC}"
else
    echo -e "${RED}✗ Docker is not running${NC}"
    echo ""
    echo "Please start Docker Desktop:"
    echo "  - macOS: Open Docker Desktop application"
    echo "  - Linux: sudo systemctl start docker"
    echo "  - Windows: Open Docker Desktop application"
    echo ""
    echo "Waiting for Docker to start..."
    while ! docker info > /dev/null 2>&1; do
        sleep 2
        echo -n "."
    done
    echo ""
    echo -e "${GREEN}✓ Docker is now running${NC}"
fi

# Step 2: Check Docker Compose
echo ""
echo -e "${YELLOW}[2/5] Checking Docker Compose...${NC}"
if docker compose version > /dev/null 2>&1; then
    DOCKER_COMPOSE_VERSION=$(docker compose version)
    echo -e "${GREEN}✓ Docker Compose: $DOCKER_COMPOSE_VERSION${NC}"
else
    echo -e "${RED}✗ Docker Compose not found${NC}"
    echo "Trying docker-compose (legacy)..."
    if docker-compose version > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Using legacy docker-compose${NC}"
        DOCKER_COMPOSE_CMD="docker-compose"
    else
        echo -e "${RED}✗ Docker Compose not available${NC}"
        exit 1
    fi
fi

# Use docker compose by default
DOCKER_COMPOSE_CMD=${DOCKER_COMPOSE_CMD:-"docker compose"}

# Step 3: Validate docker-compose.yml
echo ""
echo -e "${YELLOW}[3/5] Validating docker-compose.yml...${NC}"
if $DOCKER_COMPOSE_CMD config > /dev/null 2>&1; then
    echo -e "${GREEN}✓ docker-compose.yml is valid${NC}"
else
    echo -e "${RED}✗ docker-compose.yml has errors${NC}"
    echo "Errors:"
    $DOCKER_COMPOSE_CMD config 2>&1 | head -20
    exit 1
fi

# Step 4: Build and start services
echo ""
echo -e "${YELLOW}[4/5] Building and starting services...${NC}"
echo "This may take a few minutes on first run..."
$DOCKER_COMPOSE_CMD up -d --build

# Wait a moment for services to start
sleep 3

# Step 5: Check service status
echo ""
echo -e "${YELLOW}[5/5] Checking service status...${NC}"
$DOCKER_COMPOSE_CMD ps

echo ""
echo "=========================================="
echo -e "${GREEN}Services started!${NC}"
echo "=========================================="
echo ""
echo "Useful commands:"
echo ""
echo "  View all logs:"
echo "    $DOCKER_COMPOSE_CMD logs -f"
echo ""
echo "  View Ollama logs:"
echo "    $DOCKER_COMPOSE_CMD logs -f ollama"
echo ""
echo "  View Webapp logs:"
echo "    $DOCKER_COMPOSE_CMD logs -f webapp"
echo ""
echo "  Check service status:"
echo "    $DOCKER_COMPOSE_CMD ps"
echo ""
echo "  Stop services:"
echo "    $DOCKER_COMPOSE_CMD down"
echo ""
echo "  Pull the model (first time only):"
echo "    docker exec -it ollama-server ollama pull deepseek-r1:1.5b"
echo ""
echo "  Access the UI:"
echo "    http://localhost:8501"
echo ""
echo "=========================================="

