# Multi-stage build for minimal image size
FROM python:3.10-slim AS builder

WORKDIR /tmp

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies to /tmp/packages
COPY requirements.txt .
RUN pip install --target=/tmp/packages --no-cache-dir -r requirements.txt

# Final stage - minimal runtime image
FROM python:3.10-slim

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Copy Python packages from builder
COPY --from=builder --chown=appuser:appuser /tmp/packages /app/packages

# Set environment PATH and Python path
ENV PATH=/app/packages/bin:$PATH \
    PYTHONPATH=/app/packages \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy application code with proper ownership
COPY --chown=appuser:appuser . .

# Ensure uploads directory exists with proper permissions
RUN mkdir -p /app/uploads && chown -R appuser:appuser /app/uploads

# Collect static files as root, then ensure appuser owns everything
RUN python manage.py collectstatic --noinput --clear || true && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import http.client; http.client.HTTPConnection('localhost', 8000).request('GET', '/'); exit(0)" || exit 1

# Start gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--worker-class", "sync", "--max-requests", "1000", "--timeout", "60", "my_site.wsgi:application"]
