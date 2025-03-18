import logging

from library.entity_attributes import *

from gingham_processing import GinghamProcessor
from game_window import GameWindow
from navigation import Navigator
from companion import CompanionControlLoop
from workflow_handler import ScriptWorkflowHandler

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")

logging.getLogger('script_control').setLevel(logging.INFO)
logging.getLogger('game_window').setLevel(logging.INFO)
logging.getLogger('hardware_input').setLevel(logging.INFO)
logging.getLogger('navigation').setLevel(logging.INFO)
logging.getLogger('companion').setLevel(logging.DEBUG)

if __name__ == '__main__':
    try:
        # script workflow handler
        workflow_handler = ScriptWorkflowHandler(config_file='config.yaml')

        # game window
        game_window = GameWindow()
        game_window.set_window_parameters(config_file=workflow_handler.config_file)

        # gingham analyzer
        gingham = GinghamProcessor()

        # geometry and navigation
        navigator = Navigator()

        # companion actions
        companion = CompanionControlLoop()
        companion.initialize_companion(game_window=game_window,
                                       config_file=workflow_handler.config_file)

        workflow_handler.execute_prestart_actions()
        while True:
            workflow_handler.set_frame()
            game_window.ensure_window_active()

            # get gingham data
            screenshot = game_window.take_screenshot(savefig=False)
            gingham_pixels = gingham.pixels_analysis(data=screenshot,
                                                     n_monitoring_pixels=game_window.n_pixels['y'],
                                                     pixel_height=game_window.pixel_size['y'],
                                                     pixel_width=game_window.pixel_size['x'])

            # set session data
            session_data = gingham.to_dictionary(gingham_pixels)

            # extend session data with calculated geometry
            session_geometry = navigator.game_state_geometry(session_data)
            session_data.update(session_geometry)

            # update companion with new session data
            companion.session_data.update(session_data)

            # update script workflow controller
            workflow_handler.set_workflow_commands(session_data)

            # script workflow control
            workflow_handler.script_workflow_control()
            if workflow_handler.pause_command:
                continue

            ### companion workflow
            companion.check_movement_keys()

            # companion behaviors (defined by player commands)
            companion.define_behaviour()

            # companion duties defined by commands, statuses and navigation (positions and angles)
            companion.clear_duties()

            ### define autonomic DUTIES
            # actions at script start
            if workflow_handler.frame == 1:
                companion.add_duty(Duty.INITIALIZE)

            # response to a player message
            if companion.action_behaviour_is(Action.RESPOND):
                companion.add_duty(Duty.RESPOND)

            # mount
            if companion.mount_behaviour_is(Mount.MOUNTED):
                companion.session_data['distance_to_player_delta'] = companion.session_data[
                    'mounted_distance_to_player_delta']
                if not companion.session_data['companion_mounted']:
                    companion.add_duty(Duty.MOUNT)

            # unmount
            if companion.mount_behaviour_is(Mount.UNMOUNTED):
                if companion.session_data['companion_mounted']:
                    companion.add_duty(Duty.UNMOUNT)

            # looting
            if companion.action_behaviour_is(Action.LOOT):
                # if not session_data['companion_mounted']:
                companion.session_data['distance_to_player_delta'] = companion.session_data[
                    'looting_distance_to_player_delta']
                companion.add_duty(Duty.LOOT)

            # heal yourself
            if not companion.combat_behaviour_is(Combat.PASSIVE):
                if 0.0 < companion.session_data['companion_health'] <= companion.session_data[
                    'health_to_start_healing']:
                    companion.add_duty(Duty.HEAL_YOURSELF)

            # defend yourself
            if companion.combat_behaviour_is(Combat.DEFEND):
                if companion.session_data['companion_combat_status']:
                    companion.add_duty(Duty.DEFEND_YOURSELF)

            ### define DUTIES which depend on the player (player should be nearby)
            if companion.session_data['player_position'] and companion.session_data[
                'distance_from_companion_to_player'] < companion.session_data[
                'max_distance_from_companion_to_player']:
                companion.waiting_announced = False

                # heal player
                if not companion.combat_behaviour_is(Combat.PASSIVE):
                    if 0.0 < companion.session_data['player_health'] <= companion.session_data[
                        'health_to_start_healing']:
                        companion.add_duty(Duty.HEAL_PLAYER)

                # assist to player in combat
                if companion.combat_behaviour_is(Combat.ASSIST):
                    if companion.session_data['player_combat_status']:
                        companion.add_duty(Duty.HELP_IN_COMBAT)

                # defend player
                if companion.combat_behaviour_is(Combat.DEFEND):
                    if companion.session_data['player_combat_status'] and 0.0 < companion.session_data[
                        'player_health'] < 1.0:
                        companion.add_duty(Duty.HELP_IN_COMBAT)

                # nearing
                if companion.moving_behaviour_is(Moving.FOLLOW):
                    if companion.session_data['distance_from_companion_to_player'] >= companion.session_data[
                        'distance_to_player_delta']:
                        companion.add_duty(Duty.NEARING_WITH_PLAYER)

                # nearing for looting
                if companion.has_duty(Duty.NEARING_WITH_PLAYER):
                    if companion.has_duty(Duty.LOOT):
                        companion.add_duty(Duty.NEARING_TO_LOOT)
                        companion.remove_duty(Duty.LOOT)
                    else:
                        companion.looting_announced = False

                # nearing for helping in combat
                if companion.has_duty(Duty.NEARING_WITH_PLAYER):
                    if companion.has_duty(Duty.HELP_IN_COMBAT):
                        companion.add_duty(Duty.NEARING_TO_HELP_IN_COMBAT)
                        companion.remove_duty(Duty.HELP_IN_COMBAT)
                    else:
                        companion.helping_in_combat_announced = False

                # nearing for healing player
                if companion.has_duty(Duty.NEARING_WITH_PLAYER):
                    if companion.has_duty(Duty.HEAL_PLAYER):
                        companion.add_duty(Duty.NEARING_TO_HEAL_PLAYER)
                        companion.remove_duty(Duty.HEAL_PLAYER)
                    else:
                        companion.healing_player_announced = False

                # avoid a low obstacle
                if companion.has_duty(Duty.NEARING_WITH_PLAYER):
                    if companion.session_data['companion_average_velocity'] < companion.session_data[
                        'minimum_velocity_for_nearing'] and \
                            companion.session_data['distance_from_companion_to_player'] > companion.session_data[
                        'distance_to_start_avoid_obstacles']:
                        companion.add_duty(Duty.AVOID_LOW_OBSTACLE)

                # rotation to player facing ONLY in combat
                if companion.has_duty(Duty.HELP_IN_COMBAT) and not companion.has_duty(Duty.NEARING_WITH_PLAYER):
                    if companion.session_data['angle_between_companion_facing_and_player_facing']:
                        if abs(companion.session_data['angle_between_companion_facing_and_player_facing']) > \
                                companion.session_data[
                                    'rotation_to_player_angle_delta']:
                            companion.add_duty(Duty.ROTATE_TO_PLAYER_FACING)
                            if companion.session_data['angle_between_companion_facing_and_player_facing'] <= - \
                            companion.session_data[
                                'rotation_to_player_angle_delta']:
                                companion.add_duty(Duty.ROTATE_TO_PLAYER_FACING_LEFT)
                            elif companion.session_data['angle_between_companion_facing_and_player_facing'] > \
                                    companion.session_data[
                                        'rotation_to_player_angle_delta']:
                                companion.add_duty(Duty.ROTATE_TO_PLAYER_FACING_RIGHT)

                # rotation to player if not in should rotate to facing
                if companion.moving_behaviour_is(Moving.FOLLOW) and not companion.has_duty(
                        Duty.ROTATE_TO_PLAYER_FACING):
                    if abs(companion.session_data['angle_between_companion_facing_and_vector_to_player']) > \
                            companion.session_data[
                                'rotation_to_player_angle_delta']:
                        companion.add_duty(Duty.ROTATE_TO_PLAYER)
                        if companion.session_data['angle_between_companion_facing_and_vector_to_player'] <= - \
                        companion.session_data[
                            'rotation_to_player_angle_delta']:
                            companion.add_duty(Duty.ROTATE_TO_PLAYER_LEFT)
                        elif companion.session_data['angle_between_companion_facing_and_vector_to_player'] > \
                                companion.session_data[
                                    'rotation_to_player_angle_delta']:
                            companion.add_duty(Duty.ROTATE_TO_PLAYER_RIGHT)
            else:
                companion.add_duty(Duty.WAITING_FOR_PLAYER)

            ### define STATE based on DUTIES
            companion.define_state()

            logging.debug(f"Companion behaviours: {companion.get_behaviours()}")
            logging.debug(f"Companion duties: {companion.get_duties()}")
            logging.debug(f"Companion state: {companion.get_state()}")

            ###### companion logic
            ### movement
            # doesn't move if WAITING_FOR_PLAYER, RESPONDING or INITIALIZING
            if not companion.state_is_one_of(companion.movement_restricted_states):
                # not companion.state_is_one_of([State.INITIALIZING, State.RESPONDING, State.WAITING_FOR_PLAYER]):
                companion.rotate_to(Duty.ROTATE_TO_PLAYER)
                companion.move_to(Duty.NEARING_WITH_PLAYER)
                if companion.has_duty(Duty.AVOID_LOW_OBSTACLE):
                    companion.jump()

            ### some actions at entering the game (buffing will be the other state)
            if companion.state_is(State.INITIALIZING):
                companion.entering_the_game()
                companion.apply_buffing_rotation(ally_target='companion')

            ### respond to message
            if companion.state_is(State.RESPONDING):
                companion.ai_companion_response(companion.session_data['player_message'])

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
                companion.do_loot_actions(looting_area={'x_length': 200, 'y_length': 200,
                                                        'x_step': 35, 'y_step': 50})

            ### healing
            # player
            if companion.state_is(State.HEALING_PLAYER):
                companion.apply_healing_rotation(ally_target='player')

            # yourself
            if companion.state_is(State.HEALING_YOURSELF):
                companion.apply_healing_rotation(ally_target='companion')

            ### combat
            # help to player
            if companion.state_is(State.ATTACKING_TO_HELP):
                companion.rotate_to(Duty.ROTATE_TO_PLAYER_FACING)
                if not companion.has_duty(Duty.ROTATE_TO_PLAYER_FACING):
                    companion.apply_combat_rotation(ally_target='player_pet',
                                                    enemy_is_target_of='player')

            # defend
            if companion.state_is(State.ATTACKING_TO_DEFEND):
                companion.apply_combat_rotation(ally_target='companion',
                                                enemy_is_target_of='companion')

            companion.check_spellbook_cooldowns()

            workflow_handler.set_loop_control_execution_time()

    except KeyboardInterrupt:
        ScriptWorkflowHandler().finish_script()
