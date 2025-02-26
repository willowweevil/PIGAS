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
    ASK_TO_MESSAGE = auto()


class Duty(Enum):
    NEARING = auto()
    INITIALIZE = auto()
    AVOID_LOW_OBSTACLES = auto()
    ROTATE = auto()
    ROTATE_LEFT = auto()
    ROTATE_RIGHT = auto()
    HELP_IN_COMBAT = auto()
    HEAL = auto()
    HEAL_PLAYER = auto()
    HEAL_YOURSELF = auto()


class Companion(object):
    def __init__(self):
        self.moving_behaviour = Moving.FOLLOW
        self.combat_behaviour = Combat.ASSIST
        self.action_behaviour = Action.NONE
        self.duties = []

    def add_duty(self, duty):
        self.duties.append(duty)

    def check_duty(self, duty):
        if duty in self.duties:
            return True
        return False

    def change_behaviour(self, new_behaviour):
        if isinstance(new_behaviour, Moving):
            self.moving_behaviour = new_behaviour
        elif isinstance(new_behaviour, Combat):
            self.combat_behaviour = new_behaviour
        elif isinstance(new_behaviour, Action):
            self.action_behaviour = new_behaviour
        else:
            raise ValueError("Invalid state type.")

    def get_behaviour(self):
        return self.moving_behaviour, self.combat_behaviour, self.action_behaviour
