from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from huggingface_hub import snapshot_download
from pathlib import Path
import runpod
import torch
import os

# ────────────────────────────────────────────────
# Environment Variables
# ────────────────────────────────────────────────
MODEL_REPO = os.environ.get("MODEL_REPO")
HF_TOKEN   = os.environ.get("HF_TOKEN")

QUANTIZE    = os.environ.get("LOAD_IN_4BIT", "true").lower() == "true"
MAX_TOKENS  = int(os.environ.get("MAX_NEW_TOKENS", "512"))
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.7"))

if not MODEL_REPO:
    raise ValueError("MODEL_REPO environment variable is required")
if not HF_TOKEN and "gated" in MODEL_REPO.lower():  # optional: only enforce for gated models
    print("Warning: HF_TOKEN not set — may fail for gated/private models")

# ────────────────────────────────────────────────
# Model Path Resolution (prefer RunPod cache → fallback to runtime download)
# ────────────────────────────────────────────────
CACHE_ROOT = "/runpod-volume/huggingface-cache/hub"
MODEL_PATH = "/app/model"  # default fallback

if MODEL_REPO:
    model_cache_id = MODEL_REPO.replace("/", "--")
    cache_base = Path(CACHE_ROOT) / f"models--{model_cache_id}"

    if cache_base.exists():
        snapshot_dirs = sorted(cache_base.glob("snapshots/*"), reverse=True)  # newest first
        if snapshot_dirs:
            MODEL_PATH = str(snapshot_dirs[0])
            print(f"Using RunPod cached model at: {MODEL_PATH}")
            os.environ["HF_HUB_OFFLINE"] = "1"  # force offline loading
        else:
            print("Cache dir exists but no snapshots found — falling back to /app/model")
    else:
        print("No RunPod cache found — falling back to runtime download")

# Download only if using fallback path and model not already present
if MODEL_PATH == "/app/model" and not os.path.exists(MODEL_PATH):
    print(f"Downloading model to {MODEL_PATH} ...")
    snapshot_download(
        repo_id=MODEL_REPO,
        local_dir=MODEL_PATH,
        token=HF_TOKEN,
        resume_download=True,           # resume interrupted downloads
        local_files_only=False
    )
    print("Model download complete")

# ────────────────────────────────────────────────
# Load Tokenizer
# ────────────────────────────────────────────────
print(f"Loading tokenizer from {MODEL_PATH} ...")
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH,
    local_files_only=True,
    trust_remote_code=True
)
print("Tokenizer loaded")

# ────────────────────────────────────────────────
# Quantization Config (only if enabled)
# ────────────────────────────────────────────────
bnb_config = None
if QUANTIZE:
    print("Preparing 4-bit quantization config ...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16
    )

# ────────────────────────────────────────────────
# Load Model
# ────────────────────────────────────────────────
print(f"Loading model (quantization: {QUANTIZE}) from {MODEL_PATH} ...")
try:
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        device_map="auto",
        quantization_config=bnb_config,
        torch_dtype=torch.float16 if QUANTIZE else None,
        trust_remote_code=True,
        low_cpu_mem_usage=True
    )
    print("Model loaded successfully")
except Exception as e:
    print(f"Model loading failed: {e}")
    raise

# ────────────────────────────────────────────────
# Optional warm-up (reduces first real request latency spike)
# ────────────────────────────────────────────────
print("Performing dummy warm-up generation ...")
with torch.no_grad():
    dummy_input = tokenizer("Hello", return_tensors="pt").input_ids.to("cuda")
    _ = model.generate(dummy_input, max_new_tokens=1)
print("Warm-up complete")

# ────────────────────────────────────────────────
# Handler (called for every job)
# ────────────────────────────────────────────────
def handler(job):
    job_input = job["input"]
    prompt = job_input.get("prompt", "Hello!")

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            do_sample=(TEMPERATURE > 0)
        )

    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"response": response_text}

# ────────────────────────────────────────────────
# Start RunPod serverless worker
# ────────────────────────────────────────────────
print("Starting RunPod serverless handler ...")
runpod.serverless.start({"handler": handler})
print("Serverless handler stopped (should not reach here)")