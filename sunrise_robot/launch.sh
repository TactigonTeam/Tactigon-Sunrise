#!/bin/bash
# ============================================================
#  COMAU ROS2 Driver – Launcher
#  Gestisce il container Docker e le operazioni sul robot
# ============================================================

CONTAINER_NAME="comau_ros2"
IMAGE_NAME="comau_ros2_driver:humble"
ROBOT_TYPE="racer7-14"

# ── Colori ────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ── Utility ───────────────────────────────────────────────────
print_header() {
    echo -e "\n${BOLD}${CYAN}╔══════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${CYAN}║     COMAU ROS2 Driver – Launcher     ║${NC}"
    echo -e "${BOLD}${CYAN}║          Robot: ${ROBOT_TYPE}           ║${NC}"
    echo -e "${BOLD}${CYAN}╚══════════════════════════════════════╝${NC}\n"
}

container_running() {
    docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"
}

container_exists() {
    docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"
}

# ── Azioni ────────────────────────────────────────────────────

start_driver() {
    echo -e "${YELLOW}▶  Avvio del container e del driver COMAU...${NC}"
    if container_running; then
        echo -e "${GREEN}✔  Il container è già in esecuzione.${NC}"
    else
        docker compose up -d
        echo -e "${GREEN}✔  Container avviato. Attendi qualche secondo che il driver sia pronto.${NC}"
    fi
}

stop_driver() {
    echo -e "${YELLOW}■  Arresto del container...${NC}"
    docker compose down
    echo -e "${GREEN}✔  Container fermato.${NC}"
}

open_connection() {
    echo -e "${YELLOW}🔌  Apertura connessione TCP/IP con il robot...${NC}"
    if ! container_running; then
        echo -e "${RED}✖  Il container non è in esecuzione. Avvialo prima con l'opzione 1.${NC}"
        return 1
    fi
    docker exec "${CONTAINER_NAME}" bash -c \
        "source /opt/ros/humble/setup.bash && \
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
    docker exec "${CONTAINER_NAME}" bash -c \
        "source /opt/ros/humble/setup.bash && \
         source /ros2_humble/install/setup.bash && \
         ros2 service call /tcpip_conn_manager comau_msgs/srv/OpenConnection \
         \"open_connection: false\""
}

read_robot_status() {
    echo -e "${YELLOW}📡  Lettura stato robot (Ctrl+C per uscire)...${NC}"
    if ! container_running; then
        echo -e "${RED}✖  Il container non è in esecuzione. Avvialo prima con l'opzione 1.${NC}"
        return 1
    fi
    docker exec -it "${CONTAINER_NAME}" bash -c \
        "source /opt/ros/humble/setup.bash && \
         source /ros2_humble/install/setup.bash && \
         ros2 topic echo /robot_status"
}

show_logs() {
    echo -e "${YELLOW}📋  Log del driver (Ctrl+C per uscire)...${NC}"
    docker logs -f "${CONTAINER_NAME}"
}

open_shell() {
    echo -e "${YELLOW}🐚  Apertura shell interattiva nel container...${NC}"
    if ! container_running; then
        echo -e "${RED}✖  Il container non è in esecuzione.${NC}"
        return 1
    fi
    docker exec -it "${CONTAINER_NAME}" bash
}

build_image() {
    echo -e "${YELLOW}🔨  Build dell'immagine Docker (può richiedere diversi minuti)...${NC}"
    docker compose build
    echo -e "${GREEN}✔  Build completata.${NC}"
}

show_status() {
    echo -e "${BOLD}Stato container:${NC}"
    if container_running; then
        echo -e "  ${GREEN}● RUNNING${NC} – ${CONTAINER_NAME}"
    elif container_exists; then
        echo -e "  ${RED}● STOPPED${NC} – ${CONTAINER_NAME}"
    else
        echo -e "  ${RED}● NON ESISTE${NC} – immagine non ancora buildata o container rimosso."
    fi
    echo ""
}

# ── Menu principale ───────────────────────────────────────────
while true; do
    print_header
    show_status

    echo -e "${BOLD}  Gestione container${NC}"
    echo "  1) Build immagine Docker"
    echo "  2) Avvia il driver (start container)"
    echo "  3) Ferma il driver (stop container)"
    echo ""
    echo -e "${BOLD}  Operazioni robot${NC}"
    echo "  4) Apri connessione TCP/IP con il robot"
    echo "  5) Chiudi connessione TCP/IP con il robot"
    echo "  6) Leggi stato robot (/robot_status)"
    echo ""
    echo -e "${BOLD}  Debug${NC}"
    echo "  7) Mostra log del driver"
    echo "  8) Apri shell nel container"
    echo ""
    echo "  0) Esci"
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
        7) show_logs ;;
        8) open_shell ;;
        0) echo -e "\n${GREEN}Arrivederci!${NC}\n"; exit 0 ;;
        *) echo -e "${RED}Scelta non valida.${NC}" ;;
    esac

    echo -e "\n${CYAN}Premi INVIO per tornare al menu...${NC}"
    read -r
done