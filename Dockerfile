# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --silent
COPY frontend/ ./
RUN npm run build

# Stage 2: Serve the app using FastAPI
FROM python:3.10-slim

# Install build essentials for python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install backend python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend files
COPY backend/ ./backend/

# Copy built frontend assets from Stage 1 into backend's static directory
COPY --from=frontend-builder /app/frontend/dist ./backend/static

WORKDIR /app/backend

# Expose port (Render sets the PORT environment variable automatically)
EXPOSE 8000
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Run the FastAPI app
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
