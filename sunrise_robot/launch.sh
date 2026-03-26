#!/bin/bash
# ============================================================
#  COMAU ROS2 Driver – Launcher
#  Gestisce il container Docker e le operazioni sul robot
# ============================================================

xhost +local:docker

CONTAINER_NAME="comau_ros2"
CONTAINER_SIM_NAME="comau_ros2_sim"
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
    echo -e "${BOLD}Stato container:${NC}"
    if container_running "${CONTAINER_NAME}"; then
        echo -e "  ${GREEN}● RUNNING${NC} – ${CONTAINER_NAME} (robot reale)"
    elif container_exists "${CONTAINER_NAME}"; then
        echo -e "  ${RED}● STOPPED${NC} – ${CONTAINER_NAME}"
    else
        echo -e "  ${RED}● NON ESISTE${NC} – ${CONTAINER_NAME}"
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
    if container_running "${CONTAINER_NAME}"; then
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

open_connection() {
    echo -e "${YELLOW}🔌  Apertura connessione TCP/IP con il robot...${NC}"
    if ! container_running "${CONTAINER_NAME}"; then
        echo -e "${RED}✖  Container non in esecuzione. Avvialo con l'opzione 2.${NC}"
        return 1
    fi
    docker exec "${CONTAINER_NAME}" bash -c \
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
    docker exec "${CONTAINER_NAME}" bash -c \
        "source /opt/vulcanexus/humble/setup.bash && \
         source /ros2_humble/install/setup.bash && \
         ros2 service call /tcpip_conn_manager comau_msgs/srv/OpenConnection \
         \"open_connection: false\""
}

read_robot_status() {
    echo -e "${YELLOW}📡  Lettura stato robot (Ctrl+C per uscire)...${NC}"
    if ! container_running "${CONTAINER_NAME}"; then
        echo -e "${RED}✖  Container non in esecuzione. Avvialo con l'opzione 2.${NC}"
        return 1
    fi
    docker exec -it "${CONTAINER_NAME}" bash -c \
        "source /opt/vulcanexus/humble/setup.bash && \
         source /ros2_humble/install/setup.bash && \
         ros2 topic echo /robot_status"
}

# ── Simulazione con RViz2 ─────────────────────────────────────
#
# Usa X11 forwarding: RViz2 gira nel container ma il display
# appare sull'host Ubuntu 24.04 nativamente.
#
# Il launch file view_racer7-14.launch.py avvia:
#   - robot_state_publisher  (pubblica /tf dal URDF)
#   - joint_state_publisher  (pubblica /joint_states a zero)
#   - rviz2                  (visualizzazione 3D)
#
# Il topic /joint_states è lo stesso del robot reale:
# puoi usare l'opzione 10 per pubblicare posizioni di test,
# oppure collegare il robot reale e vedere lo stesso topic.

start_simulation() {
    echo -e "${YELLOW}🤖  Avvio simulazione racer7-14 con RViz2...${NC}"

    if container_running "${CONTAINER_SIM_NAME}"; then
        echo -e "${GREEN}✔  Simulazione già in esecuzione.${NC}"
        return 0
    fi

    if ! docker image inspect "${IMAGE_NAME}" &>/dev/null; then
        echo -e "${RED}✖  Immagine ${IMAGE_NAME} non trovata. Esegui prima la Build (opzione 1).${NC}"
        return 1
    fi

    # Abilita accesso X11 dall'host al container
    echo -e "${CYAN}   Configurazione X11 forwarding...${NC}"
    xhost +local:docker 2>/dev/null || {
        echo -e "${RED}✖  xhost non trovato. Installa: sudo apt install x11-xserver-utils${NC}"
        return 1
    }

    echo -e "${CYAN}   Avvio container con view_racer7-14.launch.py...${NC}"
    echo -e "${CYAN}   RViz2 apparirà a breve sul tuo desktop.${NC}\n"

    docker compose --profile sim up -d comau_viz

    sleep 3

    if container_running "${CONTAINER_SIM_NAME}"; then
        echo -e "${GREEN}✔  Simulazione avviata! RViz2 dovrebbe apparire sul desktop.${NC}"
        echo -e "${CYAN}   Se RViz2 non appare, controlla i log con l'opzione 7.${NC}"
        echo -e ""
        echo -e "${BOLD}  Topic attivi:${NC}"
        echo -e "  ${CYAN}/joint_states${NC}      → posizione dei joint (pubblica qui per muovere)"
        echo -e "  ${CYAN}/robot_description${NC} → URDF del racer7-14"
        echo -e "  ${CYAN}/tf  /tf_static${NC}    → trasformazioni cinematica"
        echo -e ""
        echo -e "${BOLD}  Usa l'opzione 10 per pubblicare un movimento di test.${NC}"
    else
        echo -e "${RED}✖  Il container si è fermato. Log:${NC}"
        docker logs "${CONTAINER_SIM_NAME}" 2>&1 | tail -30
        docker compose --profile sim rm -f comau_viz 2>/dev/null
    fi
}

