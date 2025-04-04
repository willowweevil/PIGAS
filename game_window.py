import subprocess
import logging
import time
import sys

import mss
from PIL import Image

if 'win' in sys.platform.lower():
    import win32gui
else:
    class MockWin32GUI:
        @staticmethod
        def GetWindowRect(*args, **kwargs):
            return False
        @staticmethod
        def GetWindowText(self, *args, **kwargs):
            return False
        @staticmethod
        def EnumWindows(self, *args, **kwargs):
            return False
        @staticmethod
        def GetForegroundWindow(*args, **kwargs):
            return False
        @staticmethod
        def SetForegroundWindow(*args, **kwargs):
            return False
    win32gui = MockWin32GUI()

from library.miscellaneous import read_yaml_file
from library.platforms import Platform


class GameWindow:
    def __init__(self):
        self.pixel_size = {'x': 5, 'y': 5}
        self.n_pixels = {'x': 201, 'y': 11}
        self.screenshot_shift = None 

        self.platform = None

        self.window_title = None
        self.window_id = None
        self.window_position = None
        self.window_size = None

        self.logger = logging.getLogger('game_window')
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)
            self.logger.propagate = False

    def set_platform(self):
        if sys.platform in ['linux', 'linux2']:
            self.platform = Platform.LINUX
        elif sys.platform in ['Windows', 'win32', 'cygwin']:
            self.platform = Platform.WINDOWS
        elif sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
            self.platform = Platform.MACOS
        else:
            self.logger.error(f"Cannot define platform: {sys.platform}")
            exit(1)
        
        self.logger.info(f"System platform was defined as {str(self.platform)[1]}")

    def set_window_title_from_config(self, config=None):
        config_data = read_yaml_file(config)
        self.window_title = config_data['game']['window-title']

    def set_window_parameters(self, config_file=None):
        if not self.platform:
            self.set_platform()
        if not self.window_title:
            self.set_window_title_from_config(config_file)
        if not self.window_id:
            self._set_window_id()
        if not self.window_position or not self.window_size:
            self._set_window_geometry()

        match self.platform:
            case Platform.LINUX:
                self.screenshot_shift = {'x': 14, 'y': 49}
            case Platform.WINDOWS:
                self.screenshot_shift = {'x': 9, 'y': 38} #{'x': 8, 'y': 31}

    def _set_window_id(self):
        """Find the window ID by title."""
        match self.platform:
            case Platform.LINUX:
                result = subprocess.run(['xdotool', 'search', '--name', f"^{self.window_title}$"], capture_output=True,
                                        text=True)
                window_ids = result.stdout.splitlines()
            case Platform.WINDOWS:
                window_ids = []
                def enum_callback(hwnd, lParam):
                    window_title = win32gui.GetWindowText(hwnd)
                    if self.window_title in window_title:
                        window_ids.append(str(hwnd))
                win32gui.EnumWindows(enum_callback, None)
            case _:
                self.logger.error("Cannot define window ID: unsupported system.")
                exit(1)

        if len(window_ids) > 0:
            self.logger.info(
                f'Found {len(window_ids)} window{'s' if len(window_ids) > 1 else ''} with name {self.window_title}: {', '.join(window_ids)}')
            if len(window_ids) > 1:
                self.logger.info(f'The first one will be activated.')
            self.window_id = window_ids[0]
        else:
            self.logger.error(f"\"{self.window_title}\": no window found.")
            exit(1)

    def _get_window_geometry(self):
        match self.platform:
            case Platform.LINUX:
                try:
                    result = subprocess.run(['xdotool', 'getwindowgeometry', self.window_id], capture_output=True, text=True)
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Failed to identify active window geometry. Error: {e}")
                    exit(1)
                except Exception as e:
                    self.logger.error(f"An unexpected error occurred during game window geometry defining: {e}")
                    exit(1)
                return result.stdout.split('\n')
            case Platform.WINDOWS:
                result = win32gui.GetWindowRect(self.window_id)
                return result
            case _:
                self.logger.error("Cannot get window geometry: unsupported system.")
                exit(1)

    def _set_window_geometry(self):
        window_raw_info = self._get_window_geometry()
        match self.platform:
            case Platform.LINUX:
                position = window_raw_info[1].lstrip().split(' ')[1].split(',')
                size = window_raw_info[2].lstrip().split(' ')[1].split('x')
            case Platform.WINDOWS:
                left, top, right, bottom = window_raw_info
                width = right - left
                height = bottom - top
                position = left, top
                size = width, height
            case _:
                self.logger.error("Cannot set window geometry: unsupported system.")
                exit(1)

    
        self.logger.debug(f"Window position: x={position[0]}, y={position[1]}")
        self.logger.debug(f"Window size: {size[0]}x{size[1]}")
        self.window_position = [int(val) for val in position]
        self.window_size = [int(val) for val in size]

    def _get_current_active_window(self):
        match self.platform:
            case Platform.LINUX:
                result = subprocess.run(['xdotool', 'getwindowfocus', 'getwindowname'], capture_output=True, text=True)
                current_window = result.stdout.split('\n')[0]
            case Platform.WINDOWS:
                result = win32gui.GetForegroundWindow()
                current_window = win32gui.GetWindowText(result)
            case _:
                self.logger.error("Cannot activate window: unsupported system.")
                exit(1)

        return current_window

    def activate_window(self):
        """Activate the window by ID."""
        match self.platform:
            case Platform.LINUX:
                try:
                    subprocess.run(['xdotool', 'windowactivate', self.window_id], capture_output=True, text=True)
                    self.logger.info(f"Window {self.window_id} activated successfully.")
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Failed to activate window {self.window_id}. Error: {e}")
                    exit(1)
                except Exception as e:
                    self.logger.error(f"Failed to activate window {self.window_id}. An unexpected error occurred: {e}")
                    exit(1)
            case Platform.WINDOWS:
                try:
                    win32gui.SetForegroundWindow(self.window_id)
                except Exception as e:
                   self.logger.error(f"Failed to activate window {self.window_id}. An unexpected error occurred: {e}")
                   exit(1)
            case _:
                self.logger.error("Cannot activate window: unsupported system.")
                exit(1)

    def ensure_window_active(self):
        current_active_window = self._get_current_active_window()
        if current_active_window != self.window_title:
            if self.window_id:
                time.sleep(1)
                self.activate_window()
            else:
                self.logger.error(f"Cannot activate window {self.window_title}. No windows found.")

    def _get_screenshot_geometry(self):
        position_x, position_y = self.window_position
        width = self.pixel_size['x'] * self.n_pixels['x']
        height = self.pixel_size['y'] * self.n_pixels['y']
        if self.screenshot_shift:
            x_shift = self.screenshot_shift['x'] if self.screenshot_shift['x'] else 0
            y_shift = self.screenshot_shift['y'] if self.screenshot_shift['y'] else 0
        else:
            x_shift, y_shift = 0, 0
        return position_x, position_y, width, height, x_shift, y_shift

    def take_screenshot(self, savefig=False, savefig_prefix='main'):
        position_x, position_y, width, height, x_shift, y_shift = self._get_screenshot_geometry()
        with mss.mss() as sct:
            try:
                area = {"top": position_y + y_shift, "left": position_x + x_shift, "width": width, "height": height}
                screenshot = sct.grab(area)
            except mss.ScreenShotError:
                self.logger.error("Unable to take a screenshot.")
                return None
            self.logger.debug(f"Took screenshot of area {width}x{height} (zero in {position_x+x_shift},{position_y+y_shift})")
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            if savefig:
                img.save(f"{savefig_prefix}_{position_x+x_shift}_{position_y+y_shift}_{height}_{width}.png")
        return img

