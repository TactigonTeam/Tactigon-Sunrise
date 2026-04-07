# Dockerfile per Integration Service con Dynamic ROS2 System Handle e FIWARE
FROM eprosima/vulcanexus:humble-base

# Impostazioni ambiente
ENV DEBIAN_FRONTEND=noninteractive
ENV IS_WORKSPACE=/is_ws

# Installazione dipendenze di base
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    cmake \
    python3-pip \
    python3-colcon-common-extensions \
    libyaml-cpp-dev \
    libboost-program-options-dev \
    libwebsocketpp-dev \
    libboost-system-dev \
    libboost-dev \
    libssl-dev \
    libcurlpp-dev \
    libasio-dev \
    libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Creazione workspace per Integration Service
RUN mkdir -p ${IS_WORKSPACE}/src

# Clone dei repository necessari
WORKDIR ${IS_WORKSPACE}/src

# Integration Service core
RUN git clone https://github.com/eProsima/Integration-Service.git is

# System Handles necessari
RUN git clone https://github.com/eProsima/ROS2-SH.git
RUN git clone https://github.com/eProsima/FIWARE-SH.git
RUN git clone https://github.com/eProsima/WebSocket-SH.git

# Build di Integration Service con Dynamic ROS2 mode
WORKDIR ${IS_WORKSPACE}
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && \
    colcon build --cmake-args \
    -DIS_ROS2_SH_MODE=DYNAMIC \
    -DBUILD_FASTDDS_EXAMPLES=OFF \
    --install-base /opt/is"

# Copia degli entrypoint scripts (CORREZIONE: usa COPY invece di echo)
COPY ros2_entrypoint.sh /ros2_entrypoint.sh
COPY is_entrypoint.sh /is_entrypoint.sh

# Rendi eseguibili gli entrypoint
RUN chmod +x /ros2_entrypoint.sh /is_entrypoint.sh

# Creazione directory per i file di configurazione
RUN mkdir -p /config

# Copia file di configurazione (opzionale, se esistono)
COPY config/*.yaml /config/

WORKDIR /config

# Entrypoint di default
ENTRYPOINT ["/ros2_entrypoint.sh"]
CMD ["bash"]