stop_simulation() {
    echo -e "${YELLOW}■  Arresto simulazione...${NC}"
    docker compose --profile sim stop comau_viz
    docker compose --profile sim rm -f comau_viz
    # Revoca accesso X11
    xhost -local:docker 2>/dev/null
    echo -e "${GREEN}✔  Simulazione fermata.${NC}"
}

# Pubblica una sequenza di joint_states per vedere il robot muoversi in RViz2.
# Funziona sia con la simulazione che con il robot reale connesso —
# stesso topic, stessi nomi di joint dall'URDF racer7-14.
publish_test_motion() {
    echo -e "${YELLOW}🦾  Pubblicazione movimento test su /joint_states...${NC}"

    # Usa qualunque container sia attivo
    local target=""
    if container_running "${CONTAINER_SIM_NAME}"; then
        target="${CONTAINER_SIM_NAME}"
        echo -e "${CYAN}   Target: simulazione${NC}"
    elif container_running "${CONTAINER_NAME}"; then
        target="${CONTAINER_NAME}"
        echo -e "${CYAN}   Target: robot reale${NC}"
    else
        echo -e "${RED}✖  Nessun container attivo. Avvia la simulazione (opz. 9) o il driver (opz. 2).${NC}"
        return 1
    fi

    echo -e "${CYAN}   Sequenza: HOME → POSE1 → POSE2 → HOME (valori in radianti, nei limiti URDF)${NC}"
    echo -e "${CYAN}   Joint: joint_1..joint_6${NC}\n"

    docker exec -it "${target}" bash -c '
        source /opt/vulcanexus/humble/setup.bash
        source /ros2_humble/install/setup.bash

        pub_joints() {
            local label=$1; shift
            local positions="[$1, $2, $3, $4, $5, $6]"
            echo "→ ${label}: ${positions} rad"
            ros2 topic pub --times 20 --rate 10 /joint_states \
                sensor_msgs/msg/JointState \
                "{
                    header: {stamp: {sec: 0, nanosec: 0}, frame_id: '"'"''"'"'},
                    name: ['"'"'joint_1'"'"','"'"'joint_2'"'"','"'"'joint_3'"'"','"'"'joint_4'"'"','"'"'joint_5'"'"','"'"'joint_6'"'"'],
                    position: ['"'"'$1'"'"', '"'"'$2'"'"', '"'"'$3'"'"', '"'"'$4'"'"', '"'"'$5'"'"', '"'"'$6'"'"'],
                    velocity: [],
                    effort: []
                }" > /dev/null 2>&1
            sleep 1
        }

        # HOME
        ros2 topic pub --times 20 --rate 10 /joint_states sensor_msgs/msg/JointState \
            "{header: {stamp: {sec: 0, nanosec: 0}, frame_id: '"'"''"'"'}, name: ['"'"'joint_1'"'"','"'"'joint_2'"'"','"'"'joint_3'"'"','"'"'joint_4'"'"','"'"'joint_5'"'"','"'"'joint_6'"'"'], position: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], velocity: [], effort: []}" \
            > /dev/null 2>&1
        echo "→ HOME:  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] rad"
        sleep 1

        # POSE 1 – nei limiti URDF: j1±2.88, j2[-1.48,2.70], j3[-2.93,0], j4±3.66, j5±2.35, j6±47
        ros2 topic pub --times 20 --rate 10 /joint_states sensor_msgs/msg/JointState \
            "{header: {stamp: {sec: 0, nanosec: 0}, frame_id: '"'"''"'"'}, name: ['"'"'joint_1'"'"','"'"'joint_2'"'"','"'"'joint_3'"'"','"'"'joint_4'"'"','"'"'joint_5'"'"','"'"'joint_6'"'"'], position: [0.5, 0.8, -0.8, 0.5, 0.5, 1.0], velocity: [], effort: []}" \
            > /dev/null 2>&1
        echo "→ POSE1: [0.5, 0.8, -0.8, 0.5, 0.5, 1.0] rad"
        sleep 1

        # POSE 2
        ros2 topic pub --times 20 --rate 10 /joint_states sensor_msgs/msg/JointState \
            "{header: {stamp: {sec: 0, nanosec: 0}, frame_id: '"'"''"'"'}, name: ['"'"'joint_1'"'"','"'"'joint_2'"'"','"'"'joint_3'"'"','"'"'joint_4'"'"','"'"'joint_5'"'"','"'"'joint_6'"'"'], position: [-0.8, 1.2, -1.5, -0.8, 1.0, -1.5], velocity: [], effort: []}" \
            > /dev/null 2>&1
        echo "→ POSE2: [-0.8, 1.2, -1.5, -0.8, 1.0, -1.5] rad"
        sleep 1

        # Torna HOME
        ros2 topic pub --times 20 --rate 10 /joint_states sensor_msgs/msg/JointState \
            "{header: {stamp: {sec: 0, nanosec: 0}, frame_id: '"'"''"'"'}, name: ['"'"'joint_1'"'"','"'"'joint_2'"'"','"'"'joint_3'"'"','"'"'joint_4'"'"','"'"'joint_5'"'"','"'"'joint_6'"'"'], position: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], velocity: [], effort: []}" \
            > /dev/null 2>&1
        echo "→ HOME:  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] rad"

        echo -e "\n✔  Sequenza completata."
    '
}

