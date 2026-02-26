#=====================
# Stage 1: Builder
#=====================
FROM python:3.13.0-slim AS builder

# Install system dependencies required for building (git is needed for fetching dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ssh \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=2.3.2
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

# Copy only dependency files first to leverage Docker layer caching
COPY pyproject.toml poetry.lock ./

# Configure Poetry to create the virtual environment in the project folder
RUN poetry config virtualenvs.in-project true

RUN --mount=type=cache,target=/root/.cache \
    --mount=type=secret,id=env \
    GITHUB_TOKEN=$(grep '^GITHUB_TOKEN=' /run/secrets/env | cut -d'=' -f2-| tr -d '"') && \
    echo "https://oauth2:${GITHUB_TOKEN}@github.com" > /root/.git-credentials && \
    git config --global credential.helper store && \
    poetry install --no-root --only main --no-interaction --no-ansi && \
    rm -f /root/.git-credentials

#=====================
# Stage 2: Runtime
#=====================
FROM python:3.13.0-slim AS runtime
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# Create a non-root user for security
RUN groupadd -g 999 appuser && \
    useradd -r -u 999 -g appuser appuser

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
# Copy the application code
COPY --chown=appuser:appuser ./pyproject.toml ./pyproject.toml
COPY --chown=appuser:appuser ./src/ ./src/

# Set environment variables to use the virtual environment automatically
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER appuser

# Run the application
CMD ["python", "-m", "src.main"]