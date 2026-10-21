
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
image_path = Path("sd_turbo_result.png")

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

print("\nMoondream 3.1 response:")
print(answer)

# # Always save the raw response
# Path("moondream3_raw.txt").write_text(
#     answer, encoding="utf-8"
# )

# 6. Validate JSON and save result
try:
    data = json.loads(answer)

    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object")

    # required_keys = {
    #     "nodes", "unary", "binary", "counts", "scene"
    # }

    # if not required_keys.issubset(data):
    #     raise ValueError(
    #         f"Missing fields: {required_keys - data.keys()}"
    #     )

    print("\nParsed JSON:")
    print(json.dumps(data, indent=2))

    with open(
        "moondream3_result.json", "w", encoding="utf-8"
    ) as f:
        json.dump(data, f, indent=2)

    print("\nResult saved to moondream3_result.json")

except (json.JSONDecodeError, ValueError, TypeError) as e:
    print(f"\nInvalid JSON response: {e}")
    print("Raw response saved to moondream3_raw.txt")
