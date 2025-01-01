# Use the Python 3.11 slim image as the base
FROM python:3.11.2-slim

# Set environment variables to disable interactive prompts and disable pip cache
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_CACHE_DIR=1

# Install dependencies for Chromium and its driver
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libgdk-pixbuf2.0-0 \
    libnss3 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libappindicator3-1 \
    libasound2 \
    libnspr4 \
    libxext6 \
    libxfixes3 \
    && rm -rf /var/lib/apt/lists/*

# Install ARM64-compatible Chromium
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb && \
    apt-get update && \
    apt-get install -y /tmp/chrome.deb && \
    rm /tmp/chrome.deb

# Download ARM64-compatible Chromium Driver (Ensure correct version for your setup)
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Set environment variables to point to Chromium and Chromedriver
ENV CHROME_BIN=/usr/bin/google-chrome-stable
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Copy the requirements.txt file into the container
COPY requirements.txt /app/requirements.txt

# Install Python dependencies from requirements.txt
RUN pip3 install -r /app/requirements.txt

# Copy the rest of your application code into the container
COPY . /app

# Set the working directory to /app
WORKDIR /app

# Expose the port Flask will run on
EXPOSE 80

# Command to run your application (Replace api_server.py with your actual entry point)
CMD ["python3", "api_server.py"]