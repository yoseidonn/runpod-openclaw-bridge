from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import runpod
import torch
import os

MODEL_PATH = "/app/model"

# 1. READ ENVIRONMENT VARIABLES
# Default to True so your worker doesn't crash on big models by accident
QUANTIZE = os.environ.get("LOAD_IN_4BIT", "true").lower() == "true"
MAX_TOKENS = int(os.environ.get("MAX_NEW_TOKENS", 512))
TEMP = float(os.environ.get("TEMPERATURE", 0.7))

# 2. DEFINE QUANTIZATION CONFIG
# This only activates if QUANTIZE is true
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",           # High quality 4-bit
    bnb_4bit_use_double_quant=True,      # Saves more memory
    bnb_4bit_compute_dtype=torch.float16 # Speeds up math on GPUs
) if QUANTIZE else None

print(f"--- Loading Model (Quantization: {QUANTIZE}) ---")

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

# 3. LOAD MODEL
# device_map="auto" is the key to balancing the model on the GPU
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    device_map="auto",
    quantization_config=bnb_config, # Will be None if QUANTIZE is false
    trust_remote_code=True
)

def handler(job):
    job_input = job["input"]
    prompt = job_input.get("prompt", "Hello!")

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    
    # Generate response
    outputs = model.generate(
        **inputs, 
        max_new_tokens=MAX_TOKENS, 
        temperature=TEMP
    )
    
    return {"response": tokenizer.decode(outputs[0], skip_special_tokens=True)}

runpod.serverless.start({"handler": handler})