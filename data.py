from models import *


# --- CIRCUITS
bahrein = Circuit(id='bahrein', name='Bahreïn', lap_length=5.412, best_lap="1' 31'' 447")
saudiarabia = Circuit(id='saudiarabia', name='Arabie Saoudite', lap_length=6.174, best_lap="1' 30'' 734")
australia = Circuit(id='australia', name='Australie', lap_length=5.278, best_lap="N/A")
imola = Circuit(id='imola', name='Imola', lap_length=4.909, best_lap="1' 15'' 484")
miami = Circuit(id='miami', name='Miami', lap_length=5.412, best_lap="1' 31'' 361")
spain = Circuit(id='spain', name='Espagne', lap_length=4.675, best_lap="1' 18'' 149")
monaco = Circuit(id='monaco', name='Monaco', lap_length=3.337, best_lap="1' 12'' 909")
azerbaidjan = Circuit(id='azerbaidjan', name='Azerbaïdjan', lap_length=6.003, best_lap="1' 43'' 009")
canada = Circuit(id='canada', name='Canada', lap_length=4.361, best_lap="1' 13'' 078")
gb = Circuit(id='gb', name='Grande-Bretagne', lap_length=5.891, best_lap="1' 27'' 097")
austria = Circuit(id='austria', name='Autriche', lap_length=4.318, best_lap="1' 05'' 619")
france = Circuit(id='france', name='France', lap_length=5.842, best_lap="1' 32'' 740")
hungary = Circuit(id='hungary', name='Hongrie', lap_length=4.381, best_lap="1' 16'' 627")
belgium = Circuit(id='belgium', name='Belgique', lap_length=7.004, best_lap="1' 41'' 252")
netherlands = Circuit(id='netherlands', name='Pays-Bas', lap_length=4.259, best_lap="1' 11'' 097")
italy = Circuit(id='italy', name="Italie", lap_length=5.793, best_lap="1' 21'' 046")
singapore = Circuit(id='singapore', name='Singapour', lap_length=5.063, best_lap="1' 41'' 905")
japan = Circuit(id='japan', name='Japon', lap_length=5.807, best_lap="1' 30'' 983")
austin = Circuit(id='austin', name='Etats-Unis', lap_length=5.513, best_lap="1' 36'' 169")
mexico = Circuit(id='mexico', name='Mexique', lap_length=4.304, best_lap="1' 17'' 774")
brazil = Circuit(id='brazil', name='Brésil', lap_length=4.309, best_lap="1' 10'' 540")
abudhabi = Circuit(id='abudhabi', name='Abu Dhabi', lap_length=5.281, best_lap="1' 26'' 103")
portugal = Circuit(id='portugal', name='Portugal', lap_length=4.653, best_lap="1' 18'' 750")
china = Circuit(id='china', name='Chine', lap_length=5.451, best_lap="1' 32'' 238")

circuits = {
    'Bahreïn': bahrein,
    'Arabie Saoudite': saudiarabia,
    'Australie': australia,
    'Imola': imola,
    'Miami': miami,
    'Espagne': spain,
    'Monaco': monaco,
    'Azerbaïdjan': azerbaidjan,
    'Canada': canada,
    'Grande-Bretagne': gb,
    'Autriche': austria,
    'France': france,
    'Hongrie': hungary,
    'Belgique': belgium,
    'Pays-Bas': netherlands,
    'Italie': italy,
    'Singapour': singapore,
    'Japon': japan,
    'Etats-Unis': austin,
    'Mexique': mexico,
    'Brésil': brazil,
    'Abu Dhabi': abudhabi,
    'Portugal': portugal,
    'Chine': china
}


