import logging
import time
import os
import shutil
import tkinter as tk

from modules.hardware_input import HardwareInputSimulator

from library.miscellaneous import read_yaml_file
from library.miscellaneous import stop_execution

from library.errors import WorkflowHandlerError


class ScriptWorkflowHandler(HardwareInputSimulator):
    def __init__(self, config_file=None):
        super().__init__()
        self.program_runs_count_file = '.local'
        self.addon_name = 'GinghamShirt'
        self.addon_directory = f'./data/addon'

        self.game_directory = None
        self.server_type = None
        self.account = None
        self.expansion = None

        self.config_data = None
        self.config_file = config_file
        self.frame = 0

        self.pause_frame = None
        self.frame_start_time = None
        self.frame_end_time = None

        self.pause_command = False
        self.disable_command = False

        self.companion = None
        self.gingham = None
        self.navigator = None
        self.game_window = None

        self.initialization()

        self.logger = logging.getLogger('script_control')

    # @staticmethod
    # def release_movement_keys():
    #     hardware_input = HardwareInputSimulator()
    #     hardware_input.release_movement_keys()
    #
    # @staticmethod
    # def stop_keyboard_listener():
    #     hardware_input = HardwareInputSimulator()
    #     hardware_input.stop_keyboard_listener()

    @staticmethod
    def define_screen_resolution():
        root = tk.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height

    @property
    def streaming(self):
        config = read_yaml_file(self.config_file, critical=True)
        other_data = config.get("other")
        if other_data:
            is_streaming = other_data.get('streaming', False)
            comment_file = other_data.get('comment_file', None)
            if is_streaming and not comment_file:
                raise WorkflowHandlerError("Streaming is active, but comment file is not found!")
        else:
            is_streaming, comment_file = False, None
        return is_streaming, comment_file

    @property
    def session_data(self):
        return {'frame': self.frame}

    def set_workflow_commands(self, session_data):
        self.pause_command = session_data['pause_script']
        self.disable_command = session_data['disable_script']

    def set_loop_control_execution_time(self):
        self.frame_end_time = time.time()
        self.logger.debug(f"Loop time was {round(self.frame_end_time - self.frame_start_time, 2)}s per frame.")

    def set_frame(self):
        self.frame_start_time = time.time()
        if not self.pause_command:
            if self.pause_frame:
                self.logger.info("PIGAS was removed from the pause.")
            self.pause_frame = None
            self.frame += 1

    def disable_script(self):
        report_disable = False
        if self.disable_command:
            logging.info("PIGAS was disabled from game.")
            if self.frame == 0:
                self.logger.warning("Please enter the \"/reload\" command to reload the game interface.")
            self.release_movement_keys()
            report_disable = True
        return report_disable

    def pause_script(self):
        report_pause = False
        if self.pause_command:
            if not self.pause_frame:
                self.pause_frame = self.frame
            if self.pause_frame == self.frame:
                self.logger.info("PIGAS was paused.")
                self.release_movement_keys()
                report_pause = True
            self.pause_frame += 1
        else:
            self.logger.debug(f"Frame #{self.frame}")
        return report_pause

    def script_workflow_control(self):
        report_disable = self.disable_script()
        _ = self.pause_script()
        return report_disable

    def set_modules(self, companion=None, gingham=None, navigator=None, game_window=None):
        self.companion = companion
        self.gingham = gingham
        self.navigator = navigator
        self.game_window = game_window
        self.logger.info("PIGAS is ready to start.")
        time.sleep(1)

    def finish_script(self):
        self.stop_keyboard_listener()
        self.release_movement_keys()
        self.logger.info("PIGAS has been disabled.")
        stop_execution(0)

    def unexpected_finish(self, e: Exception):
        self.logger.error(e)
        # self.logger.info("PIGAS just finished executing.")
        stop_execution(2)

    def get_program_runs_count(self):
        if os.path.exists(self.program_runs_count_file):
            with open(self.program_runs_count_file, 'r') as file:
                try:
                    return int(file.read().strip())
                except ValueError:
                    return 0
        return 0

    def write_program_runs_count(self, count):
        with open(self.program_runs_count_file, 'w') as file:
            file.write(str(count))

    def increment_program_runs_count(self):
        counts = self.get_program_runs_count()
        self.write_program_runs_count(counts + 1)
        return counts + 1

    def decrement_program_run_count(self):
        counts = self.get_program_runs_count()
        self.write_program_runs_count(counts + 1)
        return counts + 1

    def get_config(self):
        self.config_data = read_yaml_file(self.config_file, critical=True)

    def initialization(self):
        self.get_config()

        screen_resolution = self.define_screen_resolution()
        screen_proportions = round(screen_resolution[0] / screen_resolution[1], 2)
        if screen_proportions == round(16/9, 2):
            resolution_suffix = "16x9"
        elif screen_proportions == round(16/10, 2):
            resolution_suffix = "16x10"
        else:
            resolution_suffix = "16x9"
            self.logger.warning(f"Cannot define screen proportions (found screen resolution is {screen_resolution[0]}x{screen_resolution[1]})."
                                f"Please, set resolution in game manually.")

        game_config = self.config_data.get("game")
        if not game_config:
            raise WorkflowHandlerError(f"Incorrect \"{self.config_file}\" file!")

        self.game_directory = game_config.get("game-directory")
        if not self.game_directory:
            raise WorkflowHandlerError(f"Game directory is not set! Please, check the \"{self.config_file}\" file!")

        self.server_type = game_config.get("server-type")
        if not self.server_type:
            raise WorkflowHandlerError(f"Server type is not set! Please, check the \"{self.config_file}\" file!")
        if self.server_type != "official":
            self.server_type = "private" # working only for private servers now
            # raise WorkflowHandlerError(f"Incorrect server type (\"{self.server_type}\" is not supported). "
            #                            f"Use only \"private\" or \"official\".")

        self.expansion = game_config.get("expansion")
        if not self.expansion:
            raise WorkflowHandlerError(f"Game expansion is not set! Please, check the \"{self.config_file}\" file!")
        if self.expansion != "wotlk" and self.expansion != "cataclysm":
            raise WorkflowHandlerError(f"Incorrect expansion \"{self.expansion}\". "
                                       f"Only \"wotlk\" and \"cataclysm\" are supported. ")

        self.account = game_config.get("account")
        if not self.account:
            raise WorkflowHandlerError(f"Account is not set! Please, check the \"{self.config_file}\" file!")

        counts = self.get_program_runs_count()
        if counts == 0:
            self.logger.info("Welcome to PIGAS: Personal In-Game Adventure Sidekick!")
            self.logger.info("It's seems it's the first run of PIGAS.. Let's initialization begins!")
            time.sleep(2)
            self.copy_config(copy_from=f"./data/config/{self.expansion}/Config_{resolution_suffix}.wtf",
                             copy_to=f"{os.path.join(self.game_directory, 'WTF', 'Config.wtf')}")
            self.copy_config(copy_from=f"./data/config/{self.expansion}/bindings-cache.wtf",
                             copy_to=f"{os.path.join(self.game_directory, 'WTF', 'Account', f'{self.account.upper()}', 'bindings-cache.wtf')}")
            self.copy_addon()
        else:
            self.increment_program_runs_count()
        self.check_addon_version()


    def calibration_workflow(self, debug=False):
        if self.frame == 1:
            self.companion.send_message_to_chat("PIGAS #calibration begins!")
            time.sleep(1)
            calibrated = self.game_window.define_gingham_screenshot_shift(savefig=debug)
            if calibrated:
                self.companion.screenshot_shift = self.game_window.screenshot_shift
                #self.companion.pixels_sizes = self.game_window.pixels_sizes
                self.companion.send_message_to_chat("PIGAS #calibration complete!")
                time.sleep(0.5)
            else:
                self.companion.send_message_to_chat("PIGAS #calibration failed! Please try to change window game resolution!")
                raise WorkflowHandlerError("Failed to find \"Gingham Shirt\" position.")

    def copy_config(self, copy_from=None, copy_to=None):
        self.logger.info(f"Copying \"{copy_from}\" to \"{copy_to}\".")
        copy_to_dir = '/'.join(copy_to.split('/')[:-1])
        if not copy_to_dir:
            copy_to_dir = '\\'.join(copy_to.split('\\')[:-1])
        os.makedirs(copy_to_dir, exist_ok=True)
        shutil.copy2(copy_from, copy_to)
        self.logger.info("Copying finished.")

    def copy_addon(self):
        # copy addon
        addon_src = f"{self.addon_directory}/{self.addon_name}-{self.server_type}"
        addon_dst = os.path.join(self.game_directory, 'Interface', 'AddOns', self.addon_name)
        self.logger.info(
            f"Going to copy \"{self.addon_name}\" addon to \"{addon_dst}\".")
        if os.path.exists(addon_dst):
            self.logger.info("It seems that addon already exists in the game directory. Going to override addon.")
            shutil.rmtree(addon_dst)
        shutil.copytree(addon_src, addon_dst)
        self.logger.info("Copying finished.")
        self.logger.info("The initialization finished. Please, restart PIGAS.")
        self.increment_program_runs_count()
        stop_execution(0)

    def get_addon_version(self, filepath=None):
        version = None
        try:
            with open(filepath, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if 'version' in line.lower():
                        version = line.split(' ')[-1].strip()
            file.close()
        except FileNotFoundError:
            directory = '/'.join(filepath.split('/')[:-2])
            raise WorkflowHandlerError(
                f"Cannot find \"{self.addon_name}\" addon in {directory}. Please, check if it exists.")

        except PermissionError:
            self.logger.error(f"Cannot check version of \"{self.addon_name}\" addon. "
                              f"Please, be sure to use the actual version.")
        return version

    def check_addon_version(self):
        actual_version = self.get_addon_version(os.path.join(f"{self.addon_directory}/{self.addon_name}-{self.server_type}",
                                                             f'{self.addon_name}.toc'))
        installed_version = self.get_addon_version(
            os.path.join(self.game_directory, 'Interface', 'AddOns', self.addon_name, f'{self.addon_name}.toc'))

        if actual_version is None or installed_version is None:
            if actual_version is None:
                self.logger.error("Can't check actual version of addon.")
            if installed_version is None:
                self.logger.error("Can't check installed version of addon.")
        elif actual_version != installed_version:
            self.logger.error(
                f"Installed addon version is not actual! Actual version is {actual_version} and your version is {installed_version}!")
            self.copy_addon()

        # system_platform = define_system_platform()
        # system_platform = define_system_platform()
        # if system_platform == Platform.LINUX:
        #     try:
        #         xdpyinfo = subprocess.Popen('xdpyinfo', stdout=subprocess.PIPE)
        #         output = subprocess.check_output(('grep', 'dimensions'), stdin=xdpyinfo.stdout)
        #     except subprocess.CalledProcessError as e:
        #         self.logger.error("Cannot define screenshot resolution.")

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
#     return hdmi_monitor_shift_x, hdmi_monitor_shift_y