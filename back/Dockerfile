FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml ./

RUN pip install uv

CMD ["uv", "run", "src/main.py"]
