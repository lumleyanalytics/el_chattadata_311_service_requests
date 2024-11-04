# Dockerfile for Cloud Run

# Use the official Python image
FROM python:3.10-slim

# Set environment variables to prevent Python from writing pyc files to disk
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 for Google Cloud Run
EXPOSE 8080

# Run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "cloud_run_fetch_and_store_data:app"]
