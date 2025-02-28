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
    AVOID_LOW_OBSTACLE = auto()
    ROTATE = auto()
    ROTATE_LEFT = auto()
    ROTATE_RIGHT = auto()
    HELP_IN_COMBAT = auto()
    HEAL = auto()
    HEAL_PLAYER = auto()
    HEAL_YOURSELF = auto()


class Companion(object):
    def __init__(self):
        self.moving_behaviour = Moving.STAY
        self.combat_behaviour = Combat.PASSIVE
        self.action_behaviour = Action.NONE
        self.duties = []

    def add_duty(self, duty: Duty):
        self.duties.append(duty)

    def has_duty(self, duty: Duty) -> bool:
        if duty in self.duties:
            return True
        return False

    def get_duties(self):
        return self.duties

    def change_moving_behaviour_to(self, new_moving_behaviour: Moving):
        self.moving_behaviour = new_moving_behaviour

    def change_combat_behaviour_to(self, new_combat_behaviour: Combat):
        self.combat_behaviour = new_combat_behaviour

    def change_action_behaviour_to(self, new_action_behaviour: Action):
        self.action_behaviour = new_action_behaviour

    def get_behaviours(self):
        return self.moving_behaviour, self.combat_behaviour, self.action_behaviour
