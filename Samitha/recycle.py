import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import warnings
warnings.filterwarnings("ignore")

def setup_granite_model_hf(model_name: str = "ibm-granite/granite-3.0-2b-instruct", use_auth_token: bool = False):
    print(f"🤖 Loading {model_name} from Hugging Face...")

    auth_token =  None
    if use_auth_token:
        import os
        auth_token = os.getenv("HUGGINGFACE_TOKEN", auth_token)

    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True,
        token=auth_token
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
        trust_remote_code=True,
        token=auth_token
    )

    text_generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
        token=auth_token
    )

    print("✅ Model loaded successfully!")
    return tokenizer, model, text_generator

def create_granite_prompt(waste_material: str) -> str:
    return f"""<|system|>
You are an expert sustainability consultant specializing in waste management, recycling, and creative upcycling solutions. You provide practical, actionable advice to help people reduce waste and live more sustainably.
<|user|>
I have this waste material: "{waste_material}"

Please provide specific guidance in this format:

**RECYCLING METHOD:**
[How to properly recycle this item - where to take it, preparation steps, what it becomes]

**DIY UPCYCLE IDEA:**
[A creative way to reuse this item at home with clear steps]

**ENVIRONMENTAL IMPACT:**
[Brief explanation of why this matters for the environment]

<|assistant|>
"""

def get_sustainability_advice_hf(waste_material: str, text_generator, max_length: int = 512):
    try:
        prompt = create_granite_prompt(waste_material)
        response = text_generator(
            prompt,
            max_length=max_length,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            pad_token_id=text_generator.tokenizer.eos_token_id,
            return_full_text=False
        )
        generated_text = response[0]['generated_text'].strip()

        return {
            "success": True,
            "waste_material": waste_material,
            "advice": generated_text,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "waste_material": waste_material,
            "advice": None,
            "error": str(e)
        }

def get_advice_direct_inference(waste_material: str, tokenizer, model, max_new_tokens: int = 300):
    prompt = create_granite_prompt(waste_material)
    inputs = tokenizer(prompt, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    return response.strip()

def main():
    print("🌱 IBM Granite Sustainability Assistant (via Hugging Face)")
    print("=" * 60)

    available_models = {
        "1": "ibm-granite/granite-3.0-2b-instruct",
        "2": "ibm-granite/granite-3.0-8b-instruct",
        "3": "ibm-granite/granite-7b-instruct"
    }

    print("Available models:")
    for key, model in available_models.items():
        print(f"  {key}. {model}")

    model_choice = input("\nSelect model (1-3, default=1): ").strip() or "1"
    selected_model = available_models.get(model_choice, available_models["1"])

    try:
        tokenizer, model, text_generator = setup_granite_model_hf(selected_model, use_auth_token=True)

        print(f"\n🚀 Using model: {selected_model}")
        print("Device:", "CUDA" if torch.cuda.is_available() else "CPU")
        print("\nEnter waste materials to get sustainability advice.")
        print("Type 'quit' to exit.\n")

        while True:
            waste_material = input("Enter waste material: ").strip()

            if waste_material.lower() in ['quit', 'exit', 'q']:
                print("👋 Thanks for using the Sustainability Assistant!")
                break

            if not waste_material:
                print("Please enter a valid waste material.\n")
                continue

            print(f"\n🔍 Analyzing '{waste_material}'...")

            result = get_sustainability_advice_hf(waste_material, text_generator)

            if result["success"]:
                print("\n" + "=" * 60)
                print(f"SUSTAINABILITY ADVICE FOR: {waste_material.upper()}")
                print("=" * 60)
                print(result["advice"])
                print("=" * 60)
            else:
                print(f"❌ Error: {result['error']}")

            print()

    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Install required packages: pip install transformers torch accelerate")
        print("2. Try a smaller model if you're low on memory")
        print("3. Make sure you have sufficient disk space for model download")

def quick_sustainability_advice(waste_material: str, model_name: str = "ibm-granite/granite-3.0-2b-instruct") -> str:
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True
        )

        advice = get_advice_direct_inference(waste_material, tokenizer, model)
        return advice

    except Exception as e:
        return f"Error generating advice: {str(e)}"

def demo_example():
    print("🧪 Demo: Quick sustainability advice")

    test_materials = ["plastic water bottle", "old smartphone", "cardboard box"]

    for material in test_materials:
        print(f"\n📋 Testing: {material}")
        advice = quick_sustainability_advice(material)
        print(f"💡 Advice: {advice[:200]}...")

if __name__ == "__main__":
    # Uncomment to run demo instead of full assistant
    # demo_example()
    main()
