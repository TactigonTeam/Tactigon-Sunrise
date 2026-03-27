#!/bin/bash
# ============================================================
#  COMAU ROS2 Driver – Launcher
#  Gestisce il container Docker e le operazioni sul robot
# ============================================================

xhost +local:docker

DRIVER_CONTAINER_NAME="comau_ros2"
CONTAINER_SIM_NAME="comau_ros2_sim"
SPEECH_CONTAINER_NAME="tactigon_speech_socket"
IMAGE_NAME="comau_ros2_driver:humble"
ROBOT_TYPE="racer7-14"

# ── Colori ────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ── Utility ───────────────────────────────────────────────────
print_header() {
    echo -e "\n${BOLD}${CYAN}╔══════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${CYAN}║     COMAU ROS2 Driver – Launcher     ║${NC}"
    echo -e "${BOLD}${CYAN}║          Robot: ${ROBOT_TYPE}           ║${NC}"
    echo -e "${BOLD}${CYAN}╚══════════════════════════════════════╝${NC}\n"
}

container_running() {
    docker ps --format '{{.Names}}' | grep -q "^${1}$"
}

container_exists() {
    docker ps -a --format '{{.Names}}' | grep -q "^${1}$"
}

show_status() {
    echo -e "${BOLD}Stato containers:${NC}"
    if container_running "${DRIVER_CONTAINER_NAME}"; then
        echo -e "  ${GREEN}● RUNNING${NC} – ${DRIVER_CONTAINER_NAME} (robot reale)"
    elif container_exists "${DRIVER_CONTAINER_NAME}"; then
        echo -e "  ${RED}● STOPPED${NC} – ${DRIVER_CONTAINER_NAME}"
    else
        echo -e "  ${RED}● NON ESISTE${NC} – ${DRIVER_CONTAINER_NAME}"
    fi
    if container_running "${SPEECH_CONTAINER_NAME}"; then
        echo -e "  ${GREEN}● RUNNING${NC} – ${SPEECH_CONTAINER_NAME}"
    elif container_exists "${SPEECH_CONTAINER_NAME}"; then
        echo -e "  ${RED}● STOPPED${NC} – ${SPEECH_CONTAINER_NAME}"
    else
        echo -e "  ${RED}● NON ESISTE${NC} – ${SPEECH_CONTAINER_NAME}"
    fi
    echo ""
}

# ── Gestione container reale ──────────────────────────────────

build_image() {
    echo -e "${YELLOW}🔨  Build dell'immagine Docker (può richiedere diversi minuti)...${NC}"
    docker compose build
    echo -e "${GREEN}✔  Build completata.${NC}"
}

start_driver() {
    echo -e "${YELLOW}▶  Avvio driver COMAU (robot reale)...${NC}"
    if container_running "${DRIVER_CONTAINER_NAME}"; then
        echo -e "${GREEN}✔  Il container è già in esecuzione.${NC}"
        return 0
    fi
    docker compose up -d comau_driver
    echo -e "${GREEN}✔  Container avviato.${NC}"
}

stop_driver() {
    echo -e "${YELLOW}■  Arresto driver...${NC}"
    docker compose stop comau_driver
    docker compose rm -f comau_driver
    echo -e "${GREEN}✔  Container fermato.${NC}"
}

start_speech() {
    echo -e "${YELLOW}▶  Avvio speech${NC}"
    if container_running "${SPEECH_CONTAINER_NAME}"; then
        echo -e "${GREEN}✔  Il container è già in esecuzione.${NC}"
        return 0
    fi
    docker compose up -d speech
    echo -e "${GREEN}✔  Container avviato.${NC}"
}

stop_speech() {
    echo -e "${YELLOW}■  Arresto speech...${NC}"
    docker compose stop speech
    docker compose rm -f speech
    echo -e "${GREEN}✔  Container fermato.${NC}"
}

