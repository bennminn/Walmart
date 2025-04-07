FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    libsqlite3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install CMake from an official source
RUN wget https://github.com/Kitware/CMake/releases/download/v3.27.6/cmake-3.27.6-linux-x86_64.sh \
    && chmod +x cmake-3.27.6-linux-x86_64.sh \
    && ./cmake-3.27.6-linux-x86_64.sh --skip-license --prefix=/usr/local \
    && rm cmake-3.27.6-linux-x86_64.sh

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --clear  # Limpia y recopila archivos estáticos

# Expose the application port
EXPOSE $PORT

# Command to run the application
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]