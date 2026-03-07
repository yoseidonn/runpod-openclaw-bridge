import os
import runpod
from vllm import LLM, SamplingParams

# -------------------------
# Environment configuration
# -------------------------

MODEL_PATH = os.getenv("MODEL_PATH", "/models/Qwen3.5-35B-A3B-GPTQ-Int4")

DEFAULT_TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
DEFAULT_TOP_P = float(os.getenv("TOP_P", 0.95))
DEFAULT_MAX_TOKENS = int(os.getenv("MAX_TOKENS", 128))
GPU_MEMORY_UTILIZATION = float(os.getenv("GPU_MEMORY_UTILIZATION", 0.95))

# -------------------------
# Load model once at worker start
# -------------------------

llm = LLM(
    model=MODEL_PATH,
    dtype="auto",
    gpu_memory_utilization=GPU_MEMORY_UTILIZATION
)

# -------------------------
# RunPod handler
# -------------------------

def handler(job):
    input_data = job.get("input", {})

    prompt = input_data.get("prompt", "Hello!")

    temperature = float(input_data.get("temperature", DEFAULT_TEMPERATURE))
    top_p = float(input_data.get("top_p", DEFAULT_TOP_P))
    max_tokens = int(input_data.get("max_tokens", DEFAULT_MAX_TOKENS))

    sampling_params = SamplingParams(
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens
    )

    outputs = llm.generate(prompt, sampling_params)

    return {
        "output": outputs[0].outputs[0].text
    }

# -------------------------
# Start RunPod worker
# -------------------------

runpod.serverless.start({"handler": handler})