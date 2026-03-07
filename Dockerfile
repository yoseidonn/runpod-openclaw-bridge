FROM runpod/pytorch:2.2.1-py3.10-cuda12.1.1-devel-ubuntu22.04

# Install dependencies
RUN pip install --no-cache-dir runpod vllm huggingface-hub

# Download and bake the model during build (adjust path if needed)
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='Qwen/Qwen3.5-35B-A3B-GPTQ-Int4', local_dir='/models/Qwen3.5-35B-A3B-GPTQ-Int4')"

# Set working dir
WORKDIR /app

# Copy your handler code
COPY handler.py /app/handler.py

# Expose port if needed (RunPod handles this)
EXPOSE 8000

# RunPod serverless entrypoint
CMD ["python", "-u", "/app/handler.py"]