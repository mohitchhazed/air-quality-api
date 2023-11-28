# Use Python image
FROM python:3.9

# Set working directory in the container
WORKDIR /app

# Copy application files into the container
COPY ./app/main.py /app

# Set environment variable for the token
ENV API_TOKEN=$API_TOKEN

# Install dependencies
RUN pip install --no-cache-dir flask requests sqlalchemy apscheduler

# Expose the application's port
EXPOSE 5000

# Run the application
CMD ["python", "main.py"]

