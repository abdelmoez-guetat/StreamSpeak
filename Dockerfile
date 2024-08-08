# Use the official Python image with a slim version
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 3000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]