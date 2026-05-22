import pytest
from PIL import Image
from pathlib import Path
from app.services.visual_engine import (
    calculate_region_brightness,
    choose_watermark_color,
    apply_watermark,
)


class TestCalculateRegionBrightness:
    def test_white_image_is_bright(self):
        img = Image.new("RGB", (300, 200), color=(255, 255, 255))
        brightness = calculate_region_brightness(img, "bottom")
        assert brightness > 0.95

    def test_black_image_is_dark(self):
        img = Image.new("RGB", (300, 200), color=(0, 0, 0))
        brightness = calculate_region_brightness(img, "bottom")
        assert brightness < 0.05

    def test_different_regions(self):
        """Bottom half white, top half black"""
        img = Image.new("RGB", (300, 200), color=(0, 0, 0))
        for x in range(300):
            for y in range(100, 200):
                img.putpixel((x, y), (255, 255, 255))

        bottom_brightness = calculate_region_brightness(img, "bottom")
        top_brightness = calculate_region_brightness(img, "top")
        assert bottom_brightness > 0.9
        assert top_brightness < 0.1


class TestChooseWatermarkColor:
    def test_dark_background_returns_white_watermark(self):
        color = choose_watermark_color(0.1)
        assert color == (255, 255, 255, 180)

    def test_light_background_returns_dark_watermark(self):
        color = choose_watermark_color(0.9)
        assert color == (30, 30, 30, 180)

    def test_threshold_boundary(self):
        """0.5 is the threshold — less than 0.5 = white, >= 0.5 = dark"""
        assert choose_watermark_color(0.49) == (255, 255, 255, 180)
        assert choose_watermark_color(0.5) == (30, 30, 30, 180)


class TestAutoEnhance:
    def test_enhances_dark_image(self, tmp_path):
        from PIL import Image
        img = Image.new("RGB", (200, 200), color=(50, 50, 50))
        input_path = str(tmp_path / "dark.jpg")
        img.save(input_path)
        from app.services.visual_engine import auto_enhance
        result = auto_enhance(input_path, brightness_factor=1.3, color_factor=1.2, sharpness_factor=1.1)
        enhanced = Image.open(result)
        pixels = list(enhanced.getdata())
        avg = sum((r + g + b) / 3 for r, g, b in pixels) / len(pixels)
        assert avg > 45, "Dark image should be brightened"

    def test_enhances_light_image_mildly(self, tmp_path):
        from PIL import Image
        img = Image.new("RGB", (200, 200), color=(220, 220, 220))
        input_path = str(tmp_path / "light.jpg")
        img.save(input_path)
        from app.services.visual_engine import auto_enhance
        result = auto_enhance(input_path)
        enhanced = Image.open(result)
        assert enhanced.size == (200, 200)

    def test_preserves_dimensions(self, tmp_path):
        from PIL import Image
        img = Image.new("RGB", (300, 150), color=(128, 128, 128))
        input_path = str(tmp_path / "rect.jpg")
        img.save(input_path)
        from app.services.visual_engine import auto_enhance
        result = auto_enhance(input_path)
        enhanced = Image.open(result)
        assert enhanced.size == (300, 150)


class TestApplyWatermark:
    def test_creates_output_file(self, tmp_path):
        img = Image.new("RGB", (200, 200), color=(100, 100, 100))
        input_path = tmp_path / "input.jpg"
        img.save(input_path)

        output_path = tmp_path / "output.jpg"
        result = apply_watermark(str(input_path), str(output_path), watermark_text="TEST")

        assert Path(result).exists()
        assert result == str(output_path)

        out_img = Image.open(result)
        assert out_img.size == (200, 200)

    def test_different_positions(self, tmp_path):
        img = Image.new("RGB", (200, 200), color=(100, 100, 100))
        input_path = tmp_path / "input.jpg"
        img.save(input_path)

        for pos in ["bottom_right", "bottom_left", "top_right", "top_left"]:
            output_path = tmp_path / f"output_{pos}.jpg"
            result = apply_watermark(str(input_path), str(output_path), watermark_text="X", position=pos)
            assert Path(result).exists()

    def test_auto_position(self, tmp_path):
        img = Image.new("RGB", (200, 200), color=(100, 100, 100))
        input_path = tmp_path / "input.jpg"
        img.save(input_path)

        output_path = tmp_path / "output_auto.jpg"
        result = apply_watermark(str(input_path), str(output_path), position="auto")
        assert Path(result).exists()
