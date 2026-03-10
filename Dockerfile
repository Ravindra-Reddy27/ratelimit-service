# ==========================================
# STAGE 1: The Builder
# ==========================================
FROM python:3.11-slim as builder

WORKDIR /app

# Copy only the requirements first to cache the downloads
COPY requirements.txt .

# Install dependencies into a specific folder so we can easily copy them later
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ==========================================
# STAGE 2: The Production Image
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# Copy only the installed dependencies from the builder stage
COPY --from=builder /install /usr/local

# Copy our actual application code
COPY ./src ./src
COPY ./tests ./tests

# Expose the port FastAPI runs on
EXPOSE 8000

# The command to start the server
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]