open_connection() {
    echo -e "${YELLOW}🔌  Apertura connessione TCP/IP con il robot...${NC}"
    if ! container_running "${DRIVER_CONTAINER_NAME}"; then
        echo -e "${RED}✖  Container non in esecuzione. Avvialo con l'opzione 2.${NC}"
        return 1
    fi
    docker exec "${DRIVER_CONTAINER_NAME}" bash -c \
        "source /opt/vulcanexus/humble/setup.bash && \
         source /ros2_humble/install/setup.bash && \
         ros2 service call /tcpip_conn_manager comau_msgs/srv/OpenConnection \
         \"open_connection: true\""
}

close_connection() {
    echo -e "${YELLOW}🔌  Chiusura connessione TCP/IP con il robot...${NC}"
    if ! container_running; then
        echo -e "${RED}✖  Il container non è in esecuzione.${NC}"
        return 1
    fi
    docker exec "${DRIVER_CONTAINER_NAME}" bash -c \
        "source /opt/vulcanexus/humble/setup.bash && \
         source /ros2_humble/install/setup.bash && \
         ros2 service call /tcpip_conn_manager comau_msgs/srv/OpenConnection \
         \"open_connection: false\""
}

read_robot_status() {
    echo -e "${YELLOW}📡  Lettura stato robot (Ctrl+C per uscire)...${NC}"
    if ! container_running "${DRIVER_CONTAINER_NAME}"; then
        echo -e "${RED}✖  Container non in esecuzione. Avvialo con l'opzione 2.${NC}"
        return 1
    fi
    docker exec -it "${DRIVER_CONTAINER_NAME}" bash -c \
        "source /opt/vulcanexus/humble/setup.bash && \
         source /ros2_humble/install/setup.bash && \
         ros2 topic echo /robot_status"
}

start_joint_gui() {
    echo -e "${YELLOW}🎮  Avvio joint_state_publisher_gui...${NC}"
    docker exec -it "${DRIVER_CONTAINER_NAME}" bash -c "
        source /opt/vulcanexus/humble/setup.bash && \
        source /ros2_humble/install/setup.bash && \
        ros2 run joint_state_publisher_gui joint_state_publisher_gui
    "
}

show_logs() {
    docker logs -f "{{.Names}}" | grep -q "^${1}$"
}

open_shell() {
    docker exec -it "{{.Names}}" bash | grep -q "^${1}$"
}

# ── Menu principale ───────────────────────────────────────────
while true; do
    print_header
    show_status

    echo -e "${BOLD}  Gestione immagine${NC}"
    echo "   1) Build immagine Docker"
    echo ""
    echo -e "${BOLD}  Robot reale${NC}"
    echo "   2) Avvia driver (robot reale)"
    echo "   3) Ferma driver"
    echo "   4) Apri connessione TCP/IP"
    echo "   5) Chiudi connessione TCP/IP"
    echo "   6) Leggi /robot_status"
    echo ""
    echo -e "${BOLD}  TSkin${NC}"
    echo "   7) Avvia Speech"
    echo "   8) Ferma Speech"
    echo ""
    # echo -e "${BOLD}  Debug${NC}"
    # echo "   9) Log driver container"
    # echo "   10) Shell driver container"
    # echo "   11) Log driver container"
    # echo "   12) Shell driver container"
    echo ""
    echo "   0) Esci"
    echo ""
    echo -n "  Scelta: "
    read -r choice

    case $choice in
        1) build_image ;;
        2) start_driver ;;
        3) stop_driver ;;
        4) open_connection ;;
        5) close_connection ;;
        6) read_robot_status ;;
        7) start_speech ;;
        8) stop_speech ;;
        # 9) show_logs "${DRIVER_CONTAINER_NAME}";;
        # 10) open_shell "${DRIVER_CONTAINER_NAME}";;
        # 11) show_logs "${SPEECH_CONTAINER_NAME}";;
        # 12) open_shell "${SPEECH_CONTAINER_NAME}";;
        0) echo -e "\n${GREEN}Arrivederci!${NC}\n"; exit 0 ;;
        *) echo -e "${RED}Scelta non valida.${NC}" ;;
    esac

    echo -e "\n${CYAN}Premi INVIO per tornare al menu...${NC}"
    read -r
done