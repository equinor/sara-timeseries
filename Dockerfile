FROM python:3.13-slim AS build

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

RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN --mount=source=.git,target=.git,type=bind
RUN pip install .

FROM python:3.13-slim

WORKDIR /app
COPY --from=build /app/venv /app/venv
COPY main.py .
ENV PATH="/app/venv/bin:$PATH"

EXPOSE 8200

# Add non-root user
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser
RUN chown -R appuser:appuser /app
RUN chmod 755 /app
USER appuser

CMD ["python", "main.py"]
