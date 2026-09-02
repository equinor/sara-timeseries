FROM ghcr.io/astral-sh/uv:0.12.5@sha256:e85be844203885286c60ffad8a858d48afb6c5a5c237ca0e67f12e74b8f174b1 AS uv
FROM python:3.14-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6 AS build

COPY --from=uv /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends\
    wget \
    libgl1 \
    libglib2.0-0 \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    build-essential \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN --mount=source=.git,target=.git,type=bind uv sync --frozen --no-editable --no-dev

FROM python:3.14-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6

WORKDIR /app
COPY --from=build /app/.venv /app/.venv
COPY main.py .
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8200

# Add non-root user
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser
RUN chown -R appuser:appuser /app
RUN chmod 755 /app
USER appuser

CMD ["python", "main.py"]
