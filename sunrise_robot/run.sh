#!/usr/bin/env bash
# ============================================================
#  run.sh  —  Avvia il container MyCo con GUI + ROS2 host
# ============================================================
set -e

# Abilita X11 forwarding per il container
xhost +local:docker 2>/dev/null || true

echo "🚀 Avvio container myco_ros2 ..."
docker compose up -d

echo ""
echo "📌 Container avviato in background."
echo ""
echo "   Shell interattiva:   ./shell.sh"
echo "   Log live:            docker compose logs -f myco_ros2"
echo "   Stop:                docker compose down"
echo ""
echo "   HOST — imposta ROS_DOMAIN_ID per comunicare:"
echo "   $ export ROS_DOMAIN_ID=42"
echo "   $ ros2 topic list"