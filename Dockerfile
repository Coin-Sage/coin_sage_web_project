# Use the official Python image as the base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
        libc-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /app

# Install Python dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . /app

# Copy .env file into the container
COPY .env /.env

# Set environment variable for Django
ENV DJANGO_SETTINGS_MODULE=coin_sage_web_project.settings

# Command to run the application
CMD ["gunicorn", "coin_sage_web_project.wsgi:application", "--bind", "0.0.0.0:8000"]
