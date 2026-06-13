# Use official Playwright image with Python pre-installed
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright chromium browser (already in base image, but ensures correct version)
RUN playwright install chromium --with-deps

# Copy application code (note: .dockerignore excludes .env, data/, logs)
COPY . .

# Ensure data directory exists and is writable
# The actual data will come from the Docker volume mount
RUN mkdir -p data && chmod 777 data

# Create a non-root user for security
RUN useradd -m -u 1001 appuser && chown -R appuser:appuser /app
USER appuser

# Expose the port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/status')" || exit 1

# Run the application
CMD ["python", "run.py"]
