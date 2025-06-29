import requests
from openai import OpenAI

class LLMInterface:
    """Interface for different LLM providers"""

    @staticmethod
    def call_openai(prompt: str, api_key: str, model: str = "gpt-3.5-turbo") -> str:
        # Correct client initialization
        client = OpenAI(api_key=api_key)
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling OpenAI: {str(e)}"

    @staticmethod
    def call_ollama(prompt: str, model: str = "llama2", base_url: str = "http://localhost:11434") -> str:
        try:
            r = requests.post(
                f"{base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False}
            )
            if r.status_code == 200:
                return r.json()['response']
            return f"Error calling Ollama: {r.status_code} - {r.text}"
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"

    @staticmethod
    def generate_simple_response(query: str, context: str) -> str:
        return (
            f"**Query:** {query}\n\n"
            f"**Relevant Information:**\n{context}\n\n"
            "**Note:** Configure an LLM provider (OpenAI or Ollama) for richer answers."
        )
