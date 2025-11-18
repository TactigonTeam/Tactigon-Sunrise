FROM ros:jazzy-ros-core

# Env per evitare blocchi con apt
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Installazione dipendenze di sistema
RUN apt-get update && apt-get install -y \
    python3-pip \
    iproute2 \
    net-tools \
    bash \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY ./config/sunrise_app/fastdds.xml /root/fastdds.xml
ENV FASTRTPS_DEFAULT_PROFILES_FILE=/root/fastdds.xml
ENV ROS_DOMAIN_ID=0

# Directory dell'app
WORKDIR /app

# Copia del codice
COPY ./sunrise_app /app/sunrise_app
COPY ./sunrise_app.py /app/sunrise_app.py

# Volume per persistenza dati
VOLUME ["/data"]

RUN mkdir -p /data/config
COPY ./config/sunrise_app /data/config

# Installazione dipendenze Python
RUN pip install \
    flask==3.0.3 \
    flask-socketio==5.5.1 \
    gevent==24.2.1 \
    gevent-websocket==0.10.1 \
    requests \
    paho-mqtt

# Porta esposta
EXPOSE 5123

# Comando di avvio
CMD ["python3", "sunrise_app.py"]
