import time
import logging
import subprocess

from library.library_of_states import Duty, State, Moving, Combat, Action

from library.hardware_input import HardwareInputSimulator
from library.gingham_processing import GinghamProcessor
from library.game_window import GameWindow
from library.geometry import InGameGeometry
from companion import CompanionActions

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger('ingame_geometry').setLevel(logging.INFO)
logging.getLogger('companion_actions').setLevel(logging.INFO)

pause_frame = None
frame = 0

try:
    # keyboard inputs backend
    subprocess.run(["pkill", "ydotoold"])
    subprocess.Popen(["nohup", "ydotoold", "&"], stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)  # pipes are using to suppress ydotoold info logging

    # game window
    game_window = GameWindow()
    game_window.activate_window("World of Warcraft")
    logging.info("WoW In-Game Companion activated.")

    # keys and buttons
    inputs = HardwareInputSimulator()

    # companion actions
    companion = CompanionActions(game_window)
    # companion.set_state_to(State.NEUTRAL)

    # geometry calculation
    geometry = InGameGeometry(n_frames=20)

    time.sleep(1)
    while True:
        frame_start_time = time.time()

        logging.debug("." * 100)
        logging.debug(f"Frame #{frame}")

        screenshot = game_window.take_screenshot(savefig=False)

        gingham = GinghamProcessor(screenshot)
        gingham_pixels = gingham.pixels_analysis(n_monitoring_pixels=game_window.n_pixels['y'],
                                                 pixel_height=game_window.pixel_size['y'],
                                                 pixel_width=game_window.pixel_size['x'])
        session_data = gingham.to_dictionary(gingham_pixels)

        ### program workflow control
        # disable script from game
        if session_data['disable_script']:
            logging.warning("Control script was disabled from game.")
            if frame == 0:
                logging.warning("Enable it by sending \'disable\' in the party chat.")
            companion.hands_away_from_keyboard()
            exit(0)
        # pause script
        elif session_data['pause_script']:
            if not pause_frame:
                pause_frame = frame
            if pause_frame == frame:
                logging.info("Control script was paused.")
                companion.hands_away_from_keyboard()
            pause_frame += 1
            continue
        # end of the pause
        if not session_data['pause_script'] and pause_frame:
            companion.entering_the_game()

        ##### companion workflow
        ### extend session data with calculated geometry
        session_geometry = geometry.game_state_geometry(session_data)
        session_data.update(session_geometry)

        ### define BEHAVIOURS
        # moving
        if session_data['follow_command']:
            companion.set_moving_behaviour_to(Moving.FOLLOW)
        elif session_data['step-by-step_command']:
            companion.set_moving_behaviour_to(Moving.STEP_BY_STEP)
        else:
            companion.set_moving_behaviour_to(Moving.STAY)

        # redefine moving behaviour if player position was not defined
        if not session_data['player_position']:
            companion.set_moving_behaviour_to(Moving.STAY)

        # combat
        if session_data['assist_command']:
            companion.set_combat_behaviour_to(Combat.ASSIST)
        elif session_data['defend_command']:
            companion.set_combat_behaviour_to(Combat.DEFEND)
        elif session_data['only_heal_command']:
            companion.set_combat_behaviour_to(Combat.ONLY_HEAL)
        else:
            companion.set_combat_behaviour_to(Combat.PASSIVE)
        # actions
        if session_data['player_message']:
            companion.set_action_behaviour_to(Action.RESPOND)
        elif session_data['loot_command']:
            companion.set_action_behaviour_to(Action.LOOT)
        else:
            companion.set_action_behaviour_to(Action.NONE)

        ### define DUTIES
        companion.clear_duties()
        # actions at script start
        if frame == 0:
            companion.add_duty(Duty.INITIALIZE)
        # response to a player message
        if companion.action_behaviour_is(Action.RESPOND):
            companion.add_duty(Duty.RESPOND)
        # heal
        if not companion.combat_behaviour_is(Combat.PASSIVE):
            if session_data['player_health'] < 0.6:
                companion.add_duty(Duty.HEAL_PLAYER)
            if session_data['companion_health'] < 0.6:
                companion.add_duty(Duty.HEAL_YOURSELF)
        # combat
        if companion.combat_behaviour_is(Combat.ASSIST):
            if session_data['player_combat_status']:
                companion.add_duty(Duty.HELP_IN_COMBAT)
        if companion.combat_behaviour_is(Combat.DEFEND):
            if session_data['player_combat_status'] and session_data['player_health'] < 1.0:
                companion.add_duty(Duty.HELP_IN_COMBAT)
            elif session_data['companion_combat_status']:
                companion.add_duty(Duty.DEFEND_YOURSELF)
        # looting
        if companion.action_behaviour_is(Action.LOOT):
            companion.add_duty(Duty.LOOT)

        # define DUTIES if player position is defined
        if session_data['player_position']:
            if companion.action_behaviour_is(Action.LOOT):
                session_data['distance_to_player_delta'] = 0.075  # move closer at looting

            # nearing
            if companion.moving_behaviour_is(Moving.FOLLOW):
                if session_data['distance_from_companion_to_player'] >= session_data['distance_to_player_delta']:
                    companion.add_duty(Duty.NEARING_WITH_PLAYER)

            # rotation to player facing ONLY in combat
            if companion.has_duty(Duty.HELP_IN_COMBAT) and not companion.has_duty(Duty.NEARING_WITH_PLAYER):
                if session_data['angle_between_companion_facing_and_player_facing']:
                    if abs(session_data['angle_between_companion_facing_and_player_facing']) > session_data[
                        'rotation_to_player_angle_delta']:
                        companion.add_duty(Duty.ROTATE_TO_PLAYER_FACING)
                        if session_data['angle_between_companion_facing_and_player_facing'] <= -session_data[
                            'rotation_to_player_angle_delta']:
                            companion.add_duty(Duty.ROTATE_TO_PLAYER_FACING_LEFT)
                        elif session_data['angle_between_companion_facing_and_player_facing'] > session_data[
                            'rotation_to_player_angle_delta']:
                            companion.add_duty(Duty.ROTATE_TO_PLAYER_FACING_RIGHT)

            # avoid a low obstacle
            if companion.has_duty(Duty.NEARING_WITH_PLAYER):
                if session_data['companion_average_velocity'] < 0.0002:
                    if session_data['distance_from_companion_to_player'] > session_data['distance_to_player_delta'] * 3:
                        companion.add_duty(Duty.AVOID_LOW_OBSTACLE)

            # rotation to player if not in should rotate to facing
            if companion.moving_behaviour_is(Moving.FOLLOW) and not companion.has_duty(Duty.ROTATE_TO_PLAYER_FACING):
                if abs(session_data['angle_between_companion_facing_and_vector_to_player']) > session_data[
                    'rotation_to_player_angle_delta']:
                    companion.add_duty(Duty.ROTATE_TO_PLAYER)
                    if session_data['angle_between_companion_facing_and_vector_to_player'] <= -session_data[
                        'rotation_to_player_angle_delta']:
                        companion.add_duty(Duty.ROTATE_TO_PLAYER_LEFT)
                    elif session_data['angle_between_companion_facing_and_vector_to_player'] > session_data[
                        'rotation_to_player_angle_delta']:
                        companion.add_duty(Duty.ROTATE_TO_PLAYER_RIGHT)

        ## define STATE based on BEHAVIOURS and DUTIES
        if companion.has_duty(Duty.INITIALIZE):
            companion.set_state_to(State.BUFFING)
        elif companion.has_duty(Duty.RESPOND):
            companion.set_state_to(State.RESPONDING)
        elif companion.has_duty(Duty.LOOT):  # add NEARING_WITH_LOOTING_POINT looting nearing point
            companion.set_state_to(State.LOOTING)
        elif companion.has_duty(Duty.HEAL_PLAYER) and not companion.has_duty(Duty.NEARING_WITH_PLAYER):
            companion.set_state_to(State.HEALING_PLAYER)
        elif companion.has_duty(Duty.HEAL_YOURSELF):
            companion.set_state_to(State.HEALING_YOURSELF)
        elif companion.has_duty(Duty.HELP_IN_COMBAT) and not companion.has_duty(Duty.NEARING_WITH_PLAYER):
            if not (companion.state_is(State.ATTACKING_TO_HELP) or companion.state_is(State.ENTERING_COMBAT_TO_HELP)):
                companion.set_state_to(State.ENTERING_COMBAT_TO_HELP)
            else:
                companion.set_state_to(State.ATTACKING_TO_HELP)
        elif companion.has_duty(Duty.DEFEND_YOURSELF):
            if not (companion.state_is(State.ATTACKING_TO_DEFEND) or companion.state_is(
                    State.ENTERING_COMBAT_TO_DEFEND)):
                companion.set_state_to(State.ENTERING_COMBAT_TO_DEFEND)
            else:
                companion.set_state_to(State.ATTACKING_TO_DEFEND)
        else:
            companion.set_state_to(State.NEUTRAL)

        logging.debug(f"Companion behaviours: {companion.get_behaviours()}")
        logging.debug(f"Companion duties: {companion.get_duties()}")
        logging.debug(f"Companion state: {companion.get_state()}")

        ###### companion logic
        ### some actions at entering the game
        if companion.has_duty(Duty.INITIALIZE):
            companion.entering_the_game()

        ### cast buffs
        if companion.state_is(State.BUFFING):
            companion.target_the_ally(target='companion')
            companion.cast_spell('Power Word: Fortitude')
            companion.cast_spell('Inner Fire')

        ### answer to message
        if companion.state_is(State.RESPONDING):
            companion.hands_away_from_keyboard()
            companion.ai_companion_response(session_data['player_message'])

        ### movement
        if not companion.state_is(State.RESPONDING):
            companion.rotate_to(Duty.ROTATE_TO_PLAYER)
            companion.move_to(Duty.NEARING_WITH_PLAYER)
            if companion.has_duty(Duty.AVOID_LOW_OBSTACLE):
                companion.jump()

        ### chat-commands based logic
        # looting
        if companion.state_is(State.LOOTING):
            companion.logger.debug("Going to loot!")
            inputs.move_mouse_to_default_position(game_window)
            if not companion.has_duty(Duty.NEARING_WITH_PLAYER) and not companion.has_duty(Duty.ROTATE_TO_PLAYER):
                companion.loot(looting_area={'x_length': 200, 'y_length': 200,
                                             'x_step': 35, 'y_step': 50})
            inputs.move_mouse_to_default_position(game_window)

        ### healing
        if companion.state_is_one_of([State.HEALING_PLAYER, State.HEALING_YOURSELF]):
            if companion.state_is(State.HEALING_PLAYER):
                companion.target_the_ally(target='player')
            elif companion.state_is(State.HEALING_YOURSELF):
                companion.target_the_ally(target='companion')
            if companion.spellbook['Power Word: Shield']['ready']:
                companion.cast_spell('Power Word: Shield')
            else:
                companion.cast_spell('Flash Heal')

        ### combat
        if companion.state_is_one_of([State.ENTERING_COMBAT_TO_HELP, State.ENTERING_COMBAT_TO_DEFEND,
                                      State.ATTACKING_TO_HELP, State.ATTACKING_TO_DEFEND]):
            # rotation to player facing
            if companion.state_is_one_of([State.ENTERING_COMBAT_TO_HELP, State.ATTACKING_TO_HELP]):
                companion.rotate_to(Duty.ROTATE_TO_PLAYER_FACING)
            # battle rotation
            if not companion.has_duty(Duty.ROTATE_TO_PLAYER_FACING):
                if companion.state_is_one_of([State.ENTERING_COMBAT_TO_HELP, State.ENTERING_COMBAT_TO_DEFEND]):
                    companion.logger.debug("Enter the combat state!")
                    if companion.state_is(State.ENTERING_COMBAT_TO_HELP):
                        companion.target_the_ally(target='player_pet')
                    else:
                        companion.target_the_ally(target='companion')
                    companion.cast_spell('Power Word: Shield')

                elif companion.state_is_one_of([State.ATTACKING_TO_HELP, State.ATTACKING_TO_DEFEND]):
                    if companion.state_is(State.ATTACKING_TO_HELP):
                        companion.target_the_enemy(target_of='player')
                    else:
                        companion.target_the_enemy(target_of='companion')
                    if companion.spellbook['Penance']['ready']:
                        companion.cast_spell('Penance')
                    else:
                        companion.cast_spell('Smite')

        for spell in companion.spellbook.keys():
            if companion.spellbook[spell]['cooldown']:
                companion.check_spell_readiness(spell)

        if not session_data['pause_script']:
            pause_frame = None
            frame += 1

        logging.debug(f"Script work time is {round(time.time() - frame_start_time, 2)}s per frame")

except KeyboardInterrupt:
    HardwareInputSimulator().release_movement_keys()
    print("Monitoring stopped.")
