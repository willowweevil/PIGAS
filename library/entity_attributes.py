from enum import Enum, auto


class Moving(Enum):
    STAY = auto()
    STEP_BY_STEP = auto
    FOLLOW = auto()


class Combat(Enum):
    PASSIVE = auto()
    ONLY_HEAL = auto()
    DEFEND = auto()
    ASSIST = auto()


class Action(Enum):
    NONE = auto()
    LOOT = auto()
    RESPOND = auto()


class Duty(Enum):
    # actions
    INITIALIZE = auto()
    LOOT = auto()
    RESPOND = auto()
    WAITING_FOR_PLAYER = auto()
    # nearing
    NEARING_WITH_PLAYER = auto()
    NEARING_TO_LOOT = auto()
    NEARING_TO_HELP_IN_COMBAT = auto()
    NEARING_TO_HEAL_PLAYER = auto()
    # combat and healing
    HELP_IN_COMBAT = auto()
    DEFEND_YOURSELF = auto()
    HEAL_PLAYER = auto()
    HEAL_YOURSELF = auto()
    AVOID_LOW_OBSTACLE = auto()
    # rotations
    ROTATE_TO_PLAYER = auto()
    ROTATE_TO_PLAYER_LEFT = auto()
    ROTATE_TO_PLAYER_RIGHT = auto()
    ROTATE_TO_PLAYER_FACING = auto()
    ROTATE_TO_PLAYER_FACING_RIGHT = auto()
    ROTATE_TO_PLAYER_FACING_LEFT = auto()


class State(Enum):
    INITIALIZING = auto()
    RESPONDING = auto()
    WAITING_FOR_PLAYER = auto()
    NEARING_FOR_LOOTING = auto()
    LOOTING = auto()
    NEARING_TO_HEAL_PLAYER = auto()
    HEALING_PLAYER = auto()
    HEALING_YOURSELF = auto()
    NEARING_TO_HELP_IN_COMBAT = auto()
    ATTACKING_TO_HELP = auto()
    ATTACKING_TO_DEFEND = auto()
    NEUTRAL = auto()
    BUFFING = auto()



