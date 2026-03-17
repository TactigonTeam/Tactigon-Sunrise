#!/usr/bin/env bash
# ============================================================
#  launch.sh  —  Helper per i launch file MyCo dentro Docker
#
#  Uso:
#    ./launch.sh sim       → Gazebo + RViz (simulazione)
#    ./launch.sh gui       → Myco Control Panel GUI
#    ./launch.sh api       → Basic API server
#    ./launch.sh real      → Hardware reale (richiede privileged)
#    ./launch.sh rviz      → Solo RViz
# ============================================================
set -e

# Assicura X11
xhost +local:docker 2>/dev/null || true

CONTAINER=$(docker compose ps -q myco_ros2 2>/dev/null | head -1)
if [ -z "$CONTAINER" ]; then
    echo "⚠️  Container non in esecuzione. Avvialo prima con: ./run.sh"
    exit 1
fi

# Modello di default (cambia in myco_3_590mm, myco_5_800mm, myco_10_1000mm, ecc.)
MODEL="${MODEL:-myco_3_5_950mm}"
PKG="${MODEL}_ros2_moveit2"

case "$1" in
    sim)
        echo "🤖 Avvio simulazione Gazebo + RViz ($MODEL)..."
        docker exec -it "$CONTAINER" bash -c \
          "source /ros2_ws/install/setup.bash && \
           ros2 launch ${PKG} ${MODEL}.launch.py"
        ;;
    api)
        echo "🔌 Avvio Basic API ($MODEL)..."
        docker exec -it "$CONTAINER" bash -c \
          "source /ros2_ws/install/setup.bash && \
           ros2 launch ${PKG} ${MODEL}_basic_api.launch.py"
        ;;
    gui)
        echo "🖥️  Avvio Myco Control Panel GUI..."
        docker exec -it "$CONTAINER" bash -c \
          "source /ros2_ws/install/setup.bash && \
           ros2 launch myco_basic_api fake_myco_gui.launch.py"
        ;;
    real)
        echo "⚙️  Avvio hardware reale ($MODEL) — richiede privileged=true in compose"
        docker exec -it "$CONTAINER" bash -c \
          "source /ros2_ws/install/setup.bash && \
           ros2 launch ${PKG} ${MODEL}_moveit.launch.py"
        ;;
    rviz)
        echo "👁️  Avvio solo RViz..."
        docker exec -it "$CONTAINER" bash -c \
          "source /ros2_ws/install/setup.bash && \
           ros2 launch ${PKG} ${MODEL}_moveit_rviz.launch.py"
        ;;
    *)
        echo "Uso: MODEL=myco_3_5_950mm ./launch.sh [sim|api|gui|real|rviz]"
        echo ""
        echo "  sim    → Gazebo + RViz (simulazione)"
        echo "  api    → Basic API server"
        echo "  gui    → Myco Control Panel"
        echo "  real   → Hardware EtherCAT reale"
        echo "  rviz   → Solo RViz con MoveIt"
        echo ""
        echo "Modelli disponibili:"
        echo "  myco_3_590mm | myco_3_5_950mm | myco_5_800mm"
        echo "  myco_8_1300mm | myco_10_1000mm | myco_15_1300mm"
        ;;
esac