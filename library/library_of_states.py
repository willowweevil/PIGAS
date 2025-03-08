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
    DEFEND_YOURSELF = auto()
    HEAL = auto()
    HEAL_PLAYER = auto()
    HEAL_YOURSELF = auto()


class State(Enum):
    NEUTRAL = auto()
    ENTERING_COMBAT_TO_HELP = auto()
    ENTERING_COMBAT_TO_DEFEND = auto()
    ATTACKING_TO_DEFEND = auto()
    ATTACKING_TO_HELP = auto()
    HEALING_PLAYER = auto()
    HEALING_YOURSELF = auto()
    LOOTING = auto()
    RESPONDING = auto()
    BUFFING = auto()




