from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from models import PilotResult

from helpers.generator_config import GeneratorConfig

from datetime import datetime, time
from font_factory import FontFactory
from generators.abstract_generator import AbstractGenerator
from helpers.transform import *


class FastestGenerator(AbstractGenerator):
    DEFAULT_TIME_STR = '--:--.---'
    DEFAULT_TIME = datetime.strptime('5:59.999','%M:%S.%f').time()

    def __init__(self, config: GeneratorConfig):
        super().__init__(config)
        ranking_data = []
        for index, pilot_data in self.config.ranking.iterrows():
            pos = index + 1
            if pilot_data[3] == self.DEFAULT_TIME_STR:
                fastest_time = self.DEFAULT_TIME
            else:
                fastest_time = datetime.strptime(pilot_data[3], '%M:%S.%f').time()
            ranking_data.append({
                'time': fastest_time,
                'pilot_result': PilotResult(self.config.race.get_pilot(pilot_data[0]), pos, pilot_data[1], pilot_data[2]),
            })
        self.ranking = sorted(ranking_data, key=lambda x: x['time'])

    def _get_visual_type(self) -> str:
        return 'fastest'

    def _add_content(self, final: PngImageFile):
        title_height = self._get_visual_title_height()

        h_padding = 60
        v_padding = 40
        first_top = title_height + v_padding
        content_width = (final.width - h_padding * 3)
        content_height = final.height - first_top
        first_height = (content_height // 2)

        # RACE
        race_left = h_padding
        race_width = content_width // 4
        first_width = content_width - race_width
        race_image = self._get_race_img(race_width, first_height)
        final.paste(race_image, (race_left, first_top), race_image)

        # FIRST
        first = self.ranking[0]
        first_image = self._get_fastest_lap_img(1, first_width, first_height, first['time'], first['pilot_result'])
        first_left = race_left + race_width + h_padding
        final.paste(first_image, (first_left, first_top), first_image)

        second_and_third_top = first_top + first_height + v_padding
        second_and_third_height = content_height - first_height - v_padding
        # three times the padding : before, between and after
        second_and_third_width = (final.width - h_padding * 3) // 2
        second = self.ranking[1]
        second_image = self._get_fastest_lap_img(
            2, second_and_third_width, second_and_third_height, second['time'], second['pilot_result'])
        second_left = h_padding
        final.paste(second_image, (second_left, second_and_third_top), second_image)

        third = self.ranking[2]
        third_image = self._get_fastest_lap_img(
            3, second_and_third_width, second_and_third_height, third['time'], third['pilot_result'])
        third_left = second_left + second_and_third_width + h_padding
        final.paste(third_image, (third_left, second_and_third_top), third_image)

    def _get_race_img(self, width: int, height: int):
        img = Image.new('RGBA', (width, height), (255, 255, 0, 0))
        bg = Image.new('RGB', (width, height))
        gradient(bg, direction=GradientDirection.LEFT_TO_RIGHT)
        img.paste(bg)

        circuit_name_top = 20
        circuit_name_color = (255, 255, 255)
        circuit_name_font = FontFactory.regular(60)
        circuit_name_img = text(self.config.race.circuit.name, circuit_name_color, circuit_name_font)

        with Image.open(f'assets/circuits/flags/{self.config.race.circuit.id}.png') as flag_img:
            flag_img = resize(flag_img, width-circuit_name_img.width, circuit_name_img.height)
            space_between = 10
            circuit_name_left = (width - (circuit_name_img.width + flag_img.width + space_between)) // 2
            flag_left = circuit_name_left + circuit_name_img.width + space_between
            flag_top = circuit_name_top + (circuit_name_img.height - flag_img.height) // 2
            img.paste(circuit_name_img, (circuit_name_left, circuit_name_top))
            img.paste(flag_img, (flag_left, flag_top), flag_img)

        v_padding = 20
        length_color = (180, 180, 180)
        length_font = FontFactory.regular(36)
        length_img = text(f'Longueur: {self.config.race.circuit.lap_length} KM', length_color, length_font)
        length_left = (width - length_img.width) // 2
        length_top = circuit_name_top + circuit_name_img.height + v_padding
        img.paste(length_img, (length_left, length_top), length_img)

        map_left = 20
        map_top = length_top + length_img.height + v_padding
        map_height = height - map_top
        with Image.open(f'assets/circuits/maps/{self.config.race.circuit.id}.png') as map:
            map = resize(map, width, map_height)
            img.paste(map, (map_left, map_top), map)
        return img

    def _get_fastest_lap_img(self, position: int, width: int, height: int, time: time, pilot_result: PilotResult):
        font_size = 200 if position == 1 else 100
        font = FontFactory.bold(font_size)
        img = Image.new('RGBA', (width, height), (255, 255, 0, 0))
        bg = Image.new('RGB', (width, height))
        gradient(bg, direction=GradientDirection.RIGHT_TO_LEFT)
        img.paste(bg)

        pos_img = self._get_position_image(position, font)
        img.alpha_composite(pos_img)

        txt_left = 0
        txt_img = self._get_textual_image(position, time, pilot_result, font)
        txt_top = height - txt_img.height - 20
        img.alpha_composite(txt_img, (txt_left, txt_top))

        team_left = txt_left + txt_img.width + 40
        team_img = self._get_team_image(pilot_result, position, font, max_height=height, max_width=width-team_left)
        img.alpha_composite(team_img, (team_left, 0))
        real_width = max(pos_img.width, txt_img.width) + team_img.width
        real_height = height
        return img.crop((0, 0, real_width, real_height)) if position == 1 else img

    def _get_position_image(self, position, font):
        ext_font = FontFactory.bold(font.size//2)
        color = (0, 0, 0, 0)
        border_color = (255, 255, 255)
        pos = str(position)
        stroke_width = 4
        if pos[-1] == '1':
            ext = 'ST'
        elif pos[-1] == '2':
            ext = 'ND'
        elif pos[-1] == '3':
            ext = 'RD'
        else:
            ext = 'TH'
        pos_img = text(pos, color, font, stroke_width=stroke_width, stroke_fill=border_color)
        ext_img = text(ext, color, ext_font, stroke_width=stroke_width, stroke_fill=border_color)

        width = pos_img.width + ext_img.width
        height = max(pos_img.height, ext_img.height)
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        img.paste(pos_img, (0, 0))
        img.paste(ext_img, (pos_img.width, 0))
        return img

    def _get_textual_image(self, position, lap_time, pilot_result, base_font):
        font = FontFactory.bold(base_font.size//3)
        small_font = FontFactory.regular(font.size-10)
        color = (255, 255, 255)

        pilot_img = text(pilot_result.pilot.name, color, font)

        if lap_time == self.DEFAULT_TIME:
            lap_time_txt = self.DEFAULT_TIME_STR
        else:
            lap_time_txt = f'{lap_time.minute}:{lap_time.strftime("%S")}.{str(lap_time.microsecond//1000).zfill(3)}'
        lap_time_img = text(lap_time_txt, color, font)

        add_point_img = text('+1 point', (200, 200, 0), small_font)

        space_between = 10
        height = add_point_img.height + space_between if position == 1 else 0
        height += pilot_img.height + space_between + lap_time_img.height
        width = max(pilot_img.width, lap_time_img.width, add_point_img.width)
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        if position == 1:
            img.paste(add_point_img, (0, 0))

        pilot_top = space_between + add_point_img.height if position == 1 else 0
        img.paste(pilot_img, (0, pilot_top))

        lap_time_top = pilot_top + pilot_img.height + space_between
        img.paste(lap_time_img, (0, lap_time_top))

        return img

    def _get_team_image(self, pilot_result, position, font, max_height, max_width):
        team = pilot_result.pilot.team
        with Image.open(f'assets/team_pilots/{team.name}.png') as team_pilot_img:
            team_pilot_img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            width = team_pilot_img.width
            img = Image.new('RGBA', (width, max_height), (0, 0, 0, 0))
            img.paste(team_pilot_img, (width - team_pilot_img.width, max_height - team_pilot_img.height), team_pilot_img)

        team_font = FontFactory.bold(50 if position == 1 else 30)
        team_img = pilot_result.pilot.team.get_team_image(team_pilot_img.width, team_font)
        img.alpha_composite(team_img, (width - team_img.width, img.height-team_img.height))
        return img
