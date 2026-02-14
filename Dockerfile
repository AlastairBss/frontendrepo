# Lightweight Python base image
FROM python:3.10-slim

# Avoid buffered logs (important for debugging)
ENV PYTHONUNBUFFERED=1

# Working directory inside container
WORKDIR /app

# Copy dependencies first (Docker caching optimization)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend code
COPY . .

# Streamlit default port
EXPOSE 8501

# Start Streamlit server
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
