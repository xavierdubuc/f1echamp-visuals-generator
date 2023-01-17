import logging
import os.path
import pandas
from helpers.generator_config import FastestLap, GeneratorConfig
from models import Pilot, Race
from data import circuits, teams_idx
from data import teams as default_teams_list, pilots as default_pilots_list


_logger = logging.getLogger(__name__)

class Reader:
    VALUES_SHEET_NAME = '_values'

    def __init__(self, type: str, filepath: str = './data.xlsx', sheet_name: str = 'Race 1', out_filepath: str = None):
        self.filepath = filepath
        _logger.info(f'Data have been read from file "{os.path.realpath(filepath)}"')
        self.sheet_name = sheet_name
        self.type = type
        self.out_filepath = out_filepath

    def read(self):
        pilots, teams = self._read()
        race = self._get_race(pilots, teams)
        config = GeneratorConfig(
            type=self.type,
            output=self.out_filepath or f'./{self.type}.png',
            pilots=pilots,
            teams=teams,
            race=race
        )
        if self.type == 'presentation':
            config.description = self.data['A'][6]
        if self.type in ('results', 'details', 'fastest'):
            config.ranking = self._get_ranking()
        if self.type in ('results', 'details'):
            config.fastest_lap = self._get_fastest_lap(pilots)
        return config

    def _determine_swappings(self, pilots):
        replacements = self.data[~self.data['E'].isna()]
        return {row['E']: pilots[row['D']] for i, row in replacements.iterrows()}

    def _build_pilots_list(self, values: pandas.DataFrame):
        return {
            row['Pilotes']: Pilot(name=row['Pilotes'], team=teams_idx[row['Ecurie']], number=str(int(row['Numéro'])))
            for _, row in values.dropna().iterrows()
        }

    def _build_teams_list(self, values: pandas.DataFrame):
        return [
            teams_idx[row['Ecuries']] for _, row in values.dropna().iterrows()
        ]

    def _read(self):
        with pandas.ExcelFile(self.filepath) as xls:
            if self.VALUES_SHEET_NAME in xls.sheet_names:
                pilots_values = pandas.read_excel(xls, self.VALUES_SHEET_NAME)[['Pilotes', 'Numéro', 'Ecurie']]
                pilots = self._build_pilots_list(pilots_values)

                teams_values = pandas.read_excel(xls, self.VALUES_SHEET_NAME)[['Ecuries']]
                teams = self._build_teams_list(teams_values)
            else:
                pilots = default_pilots_list
                teams = default_teams_list

            if self.sheet_name not in xls.sheet_names:
                raise Exception(f'Please select a sheet within possible values : {xls.sheet_names}')
            if self.type in ('details', 'fastest'):
                names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
            elif self.type == 'results':
                names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
            else:
                names = ['A', 'B', 'C', 'D', 'E', 'F']
            self.data = pandas.read_excel(xls, self.sheet_name, usecols=names, names=names)
            return pilots, teams

    def _get_race(self, pilots, teams):
        race_day = self.data['B'][3]
        return Race(
            round=self.data['B'][0],
            laps=int(self.data['B'][2]),
            circuit=circuits[self.data['B'][1]],
            day=race_day.day,
            month=race_day.strftime('%b'),
            hour=self.data['B'][4].strftime('%H.%M'),
            pilots=pilots,
            teams=teams,
            swappings=self._determine_swappings(pilots)
        )

    def _get_ranking(self):
        ranking_cols = ['I', 'J', 'K', 'L']
        if self.type == 'results':
            ranking_cols = 'I'
        return self.data[ranking_cols][:20]

    def _get_fastest_lap(self, pilots:dict):
        vals = {'pilot_name': self.data['G'][22]}
        if self.type == 'details':
            vals.update({
                'lap': self.data['G'][24],
                'time': self.data['G'][26]}
            )

        return FastestLap(
            pilot=pilots.get(vals['pilot_name']),
            lap=vals.get('lap'),
            time=vals.get('time')
        )

