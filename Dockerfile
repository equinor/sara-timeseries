FROM ghcr.io/astral-sh/uv:0.13.6@sha256:af22a52f5eafef3d78e551599d405c02df61919d18028f0cea8eda93bc9986d0 AS uv
FROM python:3.15-slim@sha256:94d3426f1def7db4a106a232ac121bfd975393e5dfd40a619b955fae45fe7913 AS build

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

FROM python:3.15-slim@sha256:94d3426f1def7db4a106a232ac121bfd975393e5dfd40a619b955fae45fe7913

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
