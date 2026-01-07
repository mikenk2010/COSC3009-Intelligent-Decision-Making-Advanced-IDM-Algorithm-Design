#!/bin/bash
# Diagnostic script to check Docker setup for experiments

echo "=========================================="
echo "Docker Setup Diagnostic"
echo "=========================================="
echo ""

# Check Docker installation
echo "1. Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo "   ✅ Docker command found: $(which docker)"
    docker --version
else
    echo "   ❌ Docker command not found"
    echo "   Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi
echo ""

# Check Docker daemon
echo "2. Checking Docker daemon..."
if docker info > /dev/null 2>&1; then
    echo "   ✅ Docker daemon is running"
    docker info | grep -i "server version" | head -1
else
    echo "   ❌ Docker daemon is not running"
    echo "   Please start Docker Desktop"
    exit 1
fi
echo ""

# Check containers
echo "3. Checking containers..."
ALL_CONTAINERS=$(docker ps -a --format '{{.Names}}' | grep -E "(debate-webapp|ollama-server)" || echo "")
if [ -z "$ALL_CONTAINERS" ]; then
    echo "   ⚠️  No debate containers found"
    echo "   Run: docker compose up -d"
else
    echo "   Found containers:"
    echo "$ALL_CONTAINERS" | while read container; do
        STATUS=$(docker ps --format '{{.Names}} {{.Status}}' | grep "^$container " || echo "$container (stopped)")
        echo "     - $STATUS"
    done
fi
echo ""

# Check if debate-webapp is running
echo "4. Checking debate-webapp container..."
if docker ps --format '{{.Names}}' | grep -q "debate-webapp"; then
    echo "   ✅ debate-webapp is running"
    CONTAINER_ID=$(docker ps --format '{{.ID}}' --filter "name=debate-webapp")
    echo "   Container ID: $CONTAINER_ID"
else
    echo "   ❌ debate-webapp is not running"
    echo "   Start it with: docker compose up -d"
fi
echo ""

# Check if experimental script exists
echo "5. Checking experimental script..."
if [ -f "collect_experimental_data.py" ]; then
    echo "   ✅ collect_experimental_data.py found"
    echo "   Size: $(wc -l < collect_experimental_data.py) lines"
else
    echo "   ❌ collect_experimental_data.py not found"
    echo "   Current directory: $(pwd)"
fi
echo ""

# Check if script can be copied
if docker ps --format '{{.Names}}' | grep -q "debate-webapp"; then
    echo "6. Testing file copy..."
    if docker cp collect_experimental_data.py debate-webapp:/tmp/test_copy.py 2>/dev/null; then
        echo "   ✅ File copy test successful"
        docker exec debate-webapp rm -f /tmp/test_copy.py
    else
        echo "   ❌ File copy test failed"
    fi
    echo ""
fi

echo "=========================================="
echo "Diagnostic Complete"
echo "=========================================="

