import requests
import json

class VLLMClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.generate_url = f"{base_url}/v1/completions"

    def generate(self, prompt, max_tokens=512, temperature=0.7, top_p=0.9, stop=None):
        """Génère du texte en utilisant l'API VLLM."""
        headers = {"Content-Type": "application/json"}
        data = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stop": stop,
            "stream": False
        }

        try:
            response = requests.post(self.generate_url, headers=headers, data=json.dumps(data), timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["text"]
        except Exception as e:
            print(f"❌ Erreur lors de l'appel VLLM: {e}")
            return None

    def is_available(self):
        """Vérifie si le serveur VLLM est disponible."""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
        