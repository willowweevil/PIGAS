import os.path

import numpy as np
import time
import logging
import re
import sys

from library.miscellaneous import read_yaml_file
from hardware_input import HardwareInputSimulator
from game_window import GameWindow
from gingham_processing import GinghamProcessor
from library.miscellaneous import  read_the_context, write_the_context, add_message_to_context
from library.miscellaneous import get_open_ai_response, clear_file, read_the_last_line, get_random

from library.entity_attributes import Action, Moving, Combat, Mount, Duty, State
from library.constants import WOW_EMOTES, WOW_EMOTES_PREFIXES


class CompanionProfile(object):
    def __init__(self):
        self.mount_behaviour = Mount.UNMOUNTED
        self.moving_behaviour = Moving.STAY
        self.combat_behaviour = Combat.PASSIVE
        self.action_behaviour = Action.NONE
        self.state = State.NEUTRAL
        self.duties = []

    def set_default_behaviours(self):
        self.mount_behaviour = Mount.UNMOUNTED
        self.moving_behaviour = Moving.FOLLOW
        self.combat_behaviour = Combat.PASSIVE
        self.action_behaviour = Action.NONE

    @property
    def movement_restricted_states(self):
        return [State.INITIALIZING,
                State.RESPONDING,
                State.CHANGING_SPEED,
                State.WAITING_FOR_PLAYER,
                State.MOUNTING,
                State.UNMOUNTING]

    def get_behaviours(self):
        return self.mount_behaviour, self.moving_behaviour, self.combat_behaviour, self.action_behaviour

    def set_mount_behaviour_to(self, new_mount_behaviour: Mount):
        self.mount_behaviour = new_mount_behaviour

    def set_moving_behaviour_to(self, new_moving_behaviour: Moving):
        self.moving_behaviour = new_moving_behaviour

    def set_combat_behaviour_to(self, new_combat_behaviour: Combat):
        self.combat_behaviour = new_combat_behaviour

    def set_action_behaviour_to(self, new_action_behaviour: Action):
        self.action_behaviour = new_action_behaviour

    def mount_behaviour_is(self, mount_behaviour: Mount) -> bool:
        if self.mount_behaviour is mount_behaviour:
            return True
        return False

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

    def remove_duty(self, duty: Duty):
        if self.has_duty(duty):
            self.duties.remove(duty)

    def has_duty(self, duty: Duty) -> bool:
        if duty in self.duties:
            return True
        return False

    def has_one_of_duties(self, duties: list[Duty]) -> bool:
        if any(duty in self.duties for duty in duties):
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


