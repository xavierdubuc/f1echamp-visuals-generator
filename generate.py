import pandas
import argparse

from models import *
from data import *
from generators.results_generator import generate_results
from generators.lineups_generator import generate_lineup
from generators.presentation_generator import generate_presentation

def determine_swappings(data):
    replacements = data[~data['E'].isna()]
    return {row['E']: pilots[row['D']] for i, row in replacements.iterrows()}


argParser = argparse.ArgumentParser()
argParser.add_argument("type", help="Type de visuel")
argParser.add_argument("-s", "--sheet", help="Name of the Excel sheet to use", dest='sheet')
argParser.add_argument("-o", "--output", help="Output file to use", dest='output')
argParser.add_argument("-i", "--input", help="Input file to use", dest='input')
args = argParser.parse_args()

with pandas.ExcelFile(args.input or './data.xlsx') as xls:
    sheet_name = args.sheet or 'Race 1'
    data = pandas.read_excel(xls, sheet_name, names=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'])

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

if args.type in ('result', 'results'):
    ranking = list(data['I'])
    generate_results(race, ranking, args.output or './results.png')
elif args.type in ('lineup', 'line-up', 'lineups', 'line-ups'):
    generate_lineup(race, teams, args.output or './lineup.png')
elif args.type in ('presentation', 'presentations'):
    description = data['A'][6]
    generate_presentation(race, description, args.output or './presentation.png')
else:
    print('Please specify a valid visual type (result,lineup or presentation)')