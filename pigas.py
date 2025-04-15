import logging
import sys

from library.entity_attributes import *

from gingham_processing import GinghamProcessor
from game_window import GameWindow
from navigation import Navigator
from companion import CompanionControlLoop
from workflow_handler import ScriptWorkflowHandler
from library.miscellaneous import is_debug

if __name__ == '__main__':
    config_file = 'config.yaml'
    try:
        # log level according to config
        debug = is_debug(config_file)
        logging.basicConfig(level=logging.INFO if not debug else logging.DEBUG,
                            format="%(asctime)s %(levelname)s %(message)s")

        logging.getLogger('game_window').setLevel(logging.INFO if not debug else logging.DEBUG)
        logging.getLogger('script_control').setLevel(logging.INFO if not debug else logging.DEBUG)
        logging.getLogger('hardware_input').setLevel(logging.INFO if not debug else logging.DEBUG)
        logging.getLogger('navigation').setLevel(logging.INFO if not debug else logging.DEBUG)
        logging.getLogger('companion').setLevel(logging.INFO if not debug else logging.DEBUG)

        # script workflow handler
        workflow_handler = ScriptWorkflowHandler(config_file=config_file)

        # game window
        game_window = GameWindow()
        game_window.set_window_parameters(config_file=config_file)

        # gingham analyzer
        gingham = GinghamProcessor()

        # geometry and navigation
        navigator = Navigator(config_file=config_file)

        # companion actions
        companion = CompanionControlLoop()
        companion.initialize_companion(game_window=game_window,
                                       expansion=workflow_handler.expansion,
                                       config_file=config_file)

        workflow_handler.perform_prestart_actions()
        while True:
            ### preparations
            # check if a game window still exists
            game_window.ensure_window_exists()

            # set frame
            workflow_handler.set_frame()

            # activate a window
            if not workflow_handler.pause_command:
                game_window.ensure_window_active()

            # set session data
            session_data = workflow_handler.session_data

            # extend session data with gingham data
            screenshot = game_window.take_screenshot(savefig=debug)
            gingham_pixels = gingham.pixels_analysis(data=screenshot,
                                                     n_monitoring_pixels=game_window.n_pixels['y'],
                                                     pixel_height=game_window.pixel_size['y'],
                                                     pixel_width=game_window.pixel_size['x'])
            session_data.update(gingham.to_dictionary(gingham_pixels))

            # extend session data with calculated geometry
            session_geometry = navigator.game_state_geometry(session_data)
            session_data.update(session_geometry)

            # update companion with new session data
            companion.session_data.update(session_data)

            # check for context for comments if streaming
            if workflow_handler.streaming[0]:
                companion.set_comment_as_player_message(comment_file=workflow_handler.streaming[1])

            ### script workflow control
            # update script workflow controller
            workflow_handler.set_workflow_commands(session_data)

            # workflow control
            should_disable = workflow_handler.script_workflow_control()
            companion.workflow_report(report_disable=should_disable)
            if workflow_handler.pause_command:
                continue

            ### companion workflow
            # check if a companion is moving somewhere
            companion.check_movement_keys()

            # companion behaviors defined by player commands
            companion.define_behaviour()

            # companion duties defined by commands, statuses and navigation (positions and angles)
            companion.clear_duties()
            companion.define_duties()

            # define state based on duties
            companion.define_state()

            # logging
            companion.get_profile()

            ###### companion logic
            ### movement
            # doesn't move if:
            # INITIALIZING, RESPONDING, WAITING_FOR_PLAYER, MOUNTING, UNMOUNTING,
            # ATTACKING_FOR_DEFEND, HEALING_YOURSELF
            if not companion.state_is_one_of(companion.movement_restricted_states):
                companion.rotate_to(Duty.ROTATE_TO_PLAYER)
                companion.move_to(Duty.NEARING_WITH_PLAYER)
                if companion.has_duty(Duty.AVOID_LOW_OBSTACLE):
                    companion.jump()

            ## some actions at entering the game (buffing will be the other state)
            if companion.state_is(State.INITIALIZING):
                companion.entering_the_game()
                companion.apply_buffing_rotation(ally_target='companion')

            ### respond to message
            if companion.state_is(State.RESPONDING):
                companion.respond_to_player()

            if companion.state_is(State.CHANGING_SPEED):
                companion.changing_speed()

            ### mounting
            if companion.state_is(State.MOUNTING):
                companion.mounting()

            ### unmounting
            if companion.state_is(State.UNMOUNTING):
                companion.unmounting()

            ### announce if should to wait for the player
            if companion.state_is(State.WAITING_FOR_PLAYER):
                companion.waiting_for_player()

            ### looting
            # performs prelooting actions
            if companion.state_is(State.NEARING_FOR_LOOTING):
                companion.perform_prelooting_actions()

            # perform looting
            if companion.state_is(State.LOOTING):
                # values - part of screen around the character
                companion.do_loot_actions(looting_area={'x_length': 0.3, 'y_length': 0.3,
                                                        'x_step': 0.025, 'y_step': 0.055})

            ### healing
            # player
            if companion.state_is(State.HEALING_PLAYER) and not companion.has_duty(Duty.ROTATE_TO_PLAYER):
                companion.apply_healing_rotation(target='player')

            # yourself
            if companion.state_is(State.HEALING_YOURSELF):
                companion.apply_healing_rotation(target='companion')

            ### combat
            # help to player
            if companion.state_is(State.ATTACKING_TO_HELP):
                companion.rotate_to(Duty.ROTATE_TO_PLAYER_FACING)
                if not companion.has_one_of_duties([Duty.ROTATE_TO_PLAYER_FACING, Duty.ROTATE_TO_PLAYER]):
                    companion.apply_combat_rotation(ally_target=None,
                                                    enemy_is_target_of='player')

            # defend
            if companion.state_is(State.ATTACKING_TO_DEFEND):
                companion.apply_combat_rotation(ally_target='companion',
                                                enemy_is_target_of='companion')

            companion.check_spellbook_cooldowns()

            workflow_handler.set_loop_control_execution_time()

    except KeyboardInterrupt:
        ScriptWorkflowHandler(config_file=config_file).finish_script()

    except Exception as e:
        ScriptWorkflowHandler(config_file=config_file).unexpected_finish(e)
