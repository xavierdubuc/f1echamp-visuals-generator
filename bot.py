import logging
import disnake
from disnake.ext import commands
from datetime import datetime

from helpers.reader import Reader
from helpers.general_ranking_reader import GeneralRankingReader
from helpers.renderer import Renderer

from breaking import Renderer as BreakingRenderer

from data import teams_idx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

_logger = logging.getLogger(__name__)
TEAMS = list(teams_idx.keys())


command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True

bot = commands.InteractionBot(command_sync_flags=command_sync_flags)

FBRT_GUILD_ID = 923505034778509342
FBRT_BOT_CHAN_ID = 1074632856443289610


@bot.event
async def on_ready():
    msg = f'Mesdames messieurs {"bonjour" if 5 < datetime.now().hour < 17 else "bonsoir"} !'
    await bot.get_guild(FBRT_GUILD_ID).get_channel(FBRT_BOT_CHAN_ID).send(msg)
    print('Connected !')


@bot.event
async def on_message(msg: disnake.Message):
    if bot.user.mentioned_in(msg) and not msg.mention_everyone and msg.type != disnake.MessageType.reply:
        await msg.channel.send("Vous m'avez appelé ? Ne vous en faites Gaëtano est là ! J'vous ai déjà parlé de mon taximan brésilien ?")


@bot.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name == '❌':
        channel = await bot.fetch_channel(payload.channel_id)
        print(channel)
        message = await channel.fetch_message(payload.message_id)
        if message.author == bot.user:
            await message.delete()


@bot.slash_command(name="rankings", description='Rankings')
async def rankings(inter,
                   what: str = commands.Param(name="what", choices=[
                                              "teams", "pilots"], description="Teams pour le classement des équipes, pilots pour les pilotes")
                   ):
    _logger.info(f'{inter.user.display_name} called Rankings(what={what})')
    await inter.response.defer()

    _logger.info('Reading google sheet')
    config = GeneralRankingReader(f'{what}_ranking', 'gsheet', 'tmp.png', 4).read()
    _logger.info('Rendering image...')
    output_filepath = Renderer.render(config)
    _logger.info('Sending image...')
    with open(output_filepath, 'rb') as f:
        picture = disnake.File(f)
        await inter.followup.send(file=picture)
        _logger.info('Image sent !')


@bot.slash_command(name="race", description='Race information')
async def race(inter: disnake.ApplicationCommandInteraction,
               race_number: str = commands.Param(name="race_number", description='Le numéro de la course'),
               what: str = commands.Param(name="what", choices=[
                                          'lineup', 'presentation', 'results', 'details', 'fastest', 'pole'])
               ):
    _logger.info(f'{inter.user.display_name} called Race(race_number={race_number}, what={what})')
    sheet_name = f'Race {race_number}'
    await inter.response.defer()

    _logger.info('Reading google sheet')
    config = Reader(what, 'gsheet', sheet_name, 'tmp.png').read()

    _logger.info('Rendering image...')
    output_filepath = Renderer.render(config)

    _logger.info('Sending image...')
    with open(output_filepath, 'rb') as f:
        picture = disnake.File(f)
        await inter.followup.send(file=picture)
        _logger.info('Image sent !')


@bot.slash_command(name="breaking", description='Breaking !')
async def breaking(inter,
                   img: disnake.Attachment = commands.Param(
                       name='img', description='Image utilisée comme fond de la breaking news'),
                   main_txt: str = commands.Param(name='main_txt', description='Texte principal de la breaking news'),
                   secondary_txt: str = commands.Param(
                       name='secondary_txt', description='Texte secondaire de la breaking news'),
                   team: str = commands.Param(name='team', default=None, choices=TEAMS,
                                              description="L'équipe concernée par la breaking news"),
                   background: str = commands.Param(
                       name='background', default='255,255,255', description="La couleur de fond à utiliser (au format R,G,B ou R,G,B,A), ignoré si le paramètre team est présent"),
                   foreground: str = commands.Param(
                       name='foreground', default='0,0,0', description="La couleur du texte (au format R,G,B ou R,G,B,A), ignoré si le paramètre team est présent"),
                   padding_top: int = commands.Param(
                       name='padding_top', default=None, description="L'espace en pixel à partir duquel l'image est collée en partant du haut. 0 pour tout en haut.")
                   ):
    _logger.info(f'{inter.user.display_name} called Breaking(main_txt={main_txt}, secondary_txt={secondary_txt}, team={team}, bg={background}, fg={foreground}, pt={padding_top})')
    await inter.response.defer()

    _logger.info('Rendering image...')
    input = (await img.to_file()).fp
    renderer = BreakingRenderer(main_txt, secondary_txt, team, background, foreground,
                                output='tmp.png', input=input, padding_top=padding_top)
    output_filepath = renderer.render()

    _logger.info('Sending image...')
    with open(output_filepath, 'rb') as f:
        picture = disnake.File(f)
        await inter.followup.send(file=picture)
        _logger.info('Image sent !')

original_error_handler = bot.on_slash_command_error


async def on_slash_command_error(inter: disnake.ApplicationCommandInteraction, exception):
    what = inter.filled_options.get('what')
    await inter.delete_original_message()
    if what in ('results', 'details', 'fastest'):
        await inter.channel.send("Une erreur est survenue dans la génération, êtes-vous sûr que la Google Sheet est bien remplie ? Si oui, contactez Xion.")
    else:
        await inter.channel.send('Une erreur est survenue dans la génération, contactez Xion.')
    _logger.exception(exception)
    await original_error_handler(inter, exception)

bot.on_slash_command_error = on_slash_command_error

_logger.info('Starting...')
bot.run('MTA3NDM3NzU3NTgwNTIyNzE5OQ.GIyHdp.oQM7BPINYN4oP7LWfmE0PDhFLYFSb_8rlyGd_4')
