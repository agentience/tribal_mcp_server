FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including C++ compiler
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.1

# Copy Poetry configuration
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry to not use a virtual environment
RUN poetry config virtualenvs.create false

# Copy application code
COPY src/ /app/src/
COPY README.md /app/

# Install dependencies and the package itself
RUN poetry install --no-interaction --no-ansi --only main

# Create volume mount point
RUN mkdir -p /data

# Expose port
EXPOSE 8000

# Run the application
ENTRYPOINT ["poetry", "run"]
CMD ["mcp-api", "--host", "0.0.0.0"]