# Use an official Python runtime as a parent image
FROM --platform=linux/aarch64 python:3.9-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any necessary packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose any ports the app is using (optional, depending on your app's requirements)
# EXPOSE 1883 4840  # For example, MQTT typically uses 1883, OPC UA uses 4840

# Set environment variables (if any)
# ENV VAR_NAME value

# Define the command to run the application when the container starts
ENTRYPOINT ["python", "opc_ua_client_mqqt.py"]