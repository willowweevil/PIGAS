import numpy as np
import time
import logging

from library.hardware_input import HardwareInputSimulator
from library.game_window import GameWindow
from library.gingham_processing import pixels_analysis, get_message
from library.ai_openai import get_response
from library.library_of_states import Action, Moving, Combat, Duty, State


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


class CompanionActions(HardwareInputSimulator, GameWindow, CompanionProfile):
    def __init__(self, game_window: GameWindow):
        super().__init__()
        self.window_position = game_window.window_position
        self.window_size = game_window.window_size
        self.pixel_size = game_window.pixel_size
        self.n_pixels = game_window.n_pixels
        self.screenshot_shift = game_window.screenshot_shift
        self.forward_held = False
        self.forward_released = True
        self.left_held = False
        self.left_released = True
        self.right_held = False
        self.right_released = True

    @property
    def get_companion_position(self):
        position_x = self.window_position[0] + self.window_size[0] / 2
        position_y = self.window_position[1] + self.window_size[1] / 3 * 2
        return position_x, position_y

    def _scan_area_with_break(self, area_geometry, keywords):
        pass_keywords = keywords['pass']
        break_keywords = keywords['break']

        scan_array_x, scan_array_y = self._get_scan_array_sides(area_geometry)

        output_message = []
        for y in scan_array_y[::-1]:
            for x in scan_array_x:
                scan_message = self._get_cursor_message_for_scan(x, y)
                if scan_message:
                    if not any(keyword in scan_message for keyword in pass_keywords):
                        for key in break_keywords.keys():
                            if any(keyword in scan_message for keyword in break_keywords[key]):
                                return scan_message, key
        return output_message, False

    def _scan_whole_area(self, area_geometry):
        scan_array_x, scan_array_y = self._get_scan_array_sides(area_geometry)
        output_message = []
        for y in scan_array_y[::-1]:
            for x in scan_array_x:
                scan_message = self._get_cursor_message_for_scan(x, y)
                if scan_message:
                    output_message.append(scan_message)
        return output_message

    def _get_cursor_message_for_scan(self, cursor_x, cursor_y):
        self.move_mouse_to(cursor_x, cursor_y)
        time.sleep(0.1)  # the pause must be here, because new gingham shirts pixels are updating some time
        scan_gingham_shirt = self.take_screenshot(savefig=False, savefig_prefix='scan')
        _, _, cursor_pixels = pixels_analysis(data=scan_gingham_shirt,
                                              n_monitoring_pixels=self.n_pixels['y'],
                                              pixel_height=self.pixel_size['y'],
                                              pixel_width=self.pixel_size['x'])
        scan_message = get_message(cursor_pixels).lower()
        return scan_message

    def _get_scan_array_sides(self, area_geometry):
        area_x, area_y = area_geometry['x_length'], area_geometry['y_length']
        step_x, step_y = area_geometry['x_step'], area_geometry['y_step']
        shift_x = 0 if not 'x_shift' in area_geometry.keys() else area_geometry['x_shift']
        shift_y = 0 if not 'y_shift' in area_geometry.keys() else area_geometry['y_shift']

        position_x, position_y = self.get_companion_position
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

    def find_and_click(self, area_geometry):

        keywords = {'break': {
            'gathering': ['herbalism', 'mining', 'skinning'],
            'looting': ['corpse', 'skivvy', 'requires']
        },
            'pass': ['player']
        }

        cursor_message, break_reason = self._scan_area_with_break(area_geometry, keywords)
        if break_reason:
            self.click_mouse()
            if break_reason == 'gather':
                time.sleep(3)
        else:
            logging.info("Didn't find anything during the scan.")

    def send_message_to_chat(self, message, channel="/p", receiver=None, key_delay=20, pause=1.0):
        full_message = f"{channel} {receiver} {message}" if receiver is not None else f"{channel} {message}"
        self.release_movement_keys()
        self.press_key("enter", pause=0.2)
        self.type_text(full_message, key_delay=key_delay, pause=0.2)
        self.press_key("Return", pause=pause)

    def ai_companion_response(self, player_message, context_file='context.txt'):
        with open(context_file, 'r') as file:
            context = file.read()
            file.close()
        context += f"{player_message}\n"

        assistant_answer_start_time = time.time()
        logging.info("Getting response..")
        response = get_response(context).strip()
        if response:
            logging.info(f"Companion response: {response}")
            context += f"{response}\n\n"
            with open(context_file, "w") as f:
                f.write(context)
                f.close()
            if len(response) >= 255:
                self.send_message_to_chat(response[:255], key_delay=40)
                response = response[255:]
            self.send_message_to_chat(response, key_delay=40)
        else:
            self.send_message_to_chat("I'm too tired to speak now..", key_delay=20)
        logging.info(f"Companion answer time was {round(time.time() - assistant_answer_start_time, 2)} seconds.")

    def cast_spell(self, spell_data):
        if spell_data['cooldown']:
            if spell_data['ready']:
                self._perform_casting_actions_sequence(spell_data)
                spell_data["timestamp_of_cast"] = time.time()
                spell_data['ready'] = False
        else:
            self._perform_casting_actions_sequence(spell_data)

    def _perform_casting_actions_sequence(self, spell_data):
        action_page_number = str(spell_data['action_page_number'])
        action_button = str(spell_data['action_button'])
        self.hold_key('shift')
        self.press_key(action_page_number, pause=0.1)
        self.release_key('shift')
        self.press_key(action_button, pause=2.0)
        self.hold_key('shift')
        self.press_key("1", pause=0.1)
        self.release_key('shift')

    @staticmethod
    def check_spell_timer(input_spell):
        spell_ready = input_spell['ready']
        if not spell_ready:
            if time.time() - input_spell['timestamp_of_cast'] < input_spell["cooldown"]:
                logging.debug(
                    f"Penance cooldown. "
                    f"Should wait for {round(np.abs(time.time() - input_spell['timestamp_of_cast'] - input_spell["cooldown"]), 2)} seconds")
                input_spell['ready'] = False
            else:
                logging.debug("Penance ready")
                input_spell['ready'] = True

    def target_the_ally(self, target='player'):
        if target == 'player_pet':
            self.hold_key('shift')
        self.press_key("F2", pause=0.1)
        if target == 'player_pet':
            self.release_key('shift')

    def target_the_enemy(self):
        self.press_key("F2")
        self.press_key("F", pause=0.5)

    def start_rotation_clockwise(self):
        self.right_held = True
        self.right_released = False
        self.hold_key("d")

    def start_rotation_counterclockwise(self):
        self.left_held = True
        self.left_released = False
        self.hold_key("a")

    def stop_rotation_clockwise(self):
        self.right_held = False
        self.right_released = True
        self.release_key("d")

    def stop_rotation_counterclockwise(self):
        self.left_held = False
        self.left_released = True
        self.release_key("a")

    def start_moving_forward(self):
        self.forward_held = True
        self.forward_released = False
        self.hold_key("w")

    def stop_moving_forward(self):
        self.forward_held = False
        self.forward_released = True
        self.release_key("w")

    def jump(self):
        self.press_key('space')  # , pause=1.5)

    def loot(self, looting_area):
        self.find_and_click(looting_area)
        self.send_message_to_chat(message="Just finished to " + "#loot".lower(),
                                  channel="/p".lower(), pause=1)

    def rotate(self, duty=None):
        if not duty:
            logging.error("Cannot rotate: rotation duty not set.")
            return False
        if duty == Duty.ROTATE_TO_PLAYER:
            clockwise_rotation_duty = Duty.ROTATE_TO_PLAYER_RIGHT
            counterclockwise_rotation_duty = Duty.ROTATE_TO_PLAYER_LEFT
        elif duty == Duty.ROTATE_TO_PLAYER_FACING:
            clockwise_rotation_duty = Duty.ROTATE_TO_PLAYER_FACING_RIGHT
            counterclockwise_rotation_duty = Duty.ROTATE_TO_PLAYER_FACING_LEFT
        else:
            logging.error(f"Cannot rotate: rotation duty ({duty}) not found.")
            return False
        if self.has_duty(clockwise_rotation_duty) and not self.right_held:
            self.start_rotation_clockwise()
            logging.debug(f"Start clockwise rotation: {clockwise_rotation_duty}.")
        if not self.has_duty(clockwise_rotation_duty) and not self.right_released:
            self.stop_rotation_clockwise()
            logging.debug(f"Stop clockwise rotation: {clockwise_rotation_duty}.")
        if self.has_duty(counterclockwise_rotation_duty) and not self.left_held:
            self.start_rotation_counterclockwise()
            logging.debug(f"Start counterclockwise rotation: {counterclockwise_rotation_duty}.")
        if not self.has_duty(counterclockwise_rotation_duty) and not self.left_released:
            self.stop_rotation_counterclockwise()
            logging.debug(f"Stop counterclockwise rotation: {counterclockwise_rotation_duty}.")
        return True

    def move_to(self, duty=None):
        if not duty:
            logging.error("Cannot move: nearing duty not set.")
            return False
        if self.has_duty(duty) and not self.forward_held:
            self.start_moving_forward()
        if not self.has_duty(duty) and not self.forward_released:
            self.stop_moving_forward()
        return True

    def hands_away_from_keyboard(self):
        self.release_movement_keys()
        self.forward_held = False
        self.forward_released = True
        self.left_held = False
        self.left_released = True
        self.right_held = False
        self.right_released = True

    def entering_the_game(self):
        logging.info("Control script is active.")
        self.press_key("F2")
        self.send_message_to_chat(message="/salute", channel='/s', pause=3.0)