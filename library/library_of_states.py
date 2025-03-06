from enum import Enum, auto


class Moving(Enum):
    STAY = auto()
    FOLLOW = auto()


class Combat(Enum):
    PASSIVE = auto()
    HEAL = auto()
    ASSIST = auto()


class Action(Enum):
    NONE = auto()
    LOOT = auto()
    RESPOND = auto()


class Duty(Enum):
    INITIALIZE = auto()
    NEARING_WITH_PLAYER = auto()
    AVOID_LOW_OBSTACLE = auto()
    ROTATE_TO_PLAYER = auto()
    ROTATE_TO_PLAYER_LEFT = auto()
    ROTATE_TO_PLAYER_RIGHT = auto()
    ROTATE_TO_PLAYER_FACING = auto()
    ROTATE_TO_PLAYER_FACING_RIGHT = auto()
    ROTATE_TO_PLAYER_FACING_LEFT = auto()
    LOOT = auto()
    RESPOND = auto()
    HELP_IN_COMBAT = auto()
    HEAL = auto()
    HEAL_PLAYER = auto()
    HEAL_YOURSELF = auto()


class State(Enum):
    NEUTRAL = auto()
    ENTERING_COMBAT = auto()
    ATTACKING = auto()
    HEALING = auto()
    LOOTING = auto()
    RESPONDING = auto()
    BUFFING = auto()




