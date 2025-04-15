import logging
import time
import sys
import os
import shutil

from hardware_input import HardwareInputSimulator
from library.miscellaneous import read_yaml_file


class ScriptWorkflowHandler(HardwareInputSimulator):
    def __init__(self, config_file=None):
        super().__init__()
        self.program_runs_count_file = '.local'
        self.addon_name = 'GinghamShirt'
        self.addon_directory = f'./data/addon/{self.addon_name}'
        self.expansion = None
        self.game_directory = None

        self.config_file = config_file
        self.frame = 0

        self.pause_frame = None
        self.frame_start_time = None
        self.frame_end_time = None

        self.pause_command = False
        self.disable_command = False

        self.initialization()

        self.logger = logging.getLogger('script_control')
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)
            self.logger.propagate = False

    @property
    def streaming(self):
        config = read_yaml_file(self.config_file)
        other_data = config.get("other")
        if other_data:
            is_streaming = other_data.get('streaming', False)
            comment_file = other_data.get('comment_file', None)
            if is_streaming and not comment_file:
                self.logger.error("Streaming is active, but comment file is not found!")
                sys.exit(1)
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
                logging.info("PIGAS was removed from the pause.")
            self.pause_frame = None
            self.frame += 1

    def disable_script(self):
        report_disable = False
        if self.disable_command:
            logging.info("PIGAS was disabled from game.")
            if self.frame == 0:
                logging.warning("Enable it by sending \'#disable\' in the party chat or /reload game interface.")
            self.release_movement_keys()
            report_disable = True
        return report_disable

    def pause_script(self):
        report_pause = False
        if self.pause_command:
            if not self.pause_frame:
                self.pause_frame = self.frame
            if self.pause_frame == self.frame:
                logging.info("PIGAS was paused.")
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

    def perform_prestart_actions(self):
        self.logger.info("PIGAS is ready to start.")
        time.sleep(1)

    def finish_script(self):
        self.stop_keyboard_listener()
        self.release_movement_keys()
        self.logger.info("PIGAS has been disabled.")
        sys.exit(0)

    def unexpected_finish(self, e):
        self.logger.info(f"PIGAS just finished execution with error \"{e}\".")
        sys.exit(1)

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

    def initialization(self):
        game_config = read_yaml_file(self.config_file).get("game")
        if not game_config:
            self.logger.error(f"Incorrect \"{self.config_file}\" file!")
            sys.exit(1)

        self.game_directory = game_config.get("game-directory")
        if not self.game_directory:
            self.logger.error(f"Game directory is not set! Please, check the \"{self.config_file}\" file!")
            sys.exit(1)

        self.expansion = game_config.get("expansion")
        if not self.expansion:
            self.logger.error(f"Game expansion is not set! Please, check the \"{self.config_file}\" file!")
            sys.exit(1)

        counts = self.get_program_runs_count()
        if counts == 0:
            self.logger.info("Welcome to PIGAS: Personal In-Game Adventure Sidekick!")
            self.logger.info("It's seems it's the first run of PIGAS.. Let's initialization begins!")
            time.sleep(2)
            self.copy_config()
            self.copy_addon()
        else:
            self.increment_program_runs_count()

        self.check_addon_version()

    def copy_config(self):
        # copy Config.wtf
        config_src = f"./data/config/{self.expansion}/Config.wtf"
        config_dst = f"{os.path.join(self.game_directory, 'WTF', 'Config.wtf')}"
        self.logger.info(f"Copying \"Config.wtf\" to {config_dst}.")
        shutil.copy2(config_src, config_dst)
        self.logger.info("Copying finished.")

    def copy_addon(self):
        # copy addon
        addon_src = self.addon_directory
        addon_dst = os.path.join(self.game_directory, 'Interface', 'AddOns', self.addon_name)
        self.logger.info(f"Copying \"{self.addon_name}\" addon to {addon_dst}.")
        if not os.path.exists(addon_dst):
            shutil.copytree(addon_src, addon_dst)
        else:
            self.logger.info(f"Destination directory {addon_dst} already exists! If you need to upgrade the addon, "
                             f"please copy it by yourself!")
        self.logger.info("Copying finished.")

        self.logger.info("The initialization finished! Please, restart PIGAS.")
        self.increment_program_runs_count()
        sys.exit(0)

    def get_addon_version(self, filepath=None):
        try:
            with open(filepath, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if 'version' in line.lower():
                        version = line.split(' ')[-1]
        except FileNotFoundError:
            addon_directory = '/'.join(filepath.split('/')[:-2])
            self.logger.error(f"Cannot find \"{self.addon_name}\" addon in {addon_directory}. Please, check if it exists.")
            sys.exit(1)
        except PermissionError:
            self.logger.error(f"Cannot check version of installed \"{self.addon_name}\" addon. "
                              f"Please, be sure to use the actual version.")
        return version

    def check_addon_version(self):
        actual_version = self.get_addon_version(os.path.join(self.addon_directory, f'{self.addon_name}.toc'))
        installed_version = self.get_addon_version(
            os.path.join(self.game_directory, 'Interface', 'AddOns', self.addon_name, f'{self.addon_name}.toc'))

        if actual_version != installed_version:
            self.logger.error(
                f"Installed addon is not actual (actual version is {actual_version} and installed version is {installed_version})!"
                f"Please, copy the actual addon version to {os.path.join(self.game_directory, 'Interface', 'AddOns')}"
                f"by yourself!")
            sys.exit(0)
