FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install numpy scipy matplotlib seaborn flask requests

# Copy the experiment scripts
COPY simple_spatial_experiment.py .
COPY cloud_run_server.py .

# Expose port
EXPOSE 8080

# Run the web server
CMD ["python", "cloud_run_server.py"]
