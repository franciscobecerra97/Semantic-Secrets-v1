
from gradio_client import Client
from pathlib import Path
import shutil

# 1. Connect to remote server
model = Client("Ntdeseb/ntia")

# 2. Load prompt from TXT file
# prompt_path = Path("generation_prompt.txt")

# if not prompt_path.is_file():
#     raise FileNotFoundError(prompt_path)

# PROMPT = prompt_path.read_text(encoding="utf-8").strip()
# PROMPT = 'A red cat wearing a blue astronaut helmet, sitting on the moon.'
PROMPT = 'A realistic photograph, front view, full body. One adult person in a red striped shirt, standing inside a simple room, holding one book. The person and the book are clearly visible, separated from the background. Simple composition with two to four main objects, natural lighting, no text.'


# 3. Request remote image generation
result = model.predict(
    prompt=PROMPT,
    # model_name="stabilityai/sdxl-turbo",
    model_name="stabilityai/sdxl-turbo",
    negative_prompt="",
    seed=42,
    width=512,
    height=512,
    guidance_scale=0.0,
    num_inference_steps=4,
    api_name="/generate_image"
)

# 4. Save returned image
print("Server response:", result)

image_path = result.get("path") if isinstance(result, dict) else result

if not isinstance(image_path, str) or not Path(image_path).is_file():
    raise RuntimeError("Server did not return a usable image file")

shutil.copy2(image_path, "sd_turbo_result.png")

print("Image saved to sd_turbo_result.png")
