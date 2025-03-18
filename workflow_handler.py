import logging
import time

from hardware_input import HardwareInputSimulator


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


    def set_frame(self):
        self.frame_start_time = time.time()
        if not self.pause_command:
            self.pause_frame = None
            self.frame += 1

    def set_workflow_commands(self, session_data):
        self.pause_command = session_data['pause_script']
        self.disable_command = session_data['disable_script']

    def set_loop_control_execution_time(self):
        self.frame_end_time = time.time()
        self.logger.debug(f"Loop time was {round(self.frame_end_time - self.frame_start_time, 2)}s per frame.")

    def disable_script(self):
        if self.disable_command:
            logging.warning("Control script was disabled from game.")
            if self.frame == 0:
                logging.warning("Enable it by sending \'disable\' in the party chat.")
            self.release_movement_keys()
            exit(0)

    def pause_script(self):
        if self.pause_command:
            if not self.pause_frame:
                self.pause_frame = self.frame
            if self.pause_frame == self.frame:
                logging.info("Control script was paused.")
                self.release_movement_keys()
            self.pause_frame += 1
        else:
            self.logger.debug(f"Frame #{self.frame}")

    def script_workflow_control(self):
        self.disable_script()
        self.pause_script()

    def execute_prestart_actions(self):
        self.logger.info("WoW In-Game Companion is ready to start.")
        time.sleep(1)

    def finish_script(self):
        self.stop_keyboard_listener()
        self.release_movement_keys()
        self.logger.info("Monitoring stopped.")
