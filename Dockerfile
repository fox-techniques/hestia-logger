# Use official Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Install Hestia Logger from PyPI
RUN pip install hestia-logger

# Copy the log generator script
COPY generate_logs.py /app/generate_logs.py

# Set environment variables
ENV LOGS_DIR="/var/logs/hestia"
ENV LOG_LEVEL="INFO"

# Create logs directory
RUN mkdir -p /var/logs/hestia && chmod -R 777 /var/logs/hestia

# Ensure logs persist if mounted
VOLUME ["/var/logs/hestia"]

# Run generate_logs.py
ENTRYPOINT ["python", "/app/generate_logs.py"]
