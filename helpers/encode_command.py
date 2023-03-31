import argparse


class Command(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument("type", help="Type de visuel (grid)")
        self.add_argument("-d", "--debug", help="Debug mode ?", dest='debug', const=True, default=False, nargs='?')
        self.add_argument("--debug-start", help="Debug start in seconds", dest='debug_start', default=None)
        self.add_argument("--debug-end", help="Debug end in seconds", dest='debug_end', default=None)
        self.add_argument("--debug-step", help="Debug step in seconds", dest='debug_step', default=0.5)
        self.add_argument("-s", "--sheet", help="Name of the Excel sheet to use", dest='sheet', default='Race 1')
        self.add_argument("-o", "--output", help="Output file to use", dest='output', default='./video.mp4')
        self.add_argument("-i", "--input", help="Input file to use (use 'gsheet:TIMESHEET_ID' for google sheet (replace TIMESHEET_ID with the id of the sheet of course)", dest='input', default='gsheet')
        self.add_argument("-v", "--video", help="Video input file to use", dest='video', default='./assets/videos/china.mp4')
        self.add_argument("-a", "--audio", help="Audio file to use", dest='audio', default='./assets/videos/gaetan.mp4')

