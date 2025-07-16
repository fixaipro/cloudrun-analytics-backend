# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Allow statements and log messages to immediately appear (no buffering)
ENV PYTHONUNBUFFERED TRUE

# Install system‐level dependencies (if any).  
# Here we add gcc & libffi-dev in case causalimpact (and pandas) need to compile C extensions.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set a working directory
WORKDIR /app

# Copy in only requirements first (for better Docker caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY main.py .

# Expose the port your Flask app runs on
EXPOSE 8080

# Run the server
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "main:app"]
