#!/bin/bash
set -e

source /opt/ros/humble/setup.bash
source /ros2_humble/install/setup.bash

USE_GUI=${USE_GUI:-false}

echo "[SIM] Cercando xacro per racer7-14..."
XACRO=$(find /ros2_humble/install -name 'racer7-14_robot.urdf.xacro' | head -1)

if [ -z "$XACRO" ]; then
    echo "[SIM] ERRORE: xacro non trovato"
    exit 1
fi

echo "[SIM] Generazione URDF..."
ROBOT_DESC=$(ros2 run xacro xacro "$XACRO")

echo "[SIM] Avvio robot_state_publisher..."
ros2 run robot_state_publisher robot_state_publisher \
    --ros-args -p robot_description:="$ROBOT_DESC" &

# 👇 SOLO se richiesto
if [ "$USE_GUI" = "true" ]; then
    echo "[SIM] Avvio joint_state_publisher_gui..."
    ros2 run joint_state_publisher_gui joint_state_publisher_gui &
else
    echo "[SIM] joint_state_publisher NON avviato (attendi publisher esterno)"
fi

sleep 2

echo "[SIM] Avvio RViz2..."
exec ros2 run rviz2 rviz2 -d /root/.rviz2/comau_racer7.rviz