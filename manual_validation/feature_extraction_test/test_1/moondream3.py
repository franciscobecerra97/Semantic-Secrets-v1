
import moondream as md
from PIL import Image
from pathlib import Path
import json

# 1. Initialize Moondream 3.1 API
model = md.vl(
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlfaWQiOiIzM2NlZWQ5Yi1iZWExLTQyZDYtOTVmNi04YmRiMzUzYjEzMzMiLCJvcmdfaWQiOiJ2SG1ybmhTVEk2eVF2cEdGWFdDbnVJSkdIaVlSOWdwdiIsImlhdCI6MTc5MjQyMDc3MCwidmVyIjoxfQ.D_MEsIEH-fFWYYeajBMkiWq-kVPUua8e77gpyEC4oNw",
    model="moondream3.1-9B-A2B"
)

# 2. Load your test image
# image_name = 'bike_1.png'
image_name = 'bike_2.png'
image_path = Path(image_name)
# image_path = Path("bike_2.png")

if not image_path.is_file():
    raise FileNotFoundError(f"Image not found: {image_path}")

image = Image.open(image_path).convert("RGB")

# 3. Load extraction prompt from TXT file
prompt_path = Path("extraction_prompt.txt")

if not prompt_path.is_file():
    raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

PROMPT = prompt_path.read_text(encoding="utf-8").strip()

# 4. Execute Moondream 3.1
result = model.query(image, PROMPT)

# 5. Extract and display response
answer = result["answer"]

print("\nMoondream response:")
print(answer)

# 6. Validate JSON and save result
try:
    data = json.loads(answer)

    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object")

    print("\nParsed JSON:")
    print(json.dumps(data, indent=2))

    with open(
        image_name + ".moondream.json", "w", encoding="utf-8"
    ) as f:
        json.dump(data, f, indent=2)

    print("\nResult saved to "+ str(image_name) +".moondream.json")

except (json.JSONDecodeError, ValueError, TypeError) as e:
    print(f"\nInvalid JSON response: {e}")
    print("Raw response saved to moondream_raw.txt")
