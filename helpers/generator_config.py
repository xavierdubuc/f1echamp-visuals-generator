from dataclasses import dataclass
import enum
import pandas

from models import Pilot, Race

class GeneratorType(enum.Enum):
    Presentation = 'presentation'
    Lineup ='lineup'
    Results ='results'
    Details = 'details'
    Fastest = 'fastest'

@dataclass
class FastestLap:
    pilot: Pilot
    lap: str = None
    time: str = None

@dataclass
class GeneratorConfig:
    type: GeneratorType
    output: str
    pilots: dict
    teams: list
    race: Race
    description: str = None
    ranking: pandas.DataFrame = None
    fastest_lap: FastestLap = None

