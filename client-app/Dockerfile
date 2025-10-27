FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire dist folder (protected code)
COPY dist/ ./dist/


# Set environment variables
ENV PYTHONPATH=/app/dist/backend:/app/dist/backend/backend:/app/dist/backend/pyarmor_runtime_000000
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8001

# Change to the protected backend directory
WORKDIR /app/dist/backend/backend

# Run the protected application
CMD ["python", "main.py"]