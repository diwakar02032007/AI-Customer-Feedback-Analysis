import json
import requests
from flask import current_app
from utils.logger import logger

def query_ollama(prompt, system_prompt=None, max_timeout=3):
    """
    Query local Ollama instance (Free / Local technology).
    Gracefully falls back to None if Ollama service is not running.
    """
    try:
        base_url = current_app.config.get('OLLAMA_BASE_URL', 'http://localhost:11434')
        model = current_app.config.get('OLLAMA_MODEL', 'llama3')
        timeout = current_app.config.get('OLLAMA_TIMEOUT', max_timeout)
        
        url = f"{base_url.rstrip('/')}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 150
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        response = requests.post(url, json=payload, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            return data.get('response', '').strip()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # Ollama is offline or not responding within timeout; proceed with fast local ML fallback
        return None
    except Exception as e:
        logger.warning(f"Ollama request encountered error: {e}")
        return None

def ollama_analyze_feedback(text):
    """
    Attempt feedback analysis using local Ollama if active.
    Returns parsed dict or None if Ollama is unavailable.
    """
    sys_prompt = "You are an AI customer feedback analyst. Respond only with valid JSON containing keys: summary, recommendation."
    prompt = f"Analyze this customer feedback:\n\"{text}\"\nProvide JSON response only."
    
    response = query_ollama(prompt, system_prompt=sys_prompt)
    if not response:
        return None

    try:
        # Extract JSON substring
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end != -1:
            return json.loads(response[start:end])
    except Exception:
        pass

    return None
