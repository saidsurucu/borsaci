FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml ./
COPY src/ ./src/
COPY README.md LICENSE ./

RUN uv sync

VOLUME ["/app/.env"]

ENV PYTHONUNBUFFERED=1
ENV MAX_STEPS=20
ENV MAX_STEPS_PER_TASK=5
ENV PARALLEL_EXECUTION=true
ENV BORSA_MCP_URL=https://borsamcp.fastmcp.app/mcp

CMD ["uv", "run", "borsaci"]

