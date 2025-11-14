FROM python:3.12-slim


RUN apt-get update && apt-get install -y \
    bluetooth \
    bluez \
    libbluetooth-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

WORKDIR /app

COPY . /app

RUN pip install \
    flask==3.0.3 \
    gevent==24.2.1 \
    paho-mqtt
    


EXPOSE 5123

CMD ["python", "main.py"]
