from dataclasses import dataclass
from PIL.PngImagePlugin import PngImageFile
from PIL import Image, ImageDraw, ImageFont
from enum import Enum

from font_factory import FontFactory

@dataclass
class Dimension():
    left: int
    top: int
    right: int
    bottom: int

class GradientDirection(Enum):
    UP_TO_DOWN = -2
    DOWN_TO_UP = 2
    LEFT_TO_RIGHT = -1
    RIGHT_TO_LEFT = 1


def gradient(img: PngImageFile, direction: GradientDirection = GradientDirection.RIGHT_TO_LEFT):
    alpha = Image.linear_gradient('L').rotate(direction.value*90).resize((img.width, img.height))
    img.putalpha(alpha)

def get_round_corner_mask(img: PngImageFile, radius=50):
    mask = Image.new('1', (img.width, img.height), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle(((0,0), (mask.width, mask.height)), radius=radius, fill=1)
    return mask

def paste_rounded(bg: PngImageFile, img: PngImageFile, xy: tuple = (0, 0), radius=50):
    mask = get_round_corner_mask(img, radius)
    bg.paste(img, xy, mask)

def resize(img: PngImageFile, width, height, keep_ratio=True):
    if keep_ratio:
        img.thumbnail((width, height), Image.Resampling.LANCZOS)
        return img
    else:
        return img.resize((width, height))

def text_size(text:str, font:ImageFont.FreeTypeFont, img:PngImageFile=None, **kwargs):
    if not img:
        img = Image.new('RGB', (5000, 5000))
    draw = ImageDraw.Draw(img)
    _,_, width, height = draw.textbbox((0,0), text, font, **kwargs)
    return width, height

def text_on_gradient(txt: str, text_color, font:ImageFont.FreeTypeFont, padding=20, stroke_width=0, stroke_fill=None, **kwargs):
    txt_img = text(txt, text_color, font, stroke_width, stroke_fill, **kwargs)
    img = Image.new('RGBA', (txt_img.width+2*padding, txt_img.height+2*padding), (0, 0, 0, 0))
    gradient(img, GradientDirection.LEFT_TO_RIGHT)
    img.alpha_composite(txt_img, (padding, padding))
    return img

def text(text:str, text_color, font:ImageFont.FreeTypeFont, stroke_width=0, stroke_fill=None, **kwargs):
    width, height = text_size(text, font, stroke_width=stroke_width, **kwargs)
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, text_color, font, stroke_width=stroke_width, stroke_fill=stroke_fill, **kwargs)
    return img

def paste(img:PngImageFile, on_what:PngImageFile, left=False, top=False, with_alpha=None, use_obj=False):
    left = left if left is not False else (on_what.width-img.width) // 2
    top = top if top is not False else (on_what.height-img.height) // 2
    if with_alpha is True or (with_alpha is None and img.mode != 'RGB'):
        on_what.paste(img, (left, top), img)
    else:
        on_what.paste(img, (left, top))
    if not use_obj:
        return (left, top, left+img.width, top+img.height)
    return Dimension(left, top, left+img.width, top+img.height)

def get_max_font_size(text, width, height, Font=FontFactory.regular, initial_font_size=20):
    img = Image.new('RGB', (width, height))
    return determine_font_size(text, img, Font, initial_font_size)

def determine_font_size(text, img, Font=FontFactory.regular, initial_font_size=20):
    font_size = initial_font_size
    txt_width, txt_height = text_size(text, Font(font_size), img)
    height_offset = 10
    is_ascending = False
    while txt_width <= img.width-height_offset and txt_height <= img.height-height_offset:
        is_ascending = True
        font_size += 1
        txt_width, txt_height = text_size(text, Font(font_size), img)
    if is_ascending:
        return font_size - 1

    while txt_width >= img.width or txt_height >= img.height:
        font_size -= 1
        txt_width, txt_height = text_size(text, Font(font_size), img)
    return font_size