FROM python:3.10 AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

FROM base AS backend

EXPOSE 80
ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "--port", "80", "--workers", "2", "--reload", "main:app"]

FROM base AS frontend
RUN mkdir -p ~/.streamlit/
RUN echo "[general]"  > ~/.streamlit/credentials.toml && \
    echo "email = \"\""  >> ~/.streamlit/credentials.toml

EXPOSE 80
ENTRYPOINT ["streamlit", "run", "streamlit-api.py", "--browser.gatherUsageStats", "false", "--server.port", "80"]
