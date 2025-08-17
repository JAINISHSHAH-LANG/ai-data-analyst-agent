# Use official lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for pandas, numpy, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirement files first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Start FastAPI with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
