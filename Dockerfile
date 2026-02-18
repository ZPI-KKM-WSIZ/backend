#=====================
# Stage 1: Builder
#=====================
FROM python:3.14.0-slim AS builder

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

# Install dependencies
# Replace https with ssh
RUN git config --global url."git@github.com:".insteadOf "https://github.com/"
# --mount=type=ssh: Exposes the host's SSH agent/keys to this RUN command only
# mkdir -p ...: Adds GitHub to known_hosts to prevent "Host key verification failed"
RUN --mount=type=ssh \
    mkdir -p -m 0600 ~/.ssh && \
    ssh-keyscan github.com >> ~/.ssh/known_hosts && \
    poetry install --only main --no-root

#=====================
# Stage 2: Runtime
#=====================
FROM python:3.14-slim AS runtime

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