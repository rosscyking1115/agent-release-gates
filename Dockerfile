FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
# Sync the env once at build time; runtime `uv run` uses it without re-syncing
# (which would otherwise drop the optional api/dashboard extras).
ENV UV_NO_SYNC=1

COPY pyproject.toml uv.lock README.md streamlit_app.py ./
COPY src ./src

RUN uv sync --locked --no-dev --extra api --extra dashboard

COPY app ./app
COPY data ./data
COPY docs ./docs
COPY reports ./reports
COPY scripts ./scripts
COPY .streamlit ./.streamlit

RUN uv run --no-dev python scripts/run_all_evals.py

RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uv", "run", "--no-dev", "uvicorn", "internal_ai_agent.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
