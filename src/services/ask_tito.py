import requests
import json
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()
URL_API = os.getenv("URL_API")

def ask_tito_stream(pregunta: str):
    """
    Envía una pregunta a la IA y retorna la respuesta en streaming
    """
    url = URL_API
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
        "messages": [
            {"role": "system", "content": (
                "Eres un asistente personal. "
                "Tu nombre es Tito. "
                "Manten un tono profesional, servicial y conciso."
            )},
            {"role": "user", "content": pregunta}
        ],
        "stream": True,
        "temperature": 0.7
    }

    try:
        with requests.post(url, headers=headers, json=payload, stream=True) as response:
            if response.status_code != 200:
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
