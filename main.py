import json
from pathlib import Path
import requests
import re

# Paths
BASE_DIR = Path(__file__).parent
ENTITY_DIR = BASE_DIR / "sample_inputs" / "entities"
RELATIONSHIP_DIR = BASE_DIR / "sample_inputs" / "relationships"
PROMPT_PATH = BASE_DIR / "prompts" / "base_prompt.txt"
TARGET_DIR = BASE_DIR / "target"

# Update to the correct port (11501)
OLLAMA_URL = "http://127.0.0.1:11500/api/generate"
MODEL_NAME = "llama3"  # or whatever model you've pulled

def extract_json(text):
    """
    Extract the first JSON object from a block of text.
    """
    # Remove markdown formatting
    text = text.strip("` \n")

    # Find the first curly brace and try parsing from there
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        json_str = text[start:end + 1]
        return json_str
    return ""

def ask_ollama(full_prompt: str) -> str:
    try:
        res = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": full_prompt,
            "stream": False
        }, timeout=120)

        res.raise_for_status()
        raw_text = res.json().get("response", "").strip()

        print("🔍 Raw Ollama Response:\n", raw_text[:300], "...\n")

        json_part = extract_json(raw_text)
        if not json_part:
            raise ValueError("No valid JSON found in response.")
        return json_part

    except Exception as e:
        print(f"❌ Failed to get valid JSON: {e}")
        return ""

    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return ""

def main():
    base_prompt = PROMPT_PATH.read_text()
    TARGET_DIR.mkdir(exist_ok=True)

    for entity_file in ENTITY_DIR.glob("entity*.json"):
        num = entity_file.stem.replace("entity", "")
        relationship_file = RELATIONSHIP_DIR / f"relationship{num}.json"
        if not relationship_file.exists():
            print(f"❌ Missing relationship{num}.json — skipping.")
            continue

        entity_text = entity_file.read_text()
        relationship_text = relationship_file.read_text()

        prompt = f"{base_prompt}\n\nENTITY DATA:\n{entity_text}\n\nRELATIONSHIP DATA:\n{relationship_text}"
        print(f"🤖 Generating target{num}.json...")

        try:
            result = ask_ollama(prompt)
            # Optional: try parsing as JSON to ensure it’s valid
            parsed = json.loads(result)
            (TARGET_DIR / f"target{num}.json").write_text(json.dumps(parsed, indent=2))
            print(f"✅ Saved: target{num}.json")
        except Exception as e:
            print(f"❌ Failed for target{num}.json — {e}")

    print("🎯 All done!")

if __name__ == "__main__":
    main()
