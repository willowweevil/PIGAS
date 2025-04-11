from pynput.keyboard import Key
from pynput.mouse import Button

KEY_MAPPING = {
    # Mouse buttons
    'left': Button.left,
    'right': Button.right,
    'middle': Button.middle,

    # Modifier keys
    'shift': Key.shift,
    'ctrl': Key.ctrl,
    'alt': Key.alt,
    'cmd': Key.cmd,

    # Special keys
    'space': Key.space,
    'enter': Key.enter,
    'esc': Key.esc,
    'tab': Key.tab,
    'backspace': Key.backspace,
    'delete': Key.delete,

    # Function keys
    'f1': Key.f1,
    'f2': Key.f2,
    'f3': Key.f3,
    'f4': Key.f4,
    'f5': Key.f5,
    'f6': Key.f6,
    'f7': Key.f7,
    'f8': Key.f8,
    'f9': Key.f9,
    'f10': Key.f10,
    'f11': Key.f11,
    'f12': Key.f12,

    # Arrow keys
    'key.up': Key.up,
    'key.down': Key.down,
    'key.left': Key.left,
    'key.right': Key.right,

    # Numpad keys
    'num0': '0',
    'num1': '1',
    'num2': '2',
    'num3': '3',
    'num4': '4',
    'num5': '5',
    'num6': '6',
    'num7': '7',
    'num8': '8',
    'num9': '9',

    # Media keys
    'media_play_pause': Key.media_play_pause,
    'media_volume_mute': Key.media_volume_mute,
    'media_volume_down': Key.media_volume_down,
    'media_volume_up': Key.media_volume_up,
    'media_previous': Key.media_previous,
    'media_next': Key.media_next
}

WOW_EMOTES = [
    "/agree", "/amaze", "/angry", "/apologize", "/applaud", "/applause",
    "/attacktarget", "/bark", "/bashful", "/beckon", "/beg", "/bite",
    "/blink", "/blood", "/blow", "/blush", "/boggle", "/bonk", "/bored",
    "/bounce", "/bow", "/brb", "/burp", "/bye", "/cackle", "/calm",
    "/cat", "/catty", "/challenge", "/charge", "/cheer", "/chew",
    "/chicken", "/chuckle", "/clap", "/cold", "/comfort", "/commend",
    "/confused", "/congrats", "/congratulate", "/cough", "/cower", "/crack",
    "/cringe", "/crossarms", "/cry", "/cuddle", "/curious", "/curtsey",
    "/dance", "/disappointed", "/disapprove", "/doh", "/doom", "/drink",
    "/drool", "/duck", "/eat", "/embarrass", "/encourage", "/enemy",
    "/eye", "/facepalm", "/faint", "/fart", "/fear", "/feast", "/fidget",
    "/flee", "/flex", "/flirt", "/flop", "/follow", "/food", "/frown",
    "/gasp", "/gaze", "/giggle", "/glad", "/glare", "/gloat", "/golfclap",
    "/goodbye", "/greet", "/grin", "/groan", "/grovel", "/growl", "/guffaw",
    "/hail", "/happy", "/headache", "/healme", "/hello", "/helpme", "/hi",
    "/hug", "/hungry", "/hurry", "/huzzah", "/impatient", "/incoming",
    "/insult", "/introduce", "/jk", "/kiss", "/kneel", "/knuckles", "/laugh",
    "/lay", "/laydown", "/lick", "/listen", "/load", "/lost", "/love",
    "/mad", "/map", "/massage", "/meow", "/mercy", "/moan", "/mock", "/moo",
    "/moon", "/morning", "/mourn", "/mutter", "/nervous", "/no", "/nod",
    "/nosepick", "/oom", "/openfire", "/panic", "/party", "/pat", "/peer",
    "/pet", "/pick", "/pity", "/plead", "/point", "/poke", "/ponder", "/pounce",
    "/pout", "/praise", "/pray", "/purr", "/puzzle", "/question", "/raise",
    "/rasp", "/ready", "/rear", "/roar", "/rofl", "/roll", "/rude", "/salute",
    "/scratch", "/sexy", "/shake", "/shimmy", "/shindig", "/shiver", "/shoo",
    "/shrug", "/shy", "/sigh", "/silly", "/slap", "/sleep", "/sleepy",
    "/smell", "/smile", "/smirk", "/snarl", "/sneak", "/sneeze", "/snicker",
    "/sniff", "/snort", "/sob", "/soothe", "/sorry", "/spit", "/squeal",
    "/stand", "/stare", "/stink", "/strong", "/strut", "/surprised", "/surrender",
    "/sword", "/tackle", "/talk", "/talkex", "/talkq", "/tap", "/tease", "/thank",
    "/thanks", "/thirsty", "/threaten", "/tickle", "/tired", "/train", "/ty",
    "/veto", "/victory", "/violin", "/wait", "/warn", "/wave", "/weep", "/welcome",
    "/whine", "/whistle", "/wicked", "/wink", "/work", "/worship", "/yawn",
    "/yay", "/yell", "/yes", "/yummy"
]

