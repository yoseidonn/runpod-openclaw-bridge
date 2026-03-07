# OpenClaw Bridge: Universal LLM Inference Server (vLLM, Qwen-3.5-35B-A3B-GPTQ-Int4)

[![RunPod](https://img.shields.io/badge/Platform-RunPod-blue.svg)](https://runpod.io) [![Model](https://img.shields.io/badge/Model-Qwen3.5--35B--A3B--GPTQ--Int4-green.svg)](https://huggingface.co/Qwen/Qwen3.5-35B-A3B-GPTQ-Int4) [![vLLM](https://img.shields.io/badge/Engine-vLLM-orange.svg)](https://vllm.ai)

## Overview

OpenClaw Bridge is a high-efficiency LLM (Large Language Model) inference server using vLLM and the quantized Qwen 3.5 35B-A3B GPTQ-Int4 model. It is easily deployable across platforms: run it in serverless mode on RunPod, self-host as a Docker container for local development, use on your own VM or server (cloud or on-premises), or run on other container-compatible services.

The Docker image includes the baked model for fast cold starts and avoids runtime downloads.

Key components:
- **Handler Script**: Handles HTTP/RunPod jobs and runs inference using vLLM.
- **Dockerfile**: Pre-loads the quantized model for reproducibility and low startup latency.
- **Flexible Environment Config**: Control model path, sampling, device selection via environment variables.
- **GitHub Workflow**: Automate builds and pushes.

## Features

- **Universal Inference Server**: Run anywhere Docker is available—locally, on VMs, on-premises, or in the cloud.
- **Serverless or Traditional**: Designed for RunPod serverless but also works in standard HTTP server or job-based setups.
- **Efficient**: Quantized weights dramatically reduce VRAM (~20-25GB), suitable for A100/H100, workstation-class, or cloud GPUs.
- **RESTful Endpoints**: Supports both batch (async `/run`) and synchronous (`/runsync`) usage.
- **Easy Configuration**: Use env vars to tune compute and sampling.
- **Customizable**: All settings can be set via environment (defaults included).

## Requirements

- **Docker**: To run the container on any system or cloud provider.
- **NVIDIA GPU (Recommended)**: 40GB+ VRAM (e.g., A100/H100) for optimal performance.
- **Cloud/VM/Server**: Any Linux or Windows host with Docker (AWS, GCP, Azure, Paperspace, Lambda Labs, local etc).
- **RunPod Account** (for managed serverless deployment; optional).
- **Build/Deploy Registry**: (Optional) Docker Hub or GitHub Container Registry if deploying remotely.
- **Python dependencies baked in:**
```text
runpod==1.7.0
torch==2.3.1
vllm==0.6.1
huggingface-hub==0.24.6
```

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/openclaw-bridge.git
cd openclaw-bridge
```

### 2. Build the Docker Image (Model is downloaded at build time)
```bash
docker build -t openclaw-bridge:latest .
```
Or use the GitHub workflow in this repo for automated CI builds.

### 3. Deployment Options

#### **A. Run Locally (Bare Metal or with Docker)**
```bash
docker run --gpus all --rm -p 8000:8000 \
  -e MODEL_PATH=/models/Qwen3.5-35B-A3B-GPTQ-Int4 \
  openclaw-bridge:latest
```
- `--gpus all` enables GPU support (omit for CPU-only, noting performance will be very slow).
- Customize with environment variables as needed (see below).
- The server listens on port 8000 (or as configured).

#### **B. Deploy to Cloud VM or GPU Rental**
- Build or pull the image as above.
- Launch a VM with a suitable GPU (AWS EC2, GCP, Azure, Lambda Labs, Paperspace, etc).
- Run the container with your environment/tuning options.
- Expose and secure port 8000 for remote API access as needed.

#### **C. Serverless on RunPod**
- Go to RunPod > Serverless > New Endpoint.
- Select your public container image.
- Configure resources & environment (see below).
- Save and deploy: RunPod handles scaling automatically.

#### **D. Other Platforms**
- Use on any infrastructure supporting Docker, e.g. Kubernetes, Docker Compose, local workstation, or compatible cloud container services.

## Usage

### API Endpoints

OpenClaw Bridge runs a RunPod-compatible handler interface. Primary endpoints:
- `/runsync` — Synchronous (response in HTTP body).
- `/run` — Asynchronous (get job ID; poll `/status/<job_id>` for result).

Sample usage (`/runsync` endpoint shown):

#### Example Curl Request (local or remote, replace host/port as needed)
```bash
curl -X POST http://localhost:8000/runsync \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "Generate a Python function for factorial.",
      "max_tokens": 256,
      "temperature": 0.7,
      "top_p": 0.95
    }
  }'
```
- For RunPod deployments, use your assigned endpoint and API key.
- For local/cloud deployments, point to your deployed host:port.

#### Handler Logic

- **Input**: JSON with `prompt` (required), optional `temperature`, `top_p`, `max_tokens`.
- **Output**: JSON with `output` (model-generated text).
- All parameters fall back to values specified via environment variables if not present in request.

## Environment Variables

Set via `-e <KEY>=<VALUE>` when launching Docker, or in your cloud/serverless provider:

- `MODEL_PATH` (default: `/models/Qwen3.5-35B-A3B-GPTQ-Int4`)
- `TEMPERATURE` (default: `0.7`)
- `TOP_P` (default: `0.95`)
- `MAX_TOKENS` (default: `128`)
- `GPU_MEMORY_UTILIZATION` (default: `0.95`)
- `CPU_OFFLOAD_GB` (default: `0`)
- `VLLM_DEVICE` (default: `auto`; options: `auto`, `cuda`, `cpu`)

## Troubleshooting

- **Cold Start**: First request may be slow; subsequent calls are fast.
- **VRAM Errors**: Lower `GPU_MEMORY_UTILIZATION` or use `CPU_OFFLOAD_GB`.
- **Multiprocessing Issues**: Use Python main guard (`if __name__ == "__main__"`) for proper model init.
- **Logs**: Container and application logs will reveal most issues.

## Contributing

Pull requests are welcome for general improvements, bugfixes, or new features. Please open an issue for discussion if proposing major changes.

## License

MIT License. See LICENSE for details.