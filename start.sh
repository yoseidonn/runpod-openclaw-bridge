#!/usr/bin/env bash
set -e

# -------------------------
# Load .env if exists
# -------------------------
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# -------------------------
# Defaults
# -------------------------
MODEL_PATH="${MODEL_PATH:-/models/Qwen3.5-35B-A3B-GPTQ-Int4}"
HF_MODEL_ID="${HF_MODEL_ID:-Qwen/Qwen3.5-35B-A3B-GPTQ-Int4}"

TEMPERATURE="${TEMPERATURE:-0.7}"
TOP_P="${TOP_P:-0.95}"
MAX_TOKENS="${MAX_TOKENS:-128}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.95}"
CPU_OFFLOAD_GB="${CPU_OFFLOAD_GB:-0}"
VLLM_DEVICE="${VLLM_DEVICE:-cuda}"

export MODEL_PATH
export TEMPERATURE
export TOP_P
export MAX_TOKENS
export GPU_MEMORY_UTILIZATION
export CPU_OFFLOAD_GB
export VLLM_DEVICE

# -------------------------
# Ensure model directory
# -------------------------
mkdir -p "$MODEL_PATH"

# -------------------------
# Download model if missing
# -------------------------
if [ ! "$(ls -A $MODEL_PATH)" ]; then
    echo "Downloading model: $HF_MODEL_ID"
    python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='$HF_MODEL_ID',
    local_dir='$MODEL_PATH'
)
"
else
    echo "Model already exists at $MODEL_PATH"
fi

# -------------------------
# Run worker
# -------------------------
echo "Starting RunPod worker..."
exec python -u /app/handler.py