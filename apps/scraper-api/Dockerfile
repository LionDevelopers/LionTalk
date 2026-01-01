# Use a slim Python base

# --- Stage 1: Builder --- 
# Create new stage called builder
FROM python:3.12-slim AS builder

# Install uv by copying the binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Copy only the dependency files first (for better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment (.venv) in the container
# --frozen ensures we use the exact versions in the lockfile
# --no-install-project: tells uv to install only dependencies, not the project itself
# --mount=type=cache,target=/root/.cache/uv: caches uv downloads so we don't re-download them on every build
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev


# --- Stage 2: RUNTIME (Final Image) ---
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy only the .venv and application code from the builder stage
COPY --from=builder /app /app

# Ensure the virtual environment (.venv) is used 
ENV PATH="/app/.venv/bin:$PATH"

# Install Playwright Browsers
RUN playwright install chromium --with-deps

# Copy the rest of the application code
COPY src/ ./src/

# Cleanup & Config
# Avoid Generating .pyc files
# Set environment variable for headless mode
ENV HEADLESS=true
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN rm -rf /var/lib/apt/lists/* # Remove apt cache to save a little space after installing deps

# Default command to run your scraper
CMD ["python", "./src/scraper.py"]