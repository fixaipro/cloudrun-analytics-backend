# syntax=docker/dockerfile:1
FROM python:3.11-slim

# avoid interactive prompts
ARG DEBIAN_FRONTEND=noninteractive

# 1) Install OS‐level build tools + R + R dev headers + needed R libs + curl/xml2 for rpy2
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libffi-dev \
      wget \
      ca-certificates \
      r-base \
      r-base-dev \
      libcurl4-openssl-dev \
      libxml2-dev \
      default-jdk \
 && rm -rf /var/lib/apt/lists/*

# 2) Upgrade pip/tooling  
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 3) Copy & install Python deps  
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copy all your app code  
COPY . .

# 5) Expose port and run via gunicorn  
EXPOSE 8080
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "main:app"]
