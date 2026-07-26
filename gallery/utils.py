import io
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile


def generate_watermarked_preview(image_field, watermark_text="LightScape", max_width=1600, watermark_opacity=20):
    """
    Takes an uploaded image file, resizes it down (web-optimized),
    stamps a repeating diagonal watermark across it, and returns
    a ContentFile ready to be saved to preview_file.
    """
    img = Image.open(image_field)
    img = img.convert("RGBA")

    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        font_size = max(24, img.width // 22)
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    text = watermark_text
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]

    step_x = text_w + 100
    step_y = text_h + 100
    for y in range(-step_y, img.height + step_y, step_y):
        for x in range(-step_x, img.width + step_x, step_x):
            draw.text((x, y), text, font=font, fill=(255, 255, 255, watermark_opacity))

    overlay = overlay.rotate(30, expand=False)
    watermarked = Image.alpha_composite(img, overlay.resize(img.size))

    final_img = watermarked.convert("RGB")
    buffer = io.BytesIO()
    final_img.save(buffer, format="JPEG", quality=75, optimize=True)
    buffer.seek(0)

    return ContentFile(buffer.read())