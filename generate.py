import pandas
import argparse

from models import *
from data import *
from generators.details_generator import DetailsGenerator
from generators.fastest_generator import FastestGenerator
from generators.results_generator import generate_results
from generators.lineups_generator import generate_lineup
from generators.presentation_generator import generate_presentation


VALUES_SHEET_NAME = '_values'

def determine_swappings(data):
    replacements = data[~data['E'].isna()]
    return {row['E']: pilots[row['D']] for i, row in replacements.iterrows()}

def build_pilots_list(values:pandas.DataFrame):
    pilots = {}
    for i, row in values.iterrows():
        if isinstance(row['Pilotes'], str):
            pilots[row['Pilotes']] = Pilot(name=row['Pilotes'], team=teams_idx[row['Ecurie']], number=str(int(row['Numéro'])))
    return pilots

def build_teams_list(values:pandas.DataFrame):
    teams = []
    for i, row in values.iterrows():
        if isinstance(row['Ecuries'], str):
            teams.append(teams_idx[row['Ecuries']])
    return teams

argParser = argparse.ArgumentParser()
argParser.add_argument("type", help="Type de visuel (results, lineup, presentation)")
argParser.add_argument("-s", "--sheet", help="Name of the Excel sheet to use", dest='sheet')
argParser.add_argument("-o", "--output", help="Output file to use", dest='output')
argParser.add_argument("-i", "--input", help="Input file to use", dest='input')
args = argParser.parse_args()

with pandas.ExcelFile(args.input or './data.xlsx') as xls:
    if VALUES_SHEET_NAME in xls.sheet_names:
        pilots_values = pandas.read_excel(xls, VALUES_SHEET_NAME)[['Pilotes', 'Numéro', 'Ecurie']]
        pilots = build_pilots_list(pilots_values)

        teams_values = pandas.read_excel(xls, VALUES_SHEET_NAME)[['Ecuries']]
        teams = build_teams_list(teams_values)

    sheet_name = args.sheet or 'Race 1'
    if sheet_name not in xls.sheet_names:
        raise Exception(f'Please select a sheet within possible values : {xls.sheet_names}')
    if args.type in ('details', 'fastest'):
        names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
    elif args.type == 'results':
        names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    else:
        names = ['A', 'B', 'C', 'D', 'E', 'F']
    data = pandas.read_excel(xls, sheet_name, usecols=names, names=names)

round = int(data['B'][0])
circuit_name = data['B'][1]
laps = int(data['B'][2])
race_day = data['B'][3]
hour = data['B'][4].strftime('%H.%M')

swappings = determine_swappings(data)

race = Race(
    round = round,
    laps = laps,
    circuit = circuits[circuit_name],
    day = race_day.day,
    month = race_day.strftime('%b'),
    hour=hour,
    pilots=pilots,
    swappings=swappings
)

if args.type == 'results':
    ranking = list(data['I'][:20])
    fastest_pilot = data['G'][22]
    generate_results(race, ranking, fastest_pilot, args.output or './results.png')
elif args.type == 'details':
    ranking_data = data[['I', 'J', 'K', 'L']][:20]
    fastest_lap = { 'pilot_name': data['G'][22], 'lap': data['G'][24], 'time': data['G'][26] }
    generator = DetailsGenerator(race, ranking_data, fastest_lap, args.output or './details.png')
    generator.generate()
elif args.type == 'fastest':
    ranking_data = data[['I', 'J', 'K', 'L']][:20]
    generator = FastestGenerator(race, ranking_data, args.output or './fastest.png')
    generator.generate()
elif args.type == 'lineup':
    generate_lineup(race, teams, args.output or './lineup.png')
elif args.type == 'presentation':
    description = data['A'][6]
    generate_presentation(race, description, args.output or './presentation.png')
else:
    print('Please specify a valid visual type (results, details, fastest, lineup or presentation)')