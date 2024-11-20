FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Rename prod.env to .env.production at runtime
RUN mv src/api/prod.env src/api/.env.production

# Create necessary directories
RUN mkdir -p /cloudsql
RUN mkdir -p /tmp/pdfs

# Make sure the port is exposed
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Start the FastAPI app with uvicorn
CMD exec uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT} 