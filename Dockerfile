FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies if any are needed (e.g. for building some python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Hugging Face Spaces run as a non-root user (uid 1000)
# We need to give this user write access to the /app directory so it can create SQLite files or save model .pkl files
RUN useradd -m -u 1000 user
RUN chown -R user:user /app
USER user

# Hugging Face Spaces expects the app to run on port 7860
EXPOSE 7860

# Command to run the application using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:7860", "--timeout", "120", "--workers", "2", "run:app"]
