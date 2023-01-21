from helpers.generator_config import GeneratorConfig

from generators.details_generator import DetailsGenerator
from generators.fastest_generator import FastestGenerator
from generators.results_generator import ResultsGenerator
from generators.lineups_generator import LineupGenerator
from generators.presentation_generator import PresentationGenerator
from generators.teams_ranking_generator import TeamsRankingGenerator


class Renderer:
    generators = {
        'lineup': LineupGenerator,
        'presentation': PresentationGenerator,
        'results': ResultsGenerator,
        'details': DetailsGenerator,
        'fastest': FastestGenerator,
        'teams_ranking': TeamsRankingGenerator,
    }

    @classmethod
    def render(cls, config: GeneratorConfig):
        if not config.type in cls.generators:
            raise Exception(f'Please specify a valid visual type ({", ".join(cls.generators.keys())})')

        generator = cls.generators[config.type](config)
        return generator.generate()
