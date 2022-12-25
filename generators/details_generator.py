from PIL import Image
from PIL.PngImagePlugin import PngImageFile

from pandas import DataFrame

from models import *
from data import *
from font_factory import FontFactory
from generators.abstract_generator import AbstractGenerator

small_font = FontFactory.regular(32)
font = FontFactory.regular(38)
big_font = FontFactory.regular(56)
pilot_font = FontFactory.bold(30)

class DetailsGenerator(AbstractGenerator):
    def __init__(self, race:Race, ranking: DataFrame, fastest_lap:dict, filepath: str = './details.png'):
        super().__init__(race, filepath)
        self.ranking_data = ranking
        self.fastest_lap = fastest_lap

    def _add_content(self, final:PngImageFile):
        visual = Visual(type='result', race=self.race)

        title_height = 180
        title = visual.get_title_image(final.width, title_height)
        final.paste(title, title)

        top_h_padding = 20
        available_width = final.width - 2 * top_h_padding

        race_title_top = title_height + 20
        race_title_width = int(0.3 * available_width - top_h_padding)
        sub_title_height = 90
        date_font = FontFactory.regular(30)
        race_title_font = FontFactory.regular(50)

        # race_title_image = self.race.circuit.get_title_image(sub_title_height, race_title_font)
        race_title_image = self.race.get_title_image_simple(race_title_width, sub_title_height, date_font, race_title_font)
        race_title_left = 15
        final.paste(race_title_image, (race_title_left, race_title_top), race_title_image)

        fastest_lap_top = title_height + 20
        fastest_lap_left = race_title_width
        fastest_lap_width = int(0.7 * available_width - top_h_padding)
        fastest_lap_height = 90
        fastest_lap_img = self._get_fastest_lap_image(fastest_lap_width, fastest_lap_height)
        final.paste(fastest_lap_img, (fastest_lap_left, fastest_lap_top), fastest_lap_img)

        rankings_top = fastest_lap_top + fastest_lap_height + 30
        rankings_height = final.height - rankings_top
        rankings_img = self._get_ranking_image(final.width, rankings_height)
        final.paste(rankings_img, (0, rankings_top), rankings_img)

    def _get_fastest_lap_image(self, width: int, height: int):
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        with Image.open(f'assets/fastest_lap.png') as fstst_img:
            fstst_img.thumbnail((height, height), Image.Resampling.LANCZOS)
            img.paste(fstst_img)

        draw = ImageDraw.Draw(img)
        text_font = FontFactory.bold(40)
        text_content = 'FASTEST LAP'
        _,_, text_width, text_height = draw.textbbox((0,0), text_content, text_font)

        text_padding = 60
        black_box_width = text_width + 2 * text_padding
        black_box_left = fstst_img.width
        black_bg = Image.new('RGB', (black_box_width, height), (0,0,0))
        img.paste(black_bg, (black_box_left, 0))

        text_left = black_box_left + text_padding
        text_top = (height-text_height)//2
        draw.text((text_left, text_top), text_content, (180, 60, 220), text_font)

        pilot_bg_left = (black_box_left + black_box_width)
        pilot_bg_width = width - pilot_bg_left
        pilot_bg = Image.new('RGB', (pilot_bg_width, height), (20,20,20))
        alpha = Image.linear_gradient('L').rotate(-90).resize((pilot_bg_width,height))
        pilot_bg.putalpha(alpha)
        img.paste(pilot_bg, (pilot_bg_left, 0))

        pilot_and_lap_padding = 20
        pilot_and_lap_left = pilot_bg_left+pilot_and_lap_padding
        pilot_font = FontFactory.bold(45)
        lap_font = FontFactory.regular(25)
        lap_content = f'Lap {self.fastest_lap["lap"]}'
        _,_, pilot_width, pilot_height = draw.textbbox((0,0), self.fastest_lap['pilot_name'], pilot_font)
        _,_, lap_width, lap_height = draw.textbbox((0,0), lap_content, lap_font)
        space_between_pilot_and_lap = 10
        pilot_and_lap_height = pilot_height + lap_height + space_between_pilot_and_lap
        pilot_top = (height - pilot_and_lap_height) // 2
        lap_top = pilot_top + pilot_height + space_between_pilot_and_lap

        draw.text((pilot_and_lap_left, pilot_top), self.fastest_lap['pilot_name'], (255, 255, 255), pilot_font)
        draw.text((pilot_and_lap_left + (pilot_width-lap_width), lap_top), lap_content, (255, 255, 255), lap_font)

        time_font = FontFactory.bold(60)
        time_left = pilot_and_lap_left + max(pilot_width, lap_width) + 40
        _,_, time_width, time_height = draw.textbbox((0, 0), self.fastest_lap['time'], time_font)
        time_top = (height-time_height) // 2
        draw.text((time_left, time_top), self.fastest_lap['time'], (255, 255, 255), time_font)

        team_left = time_left + time_width + 40
        pilot = self.race.get_pilot(self.fastest_lap['pilot_name'])
        with Image.open(pilot.get_team_image()) as team_img:
            team_img.thumbnail((height, height), Image.Resampling.LANCZOS)
            img.paste(team_img, (team_left, 0), team_img)
        return img

    def _get_ranking_image(self, width: int, height: int):
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        top = 0
        hop_between_position = 38
        row_height = 60
        padding_left = 20
        padding_between = 40
        padding_right = 40
        col_width = (width - (padding_left+padding_between+padding_right)) // 2
        first_col_left = padding_left
        second_col_left = padding_left + col_width + padding_between

        maximum_split_size = 0
        for _, pilot_data in self.ranking_data.iterrows():
            _,_,w,h = ImageDraw.Draw(img).textbbox((0,0), pilot_data[1], small_font)
            if w > maximum_split_size:
                maximum_split_size = w
        for index, pilot_data in self.ranking_data.iterrows():
            # Get pilot
            pilot_name = pilot_data[0]
            pilot = self.race.get_pilot(pilot_name)

            pos = index + 1
            pilot_result = PilotResult(pilot, pos, pilot_data[1], pilot_data[2])

            left = first_col_left if index % 2 == 0 else second_col_left
            pilot_result_image = pilot_result.get_details_image(col_width, row_height, maximum_split_size)
            img.paste(pilot_result_image, (left, top))
            top += hop_between_position
        return img