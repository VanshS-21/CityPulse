# Use Python 3.11 with Debian slim for better Apache Beam compatibility
FROM python:3.11-slim-bookworm

# Set environment variables for security and performance
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONPATH=/app
ENV PATH="/home/appuser/.local/bin:$PATH"

# Set work directory
WORKDIR /app

# Install system dependencies with Debian package manager
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    git \
    curl \
    ca-certificates \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Create non-root user early for security (Debian syntax)
RUN groupadd -g 1001 appuser && useradd -u 1001 -g appuser -m appuser \
    && mkdir -p /home/appuser/.local/bin \
    && chown -R appuser:appuser /home/appuser

# Switch to non-root user for package installation
USER appuser

# Upgrade pip to latest version
RUN pip install --user --upgrade pip==24.3.1

# Copy requirements first for better caching
COPY --chown=appuser:appuser requirements.txt /app/

# Install Python dependencies as non-root user
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy application code with proper ownership
COPY --chown=appuser:appuser src/ /app/src/
COPY --chown=appuser:appuser tests/ /app/tests/
COPY --chown=appuser:appuser server/ /app/server/

# Add comprehensive health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys, os; sys.exit(0 if os.path.exists('/app/main.py') else 1)" || exit 1

# Expose port (if needed for web services)
EXPOSE 8080

# Default command
CMD ["python", "main.py"]
