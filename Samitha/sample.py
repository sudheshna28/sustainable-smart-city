from transformers import AutoTokenizer, AutoModelForCausalLM
import os

model_name = "ibm-granite/granite-3.0-2b-instruct"

# Try to load from local cache only
try:
    print("🔍 Checking local cache for model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(model_name, local_files_only=True, trust_remote_code=True)
    print("✅ Model is already downloaded and cached!")
except Exception as e:
    print("❌ Model not fully downloaded.")
    print("Error:", str(e))
