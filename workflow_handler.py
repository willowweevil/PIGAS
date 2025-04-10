import logging
import time
import sys

from hardware_input import HardwareInputSimulator
from library.miscellaneous import read_yaml_file


class ScriptWorkflowHandler(HardwareInputSimulator):
    def __init__(self, config_file=None):
        super().__init__()

        self.config_file = config_file
        self.frame = 0

        self.pause_frame = None
        self.frame_start_time = None
        self.frame_end_time = None

        self.pause_command = False
        self.disable_command = False

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
    def set_session_data(self):
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
                logging.info("Control script was removed from the pause.")
            self.pause_frame = None
            self.frame += 1

    def disable_script(self):
        report_disable = False
        if self.disable_command:
            logging.info("Control script was disabled from game.")
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
                logging.info("Control script was paused.")
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

    def execute_prestart_actions(self):
        self.logger.info("PIGAS is ready to start.")
        time.sleep(1)

    def finish_script(self):
        self.stop_keyboard_listener()
        self.release_movement_keys()
        self.logger.info("PIGAS finished.")
        sys.exit(0)

    def unexpected_finish(self, e):
        self.logger.error(f"PIGAS just finished execution with error \"{e}\".")
        sys.exit(1)
