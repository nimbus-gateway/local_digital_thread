# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Expose the necessary port (if any)
EXPOSE 5000


# Define environment variable (you may need to adjust this depending on your application)
ENV FLASK_APP=app.py


# Set the PYTHONPATH environment variable to include the src directory
ENV PYTHONPATH=/app


# Run your Flask application
# Run app.py when the container launches
CMD ["python", "app.py"]


