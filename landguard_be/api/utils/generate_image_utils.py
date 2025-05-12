import os
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
import random

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = f"{current} {word}".strip()
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)

def generate_image_with_message(message):
    template_folder = os.path.join(settings.BASE_DIR, "templates")
    image_choices = [f for f in os.listdir(template_folder) if f.endswith(('.jpg', '.png'))]

    if not image_choices:
        raise FileNotFoundError("No template images found!")

    selected_image = os.path.join(template_folder, random.choice(image_choices))
    image = Image.open(selected_image)
    draw = ImageDraw.Draw(image)

    # Font
    font_path = os.path.join(settings.BASE_DIR, "fonts", "Roman SD.ttf")
    font = ImageFont.truetype(font_path, size=60)

    # Draw text
    wrapped_text = wrap_text(message, font, 800, draw)
    draw.multiline_text((250, 400), wrapped_text, font=font, fill="#537D5D",align="center", spacing=10)

    # Output
    output_path = os.path.join(template_folder, "final_image.png")
    image.save(output_path)

    return output_path


