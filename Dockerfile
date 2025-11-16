# User Offical Python Image
FROM python:3.12-slim

# Create Working Directory
WORKDIR /app

# Install System Dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev

# Install Python Dependencies First From Requirements File
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Project Files
COPY . .

# Expose Port
EXPOSE 8000

# Run gunicorn server
CMD ["gunicorn", "vote_x_backend.wsgi:application", "--bind", "0.0.0.0:8000"]