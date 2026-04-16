# Base image
FROM python:3.12-slim

# --- THE CHEAT CODE ---
# Copy the 'uv' executable directly from the official uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# ----------------------

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .

# Install dependencies using the binary we just copied
RUN uv sync

# Copy all project files
COPY backend/ ./backend/

# Set environment variable
ENV PYTHONPATH=/app/backend/src

# Expose port and start
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "backend.src.main:app", "--host", "0.0.0.0", "--port", "8000"]