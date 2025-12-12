# check=skip=UndefinedVar
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./

RUN pip install uv

CMD ["uv", "run", "streamlit", "run", "src/app.py", "--server.address=0.0.0.0"]