class CompanionControlLoop(HardwareInputSimulator, GameWindow, CompanionProfile, GinghamProcessor):
    def __init__(self):
        super().__init__()

        self.forward_held = False
        self.forward_released = True
        self.left_held = False
        self.left_released = True
        self.right_held = False
        self.right_released = True

        self.waiting_announced = False
        self.looting_announced = False
        self.helping_in_combat_announced = False
        self.healing_player_announced = False

        self.game_window = None
        self.window_position = None
        self.window_size = None
        self.pixel_size = None
        self.n_pixels = None
        self.screenshot_shift = None

        self.directory = None

        self.name = None
        self.spellbook = None
        self.combat_rotation = None
        self.healing_rotation = None
        self.buffing_rotation = None
        self.context_file = None

        self.should_heal = False
        self.should_support = False

        self.session_data = {}

        self.logger = logging.getLogger('companion')
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)
            self.logger.propagate = False

    def initialize_companion(self, game_window, config_file=None):
        self.game_window = game_window
        self.window_position = game_window.window_position
        self.window_size = game_window.window_size
        self.pixel_size = game_window.pixel_size
        self.n_pixels = game_window.n_pixels
        self.screenshot_shift = game_window.screenshot_shift
        self.set_companion_directory(config_file)
        self.set_companion_name(config_file)
        self.set_context_file(config_file)
        self.initialize_spellbook()
        self.set_rotations()
        self.set_should_heal_and_support()

    def set_context_file(self, config):
        config_data = read_yaml_file(config)
        self.context_file = config_data['companion']['context_file']

    def set_companion_directory(self, config):
        config_data = read_yaml_file(config)
        game_extension = config_data['game']['extension']
        companion_class = config_data['companion']['class']
        self.directory = f"./data/class/{game_extension}/{companion_class}"

    def initialize_spellbook(self):
        spellbook_file = os.path.join(self.directory, "spellbook.yaml")
        spellbook = read_yaml_file(spellbook_file)
        for _, spell_info in spellbook.items():
            spell_info['ready'] = True
            spell_info['timestamp_of_cast'] = None
        self.spellbook = spellbook

    def set_rotations(self):
        rotations_file = os.path.join(self.directory, "rotations.yaml")
        rotations = read_yaml_file(rotations_file)
        self.combat_rotation = rotations.get("Combat Rotation")
        self.healing_rotation = rotations.get("Healing Rotation")
        self.buffing_rotation = rotations.get("Buffing Rotation")

    def set_companion_name(self, config):
        config_data = read_yaml_file(config)
        self.name = config_data['companion']['name']

    def set_should_heal_and_support(self):
        if self.healing_rotation:
            if self.healing_rotation.get("Healing Spells"):
                if len(self.healing_rotation.get("Healing Spells")) > 0:
                    self.should_heal = True
        if self.combat_rotation:
            if self.combat_rotation.get("Combat Spells"):
                if len(self.combat_rotation.get("Support Spells")) > 0:
                    self.should_support = True

    @property
    def companion_position_on_screen(self):
        position_x = self.window_position[0] + self.window_size[0] / 2
        position_y = self.window_position[1] + self.window_size[1] / 3 * 2
        return position_x, position_y

    '''
    Session Updates
    '''

    def update_session_data(self, session_data):
        self.session_data = session_data

    def check_movement_keys(self):
        if 'w' in self.pressed_keys:
            self.forward_held = True
            self.forward_released = False
        else:
            self.forward_held = False
            self.forward_released = True
        if 'a' in self.pressed_keys:
            self.left_held = True
            self.left_released = False
        else:
            self.left_held = False
            self.left_released = True
        if 'd' in self.pressed_keys:
            self.right_held = True
            self.right_released = False
        else:
            self.right_held = False
            self.right_released = True

    '''
    Session Profile
    '''

    def _define_moving_behaviour(self):
        moving_behaviour_mapping = {
            'follow_command': Moving.FOLLOW,
            'step_by_step_command': Moving.STEP_BY_STEP,
            'stay_command': Moving.STAY,
        }
        for command, behaviour in moving_behaviour_mapping.items():
            if self.session_data[command]:
                self.set_moving_behaviour_to(behaviour)
                break
        else:
            self.logger.error(f"Moving behaviour is not defined. Use \"{Moving.STAY}\" as default.")
            self.set_moving_behaviour_to(Moving.STAY)

    def _define_combat_behaviour(self):
        combat_behaviour_mapping = {
            'assist_command': Combat.ASSIST,
            'defend_command': Combat.DEFEND,
            'only_heal_command': Combat.ONLY_HEAL,
            'passive_command': Combat.PASSIVE
        }
        for command, behaviour in combat_behaviour_mapping.items():
            if self.session_data[command]:
                self.set_combat_behaviour_to(behaviour)
                break
        else:
            self.logger.error(f"Combat behaviour is not defined. Use \"{Combat.PASSIVE}\" as default.")
            self.set_combat_behaviour_to(Combat.PASSIVE)

    def _define_action_behaviour(self):
        action_behaviour_mapping = {
            'change_speed_command': Action.CHANGE_SPEED,
            'player_message': Action.RESPOND,
            'loot_command': Action.LOOT
        }
        for command, behaviour in action_behaviour_mapping.items():
            if self.session_data[command]:
                self.set_action_behaviour_to(behaviour)
                break
        else:
            self.set_action_behaviour_to(Action.NONE)

    def _define_mount_behaviour(self):
        if self.session_data['mount_command']:
            self.set_mount_behaviour_to(Mount.MOUNTED)
        else:
            self.set_mount_behaviour_to(Mount.UNMOUNTED)

    def define_behaviour(self, ):
        self._define_moving_behaviour()
        self._define_combat_behaviour()
        self._define_action_behaviour()
        self._define_mount_behaviour()

    def _define_initialize_duty(self):
        if self.session_data['frame'] == 1:
            self.add_duty(Duty.INITIALIZE)

    def _define_response_to_message_duty(self):
        if self.action_behaviour_is(Action.RESPOND):
            self.add_duty(Duty.RESPOND)

    def _define_mount_duty(self):
        if self.mount_behaviour_is(Mount.MOUNTED):
            self.session_data['distance_to_player_delta'] = self.session_data[
                'mounted_distance_to_player_delta']
            if not self.session_data['companion_mounted']:
                self.add_duty(Duty.MOUNT)

    def _define_unmount_duty(self):
        if self.mount_behaviour_is(Mount.UNMOUNTED):
            if self.session_data['companion_mounted']:
                self.add_duty(Duty.UNMOUNT)

    def _define_change_speed_duty(self):
        if self.action_behaviour_is(Action.CHANGE_SPEED):
            self.add_duty(Duty.CHANGE_SPEED)

    def _define_looting_duty(self):
        if self.action_behaviour_is(Action.LOOT):
            self.session_data['distance_to_player_delta'] = self.session_data[
                'looting_distance_to_player_delta']
            self.add_duty(Duty.LOOT)

    def _define_heal_yourself_duty(self):
        if not self.combat_behaviour_is(Combat.PASSIVE) and self.should_heal:
            if 0.0 < self.session_data['companion_health'] <= self.session_data['health_to_start_healing']:
                self.add_duty(Duty.HEAL_YOURSELF)

    def _define_defend_yourself_duty(self):
        if self.combat_behaviour_is(Combat.DEFEND):
            if self.session_data['companion_combat_status']:
                self.add_duty(Duty.DEFEND_YOURSELF)

    def _define_heal_player_duty(self):
        if not self.combat_behaviour_is(Combat.PASSIVE) and self.should_heal:
            if 0.0 < self.session_data['player_health'] <= self.session_data[
                'health_to_start_healing']:
                self.add_duty(Duty.HEAL_PLAYER)

    def _define_help_in_combat_duty(self):
        # assist to player in combat
        if self.combat_behaviour_is(Combat.ASSIST):
            if self.session_data['player_combat_status']:
                self.add_duty(Duty.HELP_IN_COMBAT)
        # defend player
        if self.combat_behaviour_is(Combat.DEFEND):
            if self.session_data['player_combat_status'] and 0.0 < self.session_data[
                'player_health'] < 1.0:
                self.add_duty(Duty.HELP_IN_COMBAT)

    def _define_nearing_with_player_duty(self):
        if self.moving_behaviour_is(Moving.FOLLOW):
            if self.session_data['distance_from_companion_to_player'] >= self.session_data[
                'distance_to_player_delta']:
                self.add_duty(Duty.NEARING_WITH_PLAYER)

    def _define_nearing_for_looting_duty(self):
        if self.has_duty(Duty.NEARING_WITH_PLAYER):
            if self.has_duty(Duty.LOOT):
                self.add_duty(Duty.NEARING_TO_LOOT)
                self.remove_duty(Duty.LOOT)
            else:
                self.looting_announced = False

    def _define_nearing_to_help_in_combat_duty(self):
        if self.has_duty(Duty.NEARING_WITH_PLAYER):
            if self.has_duty(Duty.HELP_IN_COMBAT):
                self.add_duty(Duty.NEARING_TO_HELP_IN_COMBAT)
                self.remove_duty(Duty.HELP_IN_COMBAT)
            else:
                self.helping_in_combat_announced = False

    def _define_nearing_to_heal_player_duty(self):
        if self.has_duty(Duty.NEARING_WITH_PLAYER):
            if self.has_duty(Duty.HEAL_PLAYER):
                self.add_duty(Duty.NEARING_TO_HEAL_PLAYER)
                self.remove_duty(Duty.HEAL_PLAYER)
            else:
                self.healing_player_announced = False

    def _define_avoid_low_obstacle_duty(self):
        if self.has_duty(Duty.NEARING_WITH_PLAYER):
            if self.session_data['companion_average_velocity'] < self.session_data[
                'minimum_velocity_for_nearing'] and \
                    self.session_data['distance_from_companion_to_player'] > self.session_data[
                'distance_to_start_avoid_obstacles']:
                self.add_duty(Duty.AVOID_LOW_OBSTACLE)

    def _define_rotation_duty(self,
                              rotation_condition: bool,
                              checking_angle: float,
                              angle_delta: float,
                              rotation_duties: dict[str, Duty]):
        if rotation_condition:
            if checking_angle:
                if abs(checking_angle) > angle_delta:
                    self.add_duty(rotation_duties['main'])
                    if checking_angle <= -angle_delta:
                        self.add_duty(rotation_duties['counterclockwise'])
                    elif checking_angle > angle_delta:
                        self.add_duty(rotation_duties['clockwise'])

    def define_duties(self):
        self._define_initialize_duty()
        self._define_response_to_message_duty()
        self._define_mount_duty()
        self._define_unmount_duty()
        self._define_looting_duty()
        self._define_change_speed_duty()
        self._define_heal_yourself_duty()
        self._define_defend_yourself_duty()

        ### define duties which depend on the player (player should be nearby)
        if self.session_data['player_position'] and self.session_data['distance_from_companion_to_player'] < \
                self.session_data['max_distance_from_companion_to_player']:
            self.waiting_announced = False

            self._define_heal_player_duty()
            self._define_help_in_combat_duty()
            self._define_nearing_with_player_duty()
            self._define_nearing_for_looting_duty()
            self._define_nearing_to_help_in_combat_duty()
            self._define_nearing_to_heal_player_duty()
            self._define_avoid_low_obstacle_duty()

            # rotation to player facing ONLY in combat
            self._define_rotation_duty(
                rotation_condition=self.has_duty(Duty.HELP_IN_COMBAT) and not self.has_duty(Duty.NEARING_WITH_PLAYER),
                checking_angle=self.session_data['angle_between_companion_facing_and_player_facing'],
                angle_delta=self.session_data['rotation_to_player_angle_delta'],
                rotation_duties={'main': Duty.ROTATE_TO_PLAYER_FACING,
                                 'counterclockwise': Duty.ROTATE_TO_PLAYER_FACING_LEFT,
                                 'clockwise': Duty.ROTATE_TO_PLAYER_FACING_RIGHT})

            # rotation to player if not in should rotate to facing
            self._define_rotation_duty(
                rotation_condition=self.moving_behaviour_is(Moving.FOLLOW) and not self.has_duty(
                    Duty.ROTATE_TO_PLAYER_FACING),
                checking_angle=self.session_data['angle_between_companion_facing_and_vector_to_player'],
                angle_delta=self.session_data['rotation_to_player_angle_delta'],
                rotation_duties={'main': Duty.ROTATE_TO_PLAYER,
                                 'counterclockwise': Duty.ROTATE_TO_PLAYER_LEFT,
                                 'clockwise': Duty.ROTATE_TO_PLAYER_RIGHT})
        else:
            self.add_duty(Duty.WAITING_FOR_PLAYER)

    def define_state(self):
        duty_to_state_mapping = {
            Duty.INITIALIZE: State.INITIALIZING,
            Duty.RESPOND: State.RESPONDING,
            Duty.CHANGE_SPEED: State.CHANGING_SPEED,
            Duty.MOUNT: State.MOUNTING,
            Duty.UNMOUNT: State.UNMOUNTING,
            Duty.LOOT: State.LOOTING,
            Duty.WAITING_FOR_PLAYER: State.WAITING_FOR_PLAYER,
            Duty.NEARING_TO_LOOT: State.NEARING_FOR_LOOTING,
            Duty.NEARING_TO_HEAL_PLAYER: State.NEARING_TO_HEAL_PLAYER,
            Duty.HEAL_PLAYER: State.HEALING_PLAYER,
            Duty.HEAL_YOURSELF: State.HEALING_YOURSELF,
            Duty.NEARING_TO_HELP_IN_COMBAT: State.NEARING_TO_HELP_IN_COMBAT,
            Duty.HELP_IN_COMBAT: State.ATTACKING_TO_HELP,
            Duty.DEFEND_YOURSELF: State.ATTACKING_TO_DEFEND,
        }
        for duty, state in duty_to_state_mapping.items():
            if self.has_duty(duty):
                self.set_state_to(state)
                break
        else:
            self.set_state_to(State.NEUTRAL)

    def get_profile(self):
        self.logger.debug(f"Companion behaviours: {self.get_behaviours()}")
        self.logger.debug(f"Companion duties: {self.get_duties()}")
        self.logger.debug(f"Companion state: {self.get_state()}")

    '''
    Area scanning and looting
    '''

    def perform_prelooting_actions(self):
        if not self.looting_announced:
            self.logger.debug("Going to loot.")
            self.move_mouse_to_default_position(self.game_window)
        self.looting_announced = True

    def announce_looting_result(self, was_found):
        if was_found:
            message_suffix = "."
            if was_found == 'gathering':
                message_suffix = ' some resources!'
            self.send_message_to_chat(message="Just finished to #loot" + message_suffix,
                                      channel="/p", pause=1)
        else:
            self.send_message_to_chat("I didn't find anything during the #looting!")

    def do_loot_actions(self, looting_area):
        self.freeze()
        cursor_message, was_found = self.search_and_click(looting_area)
        self.move_mouse_to_default_position(self.game_window)
        self.announce_looting_result(was_found)

    def search_and_click(self, area_geometry):
        keywords = {
            'break': {
                'gathering': ['herbalism', 'mining', 'skinnable'],
                'looting': ['corpse', 'requires', self.name.lower()]
            },
            'pass': ['player']
        }
        cursor_message, break_reason = self._scan_area(area_geometry, keywords, should_break=True)
        if break_reason:
            self.click_mouse(button='left', pause=1)
            return cursor_message, break_reason
        return None, None

    def _scan_area(self, area_geometry, keywords, should_break=False):
        scan_array_x, scan_array_y = self._get_scan_array_sides(area_geometry)
        output_message = []
        for y in scan_array_y[::-1]:
            for x in scan_array_x:
                scan_message = self._get_cursor_message_for_scan(x, y)
                if scan_message:
                    if should_break:
                        break_message, key = self._break_or_pass_during_the_scan(scan_message, keywords)
                        if break_message:
                            return break_message, key
                    else:
                        output_message.append(scan_message)
        return output_message, False

    def _get_scan_array_sides(self, area_geometry):

        area_x, area_y = area_geometry['x_length'] * self.window_size[0], area_geometry['y_length'] * self.window_size[
            1]
        step_x, step_y = area_geometry['x_step'] * self.window_size[0], area_geometry['y_step'] * self.window_size[1]
        shift_x = 0 if not 'x_shift' in area_geometry.keys() else area_geometry['x_shift']
        shift_y = 0 if not 'y_shift' in area_geometry.keys() else area_geometry['y_shift']

        position_x, position_y = self.companion_position_on_screen
        scan_array_x = np.linspace(position_x - area_x / 2 + shift_x,
                                   position_x + area_x / 2 + shift_x,
                                   num=int(area_x / step_x) + 1,
                                   endpoint=True,
                                   dtype=int)
        scan_array_y = np.linspace(position_y - area_y / 2 + shift_y,
                                   position_y + area_y / 2 + shift_y,
                                   num=int(area_y / step_y) + 1,
                                   endpoint=True, dtype=int)
        return scan_array_x, scan_array_y

    def _get_cursor_message_for_scan(self, cursor_x, cursor_y):
        self.move_mouse_to(cursor_x, cursor_y)
        time.sleep(0.1)  # the pause must be here, because new gingham shirts pixels are updating some time
        scan_gingham_shirt = self.take_screenshot(savefig=False, savefig_prefix='scan')
        _, _, cursor_pixels = self.pixels_analysis(
            data=scan_gingham_shirt,
            n_monitoring_pixels=self.n_pixels['y'],
            pixel_height=self.pixel_size['y'],
            pixel_width=self.pixel_size['x'])
        scan_message = self.get_message(cursor_pixels).lower()
        return scan_message

    @staticmethod
    def _break_or_pass_during_the_scan(scan_message, keywords):
        pass_keywords = keywords['pass']
        break_keywords = keywords['break']
        if not any(keyword in scan_message for keyword in pass_keywords):
            for key in break_keywords.keys():
                if any(keyword in scan_message for keyword in break_keywords[key]):
                    return scan_message, key
        return None, None

    '''
    Messaging and chatting
    '''

    def workflow_report(self, report_disable=False):
        if report_disable:
            self.send_message_to_chat("The control script was #disabled!")
            sys.exit(0)

    def respond_to_player(self):
        message_sent = False
        # player commands
        if self.session_data['player_message'].startswith("#"):
            message_sent = self.player_command_workflow()
        # console commands
        if not message_sent and self.session_data['player_message'].startswith("&"):
            message_sent = self.console_command_workflow()
        # add something in the context
        if not message_sent and self.session_data['player_message'].startswith("%"):
            add_message_to_context(self.context_file, self.session_data['player_message'][1:])
            self.send_message_to_chat("Ok, I got it.")
            message_sent = True
        # process wow-emotions
        if not message_sent and "/" in self.session_data['player_message']:
            message_sent = self.emotion_workflow()
        # process ai-responding
        if not message_sent:
            self.ai_response_workflow()

    def ai_response_in_chat(self, response, context):
        response = response.strip().replace('\n', ' ')
        self.logger.info(f"Companion response: {response}")
        context += f"\n\n{response}"
        write_the_context(self.context_file, context)
        sentences = re.split(r'(?<=[.!?])\s+', response)
        for sentence in sentences:
            self.send_message_to_chat(sentence, key_delay=40)

    def ai_response_workflow(self):
        self.freeze()
        player_message = self.session_data['player_message']
        context = read_the_context(self.context_file)
        context += f"\n{player_message}"
        assistant_answer_start_time = time.time()
        self.logger.info(f"Got player message: {player_message}")
        self.logger.info("Getting response..")
        response = get_open_ai_response(context)
        if response:
            self.ai_response_in_chat(response, context)
        else:
            self.send_message_to_chat("I'm too tired to speak now..", key_delay=20)
        self.logger.info(
            f"Companion answer time was {round(time.time() - assistant_answer_start_time, 2)} seconds.")

    def emotion_workflow(self):
        message_words = self.session_data['player_message'].split(' ')
        for word in message_words:
            if word in WOW_EMOTES:
                emote = re.sub(r'\W', '', word)
                emote_prefix = get_random(WOW_EMOTES_PREFIXES)
                self.send_message_to_chat(f"{emote_prefix} {emote}!")
                self.send_message_to_chat(f"{'/' + emote}", channel="/p")
                return True
        return False

    def player_command_workflow(self):
        command = self.session_data['player_message'][:].split(' ')[0].strip()
        send_message = self.send_message_to_chat(f"Sorry, I don't know the command {command}!")
        return send_message

    def console_command_workflow(self):
        command = self.session_data['player_message'][1:].strip()
        self.send_message_to_chat(f"Got the command: \"{command}\"!")
        self.send_message_to_chat(f"{command}", channel="/p")
        return True

    def send_message_to_chat(self, message, channel="/p", receiver=None, key_delay=20, pause=1.0):
        full_message = f"{channel} {receiver} {message}" if receiver is not None else f"{channel} {message}"
        self.logger.debug(f"Going to send a message \"{full_message}\" to the chat.")
        self.freeze()
        self.press_key("enter", pause=0.2)
        self.type_text(full_message, key_delay=key_delay, pause=0.2)
        self.press_key("enter", pause=pause)
        return True

    def set_comment_as_player_message(self, comment_file):
        comment = read_the_last_line(comment_file)
        if comment:
            self.session_data['player_message'] = comment
            clear_file(comment_file)

    '''
    Spells and casting
    '''

    def apply_buffing_rotation(self, ally_target=None):
        self.target_the_ally(ally_target)
        if self.buffing_rotation:
            buffing_spells = self.buffing_rotation.get("Buffing Spells")
            if buffing_spells:
                for spell in buffing_spells:
                    self.cast_spell(spell)

    def apply_combat_rotation(self, ally_target=None, enemy_is_target_of=None):
        if self.should_support:
            if not ally_target:
                ally_target = self.combat_rotation.get("Support Target")
            if ally_target:
                support_spells = self.combat_rotation.get("Support Spells")
                if support_spells:
                    for spell in support_spells:
                        if self.spellbook[spell]['ready']:
                            self.target_the_ally(target=ally_target)
                            self.cast_spell(spell)

        if not enemy_is_target_of:
            enemy_is_target_of = self.combat_rotation.get("Attack Target Is Target Of")
        if enemy_is_target_of:
            self.target_the_enemy(target_of=enemy_is_target_of)
            attack_spells = self.combat_rotation.get("Attack Spells")
            if attack_spells:
                for spell in attack_spells:
                    self.cast_spell(spell)

    def apply_healing_rotation(self, target=None):
        if not target:
            target = self.healing_rotation.get("Healing Target")
        self.target_the_ally(target=target)
        healing_spells = self.healing_rotation.get("Healing Spells")
        if healing_spells:
            for spell in healing_spells:
                self.cast_spell(spell)

    def cast_spell(self, spell, pause=2.0):
        spell_info = self.spellbook.get(spell)
        if spell_info:
            if spell_info['ready']:
                pause_after_cast = pause if spell_info['cast_time'] <= pause else spell_info['cast_time']
                if spell_info['cooldown']:
                    self.logger.debug(
                        f"Going to cast a {spell} (cooldown is {spell_info['cooldown']} seconds).")
                    self._perform_casting_actions_sequence(spell_info, pause=pause_after_cast)
                    spell_info["timestamp_of_cast"] = time.time()
                    spell_info['ready'] = False
                else:
                    self.logger.debug(f"Going to cast a {spell}.")
                    self._perform_casting_actions_sequence(spell_info, pause=pause_after_cast)
        else:
            self.send_message_to_chat(f"Sorry, I don't know spell \"{spell}\". Please, check spell and rotation books.")

    def _perform_casting_actions_sequence(self, spell_data, pause):
        action_page_number = str(spell_data['action_page_number'])
        action_button = str(spell_data['action_button'])
        self.hold_key('shift')
        self.press_key(action_page_number, pause=0.1)
        self.release_key('shift')
        self.press_key(action_button, pause=pause)
        self.hold_key('shift')
        self.press_key("1", pause=0.1)
        self.release_key('shift')

    '''
    Targeting
    '''

    def target_the_ally(self, target='player'):
        if target.lower().replace('_', ' ') == 'player pet':
            self.hold_key('shift')
            self.press_key("F2", pause=0.1)
            self.release_key('shift')
            self.logger.debug("Got player's pet as a target.")
        if target.lower() == 'player':
            self.press_key("F2", pause=0.1)
            self.logger.debug("Got player as a target.")
        if target.lower() == 'companion':
            self.press_key("F1", pause=0.1)
            self.logger.debug("Got myself as a target.")

    def target_the_enemy(self, target_of='player'):
        if target_of == 'player':
            self.press_key("F2")
            self.press_key("f", pause=0.3)
        elif target_of == 'companion':
            self.press_key("t", pause=0.3)

    '''
    Moving
    '''

    def freeze(self):
        current_pressed_keys = list(self.pressed_keys)
        for key in current_pressed_keys:
            self.release_key(key)

        # if self.forward_held:
        #     self.stop_moving_forward()
        # if self.right_held:
        #     self.stop_rotation_clockwise()
        # if self.left_held:as
        #     self.stop_rotation_counterclockwise()
        # self.release_key('shift')

    def move_to(self, duty=None):
        if not duty:
            self.logger.error("Cannot move: nearing duty not set.")
            return False
        if self.has_duty(duty) and not self.forward_held:
            self.logger.debug(f"Start to move forward to {duty}")
            self.start_moving_forward()
        if not self.has_duty(duty) and not self.forward_released:
            self.logger.debug(f"Stop to move forward to {duty}")
            self.stop_moving_forward()
        return True

    def rotate_to(self, duty=None):
        if not duty:
            self.logger.error("Cannot rotate: rotation duty not set.")
            return False
        if duty == Duty.ROTATE_TO_PLAYER:
            clockwise_rotation_duty = Duty.ROTATE_TO_PLAYER_RIGHT
            counterclockwise_rotation_duty = Duty.ROTATE_TO_PLAYER_LEFT
        elif duty == Duty.ROTATE_TO_PLAYER_FACING:
            clockwise_rotation_duty = Duty.ROTATE_TO_PLAYER_FACING_RIGHT
            counterclockwise_rotation_duty = Duty.ROTATE_TO_PLAYER_FACING_LEFT
        else:
            self.logger.error(f"Cannot rotate: rotation duty ({duty}) not found.")
            return False
        if self.has_duty(clockwise_rotation_duty) and not self.right_held:
            self.start_rotation_clockwise()
            self.logger.debug(f"Start clockwise rotation to {clockwise_rotation_duty}.")
        if not self.has_duty(clockwise_rotation_duty) and not self.right_released:
            self.stop_rotation_clockwise()
            self.logger.debug(f"Stop clockwise rotation to {clockwise_rotation_duty}.")
        if self.has_duty(counterclockwise_rotation_duty) and not self.left_held:
            self.start_rotation_counterclockwise()
            self.logger.debug(f"Start counterclockwise rotation to {counterclockwise_rotation_duty}.")
        if not self.has_duty(counterclockwise_rotation_duty) and not self.left_released:
            self.stop_rotation_counterclockwise()
            self.logger.debug(f"Stop counterclockwise rotation to {counterclockwise_rotation_duty}.")
        return True

    def jump(self):
        self.logger.debug("Jumping!")
        self.press_key('space')  # , pause=1.5)

    def start_rotation_clockwise(self):
        self.hold_key("d")

    def start_rotation_counterclockwise(self):
        self.hold_key("a")

    def stop_rotation_clockwise(self):
        self.release_key("d")

    def stop_rotation_counterclockwise(self):
        self.release_key("a")

    def start_moving_forward(self):
        self.hold_key("w")

    def stop_moving_forward(self):
        self.release_key("w")

    '''
    Other activities
    '''

    def changing_speed(self):
        self.send_message_to_chat("I'm going to change my #movement-speed!", pause=2.0)
        self.press_key("\\")

    def mounting(self):
        self.send_message_to_chat("I'm going to mount!")
        self.cast_spell("Mount", pause=3.0)

    def unmounting(self):
        self.send_message_to_chat("I'm going to dismount!")
        self.cast_spell("Mount")

    def waiting_for_player(self):
        if not self.waiting_announced:
            self.send_message_to_chat("Hey! I don't see you! I'll be waiting for you here..")
        self.waiting_announced = True

    def entering_the_game(self):
        self.logger.info("Companion is active.")
        self.freeze()
        self.press_key("F2")
        self.send_message_to_chat(message="/salute", channel='/s', pause=3.0)

    def check_spellbook_cooldowns(self):
        for spell in self.spellbook.keys():
            if self.spellbook[spell]['cooldown']:
                self.check_spell_readiness(spell)

    def check_spell_readiness(self, spell_name):
        input_spell = self.spellbook[spell_name]
        spell_ready = input_spell['ready']
        if not spell_ready:
            if time.time() - input_spell['timestamp_of_cast'] < float(input_spell["cooldown"]):
                self.logger.debug(
                    f"{spell_name} cooldown. "
                    f"Should wait for {round(np.abs(time.time() - input_spell['timestamp_of_cast'] - float(input_spell["cooldown"])), 2)} seconds")
                input_spell['ready'] = False
            else:
                self.logger.debug(f"{spell_name} is ready")
                input_spell['ready'] = True
                input_spell['timestamp_of_cast'] = None
