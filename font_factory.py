from PIL import ImageFont
from config import REGULAR_FONT_PATH, BOLD_FONT_PATH

class FontFactory:
    @staticmethod
    def regular(size=32, **kwargs):
        return ImageFont.truetype(REGULAR_FONT_PATH, size, encoding="unic", **kwargs)

    def bold(size=32, **kwargs):
        return ImageFont.truetype(BOLD_FONT_PATH, size, encoding="unic", **kwargs)