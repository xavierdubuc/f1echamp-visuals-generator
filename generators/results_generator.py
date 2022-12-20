from PIL import Image

from models import *
from data import *

def _get_rankings_image(race: Race, ranking: list, width: int, height: int):
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
    for index, pilot_name in enumerate(ranking):
        # Get pilot
        pilot = pilots.get(pilot_name, None)
        if not pilot:
            replaces = race.swappings[pilot_name]
            pilot = Pilot(name=pilot_name, team=replaces.team)

        pos = index + 1
        left = first_col_left if index % 2 == 0 else second_col_left
        ranking_pilot_image = pilot.get_ranking_image(pos, col_width, row_height, small_font, pilot_font)
        img.paste(ranking_pilot_image, (left, top))
        top += hop_between_position
    return img

def generate_results(race: Race, ranking: list, filepath: str = './results.png'):
    visual = Visual(type='result', race=race)
    with Image.open('assets/bg.png') as bg:
        final = bg.copy().convert('RGB')
        with Image.open('assets/bgmetal.png') as gray_filter:
            gray_filter = gray_filter.copy().resize((final.width, final.height)).convert('RGBA')
        gray_filter.putalpha(150)
        final.paste(gray_filter, gray_filter)

        # get top image
        title_height = 180
        title = visual.get_title_image(final.width, title_height)
        final.paste(title, title)

        race_title_height = 80
        right_part_width = final.width // 3
        right_part_height = final.height - title_height 
        left_part_width = final.width - right_part_width
        left_part_height = final.height - title_height - race_title_height
        # get race title
        race_title = race.get_title_image(left_part_width, left_part_height, font, big_font)
        final.paste(race_title, (0, title_height+48), race_title)

        # get circuit image
        circuit_left = int(2 * (final.width / 3))
        circuit_top = title_height + 20
        circuit_img = race.get_information_image(right_part_width, right_part_height, small_font)
        final.paste(circuit_img, (circuit_left, circuit_top), circuit_img)

        # get rankings image
        rankings_top = (title_height + race_title_height) + 80
        rankings_img = _get_rankings_image(race, ranking, left_part_width, left_part_height)
        final.paste(rankings_img, (0, rankings_top), rankings_img)
        final.save(filepath, quality=95)