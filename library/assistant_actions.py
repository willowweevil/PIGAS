import numpy as np
import subprocess
import time
import logging

from library.inputs import InputController
from library.game_window import GameWindow
from library.gingham_processing import pixels_analysis, get_message
from library.ai_openai import get_response


class AssistantActions(InputController, GameWindow):
    def __init__(self, game_window: GameWindow):
        super().__init__()
        self.window_title = game_window.window_title
        self.window_id = game_window.window_id
        self.window_position = game_window.window_position
        self.window_size = game_window.window_size
        self.pixel_size = game_window.pixel_size
        self.n_pixels = game_window.n_pixels
        self.screenshot_shift = game_window.screenshot_shift

    @property
    def assistant_position(self):
        position_x = self.window_position[0] + self.window_size[0] / 2
        position_y = self.window_position[1] + self.window_size[1] / 3 * 2
        return position_x, position_y

    def find_and_click(self, area_x, area_y, area_shift_x, area_shift_y, step_x, step_y, should_break=True):
        cursor_message, break_reason = self.scan_area(area_x, area_y, area_shift_x, area_shift_y, step_x, step_y,
                                                   should_break=should_break)
        if break_reason:
            self.click_mouse()
            if break_reason == 'gather':
                time.sleep(3)
        else:
            logging.info("Didn't find anything during the scan.")

    def scan_area(self, area_x, area_y, area_shift_x, area_shift_y, step_x, step_y, should_break=False):

        gathering_keywords = ['herbalism', 'mining']
        looting_keywords = ['corpse', 'skivvy', 'requires']
        scan_array_x, scan_array_y = self._get_scan_array_sides(area_x, area_y, area_shift_x, area_shift_y,
                                                                step_x, step_y)
        output_message = []
        for y in scan_array_y[::-1]:
            for x in scan_array_x:
                self.move_mouse_to(x, y)
                time.sleep(0.1)  # the pause must be here, because new gingham shirts pixels are updating some time
                scan_gingham_shirt = self.take_screenshot(savefig=False, savefig_prefix='scan')
                _, _, cursor_pixels = pixels_analysis(data=scan_gingham_shirt,
                                                   n_monitoring_pixels=self.n_pixels['y'],
                                                   pixel_height=self.pixel_size['y'],
                                                   pixel_width=self.pixel_size['x'])
                scan_message = get_message(cursor_pixels).lower()
                if scan_message:
                    if should_break:
                        if any(keyword in scan_message for keyword in gathering_keywords):
                            return scan_message, 'gather'
                        elif any(keyword in scan_message for keyword in looting_keywords):
                            return scan_message, 'loot'
                    else:
                        output_message.append(scan_message)
        return output_message, False

    def _get_scan_array_sides(self, area_x, area_y, area_shift_x, area_shift_y, step_x, step_y):
        character_position_x, character_position_y = self.assistant_position

        scan_array_x = np.linspace(character_position_x - area_x / 2 + area_shift_x,
                                   character_position_x + area_x / 2 + area_shift_x,
                                   num=int(area_x / step_x) + 1,
                                   endpoint=True,
                                   dtype=int)
        scan_array_y = np.linspace(character_position_y - area_y / 2 + area_shift_y,
                                   character_position_y + area_y / 2 + area_shift_y,
                                   num=int(area_y / step_y) + 1,
                                   endpoint=True, dtype=int)
        return scan_array_x, scan_array_y

    def send_message(self, message, channel="/p", receiver=None, key_delay=20, pause=1):
        full_message = f"{channel} {receiver} {message}" if receiver is not None else f"{channel} {message}"
        self.release_movement_keys()
        self.press_key("enter", pause=0.2)
        self.type_text(full_message, key_delay=key_delay, pause=0.2)
        self.press_key("Return", pause=pause)


    def assistant_response(self, player_message, context_file):
        with open(context_file, 'r') as file:
            context = file.read()
            file.close()
        context += f"{player_message}\n"

        assistant_answer_start_time = time.time()
        logging.info("Getting response..")
        response = get_response(context).strip()
        if response:
            logging.info(f"Assistant response: {response}")
            context += f"{response}\n\n"
            with open(context_file, "w") as f:
                f.write(context)
                f.close()
            if len(response) >= 255:
                self.send_message(response[:255], key_delay=40)
                response = response[255:]
            self.send_message(response, key_delay=40)
        else:
            self.send_message("I'm too tired to speak now..", key_delay=20)
        logging.info(f"Assistant answer time was {round(time.time() - assistant_answer_start_time, 2)} seconds.")