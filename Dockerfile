FROM python:3.11.2-slim


ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update && \
    apt-get install -y \
    chro