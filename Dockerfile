FROM python:3.11.2-slim


ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update && \
    apt-get install -y \
    chromium chromium-driver \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY . /app
WORKDIR /app



EXPOSE 80

CMD ["python3", "api_server.py"]