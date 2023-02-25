import os
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from models import Pilot, PilotResult, Visual

from helpers.generator_config import GeneratorConfig

from datetime import datetime, time
from font_factory import FontFactory
from generators.abstract_generator import AbstractGenerator
from helpers.transform import *


class PoleGenerator(AbstractGenerator):
    def _get_pole_pilot(self) -> Pilot:
        return self.config.race.get_pilot('majforti-07')

    def _get_visual_type(self) -> str:
        return 'pole'

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        return None

    def _generate_basic_image(self) -> PngImageFile:
        pole_pilot = self._get_pole_pilot()
        with Image.open('assets/pole/bg.png') as img:
            base = Image.new('RGB', (img.width, img.height), color=pole_pilot.team.breaking_bg_color)
        return base

    def _get_pilot_image(self, pilot:Pilot, width, height):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        possible_img_paths = [
            f'assets/pole/celebrating/{pilot.name}.png',
            f'assets/pole/celebrating/{pilot.team.name}_default.png',
            f'assets/pilots/1080x1080/{pilot.name}.png',
            f'assets/pilots/real_no_bg/{pilot.name}.png',
            f'assets/pilots/real/{pilot.name}.png',
            f'assets/pilots/1080x1080/{pilot.team.name}_default.png',
            f'assets/team_pilots/{pilot.team.name}.png'
        ]
        for img_path in possible_img_paths:
            if os.path.exists(img_path):
                break

        with Image.open(img_path) as team_pilot_img:
            img = resize(team_pilot_img, width, height)
            return img.copy()

    def _get_podium_img(self):
        color = (255, 255, 255)
        first = self._get_pole_pilot()
        second = self.config.race.get_pilot('Gros-Nain-Vert')
        third = self.config.race.get_pilot('DimDim_91270')
        separator = '  /  '
        full_text = f'1st {first.name}{separator}2nd {second.name}{separator}3rd {third.name}'.upper()
        Font = FontFactory.regular
        font = Font(24)
        width, height = text_size(full_text, font)
        img = Image.new('RGBA', (width, height), (0,0,0,0))

        first_pos_img = get_ordinal_img(1, color=color, Font=Font)
        first_pos_pos = paste(first_pos_img, img, left=0, use_obj=True)
        first_name_img = text(f'{first.name}{separator}'.upper(), color, font)
        first_name_pos = paste(first_name_img, img, first_pos_pos.right, use_obj=True)

        second_pos_img = get_ordinal_img(2, color=color, Font=Font)
        second_pos_pos = paste(second_pos_img, img, left=first_name_pos.right, use_obj=True)
        second_name_img = text(f'{second.name}{separator}'.upper(), color, font)
        second_name_pos = paste(second_name_img, img, second_pos_pos.right, use_obj=True)

        third_pos_img = get_ordinal_img(3, color=color, Font=Font)
        third_pos_pos = paste(third_pos_img, img, left=second_name_pos.right, use_obj=True)
        third_name_img = text(f'{third.name}'.upper(), color, font)
        paste(third_name_img, img, third_pos_pos.right)
        return img

    def _add_content(self, final: PngImageFile):
        pole_pilot = self._get_pole_pilot()
        draw_lines(final, pole_pilot.team.breaking_line_color, space_between_lines=10, line_width=2)
        repeat_text(final, (0,0,0, 177), pole_pilot.name.upper(), Font=FontFactory.polebg, font_size=200)

        with Visual.get_fbrt_logo(True) as logo:
            paste(resize(logo, final.width//5, final.height//5), final, left=30, top=30)
        # PILOT IMG
        pilot_img = self._get_pilot_image(pole_pilot, final.width, final.height)
        paste(pilot_img, final)


        # GRADIENT
        img_filter = Image.new('RGB', (final.width, final.height//2), pole_pilot.team.breaking_line_color)
        gradient(img_filter, GradientDirection.DOWN_TO_UP)
        paste(img_filter, final, top=final.height//2)
        # POLE TEXT
        pole_txt_img = rotated_text('POLE', (255,255,255,0), FontFactory.black(360),
                           stroke_width=15, stroke_fill=(255,255,255), angle=15)
        paste(pole_txt_img, final, top=int(0.363 * final.height))

        # PODIUM TEXT
        podium_img = self._get_podium_img()
        paste(podium_img, final, top=final.height-60)
