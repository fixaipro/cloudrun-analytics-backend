# syntax=docker/dockerfile:1
FROM python:3.11-slim

# avoid warnings, set non-interactive
ARG DEBIAN_FRONTEND=noninteractive

# install OS deps for Python builds + R + R dev headers
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libffi-dev \
      wget \
      ca-certificates \
      r-base \
      r-base-dev \
 && rm -rf /var/lib/apt/lists/*

# ensure pip is up-to-date
RUN pip install --no-cache-dir --upgrade pip

# copy in and install Python deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy our application
COPY main.py .

# expose & run
EXPOSE 8080
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "main:app"]
