import subprocess
import logging
import time

import mss
from PIL import Image

from modules.gingham_processing import GinghamProcessor

from library.miscellaneous import define_system_platform

from library.errors import GameWindowError
from library.platforms import Platform

if define_system_platform() == Platform.WINDOWS:
    import win32gui
    import win32com.client
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


class GameWindow:
    def __init__(self):

        # without message length pixels (now the message length pixels defined as [-1] element!)
        self.n_pixels = {'x': 201, 'y': 12}

        # N pixels from calibration lines (#calibration command)
        self.n_rows = 15
        self.n_cols = 85
        self.pixel_size = {'x': 5, 'y': 5}
        self.pixels_sizes = {'x': [], 'y': []}

        self.screenshot_shift = None

        self.platform = None

        self.window_title = None
        self.window_id = None
        self.window_position = None
        self.window_size = None

        self.logger = logging.getLogger('game_window')

    def _set_system_platform(self):
        self.platform = define_system_platform()

    def _set_window_title(self, config_data):
        game_config = config_data.get('game')
        if not game_config:
            raise GameWindowError(f"Game config is not set! Please, check the config file!")

        self.window_title = game_config.get('window-title', 'World of Warcraft')

    def define_gingham_screenshot_shift(self, savefig=False):
        img = self.take_screenshot(savefig=savefig, savefig_prefix='calibration', screenshot_type='calibration')

        gingham_shirt_geometry = GinghamProcessor().define_gingham_shirt_parameters(
            img,
            expected_rows = self.n_rows,
            expected_cols = self.n_cols)

        if gingham_shirt_geometry['zero_x'] is None:
            return False
        self.screenshot_shift = {'x': gingham_shirt_geometry['zero_x'], 'y': gingham_shirt_geometry['zero_y']}
        self.pixels_sizes = {'x': gingham_shirt_geometry['widths'], 'y': gingham_shirt_geometry['heights']}
        self.logger.debug(f"Screenshot shift was set to: {self.screenshot_shift}")
        self.logger.debug(f"Pixels sizes are: {self.pixels_sizes}")
        return True

    def set_window_parameters(self, config_data=None):
        if not self.platform:
            self._set_system_platform()
        if not self.window_title:
            self._set_window_title(config_data)
        if not self.window_id:
            self._set_window_id()
        if not self.window_position or not self.window_size:
            self._set_window_geometry()

        self.logger.debug(f"Successfully set game window parameters: "
                          f"platform={self.platform}; "
                          f"title={self.window_title}; "
                          f"id={self.window_id}; "
                          f"position={self.window_position}; "
                          f"size={self.window_size}.")

    def _set_window_id(self):
        """Find the window ID by title."""
        match self.platform:
            case Platform.LINUX:
                result = subprocess.run(['xdotool', 'search', '--name', f"^{self.window_title}$"],
                                        capture_output=True,
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
                window_ids = None
                raise GameWindowError("Cannot define window ID: unsupported system.")

        if len(window_ids) > 0:
            self.logger.debug(
                f'Found {len(window_ids)} window{'s' if len(window_ids) > 1 else ''} with name {self.window_title}: {', '.join(window_ids)}')
            if len(window_ids) > 1:
                self.logger.debug(f'The first one will be used.')
            self.window_id = window_ids[0]
        else:
            raise GameWindowError(f"\"{self.window_title}\": no window found.")

    def _get_window_geometry(self):
        match self.platform:
            case Platform.LINUX:
                try:
                    result = subprocess.run(['xdotool', 'getwindowgeometry', self.window_id], capture_output=True,
                                            text=True)
                except subprocess.CalledProcessError as e:
                    raise GameWindowError(f"Failed to identify active window geometry. Error: {e}")
                except Exception as e:
                    raise GameWindowError(f"An unexpected error occurred during game window geometry defining: {e}")
                return result.stdout.split('\n')
            case Platform.WINDOWS:
                result = win32gui.GetWindowRect(self.window_id)
                return result
            case _:
                raise GameWindowError("Cannot get window geometry: unsupported system.")

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
                raise GameWindowError("Cannot set window geometry: unsupported system.")

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
                raise GameWindowError("Cannot activate window: unsupported system.")

        return current_window

    def _activate_window(self):
        """Activate the window by ID."""
        match self.platform:
            case Platform.LINUX:
                try:
                    subprocess.run(['xdotool', 'windowactivate', self.window_id], capture_output=True, text=True)
                    self.logger.info(f"Window {self.window_title} (ID: {self.window_id}) activated successfully.")
                except subprocess.CalledProcessError as e:
                    raise GameWindowError(
                        f"Failed to activate window {self.window_title} (id: {self.window_id}). "
                        f"Error: {e}")
                except Exception as e:
                    raise GameWindowError(
                        f"Failed to activate window {self.window_title} (id: {self.window_id}). "
                        f"An unexpected error occurred: {e}")
            case Platform.WINDOWS:
                try:
                    win32com.client.Dispatch("WScript.Shell").SendKeys('%')
                    win32gui.SetForegroundWindow(self.window_id)
                except Exception as e:
                    error_code, function_name, _ = e.args
                    if error_code == 1400 and function_name == 'SetForegroundWindow':
                        raise GameWindowError(
                            f"Failed to activate window {self.window_title} (id: {self.window_id}). "
                            f"Window not found.")
                    else:
                        raise GameWindowError(
                            f"Failed to activate window {self.window_title} (id: {self.window_id}). "
                            f"An unexpected error occurred: {e}")
            case _:
                raise GameWindowError("Cannot activate window: unsupported system.")

    def ensure_window_active(self):
        current_active_window = self._get_current_active_window()
        if current_active_window != self.window_title:
            if self.window_id:
                time.sleep(1)
                self._activate_window()
            else:
                raise GameWindowError(f"Cannot activate window {self.window_title}. No windows found.")

    def ensure_window_exists(self):
        self._set_window_id()

    def _get_gingham_screenshot_geometry(self):
        position_x, position_y = self.window_position
        width = self.pixel_size['x'] * self.n_pixels['x'] # sum(self.pixels_sizes['x'])
        height = self.pixel_size['y'] * self.n_pixels['y']  # sum(self.pixels_sizes['y']) #
        if self.screenshot_shift:
            x_shift = self.screenshot_shift['x'] if self.screenshot_shift['x'] else 0
            y_shift = self.screenshot_shift['y'] if self.screenshot_shift['y'] else 0
        else:
            x_shift, y_shift = 0, 0
        return position_x, position_y, width, height, x_shift, y_shift

    def _get_window_screenshot_geometry(self):
        position_x, position_y = self.window_position
        width, height = self.window_size
        x_shift, y_shift = 0, 0
        return position_x, position_y, width, height, x_shift, y_shift

    def _get_calibration_screenshot_geometry(self):
        position_x, position_y = self.window_position
        width, height = [val // 2 for val in self.window_size]
        x_shift, y_shift = 0, 0
        return position_x, position_y, width, height, x_shift, y_shift

    def take_screenshot(self, savefig=False, savefig_prefix='gingham', screenshot_type='gingham'):
        match screenshot_type:
            case 'gingham':
                position_x, position_y, width, height, x_shift, y_shift = self._get_gingham_screenshot_geometry()
            case 'window':
                position_x, position_y, width, height, x_shift, y_shift = self._get_window_screenshot_geometry()
            case 'calibration':
                position_x, position_y, width, height, x_shift, y_shift = self._get_calibration_screenshot_geometry()
            case _:
                raise GameWindowError(f"Unknown screenshot type: {screenshot_type}.")

        with mss.mss() as sct:
            try:
                area = {"top": position_y + y_shift, "left": position_x + x_shift, "width": width, "height": height}
                screenshot = sct.grab(area)
            except mss.ScreenShotError as e:
                raise GameWindowError(f"An error occurs during the screenshot: {e}")
            self.logger.debug(
                f"Took screenshot of area {width}x{height} (zero in {position_x + x_shift},{position_y + y_shift})")
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            if savefig:
                img.save(
                    f"screenshot_{savefig_prefix}_zero_{position_x + x_shift},{position_y + y_shift}_size_{width}x{height}_debug.png")
        return img