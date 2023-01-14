from helpers.reader import Reader
from helpers.renderer import Renderer
from helpers.command import Command
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
output_filepath = Renderer.render(config)
_logger.info(f'Image successfully rendered in file "{os.path.realpath(output_filepath)}"')
