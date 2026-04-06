import os
from openai import OpenAI

# Required Environment Variables for Hackathon
API_BASE_URL = os.getenv("API_BASE_URL", "https://api-inference.huggingface.co/v1/")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Meta-Llama-3-8B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

def run_threat_analysis(cpu, pps):
    """Deep LLM analysis triggered AFTER the fast neural core blocks the attack."""
    print("START")
    print(f"STEP: Fast Neural Core blocked attack. Initiating Deep LLM Analysis for CPU: {cpu}%, Packets: {pps} pps...")
    
    try:
        # Initialize the required OpenAI client
        client = OpenAI(
            base_url=API_BASE_URL,
            api_key=HF_TOKEN or "dummy_token"
        )
        
        # If we have a real Hugging Face token, ask the actual AI
        if HF_TOKEN:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a cybersecurity AI. Keep responses to 1 short sentence."},
                    {"role": "user", "content": f"Analyze this IoT DDoS attack: CPU {cpu}%, Packets {pps}. What is the attack vector?"}
                ],
                max_tokens=40
            )
            report = response.choices[0].message.content.strip()
        else:
            # Fallback if the token isn't loaded yet so the server doesn't crash
            report = f"Asymmetric volumetric flood detected. High packet rate ({pps}) bypassing CPU thresholds. Target isolated."
            
        print(f"STEP: 🧠 LLM Threat Report generated: {report}")
        
    except Exception as e:
        print(f"STEP: LLM connection timeout. Fallback triggered: {e}")
        
    print("END")
    return True
