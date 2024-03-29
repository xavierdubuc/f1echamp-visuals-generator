from dataclasses import dataclass
from datetime import datetime
import pandas
from helpers.reader import Reader
from data import circuits as CIRCUITS

@dataclass
class CalendarGeneratorConfig:
    races: list
    season: int
    type: str
    output: str


class CalendarReader(Reader):
    def __init__(self, type: str, filepath: str = './data.xlsx', out_filepath: str = None, season: int = 4):
        super().__init__(type, filepath, None, out_filepath)
        self.season = season

    def read(self):
        races = self._get_races_details()
            
        config = CalendarGeneratorConfig(
            type=self.type,
            season=self.season,
            races=races,
            output=self.out_filepath or f'./output/{self.type}.png',
        )
        return config

    def _get_races_details(self):
        spreadsheet = self._get_google_spreadsheet()
        sheet_names = self._get_sheet_names_from_gsheet(spreadsheet)

        races = []
        for sheet_name in sheet_names:
            if sheet_name[:4] == 'Race':
                race_vals = spreadsheet.values().get(spreadsheetId=self.spreadsheet_id, range=f"'{sheet_name}'!A1:B22").execute()['values']
                df = pandas.DataFrame(race_vals[1:], columns=['A','B'])
                race = {
                    'index': df['B'][0],
                    'circuit': CIRCUITS.get(df['B'][1], None),
                    'type': df['B'][20],
                    'date': datetime.strptime(f"{df['B'][3]}/{datetime.now().year}", '%d/%m/%Y').date(),
                    'hour': df['B'][4]
                }
                races.append(race)

        return races
