#********************************************************************************
# Copyright (c) 2025 Next Industries s.r.l.
#
# This program and the accompanying materials are made available under the
# terms of the Apache 2.0 which is available at http://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
#
# Project Name:
# Tactigon Soul - Shape
# 
# Release date: 30/09/2025
# Release version: 1.0
#
# Contributors:
# - Massimiliano Bellino
# - Stefano Barbareschi
#********************************************************************************/

FROM python:3.8-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir tactigon_speech_socket==5.5.0.2

COPY config.json /app/config.json
COPY deepspeech-0.9.3-models.tflite /app/deepspeech-0.9.3-models.tflite
COPY sunrise.scorer /app/sunrise.scorer

ENV TSS_ADDRESS=0.0.0.0
ENV TSS_PORT=50007
ENV TSS_CONFIG=config.json

CMD ["sh", "-c", "python3 -m tactigon_speech_socket -a $TSS_ADDRESS -p $TSS_PORT -c $TSS_CONFIG"]