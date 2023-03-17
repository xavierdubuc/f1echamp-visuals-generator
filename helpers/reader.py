from dataclasses import dataclass
from datetime import datetime
import logging
import os.path
import pandas
from helpers.generator_config import FastestLap, GeneratorConfig
from models import Pilot, Race
from data import circuits, teams_idx
from data import (
    teams as DEFAULT_TEAMS_LIST,
    pilots as DEFAULT_PILOTS_LIST,
    DEFAULT_TEAM,
    RESERVIST_TEAM
)


_logger = logging.getLogger(__name__)

@dataclass
class InputData:
    sheet_names: list
    sheet_values: pandas.DataFrame
    sheet_data: pandas.DataFrame = None

class Reader:
    VALUES_SHEET_NAME = '_values'
    DEFAULT_SPREADSHEET_ID = '1JJw3YnVUXYCyjhH4J5MIbVg5OtjTIDLptx0pF2M9KV4'

    def __init__(self, type: str, filepath: str = './data.xlsx', sheet_name: str = None, out_filepath: str = None):
        self.filepath = filepath
        if self.filepath.startswith('gsheet'):
            parts = self.filepath.split(':')
            self.spreadsheet_id = parts[1] if len(parts) > 1 else self.DEFAULT_SPREADSHEET_ID
        else:
            self.spreadsheet_id = None
        self.sheet_name = sheet_name
        self.type = type
        self.out_filepath = out_filepath

    def read(self):
        pilots, teams = self._read()
        race = self._get_race(pilots, teams) if self.type != 'numbers' else None
        config = GeneratorConfig(
            type=self.type,
            output=self.out_filepath or f'./{self.type}.png',
            pilots=pilots,
            teams=teams,
            race=race
        )
        if self.type == 'presentation':
            config.description = self.data['A'][6]
        if self.type in ('pole', 'grid'):
            config.qualif_ranking = [
                race.get_pilot(self.data['G'][29]),
                race.get_pilot(self.data['G'][30]),
                race.get_pilot(self.data['G'][31]),
            ]
        if self.type in ('results', 'details', 'fastest', 'grid'):
            config.ranking = self._get_ranking()
        if self.type in ('results', 'details'):
            config.fastest_lap = self._get_fastest_lap(race)
        return config

    def _determine_swappings(self, pilots):
        replacements = self.data[['D', 'E']].where(lambda x: x != '', pandas.NA).dropna()
        out = {}
        for _, row in replacements.iterrows():
            subs = row['E']
            while out.get(subs) and len(subs) < 22:
                subs += ' '
            out[subs] = pilots.get(row['D'])
        return out

    def _build_pilots_list(self, values: pandas.DataFrame):
        return {
            row['Pilotes']: Pilot(name=row['Pilotes'], team=teams_idx.get(row['Ecurie'], RESERVIST_TEAM if row['Ecurie'] == 'R' else DEFAULT_TEAM), number=str(int(row['Numéro'])))
            for _, row in values[values['Pilotes'].notnull()].iterrows()
        }

    def _build_teams_list(self, values: pandas.DataFrame):
        return [
            teams_idx[row['Ecuries']] for _, row in values.dropna().iterrows()
        ]

    def _read(self):
        if self.spreadsheet_id:
            input_data = self._get_data_from_gsheet()
        else:
            input_data = self._get_data_from_xlsx()

        pilots, teams = self._determine_pilots_and_teams(input_data.sheet_values)
        self.data = input_data.sheet_data
        return pilots, teams

    def _determine_pilots_and_teams(self, sheet_values):
        if sheet_values is not None:
            pilots_values = sheet_values[['Pilotes', 'Numéro', 'Ecurie']]
            pilots = self._build_pilots_list(pilots_values)
            teams_values = sheet_values[['Ecuries']]
            teams = self._build_teams_list(teams_values)
        else:
            pilots = DEFAULT_PILOTS_LIST
            teams = DEFAULT_TEAMS_LIST
        return pilots, teams

    def _get_race(self, pilots, teams):
        race_day = self.data['B'][3]
        if isinstance(race_day, str):
            race_day = datetime.strptime(race_day, '%d/%m')
        hour = self.data['B'][4]
        if isinstance(hour, str):
            hour = datetime.strptime(hour, '%H:%M')

        return Race(
            round=self.data['B'][0],
            laps=int(self.data['B'][2]),
            circuit=circuits[self.data['B'][1]],
            day=race_day.day,
            month=race_day.strftime('%b'),
            hour=hour.strftime('%H.%M'),
            pilots=pilots,
            teams=teams,
            type=self.data['B'][20],
            swappings=self._determine_swappings(pilots)
        )

    def _get_ranking(self):
        ranking_cols = ['I', 'J', 'K', 'L']
        if self.type == 'results':
            ranking_cols = 'I'
        return self.data[ranking_cols][:20]

    def _get_fastest_lap(self, race:Race):
        vals = {'pilot_name': self.data['G'][22]}
        if self.type == 'details':
            vals.update({
                'lap': self.data['G'][24],
                'time': self.data['G'][26]}
            )

        return FastestLap(
            pilot=race.get_pilot(vals['pilot_name']),
            lap=vals.get('lap'),
            time=vals.get('time')
        )

    def _get_sheet_names_from_gsheet(self, spreadsheet):
        res = spreadsheet.get(spreadsheetId=self.spreadsheet_id).execute()
        return [s['properties']['title'] for s in res['sheets']]

    def _get_values_sheet_from_gsheet(self, spreadsheet):
        sheet_names = self._get_sheet_names_from_gsheet(spreadsheet)

        if self.VALUES_SHEET_NAME in sheet_names:
            vals = spreadsheet.values().get(spreadsheetId=self.spreadsheet_id, range='_values!A1:G25').execute()
            sheet_values = pandas.DataFrame(vals['values'][1:], columns=vals['values'][0])
        else:
            sheet_values = None
        return sheet_values

    def _get_data_sheet_from_gsheet(self, spreadsheet):
        race_vals = spreadsheet.values().get(spreadsheetId=self.spreadsheet_id, range=f"'{self.sheet_name}'!A1:L33").execute()['values']
        columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'][:len(race_vals[1])]
        return pandas.DataFrame(race_vals[1:], columns=columns)

    def _get_data_from_gsheet(self) -> InputData:
        spreadsheet = self._get_google_spreadsheet()
        sheet_names = self._get_sheet_names_from_gsheet(spreadsheet)
        sheet_values = self._get_values_sheet_from_gsheet(spreadsheet)

        if not self.sheet_name:
            sheet_data = None
        else:
            if self.sheet_name not in sheet_names:
                raise Exception(f'{self.sheet_name} is not a valid sheet name, please select a sheet within possible values : {sheet_names}')
            sheet_data = self._get_data_sheet_from_gsheet(spreadsheet)

        _logger.info(f'Data have been read from google spreadsheet "{self.spreadsheet_id}"')
        return InputData(
            sheet_names=sheet_names,
            sheet_values=sheet_values,
            sheet_data=sheet_data
        )

    def _get_data_from_xlsx(self) -> InputData:
        sheet_values = None
        with pandas.ExcelFile(self.filepath) as xls:
            if self.VALUES_SHEET_NAME in xls.sheet_names:
                sheet_values = pandas.read_excel(xls, self.VALUES_SHEET_NAME)[['Pilotes', 'Numéro', 'Ecurie', 'Ecuries']]

            if self.sheet_name not in xls.sheet_names:
                raise Exception(f'Please select a sheet within possible values : {xls.sheet_names}')
            names = self._get_sheet_columns()
            sheet_data = pandas.read_excel(xls, self.sheet_name, usecols=names, names=names)
            _logger.info(f'Data have been read from file "{os.path.realpath(self.filepath)}"')
            return InputData(
                sheet_names=xls.sheet_names,
                sheet_values=sheet_values,
                sheet_data=sheet_data
            )

    def _get_sheet_columns(self) -> list:
        if self.type in ('details', 'fastest'):
            return ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        if self.type == 'results':
            return ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        return ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    def _get_google_spreadsheet(self):
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('sheets', 'v4', credentials=creds)
            return service.spreadsheets()
        except HttpError as err:
            print(err)