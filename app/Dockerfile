FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.9.17 /uv /uvx /bin/
ENV UV_NO_DEV=1

WORKDIR /app
COPY ./pyproject.toml /app
COPY ./uv.lock /app
RUN uv sync --locked

COPY . /app

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
