from PIL import ImageFont
from config import REGULAR_FONT_PATH, BOLD_FONT_PATH

class FontFactory:
    @staticmethod
    def regular(size=32, **kwargs) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(REGULAR_FONT_PATH, size, encoding="unic", **kwargs)

    @staticmethod
    def bold(size=32, **kwargs) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(BOLD_FONT_PATH, size, encoding="unic", **kwargs)