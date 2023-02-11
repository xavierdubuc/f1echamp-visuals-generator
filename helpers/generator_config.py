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
    TeamsRanking = 'teams_ranking'
    PilotsRanking = 'pilots_ranking'

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
    race: Race = None
    description: str = None
    ranking: pandas.DataFrame = None
    fastest_lap: FastestLap = None
    ranking_title: str = None
    ranking_subtitle: str = None

