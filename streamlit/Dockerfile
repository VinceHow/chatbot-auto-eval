# app/Dockerfile

FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
COPY app.py .
COPY helpers.py .
COPY backend ./backend
COPY static ./static
COPY config.py .
COPY .streamlit .streamlit

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 80

ENTRYPOINT [ "streamlit", "run", "app.py", \
             "--browser.serverAddress", "0.0.0.0", \
             "--server.enableCORS", "False", \
             "--server.port", "80", \
             "--server.fileWatcherType", "none", \
             "--browser.gatherUsageStats", "false"]