WOW_EMOTES_PREFIXES = [
    "Let's",
    "I'm gonna",
    "Hey guys, I'm about to",
    "LOL I",
    "Check this out - I'm gonna",
    "",
    "Hold my ale while I",
    "Yeet! I'm about to",
    "My cat walked on keyboard and now I",
    "Oops, I accidentally",
    "By the ancient powers, I",
    "The stars compel me to",
    "As the prophecy foretold, I shall",
    "Mystic energies guide me to",
    "The whispers of the Void tell me to",
]

WOW_AREAS = {
    888: 1.0,   # Shadowglen
    894: 1.0,   # Ammen Vale
    889: 1.0,   # Valley of Trials
    890: 1.0,   # Camp Narache
    891: 1.0,   # Echo Isles
    892: 1.0,   # Deathknell
    893: 1.0,   # Sunstrider Isle
    895: 1.0,   # New Tinkertown
    864: 1.0,   # Northshire
    866: 1.0,   # Coldridge Valley
    4: 1.0,     # Durotar
    9: 1.0,     # Mulgore
    11: 1.0,    # Northern Barrens
    607: 1.0,   # Southern Barrens
    41: 1.0,    # Teldrassil
    42: 1.0,    # Darkshore
    43: 1.0,    # Ashenvale
    61: 1.0,    # Thousand Needles
    81: 1.0,    # Stonetalon Mountains
    101: 1.0,   # Desolace
    121: 1.0,   # Feralas
    141: 1.0,   # Dustwallow Marsh
    161: 1.0,   # Tanaris
    181: 1.0,   # Azshara
    182: 1.0,   # Felwood
    201: 1.0,   # Un'Goro Crater
    241: 1.0,   # Moonglade
    261: 1.0,   # Silithus
    281: 1.0,   # Winterspring
    321: 1.0,   # Orgrimmar
    362: 1.0,   # Thunder Bluff
    381: 1.0,   # Darnassus
    464: 1.0,   # Azuremyst Isle
    471: 1.0,   # The Exodar
    476: 1.0,   # Bloodmyst Isle
    606: 1.0,   # Mount Hyjal
    720: 1.0,   # Uldum
    772: 1.0,   # Ahn'Qiraj: The Fallen Kingdom
    795: 1.0,   # Molten Front
    14: 1.0,    # Eastern Kingdoms
    16: 1.0,    # Arathi Highlands
    17: 1.0,    # Badlands
    19: 1.0,    # Blasted Lands
    20: 1.0,    # Tirisfal Glades
    21: 1.0,    # Silverpine Forest
    22: 1.0,    # Western Plaguelands
    23: 1.0,    # Eastern Plaguelands
    24: 1.0,    # Hillsbrad Foothills
    26: 1.0,    # The Hinterlands
    27: 1.0,    # Dun Morogh
    28: 1.0,    # Searing Gorge
    29: 1.0,    # Burning Steppes
    30: 1.0,    # Elwynn Forest
    32: 1.0,    # Deadwind Pass
    34: 1.0,    # Duskwood
    35: 1.0,    # Loch Modan
    36: 1.0,    # Redridge Mountains
    37: 1.0,    # Northern Stranglethorn
    38: 1.0,    # Swamp of Sorrows
    39: 1.0,    # Westfall
    40: 1.0,    # Wetlands
    301: 1.0,   # Stormwind City
    341: 1.5,   # Ironforge
    382: 1.0,   # Undercity
    462: 1.0,   # Eversong Woods
    463: 1.0,   # Ghostlands
    480: 1.0,   # Silvermoon City
    499: 1.0,   # Isle of Quel'Danas
    502: 1.0,   # The Scarlet Enclave
    545: 1.0,   # Gilneas
    610: 1.0,   # Kelp'thar Forest
    611: 1.0,   # Gilneas City
    613: 1.0,   # Vashj'ir
    614: 1.0,   # Abyssal Depths
    615: 1.0,   # Shimmering Expanse
    673: 1.0,   # The Cape of Stranglethorn
    684: 1.0,   # Ruins of Gilneas
    685: 1.0,   # Ruins of Gilneas City
    689: 1.0,   # Stranglethorn Vale
    700: 1.0,   # Twilight Highlands
    708: 1.0,   # Tol Barad
    709: 1.0,   # Tol Barad Peninsula
    465: 1.0,   # Hellfire Peninsula
    466: 1.0,   # Outland
    467: 1.0,   # Zangarmarsh
    473: 1.0,   # Shadowmoon Valley
    475: 1.0,   # Blade's Edge Mountains
    477: 1.0,   # Nagrand
    478: 1.0,   # Terokkar Forest
    479: 1.0,   # Netherstorm
    481: 1.0,   # Shattrath City
    485: 1.0,   # Northrend
    486: 1.0,   # Borean Tundra
    510: 1.0,   # Crystalsong Forest
    504: 2.0,   # Dalaran
    488: 1.0,   # Dragonblight
    490: 1.0,   # Grizzly Hills
    491: 1.0,   # Howling Fjord
    541: 1.0,   # Hrothgar's Landing
    492: 1.0,   # Icecrown
    493: 1.0,   # Sholazar Basin
    495: 1.0,   # The Storm Peaks
    501: 1.0,   # Wintergrasp
    496: 1.0,   # Zul'Drak
    751: 1.0,   # The Maelstrom
    640: 1.0,   # Deepholm
    605: 1.0,   # Kezan
    544: 1.0,   # The Lost Isles
    737: 1.0,   # The Maelstrom
    806: 1.0,   # The Jade Forest
    807: 1.0,   # Valley of the Four Winds
    808: 1.0,   # The Wandering Isle
    809: 1.0,   # Kun-Lai Summit
    810: 1.0,   # Townlong Steppes
    811: 1.0,   # Vale of Eternal Blossoms
    857: 1.0,   # Krasarang Wilds
    858: 1.0,   # Dread Wastes
    862: 1.0,   # Pandaria
    873: 1.0,   # The Veiled Stair
    903: 1.0,   # Shrine of Two Moons
    905: 1.0,   # Shrine of Seven Stars
    928: 1.0,   # Isle of Thunder
    929: 1.0,   # Isle of Giants
    951: 1.0,   # Timeless Isle
    962: 1.0,   # Draenor
    978: 1.0,   # Ashran
    941: 1.0,   # Frostfire Ridge
    976: 1.0,   # Frostwall
    949: 1.0,   # Gorgrond
    971: 1.0,   # Lunarfall
    950: 1.0,   # Nagrand
    947: 1.0,   # Shadowmoon Valley
    948: 1.0,   # Spires of Arak
    1009: 1.0,  # Stormshield
    946: 1.0,   # Talador
    945: 1.0,   # Tanaan Jungle
    970: 1.0,   # Tanaan Jungle - Assault on the Dark Portal
    1011: 1.0,  # Warspear
    1007: 1.0,  # Broken Isles
    1015: 1.0,  # Aszuna
    1021: 1.0,  # Broken Shore
    1014: 1.0,  # Dalaran
    1098: 1.0,  # Eye of Azshara
    1024: 1.0,  # Highmountain
    1017: 1.0,  # Stormheim
    1033: 1.0,  # Suramar
    1018: 1.0,  # Val'sharah
    1170: 1.0,  # Mac'Aree
    1171: 1.0,  # Antoran Wastes
    1135: 1.0,  # Krokuun
    1184: 1.0,  # Argus
    401: 1.0,   # Alterac Valley
    461: 1.0,   # Arathi Basin
    935: 1.0,   # Deepwind Gorge
    482: 1.0,   # Eye of the Storm
    540: 1.0,   # Isle of Conquest
    860: 1.0,   # Silvershard Mines
    512: 1.0,   # Strand of the Ancients
    856: 1.0,   # Temple of Kotmogu
    736: 1.0,   # The Battle for Gilneas
    626: 1.0,   # Twin Peaks
    443: 1.0,   # Warsong Gulch
    878: 1.0,   # A Brewing Storm
    912: 1.0,   # A Little Patience
    899: 1.0,   # Arena of Annihilation
    883: 1.0,   # Assault on Zan'vess
    940: 1.0,   # Battle on the High Seas
    939: 1.0,   # Blood in the Snow
    884: 1.0,   # Brewmoon Festival
    955: 1.0,   # Celestial Tournament
    900: 1.0,   # Crypt of Forgotten Kings
    914: 1.0,   # Dagger in the Dark
    937: 1.0,   # Dark Heart of Pandaria
    920: 1.0,   # Domination Point (H)
    880: 1.0,   # Greenstone Village
    911: 1.0,   # Lion's Landing (A)
    1086: 1.0,  # Malorne's Nightmare
    1099: 1.0,  # The Road to Fel
    938: 1.0,   # The Secrets of Ragefire
    906: 1.0,   # Theramore's Fall (A)
    851: 1.0,   # Theramore's Fall (H)
    882: 1.0,   # Unga Ingoo
    688: 1.0,   # Blackfathom Deeps
    704: 1.0,   # Blackrock Depths
    721: 1.0,   # Blackrock Spire
    699: 1.0,   # Dire Maul
    691: 1.0,   # Gnomeregan
    750: 1.0,   # Maraudon
    680: 1.0,   # Ragefire Chasm
    760: 1.0,   # Razorfen Downs
    761: 1.0,   # Razorfen Kraul
    764: 1.0,   # Shadowfang Keep
    765: 1.0,   # Stratholme
    756: 1.0,   # The Deadmines
    690: 1.0,   # The Stockade
    687: 1.0,   # The Temple of Atal'Hakkar
    692: 1.0,   # Uldaman
    749: 1.0,   # Wailing Caverns
    686: 1.0,   # Zul'Farrak
    755: 1.0,   # Blackwing Lair
    696: 1.0,   # Molten Core
    717: 1.0,   # Ruins of Ahn'Qiraj
    766: 1.0,   # Temple of Ahn'Qiraj
    722: 1.0,   # Auchenai Crypts
    797: 1.0,   # Hellfire Ramparts
    798: 1.0,   # Magisters' Terrace
    732: 1.0,   # Mana-Tombs
    734: 1.0,   # Old Hillsbrad Foothills
    723: 1.0,   # Sethekk Halls
    724: 1.0,   # Shadow Labyrinth
    731: 1.0,   # The Arcatraz
    733: 1.0,   # The Black Morass
    725: 1.0,   # The Blood Furnace
    729: 1.0,   # The Botanica
    730: 1.0,   # The Mechanar
    710: 1.0,   # The Shattered Halls
    728: 1.0,   # The Slave Pens
    727: 1.0,   # The Steamvault
    726: 1.0,   # The Underbog
    796: 1.0,   # Black Temple
    776: 1.0,   # Gruul's Lair
    775: 1.0,   # Hyjal Summit
    799: 1.0,   # Karazhan
    779: 1.0,   # Magtheridon's Lair
    780: 1.0,   # Serpentshrine Cavern
    789: 1.0,   # Sunwell Plateau
    782: 1.0,   # The Eye
    522: 1.0,   # Ahn'kahet: The Old Kingdom
    533: 13.0,   # Azjol-Nerub
    534: 1.0,   # Drak'Tharon Keep
    530: 1.0,   # Gundrak
    525: 1.0,   # Halls of Lightning
    603: 1.0,   # Halls of Reflection
    526: 1.0,   # Halls of Stone
    602: 1.0,   # Pit of Saron
    521: 1.0,   # The Culling of Stratholme
    601: 1.0,   # The Forge of Souls
    520: 1.0,   # The Nexus
    528: 1.0,   # The Oculus
    536: 1.0,   # The Violet Hold
    542: 1.0,   # Trial of the Champion
    523: 1.0,   # Utgarde Keep
    524: 1.0,   # Utgarde Pinnacle
    604: 1.0,   # Icecrown Citadel
    535: 1.0,   # Naxxramas
    718: 1.0,   # Onyxia's Lair
    527: 1.0,   # The Eye of Eternity
    531: 1.0,   # The Obsidian Sanctum
    609: 1.0,   # The Ruby Sanctum
    543: 1.0,   # Trial of the Crusader
    529: 1.0,   # Ulduar
    532: 1.0,   # Vault of Archavon
    753: 1.0,   # Blackrock Caverns
    820: 1.0,   # End Time
    757: 1.0,   # Grim Batol
    759: 1.0,   # Halls of Origination
    819: 1.0,   # Hour of Twilight
    747: 1.0,   # Lost City of the Tol'vir
    768: 1.0,   # The Stonecore
    769: 1.0,   # The Vortex Pinnacle
    767: 1.0,   # Throne of the Tides
    816: 1.0,   # Well of Eternity
    781: 1.0,   # Zul'Aman
    793: 1.0,   # Zul'Gurub
    752: 1.0,   # Baradin Hold
    754: 1.0,   # Blackwing Descent
    824: 1.0,   # Dragon Soul
    800: 1.0,   # Firelands
    758: 1.0,   # The Bastion of Twilight
    773: 1.0,   # Throne of the Four Winds
    875: 1.0,   # Gate of the Setting Sun
    885: 1.0,   # Mogu'Shan Palace
    871: 1.0,   # Scarlet Halls
    874: 1.0,   # Scarlet Monastery
    898: 1.0,   # Scholomance
    877: 1.0,   # Shado-pan Monastery
    887: 1.0,   # Siege of Niuzao Temple
    876: 1.0,   # Stormstout Brewery
    867: 1.0,   # Temple of the Jade Serpent
    897: 1.0,   # Heart of Fear
    896: 1.0,   # Mogu'shan Vaults
    953: 1.0,   # Siege of Orgrimmar
    886: 1.0,   # Terrace of Endless Spring
    930: 1.0,   # Throne of Thunder
    984: 1.0,   # Auchindoun
    964: 1.0,   # Bloodmaul Slag Mines
    993: 1.0,   # Grimrail Depot
    987: 1.0,   # Iron Docks
    969: 1.0,   # Shadowmoon Burial Grounds
    989: 1.0,   # Skyreach
    1008: 1.0,  # The Everbloom
    995: 1.0,   # Upper Blackrock Spire
    994: 1.0,   # Highmaul
    988: 1.0,   # Blackrock Foundry
    1026: 1.0,  # Hellfire Citadel
    1081: 1.0,  # Black Rook Hold
    1146: 1.0,  # Cathedral of Eternal Night
    1087: 1.0,  # Court of Stars
    1067: 1.0,  # Darkheart Thicket
    1046: 1.0,  # Eye of Azshara
    1041: 1.0,  # Halls of Valor
    1042: 1.0,  # Maw of Souls
    1065: 1.0,  # Neltharion's Lair
    1115: 1.0,  # Return to Karazhan
    1079: 1.0,  # The Arcway
    1045: 1.0,  # Vault of the Wardens
    1066: 1.0,  # Violet Hold
    1178: 1.0,  # Seat of the Triumvirate
    1094: 1.0,  # The Emerald Nightmare
    1114: 1.0,  # Trial of Valor
    1088: 1.0,  # The Nighthold
    1147: 1.0,  # Tomb of Sargeras
    1188: 1.0,  # Antorus, the Burning Throne
    13: 1.0,    # Kalimdor
    25: 1.0    # Scott Test
}
