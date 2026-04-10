# Dockerfile per Integration Service con Dynamic ROS2 System Handle e FIWARE
FROM eprosima/vulcanexus:humble-base


ENV DEBIAN_FRONTEND=noninteractive
ENV IS_WORKSPACE=/is_ws


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

RUN mkdir -p ${IS_WORKSPACE}/src

WORKDIR ${IS_WORKSPACE}/src

RUN git clone https://github.com/eProsima/Integration-Service.git is 
RUN git clone https://github.com/eProsima/ROS2-SH.git
RUN git clone https://github.com/eProsima/FIWARE-SH.git
RUN git clone https://github.com/eProsima/WebSocket-SH.git

WORKDIR ${IS_WORKSPACE}
RUN /bin/bash -c "source /opt/vulcanexus/humble/setup.bash && \
    colcon build --merge-install --cmake-args \
    -DIS_ROS2_SH_MODE=DYNAMIC \
    -DIS_FIWARE_SH_MODE=NGSI_V2 \
    -DBUILD_FASTDDS_EXAMPLES=OFF \
    --install-base /opt/is"

COPY ros2_entrypoint.sh /ros2_entrypoint.sh
COPY is_entrypoint.sh /is_entrypoint.sh

ENV IS_PREFIX_PATH=/opt/is
ENV IS_ROS2_PREFIX_PATH=/opt/ros/humble

RUN chmod +x /ros2_entrypoint.sh /is_entrypoint.sh

RUN mkdir -p /config

COPY config/*.yaml /config/

WORKDIR /config

ENTRYPOINT ["/ros2_entrypoint.sh"]
CMD ["bash"]