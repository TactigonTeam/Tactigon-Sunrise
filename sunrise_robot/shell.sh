#!/usr/bin/env bash
# ============================================================
#  shell.sh  —  Apre una bash nel container in esecuzione
# ============================================================
set -e

CONTAINER=$(docker compose ps -q myco_ros2 2>/dev/null | head -1)

if [ -z "$CONTAINER" ]; then
    echo "⚠️  Container non in esecuzione. Avvialo prima con: ./run.sh"
    exit 1
fi

echo "🐚 Accesso shell → container MyCo ROS2 Humble"
docker exec -it "$CONTAINER" bash