# Use a high-performance PyTorch image
FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

WORKDIR /app

# 1. Setup Build Arguments (The "Gates")
ARG HF_TOKEN
ARG MODEL_REPO="meta-llama/Llama-3-8B"

# 2. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Bake the model into the image (Build Phase)
# We use the build-time HF_TOKEN to authenticate
RUN python3 -c "from huggingface_hub import snapshot_download; \
    snapshot_download(repo_id='${MODEL_REPO}', local_dir='/app/model', token='${HF_TOKEN}')"

# 4. Copy the runtime handler
COPY main.py .

# RunPod expects the -u flag for unbuffered logs
CMD [ "python", "-u", "main.py" ]