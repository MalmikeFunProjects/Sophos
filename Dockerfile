# syntax=docker/dockerfile:1.7
# ResearchDaad Crew — Dockerfile (env via sample.env at runtime)

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_NO_CACHE=1 \
    VENV_PATH=/app/.venv \
    PATH="/app/.venv/bin:${PATH}"

# Install Chromium + chromedriver (arm64) and required libs
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl ca-certificates gcc build-essential git \
      chromium chromium-driver \
      fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 \
      libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 \
      libnspr4 libnss3 libx11-6 libx11-xcb1 libxcb1 \
      libxcomposite1 libxdamage1 libxext6 libxfixes3 \
      libxkbcommon0 libxrandr2 \
    && rm -rf /var/lib/apt/lists/*

# Python deps
RUN pip install --upgrade pip && pip install --no-cache-dir uv

WORKDIR /app

# Copy project metadata AND sources BEFORE installing, so hatch/uv can see packages
COPY pyproject.toml ./
COPY src ./src

# Create venv & install the project (editable)
RUN uv venv && uv pip install -e .

# Keep the example env inside the image as placeholders (no secrets baked)
COPY sample.env .env

# Ensure the assets dir exists for GOOGLE_APPLICATION_CREDENTIALS path
RUN mkdir -p /app/assets

# Non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver
ENV RUNNING_IN_DOCKER=true

# CMD ["python", "src/research_daad/main.py"]
CMD ["python", "src/research_daad/tools/daad_scraper.py"]
