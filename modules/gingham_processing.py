import numpy as np
import re
from collections import Counter
import cv2

from library.errors import GinghamProcessorError
from library.constants import CALIBRATION_ARRAY

import matplotlib.pyplot as plt

class GinghamProcessor:
    @staticmethod
    def _get_image_array(data,
                         get_raw=False,
                         n_pixels=None,
                         x_from_to=None,
                         y_from_to=None,
                         rotate_90=False):

        try:
            img = data.convert("RGB")
            if get_raw:
                return np.array(img), None

        except AttributeError:
            raise GinghamProcessorError("No screenshot found for processing.")

        if y_from_to is None:
            y_from_to = {'from': 0, 'to': -1}
        if x_from_to is None:
            x_from_to = {'from': 0, 'to': -1}

        img_array = np.array(img)[x_from_to['from']:x_from_to['to'], y_from_to['from']:y_from_to['to'], :]
        if rotate_90:
            img_array = np.rot90(img_array, 1)
        if n_pixels:
            array_length = img_array.shape[1] // n_pixels
        else:
            array_length = None

        return img_array, array_length

    @staticmethod
    def find_subarray_index_2d(arr, subarr):
        arr, subarr = np.asarray(arr), np.asarray(subarr)
        if any(s1 < s2 for s1, s2 in zip(arr.shape, subarr.shape)):
            return -1, -1

        shape = tuple(np.subtract(arr.shape, subarr.shape) + 1) + subarr.shape
        strides = arr.strides * 2
        windows = np.lib.stride_tricks.as_strided(arr, shape=shape, strides=strides)

        comparison = (windows == subarr)
        axes = tuple(range(-subarr.ndim, 0))
        matches = np.all(comparison, axis=axes)

        match_indices = np.argwhere(matches)
        if match_indices.size == 0:
            return -1, -1
        else:
            return match_indices[0]


    # def get_calibration_array_position(self, screenshot):
    #     img, _ = self._get_image_array(screenshot, get_raw=True)
    #
    #     print(self.define_gingham_shirt_parameters(img, expected_rows=15, expected_cols=85))
    #
    #     img = img[:, :, 0]
    #     calibration_index = self.find_subarray_index_2d(img, CALIBRATION_ARRAY)
    #     return calibration_index

    def define_gingham_shirt_parameters(self, screenshot, expected_rows, expected_cols):

        data = {'zero_x': None,
                'zero_y': None,
                'widths': None,
                'heights': None}

        img, _ = self._get_image_array(screenshot, get_raw=True)
        img = img[:, :, 0] == 255
        img = np.array(img)

        for line in img:
            if sum(line) > 0:
                derivative = np.diff(line)
                data['zero_x'] = list(derivative).index(1.0)
                data['widths'] = np.diff(np.where(derivative == 1)[0].tolist()[:expected_cols + 1])
                break

        for line in img.T:
            if sum(line) > 0:
                derivative = np.diff(line)
                data['zero_y'] = list(derivative).index(1.0)
                data['heights'] = np.diff(np.where(derivative == 1)[0].tolist()[:expected_rows + 1])
                break

        return data

    @staticmethod
    def _get_dominant_color(i, img_array, array_length):
        section = img_array[:, i * array_length:(i + 1) * array_length, :]
        section_flat = section.reshape(-1, 3)
        dominant_color = Counter(map(tuple, section_flat)).most_common(1)[0][0]
        dominant_color = [color / 255.0 for color in dominant_color]
        return dominant_color

    def pixels_analysis(self, data, n_monitoring_pixels=None, pixel_height=None, pixel_width=None):
        img_array, array_length = self._get_image_array(data,
                                                        n_pixels=n_monitoring_pixels,
                                                        x_from_to={'from': 0,
                                                                   'to': pixel_height * (n_monitoring_pixels + 1)},
                                                        y_from_to={'from': 0,
                                                                   'to': pixel_width},
                                                        rotate_90=True)
        # append info about colors to the list
        data_colors = []
        for i in range(n_monitoring_pixels):
            dominant_color = self._get_dominant_color(i, img_array, array_length)
            data_colors.append(dominant_color)

        player_message_length = self._get_message_length(data_colors[-2])
        cursor_message_length = self._get_message_length(data_colors[-1])

        player_message_colors = []
        if player_message_length > 0:
            n_player_message_pixels = player_message_length // 3 + bool(player_message_length % 3)
            img_array, array_length = self._get_image_array(data,
                                                            n_pixels=n_player_message_pixels,
                                                            x_from_to={'from': 0,
                                                                       'to': pixel_height},
                                                            y_from_to={'from': pixel_width,
                                                                       'to': pixel_width * (
                                                                               n_player_message_pixels + 1)})
            for i in range(n_player_message_pixels):
                dominant_color = self._get_dominant_color(i, img_array, array_length)
                player_message_colors.append(dominant_color)

        cursor_message_colors = []
        if cursor_message_length > 0:
            n_cursor_message_pixels = cursor_message_length // 3 + bool(cursor_message_length % 3)
            img_array, array_length = self._get_image_array(data,
                                                            n_pixels=n_cursor_message_pixels,
                                                            x_from_to={'from': pixel_height,
                                                                       'to': 2 * pixel_height},
                                                            y_from_to={'from': pixel_width,
                                                                       'to': pixel_width * (
                                                                               n_cursor_message_pixels + 1)})
            for i in range(n_cursor_message_pixels):
                dominant_color = self._get_dominant_color(i, img_array, array_length)
                cursor_message_colors.append(dominant_color)

        return data_colors, player_message_colors, cursor_message_colors

    @staticmethod
    def _get_message_length(message_info_pixel):
        message_length = int(message_info_pixel[0] * 1000 + message_info_pixel[1] * 100 + message_info_pixel[2] * 10)
        return message_length

    @staticmethod
    def get_script_control_commands(script_control_pixel):
        pause = True if 0.0 < script_control_pixel < 1.0 else False
        disable = True if script_control_pixel == 1.0 else False
        return pause, disable

    def get_message(self, message_pixels):
        message = ""
        for pixel in message_pixels:
            for value in pixel:
                if value > 0:
                    value = round(value, 2)
                    character_number = int(value * 100 + 27)
                    character = chr(character_number)
                    message += character
                else:
                    message += " "
        message = self._convert_links_to_text(message)
        return message

    @staticmethod
    def cursor_message_parser(message):
        object_type, object_info = message.split(" | ")
        object_data = {}
        if object_type == "unit":
            object_data[object_type] = {}
            object_info = object_info.split('; ')
            for info in object_info:
                object_data[object_type][info.split(':')[0]] = info.split(':')[1].lstrip().rstrip()
        elif object_type == "gameobject":
            if 'requires' in object_info:
                name, profession = object_info.split(', ')
                object_data[object_type] = {'name': name, 'requires': profession.split(' ')[-1]}
            else:
                object_data[object_type] = {'info': object_info}
        return object_data

    @staticmethod
    def _convert_links_to_text(message):
        matches = re.findall(r'\[([^\]]+)\]', message)
        for match in matches:
            pattern = r'\|[0-9a-fA-F]{9}\|h(?:item|quest|spell|enchant):[^|]+\|h\[' + re.escape(match) + r'\]\|h\|r'
            message = re.sub(pattern, f'[{match}]', message)
        return message

    @staticmethod
    def session_constants():
        health_to_start_healing = 0.6
        return {'health_to_start_healing': health_to_start_healing}

    @staticmethod
    def check_bool_pixel(pixel, pixel_value):
        return True if round(pixel, 2) == pixel_value else False

    @staticmethod
    def get_map_id(pixel):
        map_id = int(((1 / pixel[0] if pixel[0] > 0 else 0) + pixel[1]) * 255)
        return map_id

    def to_dictionary(self, all_pixels):
        data_pixels, player_message_pixels, cursor_message_pixels = all_pixels[0], all_pixels[1], all_pixels[2]

        pause_script = True if 0.2 < data_pixels[0][0] < 0.3 else False
        disable_script = True if 0.4 < data_pixels[0][0] < 0.6 else False

        follow_command = self.check_bool_pixel(data_pixels[0][1],
                                               1.0)  # True if round(data_pixels[0][1], 2) == 1.0 else False
        step_by_step_command = self.check_bool_pixel(data_pixels[0][1],
                                                     0.5)  # True if round(data_pixels[0][1], 2) == 0.5 else False
        stay_command = self.check_bool_pixel(data_pixels[0][1], 0.0)

        assist_command = self.check_bool_pixel(data_pixels[0][2],
                                               1.0)  # True if round(data_pixels[0][2], 2) == 1.0 else False
        defend_command = self.check_bool_pixel(data_pixels[0][2],
                                               0.75)  # True if round(data_pixels[0][2], 2) == 0.75 else False
        only_heal_command = self.check_bool_pixel(data_pixels[0][2],
                                                  0.5)  # True if round(data_pixels[0][2], 2) == 0.5 else False
        passive_command = self.check_bool_pixel(data_pixels[0][2], 0.0)

        loot_command = self.check_bool_pixel(data_pixels[1][0], 1.0)
        mount_command = self.check_bool_pixel(data_pixels[1][1], 1.0)
        change_speed_command = self.check_bool_pixel(data_pixels[1][2], 1.0)

        companion_coordinates_pixels = data_pixels[2:4]
        companion_combat_status, companion_health, companion_mana = data_pixels[4]
        player_coordinates_pixels = data_pixels[5:7]
        player_combat_status, player_health, player_mana = data_pixels[7]

        companion_mounted, companion_breath_level, _ = data_pixels[8]

        map_id = self.get_map_id(data_pixels[9])

        player_message = self.get_message(player_message_pixels)
        cursor_message = self.get_message(cursor_message_pixels)

        session_data = {'pause_script': pause_script,
                        'disable_script': disable_script,
                        'follow_command': follow_command,
                        'step_by_step_command': step_by_step_command,
                        'stay_command': stay_command,
                        'assist_command': assist_command,
                        'defend_command': defend_command,
                        'only_heal_command': only_heal_command,
                        'passive_command': passive_command,
                        'loot_command': loot_command,
                        'mount_command': mount_command,
                        'change_speed_command': change_speed_command,
                        'player_coordinates_pixels': player_coordinates_pixels,
                        'player_combat_status': player_combat_status,
                        'player_health': player_health,
                        'player_mana': player_mana,
                        'companion_coordinates_pixels': companion_coordinates_pixels,
                        'companion_combat_status': companion_combat_status,
                        'companion_health': companion_health,
                        'companion_mana': companion_mana,
                        'companion_mounted': companion_mounted,
                        'companion_breath_level': companion_breath_level,
                        'map_id': map_id,
                        'player_message': player_message,
                        'cursor_message': cursor_message}

        session_data.update(self.session_constants())

        return session_data
