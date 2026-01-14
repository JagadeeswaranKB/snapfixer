FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Switch to a different mirror to potentially speed up apt-get
RUN sed -i 's/deb.debian.org/ftp.us.debian.org/g' /etc/apt/sources.list.d/debian.sources

# Install system dependencies

# Install system dependencies
# RUN apt-get update && apt-get install -y \
#    libgl1 \
#    libglib2.0-0 \
#    build-essential \
#    libpq-dev \
#    gettext \
#    && rm -rf /var/lib/apt/lists/*


# Install python dependencies
COPY requirements.txt /app/
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/
