#!/bin/bash
# Update script - Rebuilds Docker image with latest code changes
# This ensures your code changes are reflected in the running container

set -e

echo "=========================================="
echo "Updating Docker with Latest Code"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Rebuilding webapp image with latest code...${NC}"
docker compose build --no-cache webapp

echo ""
echo -e "${YELLOW}Step 2: Stopping existing webapp container...${NC}"
docker compose stop webapp || true

echo ""
echo -e "${YELLOW}Step 3: Removing old webapp container...${NC}"
docker compose rm -f webapp || true

echo ""
echo -e "${YELLOW}Step 4: Starting webapp with new image...${NC}"
docker compose up -d webapp

echo ""
echo -e "${YELLOW}Step 5: Waiting for webapp to start (5 seconds)...${NC}"
sleep 5

echo ""
echo "=========================================="
echo -e "${GREEN}Update Complete!${NC}"
echo "=========================================="
echo ""
echo "Your latest code changes are now live!"
echo ""
echo "View logs:"
echo "  docker compose logs -f webapp"
echo ""
echo "Access the UI:"
echo "  http://localhost:8501"
echo ""
echo "=========================================="

