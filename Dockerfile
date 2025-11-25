# Use official Python lightweight image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean

# Install Python dependencies first (cache-friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Collect static files (Admin, Swagger, DRF UI)
RUN RENDER=BUILD python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run migrations on container startup (important for free-tier Render)
CMD ["sh", "-c", "python manage.py migrate && gunicorn vote_x_backend.wsgi:application --bind 0.0.0.0:8000 --timeout 120"]