start_joint_gui() {
    echo -e "${YELLOW}🎮  Avvio joint_state_publisher_gui...${NC}"

    local target=""
    if container_running "${CONTAINER_SIM_NAME}"; then
        target="${CONTAINER_SIM_NAME}"
        echo -e "${CYAN}   Target: simulazione${NC}"
    elif container_running "${CONTAINER_NAME}"; then
        target="${CONTAINER_NAME}"
        echo -e "${CYAN}   Target: robot reale${NC}"
    else
        echo -e "${RED}✖  Nessun container attivo.${NC}"
        return 1
    fi

    docker exec -it "${target}" bash -c "
        source /opt/vulcanexus/humble/setup.bash && \
        source /ros2_humble/install/setup.bash && \
        ros2 run joint_state_publisher_gui joint_state_publisher_gui
    "
}

show_logs() {
    local target="${CONTAINER_NAME}"
    container_running "${CONTAINER_SIM_NAME}" && ! container_running "${CONTAINER_NAME}" \
        && target="${CONTAINER_SIM_NAME}"
    echo -e "${YELLOW}📋  Log di '${target}' (Ctrl+C per uscire)...${NC}"
    docker logs -f "${target}"
}

open_shell() {
    local target="${CONTAINER_NAME}"
    if ! container_running "${CONTAINER_NAME}" && container_running "${CONTAINER_SIM_NAME}"; then
        target="${CONTAINER_SIM_NAME}"
    fi
    if ! container_running "${target}"; then
        echo -e "${RED}✖  Nessun container in esecuzione.${NC}"
        return 1
    fi
    echo -e "${YELLOW}🐚  Shell in '${target}'...${NC}"
    docker exec -it "${target}" bash
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
    echo -e "${BOLD}  Simulazione (view_racer7-14.launch.py + RViz2)${NC}"
    echo "   7) Avvia simulazione  → apre RViz2 sul desktop"
    echo "   8) Pubblica movimento test su /joint_states"
    echo "   9) Avvia GUI"
    echo "   10) Ferma simulazione"
    echo ""
    echo -e "${BOLD}  Debug${NC}"
    echo "   11) Log container attivo"
    echo "   12) Shell nel container attivo"
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
        7) start_simulation ;;
        8) publish_test_motion ;;
        9) start_joint_gui ;;
        10) stop_simulation ;;
        11) show_logs ;;
        12) open_shell ;;
        0) echo -e "\n${GREEN}Arrivederci!${NC}\n"; exit 0 ;;
        *) echo -e "${RED}Scelta non valida.${NC}" ;;
    esac

    echo -e "\n${CYAN}Premi INVIO per tornare al menu...${NC}"
    read -r
done