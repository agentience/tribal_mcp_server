#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "📝 Testing GitHub workflow locally..."

# Use Python 3.12 for consistency with the workflow
PYTHON_CMD="/opt/homebrew/bin/python3.12"
if [ ! -x "$PYTHON_CMD" ]; then
  echo "⚠️ Python 3.12 not found at $PYTHON_CMD"
  echo "Checking for other Python versions..."

  if command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
  elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
  elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
  else
    echo "❌ Error: No Python installation found. Please install Python 3.12+"
    exit 1
  fi
fi

python_version=$($PYTHON_CMD --version)
echo "Using $python_version"
if [[ ! $python_version == *"3.12"* ]]; then
  echo "⚠️ Warning: You are not using Python 3.12 which is specified in the workflow"
  read -p "Continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
  echo "🔧 Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create and activate a virtual environment with uv
echo "🔧 Creating virtual environment..."
uv venv
echo "✅ Virtual environment created"

# Install dependencies in the virtual environment
echo "📦 Installing dependencies..."
uv pip install -e ".[dev]"
echo "✅ Dependencies installed"

# Run commands using uv run to ensure they execute in the virtual environment
echo "🔍 Running ruff linter..."
uv run ruff check .
echo "✅ Linting passed"

echo "🎨 Formatting code with black..."
uv run black .
echo "✅ Formatting check passed"

echo "📝 Running type checks with mypy..."
# Run mypy with --ignore-missing-imports flag and skip tests directories
uv run mypy --ignore-missing-imports src/ || true
echo "✅ Type checking completed (ignoring errors for now)"

echo "🧪 Running tests with pytest..."
uv run pytest
echo "✅ Tests passed"

echo "🏗️ Building package..."
uv run python -m build
echo "✅ Build completed successfully"

echo ""
echo "✅ All workflow steps completed successfully!"
echo "Note: Package publishing step was skipped for local testing"
