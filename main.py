from transformers import AutoModelForCausalLM, AutoTokenizer
import runpod
import torch
import os

# The path where the Dockerfile "baked" the model
MODEL_PATH = "/app/model"

# Runs on worker startup
print("--- Loading Model into VRAM ---")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH, 
    device_map="auto", 
    torch_dtype=torch.float16
)

# Runs per request by runpod serverless
def handler(job):
    # Retrieve runtime settings from RunPod Dashboard Environment Variables
    max_tokens = int(os.environ.get("MAX_NEW_TOKENS", 512))
    temp = float(os.environ.get("TEMPERATURE", 0.7))

    job_input = job["input"]
    prompt = job_input.get("prompt")

    # Simple Inference Logic
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=max_tokens, temperature=temp)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return {"response": response}

runpod.serverless.start({"handler": handler})