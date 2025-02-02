# Use Python 3.9 as base image for TensorFlow compatibility
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libasound2-dev \
    libjack-dev \
    portaudio19-dev \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the magenta source code and our generation script
COPY magenta-main /app/magenta-main
COPY generate_edm.py /app/

# Install Python dependencies
RUN pip install --no-cache-dir numpy==1.23.5 && \
    pip install --no-cache-dir h5py==3.1.0 && \
    pip install --no-cache-dir tensorflow==2.9.1 && \
    pip install --no-cache-dir tensorflow-io-gcs-filesystem==0.23.1 && \
    pip install --no-cache-dir protobuf==3.19.6 && \
    pip install --no-cache-dir note-seq==0.0.3 && \
    pip install --no-cache-dir -e magenta-main

# Set environment variables
ENV PYTHONPATH=/app/magenta-main:$PYTHONPATH

# Run the EDM generation script
CMD ["python", "generate_edm.py"]
