from helpers.reader import Reader
from helpers.calendar_reader import CalendarReader
from helpers.general_ranking_reader import GeneralRankingReader
from helpers.encoder import Encoder
from helpers.renderer import Renderer
from helpers.command import Command
from helpers.generator_config import GeneratorType
import os.path

import logging

GENERAL_RANKING_TYPES = (GeneratorType.TeamsRanking.value, GeneratorType.PilotsRanking.value)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
_logger = logging.getLogger(__name__)

args = Command().parse_args()
if args.type in GENERAL_RANKING_TYPES:
    config = GeneralRankingReader(args.type, args.input, args.output, args.season, args.metric).read()
elif args.type == 'calendar':
    config = CalendarReader(args.type, args.input, args.output, args.season).read()
else:
    config = Reader(args.type, args.input, args.sheet, args.output).read()
if config.type == 'video':
    output_filepath = Encoder.encode(config)
    _logger.info(f'Video successfully encoded in file "{os.path.realpath(output_filepath)}"')
else:
    output_filepath = Renderer.render(config)
    _logger.info(f'Image successfully rendered in file "{os.path.realpath(output_filepath)}"')
