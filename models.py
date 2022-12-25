from dataclasses import dataclass
from PIL import Image, ImageDraw
from config import REGULAR_FONT_PATH, BOLD_FONT_PATH
from font_factory import FontFactory

@dataclass
class Team:
    name: str
    title: str
    subtitle: str
    main_color: str = 'white'
    secondary_color: str = 'black'
    box_color: str = 'black'

    def get_image(self):
        return f'assets/teams/{self.name}.png'

    def get_lineup_image(self, width, height, pilots):
        # team

        img = Image.new('RGBA', (width,height), (0,0,0,0))

        font_size = 28
        small_font_size = font_size - 8
        line_separation = font_size + 4
        box_width = 10
        box_height = font_size+line_separation
        # Build an alpha/transparency channel
        bg = Image.new('RGB', (width, box_height))
        alpha = Image.linear_gradient('L').rotate(90).resize((width,box_height))
        bg.putalpha(alpha)

        img.paste(bg)
        draw = ImageDraw.Draw(img)
        
        big_font = FontFactory.regular(font_size+10)
        font = FontFactory.bold(font_size)
        small_font = FontFactory.regular(small_font_size)

        # box
        draw.rectangle(((0,0), (box_width, box_height)), fill=self.box_color)

        # Name
        padding_top = 4
        padding_after_box = box_width + 20
        draw.text(
            (padding_after_box, padding_top),
            self.title.upper(),
            fill=(255, 255, 255),
            font=font
        )
        draw.text(
            (padding_after_box, padding_top+line_separation),
            self.subtitle,
            fill=(255, 255, 255),
            font=small_font
        )

        # logo
        with Image.open(self.get_image()) as team_image:
            padding = 4
            image_size = box_height - padding
            left = width // 3 - team_image.width - 10
            top = 0
            team_image.thumbnail((image_size, image_size), Image.Resampling.LANCZOS)
            img.paste(team_image, (left, top), team_image)

        left = width // 3 + 20
        draw = ImageDraw.Draw(img)
        padding_top = 12
        for pilot in pilots:

            # NUMBER
            pos_left = left + (0 if len(pilot.number) == 2 else 10)
            draw.text(
                (pos_left, padding_top),
                pilot.number,
                fill=self.secondary_color,
                stroke_fill=self.main_color,
                stroke_width=2,
                font=big_font
            )

            # NAME
            left_name = 70
            draw.text(
                (left+left_name, padding_top),
                pilot.name,
                fill=(255, 255, 255),
                font=big_font
            )
            left = int(2 * (width / 3)) + 20 * 2
        return img

@dataclass
class Pilot:
    name: str
    team: Team = None
    number: str = 'Re'
    title: str = None

    def get_team_image(self):
        return self.team.get_image() if self.team else ''

    def get_image(self, width: int, height: int, number_font, pilot_font):
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        draw_canvas = ImageDraw.Draw(img)
        # NUMBER
        pos_left = 2 if len(self.number) == 2 else 12
        draw_canvas.text(
            (pos_left, 14),
            self.number,
            fill=self.team.secondary_color,
            stroke_fill=self.team.main_color,
            stroke_width=3,
            font=number_font
        )

        # NAME
        left_name = 70
        draw_canvas.text(
            (left_name, 14),
            self.name,
            (255,255,255),
            pilot_font
        )

        # TEAM
        with Image.open(self.get_team_image()) as team_image:
            padding = 4
            image_size = height - padding
            team_image.thumbnail((image_size, image_size), Image.Resampling.LANCZOS)
            img.paste(team_image, ((width - team_image.width) - padding, padding//2), team_image)

        return img

    def get_ranking_image(self, position:int, width: int, height: int, number_font, pilot_font, has_fastest_lap:bool = False):
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))

        if has_fastest_lap:
            bg_color = (180, 60, 220)
        else:
            bg_color = (0,0,0)
        grid_position_bg = Image.new('RGB', (width, height), bg_color)
        alpha = Image.linear_gradient('L').rotate(-90).resize((width,height))
        grid_position_bg.putalpha(alpha)
        img.paste(grid_position_bg, (5,0))

        white_box_width = height
        with Image.open(f'assets/results/positions/{position}.png') as tmp:
            grid_position_number = tmp.copy().convert('RGBA')
            grid_position_number.thumbnail((white_box_width, height), Image.Resampling.LANCZOS)
            img.paste(grid_position_number, grid_position_number)

        pilot_image = self.get_image(width - (white_box_width+15), height, number_font, pilot_font)
        img.paste(pilot_image, (white_box_width+15, 0), pilot_image)
        if has_fastest_lap:
            with Image.open(f'assets/fastest_lap.png') as fstst_img:
                fstst_img.thumbnail((height, height), Image.Resampling.LANCZOS)
                img.paste(fstst_img, (width-fstst_img.width * 2, 0))

        return img