# --- TEAMS
redbull = Team(
    name='RedBull',
    title='Oracle Red Bull',
    subtitle="Racing",
    main_color=(215,190,50),
    secondary_color=(0, 0, 186),
    box_color= (0,0,186)
)
mercedes = Team(
    name='Mercedes',
    title='Mercedes',
    subtitle="AMG Petronas F1 Team",
    main_color=(0, 179, 158),
    secondary_color=(0, 0, 0),
    box_color=(0, 179, 158)
)
mclaren = Team(
    name='McLaren',
    title='McLaren',
    subtitle='F1 Team',
    main_color=(224, 146, 12),
    secondary_color=(40, 40, 40),
    box_color=(224, 146, 12)
)
haas = Team(
    name='Haas',
    title='Haas',
    subtitle='F1 Team',
    main_color=(200, 10, 15),
    secondary_color=(211, 211, 211),
    box_color=(211, 211, 211)
)
alpine = Team(
    name='Alpine',
    title='BWT Alpine',
    subtitle='F1 Team',
    main_color=(10, 130, 210),
    secondary_color=(0, 0, 0),
    box_color=(9, 118, 193),
)
ferrari = Team(
    name='Ferrari',
    title='Ferrari',
    subtitle='Scuderia',
    main_color=(255,200,200),
    secondary_color=(255,0,0),
    box_color=(167,8,6),
)
williams = Team(
    name='Williams',
    title='Williams',
    subtitle="Racing",
    main_color=(6, 76, 187),
    secondary_color=(255, 255, 255),
    box_color=(6, 76, 187),
)
alfa_romeo = Team(
    name='AlfaRomeo',
    title='Alfa Romeo',
    subtitle='F1 Team ORLEN',
    main_color=(114, 4, 5),
    secondary_color=(255, 255, 255),
    box_color=(114, 4, 5)
)
aston_martin = Team(
    name='AstonMartin',
    title='Aston Martin',
    subtitle='Aramco Cognizant F1 Team',
    main_color=(14, 104, 88),
    secondary_color=(255, 255, 255),
    box_color=(14, 104, 88),
)
alpha_tauri = Team(
    name="AlphaTauri",
    title="AlphaTauri",
    subtitle='Scuderia',
    main_color=(40, 64, 90),
    secondary_color=(200, 200, 200),
    box_color=(40, 64, 90),
)
teams = [
    redbull,
    mercedes,
    mclaren,
    haas,
    alpine,
    ferrari,
    williams,
    alfa_romeo,
    aston_martin,
    alpha_tauri
]

# --- PILOTS
pilots = {
    # REDBULL
    'majforti-07': Pilot(name='Majforti07', team=redbull, number='37', title='majforti-07'),
    'VRA-RedAym62': Pilot(name='VRA-RedAym62', team=redbull, number='62'),
    # MERCEDES'
    'FBRT_CiD16': Pilot(name='FBRT_CiD16', team=mercedes, number='61'),
    # 'FBRT_Naax': Pilot(name='FBRT_Naax', team=mercedes, number='30'),
    'xJuzooo': Pilot(name='xJuzooo', team=mercedes, number='89'),
    # MCLAREN
    'ewocflo': Pilot(name='ewocflo', team=mclaren, number='66'),
    'FBRT_JCDARCH9': Pilot(name='FBRT_JCDARCH9', team=mclaren, number='90'),
    # HAAS
    'Gros-Nain-Vert': Pilot(name='Gros-Nain-Vert', team=haas, number='72'),
    'Xionhearts': Pilot(name='Xionhearts', team=haas, number='2'),
    # ALPINE
    'Juraptors': Pilot(name='Juraptors', team=alpine, number='19'),
    'APX_Maxeagle': Pilot(name='APX_Maxeagle', team=alpine, number='45'),
    # FERRARI
    'xKayysor': Pilot(name='xKayysor', team=ferrari, number='15'),
    'Prolactron': Pilot(name='Prolactron', team=ferrari, number='95'),
    # WILLIAMS
    'DimDim_91270': Pilot(name='DimDim_91270', team=williams, number='91'),
    'FBRT_Seb07': Pilot(name='FBRT_Seb07', team=williams, number='7'),
    # ALFA ROMEO
    'WSC_Gregy21': Pilot(name='WSC_Gregy21', team=alfa_romeo, number='21'),
    'TheLoulou29': Pilot(name='TheLoulou29', team=alfa_romeo, number='68'),
    # ASTON MARTIN
    'FBRT_REMBRO': Pilot(name='FBRT_REMBRO', team=aston_martin, number='78'),
    'FBRT_Nico': Pilot(name='FBRT_Nico', team=aston_martin, number='29'),
    # ALPHA TAURI
    'Iceman7301': Pilot(name='Iceman7301', team=alpha_tauri, number='69'),
    'MoonLight_RR': Pilot(name='MoonLight_RR', team=alpha_tauri, number='98')
}
