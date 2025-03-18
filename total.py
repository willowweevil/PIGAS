import logging
import time

from companion import CompanionControlLoop
from library.miscellaneous import read_yaml_file



class TotalController:
    def __init__(self):
        self.pause = False
        self.frame = 0
        self.initial_frame = 1
        self.pause_frame = None
        self.frame_start_time = None
        self.frame_end_time = None
        self.companion = CompanionControlLoop()

        super().__init__()

        self.logger = logging.getLogger('script_control')
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)
            self.logger.propagate = False
    #
    # def read_config(self):
    #     config_data = read_yaml_file('config.yml')
    #     self.

    def get_companion(self, companion):
        self.companion = companion

    def set_loop_control_execution_time(self):
        self.frame_end_time = time.time()
        self.logger.debug(f"Loop time was {round(self.frame_end_time - self.frame_start_time, 2)}s per frame.")

    def program_workflow_control(self):
        # disable script
        if self.companion.session_data['disable_script']:
            logging.warning("Control script was disabled from game.")
            if self.frame == 0:
                logging.warning("Enable it by sending \'disable\' in the party chat.")
            self.companion.freeze()
            exit(0)
        # pause script
        elif self.companion.session_data['pause_script']:
            if not self.pause_frame:
                self.pause_frame = self.frame
            if self.pause_frame == self.frame:
                logging.info("Control script was paused.")
                self.companion.freeze()
            self.pause_frame += 1
            self.pause = True
        else:
            self.logger.debug(f"Frame #{self.frame}")
            self.pause = False

        if not self.pause and self.pause_frame:
            self.companion.entering_the_game()

    def set_frame(self):
        self.frame_start_time = time.time()
        if not self.pause:
            self.pause_frame = None
            self.frame += 1

    def start(self):
        self.logger.info("WoW In-Game Companion is ready to start.")
        time.sleep(1)

    def end(self):
        self.companion.release_movement_keys()
        self.logger.info("Monitoring stopped.")