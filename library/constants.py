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

    # Arrow keys (both versions)
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
