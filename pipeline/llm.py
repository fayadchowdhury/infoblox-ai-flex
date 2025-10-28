from openai import OpenAI
from dotenv import load_dotenv
import os
import json

class GPTClient:
    def __init__(self, model="gpt-4o-mini", temperature=0.2):
        # Load environment variables from .env
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env")

        # Initialize the OpenAI client
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def generate(self, system_prompt: str, prompt: str) -> str:
        """Send a prompt and return the model's text output."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.temperature,
        )
        response = response.choices[0].message.content.strip()
        if response.startswith("```"):
            response = response.strip("`").replace("json", "", 1).strip()

        return json.loads(response)
