from abc import ABC, abstractmethod
from models import Race
from PIL import Image
from PIL.PngImagePlugin import PngImageFile

class AbstractGenerator(ABC):
    def __init__(self, race:Race, filepath: str = './tmp.png'):
        self.race = race
        self.filepath = filepath

    def generate(self):
        base_img = self._generate_basic_image()
        self._add_content(base_img)
        base_img.save(self.filepath, quality=95)

    def _generate_basic_image(self) -> PngImageFile:
        with Image.open('assets/bg.png') as bg:
            base = bg.copy().convert('RGB')
        with Image.open('assets/bgmetal.png') as gray_filter:
            gray_filter = gray_filter.copy().resize((base.width, base.height)).convert('RGBA')
        gray_filter.putalpha(150)
        base.paste(gray_filter, gray_filter)
        return base

    @abstractmethod
    def _add_content(base_img: PngImageFile):
        pass