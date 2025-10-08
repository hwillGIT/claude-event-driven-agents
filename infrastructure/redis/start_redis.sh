#!/bin/bash
# Start Redis container with Docker Compose

echo "🚀 Starting Redis container..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop first."
    exit 1
fi

# Start Redis container
docker-compose up -d redis

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
for i in {1..10}; do
    if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is running and ready!"
        break
    fi
    sleep 1
done

# Show container status
echo ""
docker-compose ps

# Show connection info
echo ""
echo "📍 Redis Connection Info:"
echo "  Host: localhost"
echo "  Port: 6379"
echo "  Test: redis-cli ping"
echo ""
echo "🔧 Redis Commander (GUI):"
echo "  URL: http://localhost:8081"
echo "  Start: docker-compose up -d redis-commander"
echo ""
echo "🛑 Stop Redis:"
echo "  docker-compose down"