#!/bin/bash

# ============================================================
#  COMAU ROS2 Driver – Launcher
# ============================================================

xhost +local:docker

SUNRISE_CONTAINER="sunrise"
DRIVER_CONTAINER="sunrise-comau"
SPEECH_CONTAINER="tactigon-speech-socket"
FIWARE_CONTAINER="integration-service"
ORION_CONTAINER="fiware-orion"
GRAFANA_CONTAINER="sunrise-grafana"
DB_CONTAINER="sunrise-timescaledb"
MINTAKA_CONTAINER="sunrise-mintaka"

DRIVER_SETUP="source /opt/vulcanexus/humble/setup.bash && source /comau_driver/install/setup.bash"
SUNRISE_SETUP="source /opt/vulcanexus/jazzy/setup.bash && source /sunrise/install/setup.bash"

# ── Colors ──────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ── Generic helpers ─────────────────────────────────────────
print_header() {
    echo -e "\n${BOLD}${CYAN}=== Sunrise Launcher ===${NC}\n"
}

container_running() {
    docker ps --format '{{.Names}}' | grep -q "^$1$"
}

container_exists() {
    docker ps -a --format '{{.Names}}' | grep -q "^$1$"
}

docker_start() {
    local service=$1
    local name=$2

    echo -e "${YELLOW}Starting $name...${NC}"

    if container_running "$name"; then
        echo -e "${GREEN}Already running.${NC}"
        return
    fi

    docker compose up -d "$service"
    echo -e "${GREEN}Started.${NC}"
}

docker_stop() {
    local service=$1
    local name=$2

    echo -e "${YELLOW}Stopping $name...${NC}"

    docker compose stop "$service"
    docker compose rm -f "$service"

    echo -e "${GREEN}Stopped.${NC}"
}

docker_exec_ros() {
    local setup=$1
    local container=$2
    local cmd=$3

    docker exec -it "$container" bash -c "$setup && $cmd"
}

docker_start_fiware() {
    docker compose up -d "$GRAFANA_CONTAINER"
    docker compose up -d "$FIWARE_CONTAINER"
    docker compose up -d "$ORION_CONTAINER"
    docker compose up -d "$DB_CONTAINER"
    docker compose up -d "$MINTAKA_CONTAINER"
}

docker_stop_fiware() {
    docker compose stop "$GRAFANA_CONTAINER"
    docker compose stop "$FIWARE_CONTAINER"
    docker compose stop "$ORION_CONTAINER"
    docker compose stop "$DB_CONTAINER"
    docker compose stop "$MINTAKA_CONTAINER"
}

# ── ROS Commands ────────────────────────────────────────────

run_sunrise_node() {
    local node=$1
    local config=$2

    echo -e "${YELLOW}Running Sunrise node: $node${NC}"

    docker_exec_ros "$SUNRISE_SETUP" \
        "$SUNRISE_CONTAINER" \
        "ros2 run sunrise $node $config"
}

call_tcp_service() {
    local value=$1

    docker_exec_ros "$DRIVER_SETUP" \
        "$DRIVER_CONTAINER" \
        "ros2 service call /tcpip_conn_manager comau_msgs/srv/OpenConnection \"open_connection: $value\""
}

echo_robot_status() {
    docker_exec_ros "$DRIVER_SETUP" \
        "$DRIVER_CONTAINER" \
        "ros2 topic echo /robot_status"
}

start_joint_gui() {
    docker_exec_ros "$DRIVER_SETUP" \
        "$DRIVER_CONTAINER" \
        "ros2 run joint_state_publisher_gui joint_state_publisher_gui"
}

# ── Status ──────────────────────────────────────────────────

show_status() {
    echo -e "${BOLD}Container status:${NC}"

    for c in "$SUNRISE_CONTAINER" "$DRIVER_CONTAINER" "$SPEECH_CONTAINER" "$FIWARE_CONTAINER" "$ORION_CONTAINER" "$GRAFANA_CONTAINER" "$DB_CONTAINER" "$MINTAKA_CONTAINER"; do
        if container_running "$c"; then
            echo -e "  ${GREEN}● RUNNING${NC} - $c"
        elif container_exists "$c"; then
            echo -e "  ${RED}● STOPPED${NC} - $c"
        else
            echo -e "  ${RED}● NOT EXISTING${NC} - $c"
        fi
    done

    echo ""
}

# ── Menu ────────────────────────────────────────────────────
while true; do
    print_header
    show_status

    echo "1) Build containers"
    echo "2) Start Sunrise container"
    echo "3) Stop Sunrise container"
    echo "4) Start Driver"
    echo "5) Stop Driver"
    echo "6) Open TCP connection"
    echo "7) Close TCP connection"
    echo "8) Robot status"
    echo "9) Start Speech"
    echo "10) Stop Speech"
    echo "11) Start db+grafana+fiware"
    echo "12) Stop db+grafana+fiware"
    echo ""
    echo "20) Run sunrise_bridge"
    echo "21) Run mission_controller"
    echo "22) Run sunrise_comau"
    echo ""
    echo "0) Exit"

    read -rp "Choice: " choice

    case $choice in
        1) docker compose build ;;
        2) docker_start sunrise "$SUNRISE_CONTAINER" ;;
        3) docker_stop sunrise "$SUNRISE_CONTAINER" ;;
        4) docker_start comau_driver "$DRIVER_CONTAINER" ;;
        5) docker_stop comau_driver "$DRIVER_CONTAINER" ;;
        6) call_tcp_service true ;;
        7) call_tcp_service false ;;
        8) echo_robot_status ;;
        9) docker_start speech "$SPEECH_CONTAINER" ;;
        10) docker_stop speech "$SPEECH_CONTAINER" ;;
        11) docker_start_fiware ;;
        12) docker_stop_fiware ;;

        20) run_sunrise_node sunrise_bridge "./config/sunrise_bridge.json" ;;
        21) run_sunrise_node mission_controller "./config/mission_controller.json" ;;
        22) run_sunrise_node sunrise_comau "./config/sunrise_comau.json" ;;

        0) exit 0 ;;
        *) echo -e "${RED}Invalid choice${NC}" ;;
    esac

    read -rp "Press ENTER to continue..."
done