import argparse
from data import teams_idx
from font_factory import FontFactory
from models import Visual
from helpers.transform import *
from PIL import Image, ImageDraw

class BreakingCommand(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument("main", help="Main (first) line of text")
        self.add_argument("second", help="Second line of text")
        self.add_argument("-t", "--team", help="Concerned team", dest='team', default=None)
        self.add_argument("-b", "--background", help="Background color to use (ignored if -t/--team is specified)", dest='bg', default="255,255,255")
        self.add_argument("-f", "--foreground", help="Foreground color to use (ignored if -t/--team is specified)", dest='fg', default="0,0,0")
        self.add_argument("-o", "--output", help="Output file to use", dest='output', default=None)
        self.add_argument("-i", "--input", help="Image to use as main picture", dest='input', default='assets/circuits/photos/belgium.png')

class Renderer:
    def __init__(self, main:str, second:str, team_name:str, bg:tuple, fg:tuple, output:str, input:str):
        self.bg_color = tuple(int(a) for a in bg.split(','))
        self.fg_color = tuple(int(a) for a in fg.split(','))
        self.main = main.upper()
        self.second = second.upper()
        self.output = output
        self.input = input
        self.team = teams_idx.get(team_name)
        if self.team:
            self.bg_color = self.team.standing_bg
            self.fg_color = self.team.standing_fg

    def render(self):
        with Image.open('assets/breaking/bg.png') as bg:
            final = bg.copy().convert('RGB')

        final = Image.new('RGB', (final.width, final.height), self.bg_color)
        top_breaking_height = 155
        bottom_message_height = 215
        space_top_middle = 30
        space_bottom_middle = 45
        middle_img_height = final.height - top_breaking_height - bottom_message_height - space_top_middle - space_bottom_middle

        top_img = self._get_top_breaking_img(bg.width, top_breaking_height)
        top_dim = paste(top_img, final, left=0, top=0, use_obj=True)

        middle_img = self._get_middle_picture_img(bg.width, middle_img_height)
        middle_dim = paste(middle_img, final, left=0, top=top_dim.bottom+space_top_middle, use_obj=True)

        bottom_img = self._get_bottom_message_img(bg.width, bottom_message_height)
        bottom_dim = paste(bottom_img, final, left=0, top=middle_dim.bottom+space_bottom_middle)

        final.save(args.output or 'breaking.png', quality=95)

    def _get_top_breaking_img(self, width:int, height:int):
        img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        left_padding = 25
        between_padding = 40
        with Visual.get_fbrt_logo(no_border=True) as logo:
            logo = resize(logo, int(0.15 * width), height)
            logo_dim = paste(logo, img, left_padding, use_obj=True, with_alpha=True)

        font = FontFactory.black(131)
        txt = text('BREAKING', self.fg_color, font)
        paste(txt, img, logo_dim.right + between_padding, use_obj=True)

        return img

    def _get_middle_picture_img(self, width:int, height:int):
        img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        with Image.open(self.input) as picture:
            paste(picture, img, left=0, top=0)
        draw = ImageDraw.Draw(img)
        #    -------------- (0,0) (185, 0)
        #   /             |
        #  /              |
        # /               | (0, 185)
        # |               |
        # |               | (width, height - 385)
        # |              /
        # |             /
        # |            /
        # ------------- (width-385, height) (width,height)
        upper_dim = 185
        upper_triangle = [
            (0,0),
            (upper_dim, 0),
            (0, upper_dim)
        ]
        lower_dim = 385
        lower_triangle = [
            (width, height - lower_dim),
            (width, height),
            (width - lower_dim, height)
        ]
        draw.polygon(upper_triangle, (0,0,0,0))
        draw.polygon(lower_triangle, (0,0,0,0))

        if self.team:
            with Image.open(self.team.get_image()) as team_img:
                paste(resize(team_img, 175, 175), img, width-team_img.width-30, height-team_img.height)
        return img

    def _get_bottom_message_img(self, width:int, height:int):
        img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        left_padding = 85
        right_padding = 45
        between_padding = 25

        main_font = FontFactory.black(84) # TODO compute auto
        main_txt = text(self.main, self.fg_color, main_font)
        main_left = width - main_txt.width - right_padding
        main_dim = paste(main_txt, img, top=0, left=main_left, use_obj=True)

        second_font = FontFactory.regular(50)
        second_txt = text(self.second, self.fg_color, second_font)
        second_left = width - second_txt.width - right_padding
        paste(second_txt, img, left=second_left, top=main_dim.bottom+between_padding, use_obj=True)

        return img

####### MAIN

args = BreakingCommand().parse_args()
Renderer(args.main, args.second, args.team, args.bg, args.fg, args.output, args.input).render()

