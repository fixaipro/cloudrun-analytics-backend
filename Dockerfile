# syntax=docker/dockerfile:1
FROM python:3.11-slim

# avoid interactive prompts
ARG DEBIAN_FRONTEND=noninteractive

# 1) Install OS-level build tools + R + R dev headers
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libffi-dev \
      wget \
      ca-certificates \
      r-base \
      r-base-dev \
 && rm -rf /var/lib/apt/lists/*

# 2) Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# 3) Copy & install Python deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copy your app
COPY main.py .

# 5) Expose port and run via gunicorn
EXPOSE 8080
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "main:app"]
