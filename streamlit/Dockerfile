# app/Dockerfile

FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
COPY 👋_Welcome.py .
COPY pages ./pages
COPY authenticator ./authenticator
COPY config.yaml .
COPY config.py .
COPY .streamlit .streamlit
COPY .static .static

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

CMD streamlit run 👋_Welcome.py --server.port $PORT --server.address 0.0.0.0
# ENTRYPOINT ["streamlit", "run", "👋_Welcome.py", "--server.port=${PORT}", "--server.address=0.0.0.0"]
# ENTRYPOINT [ "streamlit", "run", "👋_Welcome.py", \
#              "--browser.serverAddress", "0.0.0.0", \
#              "--server.enableCORS", "False", \
#              "--server.port", "80", \
#              "--server.fileWatcherType", "none", \
#              "--browser.gatherUsageStats", "false"]
