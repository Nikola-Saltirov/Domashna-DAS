# Use an official Python runtime as a parent image
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# Add Microsoft package repository
RUN wget https://packages.microsoft.com/config/debian/10/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb

# Install .NET SDK
RUN apt-get update && apt-get install -y dotnet-sdk-6.0 

# Install required dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Generate the locale
RUN echo "de_DE.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen de_DE.UTF-8 && \
    dpkg-reconfigure --frontend=noninteractive locales

# Set locale environment variables
ENV LANG=de_DE.UTF-8 \
    LANGUAGE=de_DE:de \
    LC_ALL=de_DE.UTF-8

# Set working directory
WORKDIR /app

# Copy Python script and requirements file into the image
COPY requirements.txt /app/
COPY . /app
COPY ./temp_stocks/ /app/temp_stocks/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask port
EXPOSE 5000

# Run the Python script
CMD ["python", "main_app.py"]
