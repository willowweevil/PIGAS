import subprocess
import logging
import mss
from PIL import Image
from library.other import read_yaml_file
import time


def run_game():
    start_game_command = read_yaml_file('config.yaml')['game']['run']
    try:
        subprocess.run(['nohup'] + start_game_command.split(' ') + ['&'], capture_output=True, text=True)
        logging.info("The game successfully started.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to start the game. Error: {e}")
        exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred at game start: {e}")
        exit(1)

class GameWindow:
    def __init__(self):

        self.pixel_size = {'x': 5, 'y': 5}
        self.n_pixels = {'x': 201, 'y': 10}
        self.screenshot_shift = {'x': 14, 'y': 49}

        self.window_title = None
        self.window_id = None
        self.window_position = None
        self.window_size = None

    def _find_window(self):
        """Find the window ID by title."""
        result = subprocess.run(['xdotool', 'search', '--name', f"^{self.window_title}$"], capture_output=True,
                                text=True)
        window_ids = result.stdout.splitlines()
        if len(window_ids) > 0:
            logging.info(
                f'Found {len(window_ids)} window{'s' if len(window_ids) > 1 else ''} with name {self.window_title}: {', '.join(window_ids)}')
            if len(window_ids) > 1:
                logging.info(f'The first one will be activated.')
            self.window_id = window_ids[0]
        else:
            logging.error(f"\"{self.window_title}\": no window found.")# Trying to run new game window.")
            exit(1)
            #run_game()

    def _get_window_geometry(self):
        try:
            result = subprocess.run(['xdotool', 'getwindowgeometry', self.window_id], capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to identify active window geometry. Error: {e}")
            exit(1)
        except Exception as e:
            logging.error(f"An unexpected error occurred during game window geometry defining: {e}")
            exit(1)
        return result.stdout.split('\n')

    def _define_window_geometry(self):
        window_raw_info = self._get_window_geometry()
        position = window_raw_info[1].lstrip().split(' ')[1].split(',')
        size = window_raw_info[2].lstrip().split(' ')[1].split('x')
        logging.debug(f"Window position: x={position[0]}, y={position[1]}")
        logging.debug(f"Window size: {size[0]}x{size[1]}")
        self.window_position = [int(val) for val in position]
        self.window_size = [int(val) for val in size]

    def activate_window(self, window_title):
        """Activate the window by ID."""

        self.window_title = window_title
        if not self.window_id:
            self._find_window()

        if not self.window_position or not self.window_size:
            self._define_window_geometry()

        if self.window_id:
            try:
                subprocess.run(['xdotool', 'windowactivate', self.window_id], capture_output=True, text=True)
                logging.info(f"Window {self.window_id} activated successfully.")
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to activate window {self.window_id}. Error: {e}")
                exit(1)
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                exit(1)
        else:
            logging.error(f"Cannot activate window {self.window_title}. No windows found.")
            exit(1)

    def _get_screenshot_geometry(self):
        if not self.window_position or not self.window_size:
            self._define_window_geometry()
        position_x, position_y = self.window_position
        width = self.pixel_size['x'] * self.n_pixels['x']
        height = self.pixel_size['y'] * self.n_pixels['y']
        x_shift = self.screenshot_shift['x']
        y_shift = self.screenshot_shift['y']
        return position_x, position_y, width, height, x_shift, y_shift

    def take_screenshot(self, savefig=False, savefig_prefix='main'):
        position_x, position_y, width, height, x_shift, y_shift = self._get_screenshot_geometry()
        with mss.mss() as sct:
            try:
                area = {"top": position_y + y_shift, "left": position_x + x_shift, "width": width, "height": height}
                screenshot = sct.grab(area)
            except mss.ScreenShotError:
                logging.error("Unable to take a screenshot.")
                return None
            logging.debug(f"Took screenshot of area {width}x{height} (zero in {position_x},{position_y})")
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            if savefig:
                img.save(f"{savefig_prefix}_{position_x}_{position_y}_{height}_{width}.png")
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
