# RunPod OpenClaw Bridge

A lightweight, high-performance **inference bridge** for the **OpenClaw** ecosystem, designed to run large quantized LLMs (like Qwen 3.5B–35B GGUF models) on **RunPod Serverless GPUs**.

This version uses **runtime model loading** + **RunPod Cached Models** to avoid baking huge model weights into the Docker image, solving GitHub Actions disk space limits and enabling fast, cheap, auto-scaling inference.

## Key Features

- **Runtime model loading** — downloads only once (or uses RunPod cache) → lightweight image (~2–4 GB)
- **RunPod Cached Models** support — near-instant cold starts after first boot
- **Pay-per-use serverless** — charged only for active inference time (scale-to-zero)
- **GitHub Actions CI/CD** — builds → pushes to GHCR → auto-updates RunPod endpoint
- **Local parity** — same `docker compose` workflow works locally for development & testing
- **OpenClaw compatible** — JSON input/output ready for ReAct loops, tool calling, heartbeats
- **4-bit quantization** — efficient memory usage via BitsAndBytes (nf4 + double quant)

## Project Structure

```text
├── main.py               # RunPod handler + model loading logic
├── Dockerfile            # Lightweight runtime image (no model baking)
├── docker-compose.yml    # Local testing & build bridge
├── requirements.txt      # Dependencies (transformers, runpod, bitsandbytes, etc.)
├── .github/workflows/    # Auto-build, push & RunPod update
└── .env.example          # Template for local env vars (gitignore'd)
```

## Quick Start – Local Development
1. Clone the repo
```bash
git clone https://github.com/yusuf/runpod-openclaw-bridge.git
cd runpod-openclaw-bridge
```

2. Copy and fill .env (for local testing only)Bashcp .env.example .env
Edit .env with your values:
```bash
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MODEL_REPO=unsloth/Qwen3.5-35B-A3B-GGUF
```

3. Build & run locally (GPU recommended)
```bash
docker compose build
docker compose up
```

→ The container will download the model on first run (may take 5–20 min), then start the handler.
4. Test locally (from another terminal)
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "Tell me a short joke about Istanbul traffic"}}'Or use /runsync for blocking response.
```

## Deployment to RunPod Serverless
### Push to GitHub (main branch)
→ GitHub Actions automatically:
Builds the lightweight image
Pushes to ghcr.io/yusuf/runpod-openclaw-bridge:latest
Triggers RunPod endpoint update (if secrets are set)

### Configure the RunPod Endpoint (one-time)
Create new Serverless Endpoint → Load Balancer type
Container image: ghcr.io/yusuf/runpod-openclaw-bridge:latest
GPU: 24 GB (RTX 3090 / L4 class recommended)
Container disk: 80–100 GB (fallback download safety)
Model field: https://huggingface.co/unsloth/Qwen3.5-35B-A3B-GGUF (enables caching)
Start command: leave blank (uses Dockerfile CMD)
Ports: leave blank (uses internal 8000)

Environment variables:
```text
MODEL_REPO=unsloth/Qwen3.5-35B-A3B-GGUF
HF_TOKEN=          (set as Secret)
LOAD_IN_4BIT=true
MAX_NEW_TOKENS=512
TEMPERATURE=0.7
```

Test the endpoint
```bash
curl -X POST https://<your-endpoint-id>.api.runpod.ai/runsync \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "Write a haiku about the Bosphorus at night"}}'
```  
First request may take 5–20 minutes (cold start + model load/cache). Subsequent requests are fast if worker stays warm.

## Required GitHub Secrets (for CI/CD)
| Secret | Required? | Purpose |
|--------|-----------|---------|
| GITHUB_TOKEN | Auto | Used by docker/login-action |
| RUNPOD_API_KEY | Optional | Auto-update RunPod endpoint after push |
| RUNPOD_ENDPOINT_ID | Optional | Your endpoint ID to update |

## Billing & Cost Notes
Pay-per-use: Charged per second of active worker time (~$0.00019/s for 24 GB Flex).
Cold starts: First boot + model load can cost $0.05–$0.30 once.
Idle: $0 if min workers = 0 (scale-to-zero).
Always-warm option: Set min workers = 1 → ~$15–25/day (good for low-latency needs).
Prepaid credits: Add $10–$20 via dashboard to start (auto-recharge recommended).

## Security Notes
- Never commit HF_TOKEN or other secrets.
- Use Secrets in RunPod dashboard for sensitive values.
- Endpoint is public by default — add auth in handler if needed later.

## About
Built by Yusuf __(@yoseidonn)__ — exploring autonomous AI agents, serverless inference, and DevOps automation.
Questions / issues? Open an issue or reach out on GitHub.
Happy inferencing! 