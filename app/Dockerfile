# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirement file first to leverage cache
COPY ../requirements.txt .

# Install dependencies
# Note: In a real prod env, we might want to install pytorch strictly for cpu if no gpu
# but for now we trust requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY ../app ./app

# Expose port
EXPOSE 8000

# Run the application
# We assume the docker context is the root so we can copy app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
