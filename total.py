import logging

from companion import CompanionControlLoop



class TotalController():
    def __init__(self):
        self.frame = 0
        self.pause_frame = None
        super().__init__()

        self.logger = logging.getLogger('script_control')
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)
            self.logger.propagate = False

    # def program_workflow_control(self):
    #     # disable script from game
    #     if self.session_data['disable_script']:
    #         logging.warning("Control script was disabled from game.")
    #         if self.frame == 0:
    #             logging.warning("Enable it by sending \'disable\' in the party chat.")
    #         self.freeze()
    #         exit(0)
    #     # pause script
    #     elif self.session_data['pause_script']:
    #         if not self.pause_frame:
    #             pause_frame = self.frame
    #         if self.pause_frame == self.frame:
    #             logging.info("Control script was paused.")
    #             self.freeze()
    #         self.pause_frame += 1
    #         #continue # <--- ?
    #     else:
    #         logging.debug(f"Frame #{self.frame}")
    #     # end of the pause
    #     if not self.session_data['pause_script'] and self.pause_frame:
    #         self.entering_the_game()