@dataclass
class Circuit:
    id: str
    name: str
    lap_length: float
    best_lap: str

    def get_title_image(self, height:int, font):
        tmp = Image.new('RGBA', (5000, height), (255, 0, 0, 0))
        tmp_draw = ImageDraw.Draw(tmp)
        # circuit name
        _,_,text_width,text_height = tmp_draw.textbbox((0,0), self.name, font)
        text_top = (height - text_height) // 2
        # flag
        with Image.open(f'assets/circuits/flags/{self.id}.png') as flag:
            flag.thumbnail((height,height), Image.Resampling.LANCZOS)

            padding_between = 30
            width = text_width + flag.width + padding_between
            img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            flag_left = text_width + padding_between
            draw.text((0, text_top), self.name, (255, 255, 255), font)
            img.paste(flag, (flag_left, text_top), flag)
        return img

@dataclass
class Race:
    round: int
    laps: int
    day: str
    month: str
    hour: str
    circuit: Circuit
    pilots: dict
    swappings: dict = None

    def get_total_length(self):
        return self.laps * self.circuit.lap_length

    def get_title(self):
        return f'RACE {self.round} RESULT'

    def get_title_image(self, width: int, height: int, font, big_font):
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        # bg
        with Image.open(f'assets/results/bgdate.png') as bg_date:
            bg_date.thumbnail((int(3 * width / 4), height), Image.Resampling.LANCZOS)
        img.paste(bg_date)
        draw_canvas = ImageDraw.Draw(img)
        left = 20
        top = 0
        # day
        draw_canvas.text((left,top+15), f'{self.day}.', 'white', font)
        # month
        draw_canvas.text((left+80,top+15), self.month, 'grey', font)
        # circuit name
        draw_canvas.text((left+250,top+5), self.circuit.name, 'white', big_font)
        # flag
        with Image.open(f'assets/circuits/flags/{self.circuit.id}.png') as flag:
            flag.thumbnail((100,100), Image.Resampling.LANCZOS)
            img.paste(flag, (bg_date.width - flag.width - 10, top-2), flag)
        return img

    def get_title_image_simple(self, width:int, height:int, date_font, circuit_font):
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        day_left = 10
        _,_,day_width,day_height = draw.textbbox((0,0), f'{self.day}.', date_font)
        _,_,month_width, month_height = draw.textbbox((0,0), self.month, date_font)
        day_top = (height-day_height) // 2
        month_top = (height-month_height) // 2
        month_left = day_left+day_width + 10

        # day
        draw.text((day_left, day_top), f'{self.day}.', 'white', date_font)
        # month
        draw.text((month_left,month_top), self.month, 'grey', date_font)

        circuit_img = self.circuit.get_title_image(height, circuit_font)
        circuit_top = (height-circuit_img.height) // 2
        circuit_left = month_left + month_width + 20
        img.paste(circuit_img, (circuit_left, circuit_top), circuit_img)
        return img

    def get_just_information_image(self, width: int, height: int, font):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        bg_top = 0
        bg = Image.new('RGB', (width, height), (80, 80, 80))
        alpha = Image.linear_gradient('L').rotate(90).resize((width, height))
        # alpha = alpha.crop((alpha.width/2, 0, alpha.width, alpha.height)).resize((width, height))
        bg.putalpha(alpha)
        img.paste(bg, (0, bg_top), bg)

        draw_canvas = ImageDraw.Draw(img)
        with Image.open('assets/results/redcorner.png') as red_corner:
            red_corner = red_corner.convert('RGBA')
            img.paste(red_corner, (0, bg_top), red_corner)
        draw_canvas.rectangle(((0,bg_top+red_corner.height), (9, bg_top+red_corner.height+325)), fill=(255, 0, 0))
        draw_canvas.rectangle(((red_corner.width-2,bg_top), (width, bg_top+9)), fill=(255, 0, 0))

        # infos
        title_color = (0,0,0)
        info_color = (255, 255, 255)
        draw_canvas.text((50,bg_top+50), f'Longueur', title_color, font)
        draw_canvas.text((350,bg_top+50), f'Nombre de tours', title_color, font)
        draw_canvas.text((50,bg_top+100), f'{self.circuit.lap_length} Km', info_color, font)
        draw_canvas.text((350,bg_top+100), f'{self.laps} tours', info_color, font)
        draw_canvas.text((50,bg_top+175), f'Distance totale', title_color, font)
        draw_canvas.text((50,bg_top+225), f'{self.get_total_length()} Km', info_color, font)
        draw_canvas.text((50,bg_top+300), f'Meilleur temps', title_color, font)
        draw_canvas.text((50,bg_top+350), f'{self.circuit.best_lap}', info_color, font)

        # map
        with Image.open(f'assets/circuits/maps/{self.circuit.id}.png') as map:
            map.thumbnail((width, height//2), Image.Resampling.LANCZOS)
            img.paste(map, (width - map.width, height - map.height), map)
        return img

    def get_information_image(self, width: int, height: int, font):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        # photo
        with Image.open(f'assets/circuits/photos/{self.circuit.id}.png') as photo:
            photo.thumbnail((width, height), Image.Resampling.LANCZOS)
            alpha = Image.linear_gradient('L').rotate(180).resize((photo.width, photo.height))
            alpha = alpha.crop((0, 0, alpha.width, alpha.height/2)).resize((photo.width, photo.height))
            photo.putalpha(alpha)
            img.paste(photo)

        bg_top = int(3 * (photo.height / 4))
        bg = Image.new('RGB', (width, height), (120, 120, 120))
        alpha = Image.linear_gradient('L').rotate(90).resize((width, height))
        alpha = alpha.crop((alpha.width/2, 0, alpha.width, alpha.height)).resize((width, height))
        bg.putalpha(alpha)
        img.paste(bg, (0, bg_top), bg)

        draw_canvas = ImageDraw.Draw(img)
        with Image.open('assets/results/redcorner.png') as red_corner:
            red_corner = red_corner.convert('RGBA')
            img.paste(red_corner, (0, bg_top), red_corner)
        draw_canvas.rectangle(((0,bg_top+red_corner.height), (9, bg_top+red_corner.height+300)), fill=(255, 0, 0))
        draw_canvas.rectangle(((red_corner.width-2,bg_top), (width, bg_top+9)), fill=(255, 0, 0))

        # infos
        title_color = (0,0,0)
        info_color = (255, 255, 255)
        draw_canvas.text((50,bg_top+25), f'Longueur', title_color, font)
        draw_canvas.text((350,bg_top+25), f'Nombre de tours', title_color, font)
        draw_canvas.text((50,bg_top+75), f'{self.circuit.lap_length} Km', info_color, font)
        draw_canvas.text((350,bg_top+75), f'{self.laps} tours', info_color, font)
        draw_canvas.text((50,bg_top+150), f'Distance totale', title_color, font)
        draw_canvas.text((50,bg_top+200), f'{self.get_total_length()} Km', info_color, font)
        draw_canvas.text((50,bg_top+275), f'Meilleur temps', title_color, font)
        draw_canvas.text((50,bg_top+325), f'{self.circuit.best_lap}', info_color, font)

        # map
        with Image.open(f'assets/circuits/maps/{self.circuit.id}.png') as map:
            map.thumbnail((625, 5000), Image.Resampling.LANCZOS)
            img.paste(map, (width - map.width, height - map.height), map)
        return img

    def get_pilots(self, team):
        main_pilots = [pilot for pilot in self.pilots.values() if pilot.team == team]
        if not self.swappings or len(self.swappings) == 0:
            return main_pilots
        else:
            out = []
            for pilot in main_pilots:
                pilot_to_append = pilot
                for replace_name, replaced_pilot in self.swappings.items():
                    if replaced_pilot == pilot:
                        pilot_to_append = Pilot(name=replace_name, team=team)
                        break
                out.append(pilot_to_append)
            return out

    def get_pilot(self, pilot_name:str) -> Pilot:
        pilot = self.pilots.get(pilot_name, None)
        if not pilot:
            replaces = self.swappings.get(pilot_name)
            if not replaces:
                pilot_name = 'Unknown'
                team = self._default_team # FIXME redbull is used as default value, maybe create a fake team instead
            else:
                team = replaces.team
            pilot = Pilot(name=pilot_name, team=team)
        return pilot

    _default_team = Team(
        name='RedBull',
        title='Unknown',
        subtitle="Team",
        main_color=(0,0,0),
        secondary_color=(0, 0, 0),
        box_color= (0,0,0)
    )

@dataclass
class Visual:
    type: str
    race: Race

    def get_title_image(self, width:int, height: int):
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        # background
        with Image.open(f'assets/results/bgtop.png') as tmp:
            bg_top = tmp.copy().convert('RGBA')
            bg_top.thumbnail((width, height), Image.Resampling.LANCZOS)
            img.paste(bg_top, (0, 0), bg_top)

        # FBRT logo
        with Image.open(f'assets/fbrt.png') as fbrt:
            fbrt.thumbnail((width//3, height), Image.Resampling.LANCZOS)
            left = (width//3 - fbrt.width) // 2 # centered in the left cell
            top = (height-fbrt.height)//2 # centered
            img.paste(fbrt, (left, top), fbrt)

        # Title
        if self.type == 'result':
            title = self._get_race_result_title(width//3, height)
            top = (height - title.height) // 2 # centered
        elif self.type == 'lineup':
            title = self._get_race_lineup_title(width//3, height)
            top = height // 3
        elif self.type == 'presentation':
            title = self._get_race_presentation_title(width//3, height)
            top = height // 3
        left = (width - title.width) // 2 # centered
        img.paste(title, (left, top), title)

        # F1 22
        logof1 = 'f122_black' if self.type == 'presentation' else 'f122'
        with Image.open(f'assets/{logof1}.png') as f122:
            f122.thumbnail((width//4, height), Image.Resampling.LANCZOS)
            left = (width - f122.width) - 40 # right aligned, with a small padding
            top = (height-f122.height)//2 # centered
            img.paste(f122, (left, top), f122)
        return img

    def _get_race_result_title(self, width, height):
        with Image.open(f'assets/race_numbers/Race{self.race.round}.png') as title:
            title.thumbnail((width, height), Image.Resampling.LANCZOS)
            return title

    def _get_race_lineup_title(self, width, height):
        if len(str(self.race.round)) == 1:
            font_size = 68
            padding_right = 60
        else:
            font_size = 64
            padding_right = 90
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        font = FontFactory.bold(font_size)
        draw_img = ImageDraw.Draw(img)
        draw_img.text((0,0), 'LINE UP - RACE', (255, 255, 255), font)
        draw_img.text((width-padding_right,0), f'{self.race.round}', (255, 0, 0), font)
        return img

    def _get_race_presentation_title(self, width, height):
        font_size = 68
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        font = FontFactory.bold(font_size)
        draw_img = ImageDraw.Draw(img)
        _, _, whole_width, _ = draw_img.textbbox((0, 0), f'RACE {self.race.round}', font)
        _, _, race_width, _ = draw_img.textbbox((0, 0), f'RACE', font)
        race_left = (width-whole_width) // 2
        number_left = race_left + race_width + 20
        draw_img.text((race_left,0), 'RACE', (255, 255, 255), font)
        draw_img.text((number_left,0), f'{self.race.round}', (255, 0, 0), font)
        return img

@dataclass
class PilotResult:
    pilot: Pilot
    position: int
    split: str
    tyres: str

    def get_details_image(self, width:int, height:int, largest_split_width:int):
        small_font = FontFactory.regular(32)
        pilot_font = FontFactory.bold(30)
        pilot_image = self.pilot.get_ranking_image(self.position, width, height, small_font, pilot_font, False)
        draw = ImageDraw.Draw(pilot_image)
        split = self.split if (self.position == 1 or self.split in ('NT', 'DSQ')) else f'+{self.split}'
        _,_,real_split_width, split_height = draw.textbbox((0,0), split, small_font)
        diff = largest_split_width - real_split_width
        pilot_right = 460

        split_left = pilot_right + diff
        draw.text((split_left, (height-split_height)//2), split, (255, 255, 255), small_font)

        current_left = split_left+real_split_width + 20
        for tyre in self.tyres:
            with Image.open(f'./assets/tyres/{tyre}.png') as tyre_img:
                tyre_img.thumbnail((height, height))
                pilot_image.paste(tyre_img, (current_left, 0), tyre_img)
                # tyre_img has a transparent contour
                current_left += (tyre_img.width-12)

        return pilot_image
