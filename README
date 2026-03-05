# OpenClaw RunPod Worker
An autonomous AI agent worker built for the __OpenClaw__ ecosystem and optimized for __RunPod Serverless GPU inference__. This worker **bakes** Large Language Models (LLMs) into a Docker container to provide high-performance, low-latency reasoning for autonomous background tasks and remote triggers.

## Key Features
- Serverless Optimization: Designed for RunPod Serverless—pay only for the seconds the GPU is active during a task or heartbeat.
- Model Baking: Downloads and packages model weights (Llama 3, Mistral, etc.) during the Docker build phase to eliminate runtime download delays.
- Hybrid CI/CD: Uses a unified Docker Compose workflow for both local development and GitHub Actions deployment.
- Dynamic Configuration: Control inference parameters (Temperature, Max Tokens) via RunPod environment variables without rebuilding the image.
- OpenClaw Ready: Standardized JSON I/O compatible with OpenClaw's ReAct loop and tool-calling logic.

## Project Structure
```bash
├── main.py              # RunPod Handler & Inference Logic
├── Dockerfile           # The "Baking" Blueprint (Build-time)
├── docker-compose.yml   # Bridge for Local/Cloud builds
├── requirements.txt     # Python Dependencies
├── .github/workflows/   # Automated CI/CD (GitHub Actions)
└── .env                 # Local environment variables (Hidden)
```

## Setup & Deployment
1. Local Development
To build and test the worker on your local machine:

1.1. Create a .env file:
```bash
HF_TOKEN=your_huggingface_token
MODEL_REPO=meta-llama/Llama-3-8B
```

1.2. Build using Docker Compose:
```bash
docker compose build
```

1.3. Test the handler logic:
```bash
python main.py --test_input '{"input": {"prompt": "Check VPS status"}}'
```

2. GitHub Actions Deployment
The repository is configured to build and push to GHCR (GitHub Container Registry) automatically on every push to main.

Required GitHub Secrets:
- HF_TOKEN: Your Hugging Face Read Token (required for gated models).
- RUNPOD_API_KEY (Optional): To trigger automatic endpoint updates.
- RUNPOD_ENDPOINT_ID (Optional): Your specific Serverless Endpoint ID.

Required GitHub Variables:
- RUNPOD_MODEL_REPO: The model to bake (e.g., meta-llama/Llama-3-8B).

## Runtime Configuration (RunPod Dashboard)
Once deployed, you can tune the worker's behavior in the RunPod Console using these Environment Variables:
| Varbiables  | Default  | Description  |
|---|---|---|
| MAX_NEW_TOKENS  | 512  | Limits the length of the AI response.  |
|  TEMPERATURE | 0.7  | Controls the "creativity" of the model.  |

## Security & Best Practices
Secret Management: Secrets are passed as Build Arguments (ARG) during the Docker build phase and are never committed to the repository.

Containerization: The worker runs in an isolated environment. If granting the agent SSH access to manage VPS servers, use a dedicated, low-privilege SSH key.

DevOps Standards: Follows a "Build once, run anywhere" philosophy using Docker Compose parity.


## 🎓 About the Project
Developed by __Yusuf (github@yoseidonn)__, a Computer Science student at Istanbul University - Cerrahpaşa and DevOps Intern at Onkatec. This project explores the intersection of Backend Development, Network Security, and Autonomous AI Systems.