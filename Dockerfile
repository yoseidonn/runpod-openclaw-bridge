# Use a high-performance PyTorch image
FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

WORKDIR /app

# 1. Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy the Runtime Handler
COPY main.py .

# 3. Run the Worker
CMD [ "python", "-u", "main.py" ]
