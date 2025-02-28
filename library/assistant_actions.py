import numpy as np
import subprocess
import time
import logging

from library.hardware_input import HardwareInputSimulator
from library.game_window import GameWindow
from library.gingham_processing import pixels_analysis, get_message
from library.ai_openai import get_response


class CompanionActions(HardwareInputSimulator, GameWindow):
    def __init__(self, game_window: GameWindow):
        super().__init__()
        self.window_position = game_window.window_position
        self.window_size = game_window.window_size
        self.pixel_size = game_window.pixel_size
        self.n_pixels = game_window.n_pixels
        self.screenshot_shift = game_window.screenshot_shift

    @property
    def get_companion_position(self):
        position_x = self.window_position[0] + self.window_size[0] / 2
        position_y = self.window_position[1] + self.window_size[1] / 3 * 2
        return position_x, position_y

    def find_and_click(self, area_geometry):

        keywords = {'break': {
            'gathering': ['herbalism', 'mining'],
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

    # to Companion main class
    # def loot
    # def move
    # def rotate
    # def attack

    def send_message_to_chat(self, message, channel="/p", receiver=None, key_delay=20, pause=1):
        full_message = f"{channel} {receiver} {message}" if receiver is not None else f"{channel} {message}"
        self.release_movement_keys()
        self.press_key("enter", pause=0.2)
        self.type_text(full_message, key_delay=key_delay, pause=0.2)
        self.press_key("Return", pause=pause)

    def ai_companion_response(self, player_message, context_file):
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
