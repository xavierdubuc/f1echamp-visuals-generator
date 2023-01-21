import argparse


class Command(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument("type", help="Type de visuel (results, lineup, presentation, fastest, details)")
        self.add_argument("-s", "--sheet", help="Name of the Excel sheet to use", dest='sheet', default='Race 1')
        self.add_argument("-o", "--output", help="Output file to use", dest='output', default=None)
        self.add_argument("-i", "--input", help="Input file to use", dest='input', default='./data.xlsx')
