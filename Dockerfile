FROM python:3.12-slim

WORKDIR /app

# Install Git because RepoReview clones GitHub repositories
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better Docker layer caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app ./app
COPY frontend ./frontend
COPY main.py .

# Streamlit port
EXPOSE 8501

# Run RepoReview AI
CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]