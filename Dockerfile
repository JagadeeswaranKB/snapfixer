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

# Expose port
EXPOSE 8000

# Start gunicorn
CMD ["gunicorn", "validphoto.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "300", "--log-level", "debug"]
