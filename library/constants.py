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

WOW_AREAS = {
    888: 0.15,   # Shadowglen
    894: 0.15,   # Ammen Vale
    889: 0.15,   # Valley of Trials
    890: 0.15,   # Camp Narache
    891: 0.15,   # Echo Isles
    892: 0.15,   # Deathknell
    893: 0.15,   # Sunstrider Isle
    895: 0.15,   # New Tinkertown
    864: 0.15,   # Northshire
    866: 0.15,   # Coldridge Valley
    4: 0.15,     # Durotar
    9: 0.15,     # Mulgore
    11: 0.15,    # Northern Barrens
    607: 0.15,   # Southern Barrens
    41: 0.15,    # Teldrassil
    42: 0.15,    # Darkshore
    43: 0.15,    # Ashenvale
    61: 0.15,    # Thousand Needles
    81: 0.15,    # Stonetalon Mountains
    101: 0.15,   # Desolace
    121: 0.15,   # Feralas
    141: 0.15,   # Dustwallow Marsh
    161: 0.15,   # Tanaris
    181: 0.15,   # Azshara
    182: 0.15,   # Felwood
    201: 0.15,   # Un'Goro Crater
    241: 0.15,   # Moonglade
    261: 0.15,   # Silithus
    281: 0.15,   # Winterspring
    321: 0.15,   # Orgrimmar
    362: 0.15,   # Thunder Bluff
    381: 0.15,   # Darnassus
    464: 0.15,   # Azuremyst Isle
    471: 0.15,   # The Exodar
    476: 0.15,   # Bloodmyst Isle
    606: 0.15,   # Mount Hyjal
    720: 0.15,   # Uldum
    772: 0.15,   # Ahn'Qiraj: The Fallen Kingdom
    795: 0.15,   # Molten Front
    14: 0.15,    # Eastern Kingdoms
    16: 0.15,    # Arathi Highlands
    17: 0.15,    # Badlands
    19: 0.15,    # Blasted Lands
    20: 0.15,    # Tirisfal Glades
    21: 0.15,    # Silverpine Forest
    22: 0.15,    # Western Plaguelands
    23: 0.15,    # Eastern Plaguelands
    24: 0.15,    # Hillsbrad Foothills
    26: 0.15,    # The Hinterlands
    27: 0.15,    # Dun Morogh
    28: 0.15,    # Searing Gorge
    29: 0.15,    # Burning Steppes
    30: 0.15,    # Elwynn Forest
    32: 0.15,    # Deadwind Pass
    34: 0.15,    # Duskwood
    35: 0.15,    # Loch Modan
    36: 0.15,    # Redridge Mountains
    37: 0.15,    # Northern Stranglethorn
    38: 0.15,    # Swamp of Sorrows
    39: 0.15,    # Westfall
    40: 0.15,    # Wetlands
    301: 0.15,   # Stormwind City
    341: 0.2,   # Ironforge
    382: 0.15,   # Undercity
    462: 0.15,   # Eversong Woods
    463: 0.15,   # Ghostlands
    480: 0.15,   # Silvermoon City
    499: 0.15,   # Isle of Quel'Danas
    502: 0.15,   # The Scarlet Enclave
    545: 0.15,   # Gilneas
    610: 0.15,   # Kelp'thar Forest
    611: 0.15,   # Gilneas City
    613: 0.15,   # Vashj'ir
    614: 0.15,   # Abyssal Depths
    615: 0.15,   # Shimmering Expanse
    673: 0.15,   # The Cape of Stranglethorn
    684: 0.15,   # Ruins of Gilneas
    685: 0.15,   # Ruins of Gilneas City
    689: 0.15,   # Stranglethorn Vale
    700: 0.15,   # Twilight Highlands
    708: 0.15,   # Tol Barad
    709: 0.15,   # Tol Barad Peninsula
    465: 0.15,   # Hellfire Peninsula
    466: 0.15,   # Outland
    467: 0.15,   # Zangarmarsh
    473: 0.15,   # Shadowmoon Valley
    475: 0.15,   # Blade's Edge Mountains
    477: 0.15,   # Nagrand
    478: 0.15,   # Terokkar Forest
    479: 0.15,   # Netherstorm
    481: 0.15,   # Shattrath City
    485: 0.15,   # Northrend
    486: 0.15,   # Borean Tundra
    510: 0.15,   # Crystalsong Forest
    504: 0.15,   # Dalaran
    488: 0.15,   # Dragonblight
    490: 0.15,   # Grizzly Hills
    491: 0.15,   # Howling Fjord
    541: 0.15,   # Hrothgar's Landing
    492: 0.15,   # Icecrown
    493: 0.15,   # Sholazar Basin
    495: 0.15,   # The Storm Peaks
    501: 0.15,   # Wintergrasp
    496: 0.15,   # Zul'Drak
    751: 0.15,   # The Maelstrom
    640: 0.15,   # Deepholm
    605: 0.15,   # Kezan
    544: 0.15,   # The Lost Isles
    737: 0.15,   # The Maelstrom
    806: 0.15,   # The Jade Forest
    807: 0.15,   # Valley of the Four Winds
    808: 0.15,   # The Wandering Isle
    809: 0.15,   # Kun-Lai Summit
    810: 0.15,   # Townlong Steppes
    811: 0.15,   # Vale of Eternal Blossoms
    857: 0.15,   # Krasarang Wilds
    858: 0.15,   # Dread Wastes
    862: 0.15,   # Pandaria
    873: 0.15,   # The Veiled Stair
    903: 0.15,   # Shrine of Two Moons
    905: 0.15,   # Shrine of Seven Stars
    928: 0.15,   # Isle of Thunder
    929: 0.15,   # Isle of Giants
    951: 0.15,   # Timeless Isle
    962: 0.15,   # Draenor
    978: 0.15,   # Ashran
    941: 0.15,   # Frostfire Ridge
    976: 0.15,   # Frostwall
    949: 0.15,   # Gorgrond
    971: 0.15,   # Lunarfall
    950: 0.15,   # Nagrand
    947: 0.15,   # Shadowmoon Valley
    948: 0.15,   # Spires of Arak
    1009: 0.15,  # Stormshield
    946: 0.15,   # Talador
    945: 0.15,   # Tanaan Jungle
    970: 0.15,   # Tanaan Jungle - Assault on the Dark Portal
    1011: 0.15,  # Warspear
    1007: 0.15,  # Broken Isles
    1015: 0.15,  # Aszuna
    1021: 0.15,  # Broken Shore
    1014: 0.15,  # Dalaran
    1098: 0.15,  # Eye of Azshara
    1024: 0.15,  # Highmountain
    1017: 0.15,  # Stormheim
    1033: 0.15,  # Suramar
    1018: 0.15,  # Val'sharah
    1170: 0.15,  # Mac'Aree
    1171: 0.15,  # Antoran Wastes
    1135: 0.15,  # Krokuun
    1184: 0.15,  # Argus
    401: 0.15,   # Alterac Valley
    461: 0.15,   # Arathi Basin
    935: 0.15,   # Deepwind Gorge
    482: 0.15,   # Eye of the Storm
    540: 0.15,   # Isle of Conquest
    860: 0.15,   # Silvershard Mines
    512: 0.15,   # Strand of the Ancients
    856: 0.15,   # Temple of Kotmogu
    736: 0.15,   # The Battle for Gilneas
    626: 0.15,   # Twin Peaks
    443: 0.15,   # Warsong Gulch
    878: 0.15,   # A Brewing Storm
    912: 0.15,   # A Little Patience
    899: 0.15,   # Arena of Annihilation
    883: 0.15,   # Assault on Zan'vess
    940: 0.15,   # Battle on the High Seas
    939: 0.15,   # Blood in the Snow
    884: 0.15,   # Brewmoon Festival
    955: 0.15,   # Celestial Tournament
    900: 0.15,   # Crypt of Forgotten Kings
    914: 0.15,   # Dagger in the Dark
    937: 0.15,   # Dark Heart of Pandaria
    920: 0.15,   # Domination Point (H)
    880: 0.15,   # Greenstone Village
    911: 0.15,   # Lion's Landing (A)
    1086: 0.15,  # Malorne's Nightmare
    1099: 0.15,  # The Road to Fel
    938: 0.15,   # The Secrets of Ragefire
    906: 0.15,   # Theramore's Fall (A)
    851: 0.15,   # Theramore's Fall (H)
    882: 0.15,   # Unga Ingoo
    688: 0.15,   # Blackfathom Deeps
    704: 0.15,   # Blackrock Depths
    721: 0.15,   # Blackrock Spire
    699: 0.15,   # Dire Maul
    691: 0.15,   # Gnomeregan
    750: 0.15,   # Maraudon
    680: 0.15,   # Ragefire Chasm
    760: 0.15,   # Razorfen Downs
    761: 0.15,   # Razorfen Kraul
    764: 0.15,   # Shadowfang Keep
    765: 0.15,   # Stratholme
    756: 0.15,   # The Deadmines
    690: 0.15,   # The Stockade
    687: 0.15,   # The Temple of Atal'Hakkar
    692: 0.15,   # Uldaman
    749: 0.15,   # Wailing Caverns
    686: 0.15,   # Zul'Farrak
    755: 0.15,   # Blackwing Lair
    696: 0.15,   # Molten Core
    717: 0.15,   # Ruins of Ahn'Qiraj
    766: 0.15,   # Temple of Ahn'Qiraj
    722: 0.15,   # Auchenai Crypts
    797: 0.15,   # Hellfire Ramparts
    798: 0.15,   # Magisters' Terrace
    732: 0.15,   # Mana-Tombs
    734: 0.15,   # Old Hillsbrad Foothills
    723: 0.15,   # Sethekk Halls
    724: 0.15,   # Shadow Labyrinth
    731: 0.15,   # The Arcatraz
    733: 0.15,   # The Black Morass
    725: 0.15,   # The Blood Furnace
    729: 0.15,   # The Botanica
    730: 0.15,   # The Mechanar
    710: 0.15,   # The Shattered Halls
    728: 0.15,   # The Slave Pens
    727: 0.15,   # The Steamvault
    726: 0.15,   # The Underbog
    796: 0.15,   # Black Temple
    776: 0.15,   # Gruul's Lair
    775: 0.15,   # Hyjal Summit
    799: 0.15,   # Karazhan
    779: 0.15,   # Magtheridon's Lair
    780: 0.15,   # Serpentshrine Cavern
    789: 0.15,   # Sunwell Plateau
    782: 0.15,   # The Eye
    522: 0.15,   # Ahn'kahet: The Old Kingdom
    533: 2.0,   # Azjol-Nerub
    534: 0.15,   # Drak'Tharon Keep
    530: 0.15,   # Gundrak
    525: 0.15,   # Halls of Lightning
    603: 0.15,   # Halls of Reflection
    526: 0.15,   # Halls of Stone
    602: 0.15,   # Pit of Saron
    521: 0.15,   # The Culling of Stratholme
    601: 0.15,   # The Forge of Souls
    520: 0.15,   # The Nexus
    528: 0.15,   # The Oculus
    536: 0.15,   # The Violet Hold
    542: 0.15,   # Trial of the Champion
    523: 0.15,   # Utgarde Keep
    524: 0.15,   # Utgarde Pinnacle
    604: 0.15,   # Icecrown Citadel
    535: 0.15,   # Naxxramas
    718: 0.15,   # Onyxia's Lair
    527: 0.15,   # The Eye of Eternity
    531: 0.15,   # The Obsidian Sanctum
    609: 0.15,   # The Ruby Sanctum
    543: 0.15,   # Trial of the Crusader
    529: 0.15,   # Ulduar
    532: 0.15,   # Vault of Archavon
    753: 0.15,   # Blackrock Caverns
    820: 0.15,   # End Time
    757: 0.15,   # Grim Batol
    759: 0.15,   # Halls of Origination
    819: 0.15,   # Hour of Twilight
    747: 0.15,   # Lost City of the Tol'vir
    768: 0.15,   # The Stonecore
    769: 0.15,   # The Vortex Pinnacle
    767: 0.15,   # Throne of the Tides
    816: 0.15,   # Well of Eternity
    781: 0.15,   # Zul'Aman
    793: 0.15,   # Zul'Gurub
    752: 0.15,   # Baradin Hold
    754: 0.15,   # Blackwing Descent
    824: 0.15,   # Dragon Soul
    800: 0.15,   # Firelands
    758: 0.15,   # The Bastion of Twilight
    773: 0.15,   # Throne of the Four Winds
    875: 0.15,   # Gate of the Setting Sun
    885: 0.15,   # Mogu'Shan Palace
    871: 0.15,   # Scarlet Halls
    874: 0.15,   # Scarlet Monastery
    898: 0.15,   # Scholomance
    877: 0.15,   # Shado-pan Monastery
    887: 0.15,   # Siege of Niuzao Temple
    876: 0.15,   # Stormstout Brewery
    867: 0.15,   # Temple of the Jade Serpent
    897: 0.15,   # Heart of Fear
    896: 0.15,   # Mogu'shan Vaults
    953: 0.15,   # Siege of Orgrimmar
    886: 0.15,   # Terrace of Endless Spring
    930: 0.15,   # Throne of Thunder
    984: 0.15,   # Auchindoun
    964: 0.15,   # Bloodmaul Slag Mines
    993: 0.15,   # Grimrail Depot
    987: 0.15,   # Iron Docks
    969: 0.15,   # Shadowmoon Burial Grounds
    989: 0.15,   # Skyreach
    1008: 0.15,  # The Everbloom
    995: 0.15,   # Upper Blackrock Spire
    994: 0.15,   # Highmaul
    988: 0.15,   # Blackrock Foundry
    1026: 0.15,  # Hellfire Citadel
    1081: 0.15,  # Black Rook Hold
    1146: 0.15,  # Cathedral of Eternal Night
    1087: 0.15,  # Court of Stars
    1067: 0.15,  # Darkheart Thicket
    1046: 0.15,  # Eye of Azshara
    1041: 0.15,  # Halls of Valor
    1042: 0.15,  # Maw of Souls
    1065: 0.15,  # Neltharion's Lair
    1115: 0.15,  # Return to Karazhan
    1079: 0.15,  # The Arcway
    1045: 0.15,  # Vault of the Wardens
    1066: 0.15,  # Violet Hold
    1178: 0.15,  # Seat of the Triumvirate
    1094: 0.15,  # The Emerald Nightmare
    1114: 0.15,  # Trial of Valor
    1088: 0.15,  # The Nighthold
    1147: 0.15,  # Tomb of Sargeras
    1188: 0.15,  # Antorus, the Burning Throne
    13: 0.15,    # Kalimdor
    25: 0.15    # Scott Test
}
