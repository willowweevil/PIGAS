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
    NEARING = auto()
    INITIALIZE = auto()
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


class CompanionProfile(object):
    def __init__(self):
        self.moving_behaviour = Moving.STAY
        self.combat_behaviour = Combat.PASSIVE
        self.action_behaviour = Action.NONE
        self.state = State.NEUTRAL
        self.duties = []

    def set_default_behaviours(self):
        self.moving_behaviour = Moving.STAY
        self.combat_behaviour = Combat.PASSIVE
        self.action_behaviour = Action.NONE

    def get_behaviours(self):
        return self.moving_behaviour, self.combat_behaviour, self.action_behaviour

    def set_moving_behaviour_to(self, new_moving_behaviour: Moving):
        self.moving_behaviour = new_moving_behaviour

    def set_combat_behaviour_to(self, new_combat_behaviour: Combat):
        self.combat_behaviour = new_combat_behaviour

    def set_action_behaviour_to(self, new_action_behaviour: Action):
        self.action_behaviour = new_action_behaviour

    def action_behaviour_is(self, action_behavior: Action) -> bool:
        if self.action_behaviour is action_behavior:
            return True
        return False

    def moving_behaviour_is(self, moving_behaviour: Moving) -> bool:
        if self.moving_behaviour is moving_behaviour:
            return True
        return False

    def combat_behaviour_is(self, combat_behaviour: Combat) -> bool:
        if self.combat_behaviour is combat_behaviour:
            return True
        return False

    def clear_duties(self):
        self.duties = []

    def get_duties(self):
        return self.duties

    def add_duty(self, duty: Duty):
        self.duties.append(duty)

    def has_duty(self, duty: Duty) -> bool:
        if duty in self.duties:
            return True
        return False

    def set_default_state(self):
        self.state = State.NEUTRAL

    def get_state(self):
        return self.state

    def set_state_to(self, state: State):
        self.state = state

    def state_is(self, state: State) -> bool:
        if self.state is state:
            return True
        return False

    def state_is_one_of(self, states_list: list[State]) -> bool:
        if self.state in states_list:
            return True
        return False

