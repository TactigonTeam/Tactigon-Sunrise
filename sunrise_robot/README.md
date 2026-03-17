# MyCo Robot — Docker ROS2 Humble

Container Docker con **ROS2 Humble** e il repository [Comau/MyCo-ROS2](https://github.com/Comau/MyCo-ROS2) già compilato.

Supporta:
- **GUI** (RViz, Gazebo, Myco Control Panel) via X11 forwarding
- **Comunicazione con host Ubuntu 24.04 + ROS2 Jazzy** via `network_mode: host` + `ROS_DOMAIN_ID`

---

## Struttura

```
myco_docker/
├── Dockerfile            # Immagine ROS2 Humble + MyCo buildato
├── docker-compose.yml    # Servizio con rete host + X11
├── ros_entrypoint.sh     # Entrypoint (source setup + env)
├── build.sh              # Builda l'immagine
├── run.sh                # Avvia il container
├── shell.sh              # Shell interattiva nel container
└── launch.sh             # Helper per i launch file MyCo
```

---

## Requisiti sull'host

```bash
# Docker + Compose plugin
sudo apt install docker.io docker-compose-plugin
sudo usermod -aG docker $USER   # poi rilogga

# ROS2 Jazzy già installato (host Ubuntu 24.04)
```

---

## 1 — Build

```bash
chmod +x *.sh
./build.sh
```

La build clona il repo, installa tutte le dipendenze e fa `colcon build`.  
Ci vogliono ~10–20 min alla prima esecuzione.

---

## 2 — Avvio

```bash
./run.sh
```

Il container parte in background con:
- rete condivisa con l'host (`network_mode: host`)
- X11 forwarding attivo

---

## 3 — GUI (RViz / Gazebo / Control Panel)

```bash
# Simulazione Gazebo + RViz (modello default: myco_3_5_950mm)
./launch.sh sim

# Myco Control Panel
./launch.sh gui

# Basic API
./launch.sh api

# Cambiare modello robot:
MODEL=myco_5_800mm ./launch.sh sim
```

Modelli disponibili:
| Variabile MODEL | Robot |
|---|---|
| `myco_3_590mm` | MyCo 3 – 590 mm |
| `myco_3_5_950mm` | MyCo 3.5 – 950 mm *(default)* |
| `myco_5_800mm` | MyCo 5 – 800 mm |
| `myco_8_1300mm` | MyCo 8 – 1300 mm |
| `myco_10_1000mm` | MyCo 10 – 1000 mm |
| `myco_15_1300mm` | MyCo 15 – 1300 mm |

---

## 4 — Comunicazione con ROS2 Jazzy sull'host

Il container usa `network_mode: host` + `ROS_DOMAIN_ID=42`.  
Sul tuo terminale host **Jazzy** basta impostare lo stesso domain ID:

```bash
export ROS_DOMAIN_ID=42

# Verifica: dovresti vedere i topic del container
ros2 topic list
ros2 node list
```

> **Nota:** Jazzy e Humble usano entrambi DDS (FastDDS di default).  
> La comunicazione cross-version funziona per messaggi standard (`std_msgs`, `sensor_msgs`, `geometry_msgs`, ecc.).  
> I messaggi custom di MyCo (`myco_robot_msgs`) devono essere compilati anche sull'host Jazzy se vuoi usarli da lì.

### Compilare myco_robot_msgs su host Jazzy (opzionale)

```bash
mkdir -p ~/jazzy_myco_ws/src
cd ~/jazzy_myco_ws/src
git clone https://github.com/Comau/MyCo-ROS2.git --depth=1
cd ..
# Compila solo i messaggi
colcon build --packages-select myco_robot_msgs
source install/setup.bash
```

---

## 5 — Hardware reale (EtherCAT)

Per usare il robot fisico:

1. Copia `myco_drivers.yaml` (fornito da Comau) in `./config/`  
2. Decommenta il volume `./config` in `docker-compose.yml`  
3. Imposta `privileged: true` e `network_mode: host` (già configurato)  
4. Avvia:

```bash
./run.sh
./launch.sh real
```

---

## Shell interattiva

```bash
./shell.sh
# oppure direttamente:
docker exec -it $(docker compose ps -q myco_ros2) bash
```

---

## Troubleshooting

| Problema | Soluzione |
|---|---|
| `cannot open display` | `xhost +local:docker` poi riprova |
| No topics visibili dall'host | `export ROS_DOMAIN_ID=42` sull'host |
| Gazebo lento / crash | Aggiungi `-e LIBGL_ALWAYS_SOFTWARE=1` in compose |
| Build fallisce su `soem_ros2` | Riprova, a volte è un problema di rete nel clone |