FROM python:3.12-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

RUN pip install --no-cache-dir "poetry==1.8.3" && poetry --version

COPY --chown=user pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create true \
 && poetry config virtualenvs.in-project true \
 && poetry install --no-interaction --no-ansi --only main

ENV PATH="/app/.venv/bin:$PATH"

COPY --chown=user src /app/src

EXPOSE 7860

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
