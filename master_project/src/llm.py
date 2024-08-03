import requests
import logging


class CustomLLM:
    def __init__(self, model: str, api_url: str):
        self.model = model
        self.api_url = api_url

    def generate_response(self, persona: str, prompt: str) -> str:
        
        try:
            response = requests.post(
                self.api_url,
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'system': persona
                }
            )
            response.raise_for_status()
            result = response.json().get('response', '').strip()
            return result
        except Exception as e:
            logging.warning(f"Error occurred during LLM call: {e}")
            return "Error occurred during LLM call"

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')



