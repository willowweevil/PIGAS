import numpy as np
import re
from collections import Counter
from pprint import pprint
from matplotlib import pyplot as plt
import matplotlib as mpl

mpl.use('TkAgg')


def get_image_array(data,
                    n_pixels=None,
                    x_from_to=None,
                    y_from_to=None,
                    rotate_90=False):
    if y_from_to is None:
        y_from_to = {'from': 0, 'to': -1}
    if x_from_to is None:
        x_from_to = {'from': 0, 'to': -1}
    img = data.convert("RGB")
    img_array = np.array(img)[x_from_to['from']:x_from_to['to'], y_from_to['from']:y_from_to['to'], :]
    if rotate_90:
        img_array = np.rot90(img_array, 1)
    array_length = img_array.shape[1] // n_pixels

    return img_array, array_length


def get_dominant_color(i, img_array, array_length):
    section = img_array[:, i * array_length:(i + 1) * array_length, :]
    section_flat = section.reshape(-1, 3)
    dominant_color = Counter(map(tuple, section_flat)).most_common(1)[0][0]
    dominant_color = [color / 255.0 for color in dominant_color]
    return dominant_color


def pixels_analysis(data=None, n_monitoring_pixels=None, pixel_height=None, pixel_width=None):
    img_array, array_length = get_image_array(data, n_monitoring_pixels,
                                              x_from_to={'from': 0,
                                                         'to': pixel_height * (n_monitoring_pixels + 1)},
                                              y_from_to={'from': 0,
                                                         'to': pixel_width},
                                              rotate_90=True)
    # append info about colors to the list
    data_colors = []
    for i in range(n_monitoring_pixels):
        dominant_color = get_dominant_color(i, img_array, array_length)
        data_colors.append(dominant_color)

    player_message_length = get_message_length(data_colors[-2])
    cursor_message_length = get_message_length(data_colors[-1])

    player_message_colors = []
    if player_message_length > 0:
        n_player_message_pixels = player_message_length // 3 + bool(player_message_length % 3)
        img_array, array_length = get_image_array(data, n_player_message_pixels,
                                                  x_from_to={'from': 0,
                                                             'to': pixel_height},
                                                  y_from_to={'from': pixel_width,
                                                             'to': pixel_width * (n_player_message_pixels + 1)})
        for i in range(n_player_message_pixels):
            dominant_color = get_dominant_color(i, img_array, array_length)
            player_message_colors.append(dominant_color)

    cursor_message_colors = []
    if cursor_message_length > 0:
        n_cursor_message_pixels = cursor_message_length // 3 + bool(cursor_message_length % 3)
        img_array, array_length = get_image_array(data, n_cursor_message_pixels,
                                                  x_from_to={'from': pixel_height,
                                                             'to': 2 * pixel_height},
                                                  y_from_to={'from': pixel_width,
                                                             'to': pixel_width * (n_cursor_message_pixels + 1)})
        for i in range(n_cursor_message_pixels):
            dominant_color = get_dominant_color(i, img_array, array_length)
            cursor_message_colors.append(dominant_color)

    return data_colors, player_message_colors, cursor_message_colors


def get_message_length(message_info_pixel):
    message_length = int(message_info_pixel[0] * 1000 + message_info_pixel[1] * 100 + message_info_pixel[2] * 10)
    return message_length

def get_script_control_commands(script_control_pixel):
    pause = True if 0.0 < script_control_pixel < 1.0 else False
    disable = True if script_control_pixel == 1.0 else False
    return pause, disable


def get_message(message_pixels):
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
    message = convert_links_to_text(message)
    return message


def convert_links_to_text(message):
    matches = re.findall(r'\[([^\]]+)\]', message)
    for match in matches:
        pattern = r'\|[0-9a-fA-F]{9}\|h(?:item|quest|spell|enchant):[^|]+\|h\[' + re.escape(match) + r'\]\|h\|r'
        message = re.sub(pattern, f'[{match}]', message)
    return message
