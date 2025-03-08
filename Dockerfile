FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including C++ compiler
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy application requirements
COPY requirements.txt pyproject.toml setup.py /app/

# Copy application code
COPY src/ /app/src/
COPY README.md /app/

# Install dependencies and the package itself
RUN uv pip install --system -r requirements.txt
RUN uv pip install --system -e .

# Create volume mount point
RUN mkdir -p /data

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "learned_knowledge_mcp.app", "--host", "0.0.0.0"]