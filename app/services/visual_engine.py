from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
from pathlib import Path
from app.core.config import get_settings

settings = get_settings()


def calculate_region_brightness(image: Image.Image, region: str) -> float:
    """计算图片指定区域的亮度"""
    width, height = image.size
    img_rgb = image.convert("RGB")

    regions = {
        "top": (0, 0, width, height // 3),
        "bottom": (0, 2 * height // 3, width, height),
        "left": (0, 0, width // 3, height),
        "right": (2 * width // 3, 0, width, height),
        "center": (width // 4, height // 4, 3 * width // 4, 3 * height // 4),
    }

    bbox = regions.get(region, regions["bottom"])
    cropped = img_rgb.crop(bbox)
    pixels = list(cropped.getdata())
    avg = sum((r + g + b) / 3 for r, g, b in pixels) / len(pixels)
    return avg / 255.0


def choose_watermark_color(brightness: float) -> tuple:
    """根据亮度选择水印颜色"""
    if brightness < 0.5:
        return (255, 255, 255, 180)
    return (30, 30, 30, 180)


def auto_enhance(
    image_path: str,
    brightness_factor: float = 1.15,
    color_factor: float = 1.18,
    sharpness_factor: float = 1.12,
) -> str:
    """自动优化图片：提亮 + 增加色彩饱和度 + 锐化。
    返回原始图片路径（原地修改），不改变尺寸。
    """
    from PIL import Image, ImageEnhance

    img = Image.open(image_path).convert("RGB")
    original_width, original_height = img.size

    brightness = sum(img.convert("L").getdata()) / (img.width * img.height)

    if brightness < 100:
        brightness_factor = min(brightness_factor * 1.3, 1.35)
    elif brightness > 200:
        brightness_factor = max(brightness_factor * 0.5, 1.0)

    img = ImageEnhance.Brightness(img).enhance(brightness_factor)
    img = ImageEnhance.Color(img).enhance(color_factor)
    img = ImageEnhance.Sharpness(img).enhance(sharpness_factor)

    if img.size != (original_width, original_height):
        img = img.resize((original_width, original_height), Image.LANCZOS)

    img.save(image_path, "JPEG", quality=92)
    return image_path


def apply_watermark(
    image_url: str,
    output_path: str,
    watermark_text: str = "BIKON",
    position: str = "auto",
) -> str:
    """对图片添加水印"""
    img = Image.open(image_url).convert("RGBA")
    width, height = img.size

    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    font_size = max(width, height) // 20
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    positions = {
        "bottom_right": (width - text_w - 20, height - text_h - 20),
        "bottom_left": (20, height - text_h - 20),
        "top_right": (width - text_w - 20, 20),
        "top_left": (20, 20),
    }

    if position == "auto" or position not in positions:
        brightness = calculate_region_brightness(img.convert("RGB"), "bottom")
        pos = "bottom_right" if brightness > 0.5 else "bottom_right"
    else:
        pos = position

    x, y = positions.get(pos, positions["bottom_right"])
    brightness = calculate_region_brightness(
        img.convert("RGB"), "bottom" if "bottom" in pos else "top"
    )
    color = choose_watermark_color(brightness)

    draw.text((x, y), watermark_text, font=font, fill=color)

    watermarked = Image.alpha_composite(img, txt_layer).convert("RGB")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    watermarked.save(output_path, "JPEG", quality=92)
    return output_path
