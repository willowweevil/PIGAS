import time
import subprocess
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button


class InputController:
    def __init__(self):
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

    @staticmethod
    def _transform_input_key_or_button(input_key):
        output_key = input_key
        match input_key.lower():
            case 'left':
                output_key = Button.left
            case 'right':
                output_key = Button.right
            case 'shift':
                output_key = Key.shift
            case 'space':
                output_key = Key.space
            case 'f1':
                output_key = Key.f1
            case 'f2':
                output_key = Key.f2
        if input_key.lower() in ['enter', 'return']:
            output_key = Key.enter
        return output_key

    @staticmethod
    def type_text(message, key_delay=20, pause=1.0):
        subprocess.run(["ydotool", "type", "--key-delay", f"{key_delay}", message], stderr=subprocess.DEVNULL)
        time.sleep(pause)

    def move_mouse_to_default_position(self, game_window):
        delta_x = 50
        delta_y = 50
        position_x = game_window.window_position[0] + game_window.window_size[0] - delta_x
        position_y = game_window.window_position[1] + game_window.window_size[1] - delta_y
        self.move_mouse_to(position_x, position_y)

    def move_mouse_to(self, x, y, pause=0):
        self.mouse.position = (x, y)
        time.sleep(pause)

    def click_mouse(self, button='right', click_count=1, pause=0):
        button = self._transform_input_key_or_button(button)
        self.mouse.click(button, click_count)
        time.sleep(pause)

    def press_key(self, key, pause=0.05):
        key = self._transform_input_key_or_button(key)
        self.keyboard.tap(key)
        time.sleep(pause)

    def hold_key_for_time(self, key, duration=1):
        key = self._transform_input_key_or_button(key)
        self.keyboard.press(key)
        time.sleep(duration)
        self.keyboard.release(key)

    def hold_key(self, key):
        key = self._transform_input_key_or_button(key)
        self.keyboard.press(key)

    def release_key(self, key):
        key = self._transform_input_key_or_button(key)
        self.keyboard.release(key)

    def send_message_as_api_function(self, message=None, chat_type="WHISPER", channel="player", pause=1, key_delay=12):
        """
        :param key_delay:
        :param message: text of your message
        :param chat_type: SAY EMOTE YELL PARTY GUILD OFFICER RAID RAID_WARNING INSTANCE_CHAT BATTLEGROUND WHISPER CHANNEL
        :param channel: player party1 ...
        :param pause: pause after a message
        :return:
        """
        self.release_movement_keys()
        full_message = f'/run SendChatMessage(\"{message}\", \"{chat_type}\", nil, UnitName(\"{channel}\"))'
        self.keyboard.tap(Key.enter)
        time.sleep(0.2)
        subprocess.run(["ydotool", "type", "--key-delay", f"{key_delay}", full_message])
        time.sleep(0.2)
        self.keyboard.tap(Key.enter)
        time.sleep(pause)

    def release_movement_keys(self):
        self.release_key("w"), self.release_key("a"), self.release_key("s"), self.release_key("d")

# class InputControllerXdotool:
#
#     def __init__(self, game_window=None):
#         self.game_window = game_window
#
#     def move_mouse_to_default_position(self):
#         delta_x = 50
#         delta_y = 50
#         position_x = self.game_window.window_position[0] + self.game_window.window_size[0] - delta_x
#         position_y = self.game_window.window_position[1] + self.game_window.window_size[1] - delta_y
#         self.move_mouse(position_x, position_y)
#
#     @staticmethod
#     def move_mouse(x, y, pause=0):
#         subprocess.run(['xdotool', 'mousemove', str(x), str(y)])
#         time.sleep(pause)
#
#     @staticmethod
#     def click_mouse(button='left'):
#         match button:
#             case 'left':
#                 button = '1'
#             case 'right':
#                 button = '3'
#         subprocess.run(['xdotool', 'click', button])
#
#     @staticmethod
#     def press_key(key, pause=0.1):
#         if key == Key.space:
#             key = "space"
#         subprocess.run(['xdotool', 'key', key])
#         time.sleep(pause)
#
#     @staticmethod
#     def hold_key_for_time(key, duration=1):
#         subprocess.run(['xdotool', 'keydown', key], check=True)
#         time.sleep(duration)
#         subprocess.run(['xdotool', 'keyup', key], check=True)
#
#     @staticmethod
#     def hold_key(key):
#         if key == Key.shift:
#             key = "shift"
#         subprocess.run(['xdotool', 'keydown', key], check=True)
#
#     @staticmethod
#     def release_key(key):
#         if key == Key.shift:
#             key = "shift"
#         subprocess.run(['xdotool', 'keyup', key], check=True)
#
#     # @staticmethod
#     # def type_text(text, pause=1):
#     #     subprocess.run(["xdotool", "key", "Return"])
#     #     subprocess.run(["xdotool", "type", text])
#     #     subprocess.run(["xdotool", "key", "Return"])
#     #     time.sleep(pause)
#
#     @staticmethod
#     def type_text(message, key_delay=20, pause=1.0):
#         subprocess.run(["ydotool", "type", "--key-delay", f"{key_delay}", message], stderr=subprocess.DEVNULL)
#         time.sleep(pause)
#
#     # def send_message(self, message, channel="/p", receiver=None, key_delay=20, pause=1):
#     #     self.release_movement_keys()
#     #     full_message = f"{channel} {receiver} {message}" if receiver is not None else f"{channel} {message}"
#     #     subprocess.run(["xdotool", "key", "Return"])
#     #     time.sleep(0.2)
#     #     subprocess.run(["ydotool", "type", "--key-delay", f"{key_delay}", full_message], stderr=subprocess.DEVNULL)
#     #     time.sleep(0.2)
#     #     subprocess.run(["xdotool", "key", "Return"])
#     #     time.sleep(pause)
#
#     @staticmethod
#     def send_message_as_api_function(self, message=None, chat_type="WHISPER", channel="player", pause=1, delay=12):
#         """
#         :param message: text of your message
#         :param chat_type: SAY EMOTE YELL PARTY GUILD OFFICER RAID RAID_WARNING INSTANCE_CHAT BATTLEGROUND WHISPER CHANNEL
#         :param channel: player party1 ...
#         :param pause: pause after a message
#         :return:
#         """
#         self.release_movement_keys()
#         full_message = f'/run SendChatMessage(\"{message}\", \"{chat_type}\", nil, UnitName(\"{channel}\"))'
#         subprocess.run(["xdotool", "key", "Return"])
#         time.sleep(0.2)
#         subprocess.run(["ydotool", "type", "--key-delay", f"{delay}", full_message])
#         time.sleep(0.2)
#         subprocess.run(["xdotool", "key", "Return"])
#         time.sleep(pause)
#
#     def release_movement_keys(self):
#         self.release_key("w"), self.release_key("a"), self.release_key("s"), self.release_key("d")
