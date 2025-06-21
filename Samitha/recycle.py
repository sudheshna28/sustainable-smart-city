import requests
import json
import os
import warnings
warnings.filterwarnings("ignore")

class GraniteAPIClient:
    def __init__(self, api_key: str, endpoint: str = "https://us-south.ml.cloud.ibm.com"):
        """
        Initialize the IBM Granite API client
        
        Args:
            api_key: Your IBM Watson Machine Learning API key
            endpoint: IBM Watson ML endpoint (default: us-south)
        """
        self.api_key = api_key
        self.endpoint = endpoint.rstrip('/')
        self.access_token = None
        self.project_id = None  # You'll need to set this
        
    def authenticate(self):
        """Get access token using API key"""
        try:
            auth_url = "https://iam.cloud.ibm.com/identity/token"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
            data = {
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self.api_key
            }
            
            print(f"🔑 Using API key: {self.api_key[:10]}...{self.api_key[-4:] if len(self.api_key) > 14 else '[hidden]'}")
            
            response = requests.post(auth_url, headers=headers, data=data)
            
            if response.status_code != 200:
                print(f"❌ Authentication failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            print("✅ Successfully authenticated with IBM Watson ML")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error during authentication: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Authentication failed: {str(e)}")
            return False
    
    def set_project_id(self, project_id: str):
        """Set the Watson ML project ID"""
        self.project_id = project_id
    
    def generate_text(self, prompt: str, model_id: str = "ibm/granite-3-2b-instruct", 
                     max_new_tokens: int = 300, temperature: float = 0.7):
        """
        Generate text using IBM Granite model via API
        
        Args:
            prompt: Input prompt
            model_id: Model identifier (default: granite-3-2b-instruct)
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        """
        if not self.access_token:
            print("❌ Not authenticated. Please call authenticate() first.")
            return None
            
        try:
            url = f"{self.endpoint}/ml/v1/text/generation?version=2023-05-29"
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
            
            payload = {
                "input": prompt,
                "parameters": {
                    "decoding_method": "sample",
                    "max_new_tokens": max_new_tokens,
                    "temperature": temperature,
                    "top_p": 0.9,
                    "repetition_penalty": 1.1
                },
                "model_id": model_id,
                "project_id": self.project_id
            }
            
            print(f"🔗 Making request to: {url}")
            print(f"📋 Using model: {model_id}")
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                print(f"❌ API request failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return None
            
            result = response.json()
            
            if "results" not in result or not result["results"]:
                print(f"❌ Unexpected response format: {result}")
                return None
                
            generated_text = result["results"][0]["generated_text"]
            return generated_text.strip()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error during text generation: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Error generating text: {str(e)}")
            return None

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

def get_sustainability_advice_api(waste_material: str, client: GraniteAPIClient, 
                                model_id: str = "ibm/granite-3-2b-instruct"):
    """Get sustainability advice using IBM Granite API"""
    try:
        prompt = create_granite_prompt(waste_material)
        response = client.generate_text(prompt, model_id=model_id)
        
        if response:
            return {
                "success": True,
                "waste_material": waste_material,
                "advice": response,
                "error": None
            }
        else:
            return {
                "success": False,
                "waste_material": waste_material,
                "advice": None,
                "error": "Failed to generate response"
            }
            
    except Exception as e:
        return {
            "success": False,
            "waste_material": waste_material,
            "advice": None,
            "error": str(e)
        }

def setup_client():
    """Setup the IBM Granite API client with credentials"""
    print("🤖 Setting up IBM Granite API Client...")
    
    # Get API key from environment variable or set it directly
    api_key = os.getenv("IBM_API_KEY")
    if not api_key:
        print("❌ IBM_API_KEY environment variable not found!")
        print("Please set it with: export IBM_API_KEY='your_api_key_here'")
        return None
    
    # Your specific project ID
    project_id = "ce2ced52-0815-4c93-9d49-6f105f4ff799"
    
    # Initialize client with your endpoint
    client = GraniteAPIClient(api_key, "https://us-south.ml.cloud.ibm.com")
    client.set_project_id(project_id)
    
    # Authenticate
    if client.authenticate():
        print(f"✅ Project ID set: {project_id}")
        return client
    else:
        return None

# Alternative: Quick fix for testing
def quick_test():
    """Quick test with hardcoded values - replace with your actual values"""
    api_key = "your_api_key_here"  # Replace with your actual API key
    project_id = "your_project_id_here"  # Replace with your actual project ID
    
    client = GraniteAPIClient(api_key)
    client.set_project_id(project_id)
    
    if client.authenticate():
        result = get_sustainability_advice_api("plastic", client)
        if result["success"]:
            print(result["advice"])
        else:
            print(f"Error: {result['error']}")
    else:
        print("Authentication failed")

# Updated main function
def main():
    print("🌱 IBM Granite Sustainability Assistant (API Version)")
    print("=" * 60)
    
    # Check if API key is set
    if not os.getenv("IBM_API_KEY"):
        print("❌ Missing IBM_API_KEY environment variable")
        print("Set it with: export IBM_API_KEY='your_api_key_here'")
        return
    
    # Available models
    available_models = {
        "1": "ibm/granite-3-2b-instruct",
        "2": "ibm/granite-3-8b-instruct",
        "3": "ibm/granite-20b-multilingual"
    }
    
    print("Available models:")
    for key, model in available_models.items():
        print(f"  {key}. {model}")
    
    model_choice = input("\nSelect model (1-3, default=1): ").strip() or "1"
    selected_model = available_models.get(model_choice, available_models["1"])
    
    # Setup API client
    client = setup_client()
    if not client:
        print("❌ Failed to setup API client. Exiting.")
        return
    
    print(f"\n🚀 Using model: {selected_model}")
    print("Endpoint: https://us-south.ml.cloud.ibm.com")
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
        
        result = get_sustainability_advice_api(waste_material, client, selected_model)
        
        if result["success"]:
            print("\n" + "=" * 60)
            print(f"SUSTAINABILITY ADVICE FOR: {waste_material.upper()}")
            print("=" * 60)
            print(result["advice"])
            print("=" * 60)
        else:
            print(f"❌ Error: {result['error']}")
        
        print()

if __name__ == "__main__":
    main()
    # Uncomment below for quick test
    # quick_test()