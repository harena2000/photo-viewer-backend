# Use official Python image
FROM python:3.11-alpine

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt watchdog


# Copy project files
COPY . .

# Expose port (optional, for debugging)
EXPOSE 8000

# Entrypoint is handled by docker-compose
CMD ["sleep", "infinity"]
