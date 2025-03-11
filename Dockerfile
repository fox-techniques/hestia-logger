# Use official Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry install --without dev

# Set environment variables
ENV ENVIRONMENT="container"
ENV LOGS_DIR="/var/logs/hestia"
ENV LOG_LEVEL="INFO"
ENV ENABLE_INTERNAL_LOGGER="true"

# Create logs directory with proper permissions
RUN mkdir -p /var/logs/hestia && chmod -R 777 /var/logs/hestia

# Define entrypoint
CMD ["poetry", "run", "python", "hestia_logger/main.py"]
