from helpers.reader import Reader
from helpers.encoder import Encoder
from helpers.encode_command import Command
from helpers.generator_config import GeneratorType
import os.path

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
_logger = logging.getLogger(__name__)

args = Command().parse_args()
config = Reader(args.type, args.input, args.sheet, args.output).read()
encoder = Encoder(config, args.video, args.audio, args.debug, args.debug_start, args.debug_end, args.debug_step)
output_filepath = encoder.encode()
_logger.info(f'Video successfully encoded in file "{os.path.realpath(output_filepath)}"')