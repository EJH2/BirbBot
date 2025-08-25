FROM python:3.13.5-slim AS builder

# Set environment variables
ENV POETRY_HOME="/opt/poetry"
ENV PATH="/opt/poetry/bin:$PATH"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Make app directory
RUN mkdir -p /app

# Set work directory
WORKDIR /app

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock /app/

# Configure Poetry and install dependencies
RUN  poetry config virtualenvs.in-project true && \
     poetry install --no-interaction --no-ansi

FROM builder AS app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV POETRY_HOME="/opt/poetry"

# Create directory for Docker secrets
RUN mkdir -p /run/secrets/

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser

# Copy pertinent builder stage files to app
COPY --from=builder /opt/poetry/ /opt/poetry/
COPY --from=builder /app/ /app/

# Copy project files into container
COPY main.py /app

# Set container user to appuser
USER appuser

# Set working directory
WORKDIR /app

# Command to run the application
CMD ["poetry", "run", "python", "main.py"]