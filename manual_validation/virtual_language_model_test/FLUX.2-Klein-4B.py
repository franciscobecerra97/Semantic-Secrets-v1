
import fal_client
from pathlib import Path
from urllib.request import urlopen

# 1. Configure API key
API_KEY = "PASTE_YOUR_ACTUAL_API_KEY_HERE"
MODEL = "fal-ai/flux-2/klein/4b"

# IMPORTANT: Create authenticated client
client = fal_client.SyncClient(key=API_KEY)

# 2. Define prompt
PROMPT = (
    "A realistic photograph, front view, full body. "
    "One adult person in a red striped shirt, standing "
    "inside a simple room, holding one book. "
    "The person and the book are clearly visible, "
    "separated from the background. "
    "Simple composition with two to four main objects, "
    "natural lighting, no text."
)

# 3. Request remote image generation
# IMPORTANT: Use client.subscribe, not fal_client.subscribe
result = client.subscribe(
    MODEL,
    arguments={
        "prompt": PROMPT,
        "seed": 42,
        "image_size": {
            "width": 1024,
            "height": 1024
        },
        "num_inference_steps": 4,
        "num_images": 1,
        "output_format": "png"
    }
)

# 4. Save returned image
print("Server response:", result)

images = result.get("images", [])

if not images or not images[0].get("url"):
    raise RuntimeError("Server did not return an image URL")

image_url = images[0]["url"]
output_path = Path("flux2_klein_result.png")

with urlopen(image_url, timeout=120) as response:
    output_path.write_bytes(response.read())

print(f"Image saved to {output_path}")
