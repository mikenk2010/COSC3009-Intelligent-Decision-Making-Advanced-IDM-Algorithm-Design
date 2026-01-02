#!/bin/bash
# Comprehensive Debug and Fix Script for Multi-Agent Debate System

set -e

echo "=========================================="
echo "Docker Debug & Fix Script"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Step 1: Check Docker
echo -e "${BLUE}[STEP 1] Checking Docker...${NC}"
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker is running${NC}"
    docker --version
    docker compose version
else
    echo -e "${RED}✗ Docker is NOT running${NC}"
    echo ""
    echo "Please start Docker Desktop and run this script again."
    exit 1
fi
echo ""

# Step 2: Clean up any existing containers
echo -e "${BLUE}[STEP 2] Cleaning up existing containers...${NC}"
docker compose down -v 2>/dev/null || true
docker rm -f ollama-server debate-webapp 2>/dev/null || true
echo -e "${GREEN}✓ Cleanup complete${NC}"
echo ""

# Step 3: Check ports
echo -e "${BLUE}[STEP 3] Checking if ports are available...${NC}"
if lsof -i :11434 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Port 11434 is in use${NC}"
    lsof -i :11434
    read -p "Kill the process? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti :11434 | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✓ Port 11434 freed${NC}"
    fi
else
    echo -e "${GREEN}✓ Port 11434 is available${NC}"
fi

if lsof -i :8501 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Port 8501 is in use${NC}"
    lsof -i :8501
    read -p "Kill the process? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti :8501 | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✓ Port 8501 freed${NC}"
    fi
else
    echo -e "${GREEN}✓ Port 8501 is available${NC}"
fi
echo ""

# Step 4: Validate docker-compose.yml
echo -e "${BLUE}[STEP 4] Validating docker-compose.yml...${NC}"
if docker compose config > /dev/null 2>&1; then
    echo -e "${GREEN}✓ docker-compose.yml is valid${NC}"
else
    echo -e "${RED}✗ docker-compose.yml has errors:${NC}"
    docker compose config
    exit 1
fi
echo ""

# Step 5: Start Ollama (simplified - no custom command)
echo -e "${BLUE}[STEP 5] Starting Ollama service...${NC}"
echo "Starting with simplified configuration..."

# Create a temporary simplified docker-compose for Ollama
cat > docker-compose.ollama.yml << 'EOF'
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama-server
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"

volumes:
  ollama_data:
    driver: local
EOF

docker compose -f docker-compose.ollama.yml up -d ollama
echo -e "${GREEN}✓ Ollama container started${NC}"
echo ""

# Step 6: Wait for Ollama to be ready
echo -e "${BLUE}[STEP 6] Waiting for Ollama to be ready...${NC}"
echo "This may take 10-30 seconds..."
COUNTER=0
MAX_WAIT=60
while [ $COUNTER -lt $MAX_WAIT ]; do
    if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama is ready!${NC}"
        break
    fi
    COUNTER=$((COUNTER + 1))
    echo -n "."
    sleep 1
done
echo ""

if [ $COUNTER -eq $MAX_WAIT ]; then
    echo -e "${RED}✗ Ollama did not become ready${NC}"
    echo "Checking logs..."
    docker compose -f docker-compose.ollama.yml logs ollama | tail -20
    exit 1
fi

# Step 7: Pull the model
echo -e "${BLUE}[STEP 7] Pulling deepseek-r1:1.5b model...${NC}"
echo "This will take 2-5 minutes on first run..."
docker exec ollama-server ollama pull deepseek-r1:1.5b
echo -e "${GREEN}✓ Model pulled successfully${NC}"
echo ""

# Step 8: Verify model
echo -e "${BLUE}[STEP 8] Verifying model...${NC}"
docker exec ollama-server ollama list
echo ""

# Step 9: Start webapp
echo -e "${BLUE}[STEP 9] Starting webapp service...${NC}"
docker compose up -d --build webapp
echo -e "${GREEN}✓ Webapp container started${NC}"
echo ""

# Step 10: Wait for webapp
echo -e "${BLUE}[STEP 10] Waiting for webapp to be ready...${NC}"
sleep 5
COUNTER=0
MAX_WAIT=30
while [ $COUNTER -lt $MAX_WAIT ]; do
    if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Webapp is ready!${NC}"
        break
    fi
    COUNTER=$((COUNTER + 1))
    echo -n "."
    sleep 1
done
echo ""

# Step 11: Final status
echo ""
echo "=========================================="
echo -e "${GREEN}STATUS CHECK${NC}"
echo "=========================================="
docker compose ps
echo ""

echo "=========================================="
echo -e "${GREEN}SUCCESS!${NC}"
echo "=========================================="
echo ""
echo "Services are running:"
echo "  - Ollama: http://localhost:11434"
echo "  - Webapp: http://localhost:8501"
echo ""
echo "View logs:"
echo "  docker compose logs -f ollama"
echo "  docker compose logs -f webapp"
echo ""
echo "Access the UI:"
echo "  Open http://localhost:8501 in your browser"
echo ""

