#!/bin/bash
set -e

# Set environment variables for GDAL
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal

# Wait for the database (optional)
# echo "Waiting for PostgreSQL..."
# until nc -z $DB_HOST $DB_PORT; do
#   echo "Waiting for DB at $DB_HOST:$DB_PORT..."
#   sleep 2
# done

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start the Uvicorn server (dev mode)
echo "Starting Uvicorn server..."
exec uvicorn core.asgi:application --host 0.0.0.0 --port 8000 --reload