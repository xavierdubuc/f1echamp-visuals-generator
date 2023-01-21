import pandas
from helpers.generator_config import GeneratorType
from helpers.generator_config import GeneratorConfig
from helpers.reader import Reader

class GeneralRankingReader(Reader):

    def __init__(self, type: str, filepath: str = './data.xlsx', out_filepath: str = None):
        super().__init__(type, filepath, None, out_filepath)
        if type == GeneratorType.PilotsRanking.value:
            self.sheet_name = 'Pilots Ranking'
        if type == GeneratorType.TeamsRanking.value:
            self.sheet_name = 'Teams Ranking'

    def read(self):
        pilots, teams = self._read()
        ranking = self._get_general_ranking()
        config = GeneratorConfig(
            type=self.type,
            output=self.out_filepath or f'./{self.type}.png',
            pilots=pilots,
            teams=teams,
            ranking=ranking
        )
        return config

    def _get_data_sheet_from_gsheet(self, spreadsheet):
        range_str = f"'{self.sheet_name}'!A1:P50"
        vals = spreadsheet.values().get(spreadsheetId=self.spreadsheet_id, range=range_str).execute()['values']
        columns = vals[0] 
        values = [
            row + ([None] * (len(columns) - len(row)))
            for row in vals[1:]
        ]
        return pandas.DataFrame(values, columns=vals[0])

    def _get_general_ranking(self):
        A = 'Ecurie' if self.type == GeneratorType.TeamsRanking.value else 'Pilot'
        return self.data[[A,'Total']].where(lambda x: x != '', pandas.NA).dropna()