# def get_initial_monitor_parameters():
#     hdmi_monitor_shift_x, hdmi_monitor_shift_y = None, None
#     try:
#         xrandr = subprocess.Popen('xrandr', stdout=subprocess.PIPE)
#         output = subprocess.check_output(('grep', 'HDMI'), stdin=xrandr.stdout)
#         xrandr.wait()
#         hdmi_monitor_shift_x, hdmi_monitor_shift_y = re.search(r"[0-9]{3,4}x[0-9]{3,4}", str(output))[0].split('x')
#         logging.info("Second HDMI monitor found. The game window should be on the first (native) screen.")
#     except subprocess.CalledProcessError as e:
#         logging.info("Second HDMI monitor not found.")
#
#     return hdmi_monitor_shift_x, hdmi_monitor_shift_y

# def run_game():
#     start_game_command = read_yaml_file('config.yaml')['game']['run']
#     try:
#         subprocess.run(['nohup'] + start_game_command.split(' ') + ['&'], capture_output=True, text=True)
#         logging.info("The game successfully started.")
#     except subprocess.CalledProcessError as e:
#         logging.error(f"Failed to start the game. Error: {e}")
#         exit(1)
#     except Exception as e:
#         logging.error(f"An unexpected error occurred at game start: {e}")
#         exit(1)
