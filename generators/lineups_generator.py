from PIL import Image

from models import *
from data import *

def _get_team_lineups_image(race: Race, teams: list, width:int, height:int):
    padding_bottom = 20
    lineup_height = height - padding_bottom

    img = Image.new('RGBA', (width, lineup_height), (255, 0, 0, 0))
    line_hop = 5
    line_height = int((lineup_height / 10) - line_hop)
    top = 0
    for team in teams:
        lineup_img = team.get_lineup_image(width, line_height, race.get_pilots(team))
        img.paste(lineup_img, (0, top))
        top += line_height + line_hop
    return img

def generate_lineup(race: Race, teams: list, filepath: str = './results.png'):
    visual = Visual(type='lineup', race=race)
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

        lineup_top = title_height + 30
        padding_h = 100
        team_lineups_image = _get_team_lineups_image(race, teams, final.width - (2 * padding_h), final.height - lineup_top)
        final.paste(team_lineups_image, (padding_h, lineup_top), team_lineups_image)

        final.save(filepath, quality=95)
