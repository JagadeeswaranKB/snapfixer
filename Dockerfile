FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    libpq-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*


# Install python dependencies
COPY requirements.txt /app/
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files during build
RUN python manage.py collectstatic --noinput

# Make start script executable
RUN chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Start via script
CMD ["/app/start.sh"]
