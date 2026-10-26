
from gradio_client import Client, handle_file
from pathlib import Path
import json

# 1. Initialize SmolVLM2 API
model = Client("HuggingFaceTB/SmolVLM2")

# 2. Load your test image
# image_name = 'bike_1.png'
image_name = 'bike_2.png'
image_path = Path(image_name)
# image_path = Path("bike_2.png")

if not image_path.is_file():
    raise FileNotFoundError(f"Image not found: {image_path}")

# 3. Load extraction prompt from TXT file
prompt_path = Path("extraction_prompt.txt")

if not prompt_path.is_file():
    raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

PROMPT = prompt_path.read_text(encoding="utf-8").strip()

# 4. Execute SmolVLM2
result = model.predict(
    input_dict={
        "text": PROMPT,
        "files": [handle_file(str(image_path))]
    },
    max_tokens=500,
    api_name="/chat"
)

# 5. Display raw response
print("\nSmolVLM2 response:")
print(result)

# 6. Validate JSON and save result
try:
    data = json.loads(result) if isinstance(result, str) else result

    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object")

    print("\nParsed JSON:")
    print(json.dumps(data, indent=2))

    with open(
        image_name + ".smolVLM.json", "w", encoding="utf-8"
    ) as f:
        json.dump(data, f, indent=2)

    print("\nResult saved to smolvlm2_result.json")

except (json.JSONDecodeError, ValueError, TypeError) as e:
    print(f"\nInvalid JSON response: {e}")
