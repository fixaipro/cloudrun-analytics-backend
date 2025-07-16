# Use an official Python runtime as a parent image
FROM python:3.11-slim

# no output buffering
ENV PYTHONUNBUFFERED TRUE

# install build tools for any C extensions
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# set working dir
WORKDIR /app

# install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY main.py .

# expose port
EXPOSE 8080

# use Gunicorn in production
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "main:app"]
