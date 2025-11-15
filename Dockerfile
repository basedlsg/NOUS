# Use the official Python image as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for autonomous experiment
RUN pip install --no-cache-dir \
    google-cloud-storage \
    openai \
    groq \
    requests

# Copy the entire project directory into the container
COPY . .

# Set the entry point for the container
ENTRYPOINT ["python", "autonomous_spatial_experiment.py"]
