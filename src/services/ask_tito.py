import requests
import json
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()
URL_API = os.getenv("URL_API")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

def ask_tito_stream(pregunta: str):
    """
    Envía una pregunta a la IA y retorna la respuesta en streaming
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": pregunta}
        ],
        "stream": True,
        "temperature": 0.7
    }

    try:
        with requests.post(url, headers=headers, json=payload, stream=True) as response:
            if response.status_code != 200:
                detalle_error = response.text.strip()
                if detalle_error:
                    yield f"Error API: {response.status_code} - {detalle_error}"
                else:
                    yield f"Error API: {response.status_code}"
                return
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data: "):
                        data_str = decoded_line[6:] # Removing 'data: ' prefix
                        if data_str == "[DONE]":
                            break
                        try:
                            data_json = json.loads(data_str)
                            choices = data_json.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        print(f"Error streaming response: {e}")
        yield "Hubo un error al comunicarse con la IA."
