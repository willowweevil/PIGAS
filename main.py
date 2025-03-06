import time

import subprocess

from library.hardware_input import HardwareInputSimulator

from companion import CompanionActions

from library.game_window import GameWindow
from library.geometry import *
from library.gingham_processing import *

from library.library_of_states import Duty, State, Moving, Combat, Action

coordinates_logger = logging.getLogger('Coordinates')

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
coordinates_logger.setLevel(logging.INFO)

nearing_position = (0, 0)
pause_frame = None
frame = 0

number_of_calculation_frames = 20
last_assistant_coordinates = [0] * number_of_calculation_frames
last_player_coordinates = [[0, 0], [0, 0]]
rotate_per_second = 180

spells = {"Penance":
              {"action_button": "-", "cooldown": 12, "cast_time": 0, "action_page_number": 1,
               "ready": True, "timestamp_of_cast": None},
          "Power Word: Shield":
              {"action_button": "=", "cooldown": 15, "cast_time": 0, "action_page_number": 1,
               "ready": True, "timestamp_of_cast": None},
          "Smite":
              {"action_button": "1", "cooldown": 0, "cast_time": 0, "action_page_number": 1,
               "ready": True, "timestamp_of_cast": None},
          "Physic Scream":
              {"action_button": "0", "cooldown": 30, "cast_time": 0, "action_page_number": 1,
               "ready": True, "timestamp_of_cast": None},
          "Inner Fire":
              {"action_button": "1", "cooldown": 0, "cast_time": 0, "action_page_number": 2,
               "ready": True, "timestamp_of_cast": None},
          "Power Word: Fortitude":
              {"action_button": "2", "cooldown": 0, "cast_time": 0, "action_page_number": 2,
               "ready": True, "timestamp_of_cast": None},
          "Flash Heal":
              {"action_button": "3", "cooldown": 0, "cast_time": 1.5, "action_page_number": 2,
               "ready": True, "timestamp_of_cast": None},
          "Renew":
              {"action_button": "4", "cooldown": 0, "cast_time": 0, "action_page_number": 2,
               "ready": True, "timestamp_of_cast": None}
          }

try:
    # keyboard inputs backend
    subprocess.run(["pkill", "ydotoold"])
    subprocess.Popen(["nohup", "ydotoold", "&"], stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)  # pipes are using to suppress ydotoold info logging

    # game window
    game_window = GameWindow()
    game_window.activate_window("World of Warcraft")
    logging.info("WoW Assistant Control Manager is activated.")

    # keys and buttons
    inputs = HardwareInputSimulator()

    # companion actions
    companion = CompanionActions(game_window)
    companion.set_state_to(State.NEUTRAL)
    companion.entering_the_game()

    time.sleep(1)
    while True:
        frame_start_time = time.time()

        logging.debug("." * 100)
        logging.debug(f"Frame #{frame}")

        gingham_shirt = game_window.take_screenshot(savefig=False)
        data_pixels, player_message_pixels, cursor_message_pixels = pixels_analysis(data=gingham_shirt,
                                                                                    n_monitoring_pixels=
                                                                                    game_window.n_pixels['y'],
                                                                                    pixel_height=
                                                                                    game_window.pixel_size['y'],
                                                                                    pixel_width=
                                                                                    game_window.pixel_size['x'])
        ### script manipulation
        pause_script, disable_script = get_script_control_commands(data_pixels[0][0])

        # disable script from game
        if disable_script:
            logging.warning("Control script was disabled from game.")
            if frame == 0:
                logging.warning("Enable it by sending \'disable\' in the party chat.")
            companion.hands_away_from_keyboard()
            exit(0)

        # pause script
        elif pause_script:
            if not pause_frame:
                pause_frame = frame
            if pause_frame == frame:
                logging.info("Control script was paused.")
                companion.hands_away_from_keyboard()
            pause_frame += 1
            continue

        # end of the pause
        if not pause_script and pause_frame:
            companion.entering_the_game()

        ##### main workflow
        ##### calculations
        ### get input data
        _, follow_command, assist_command = [val // 1.0 for val in data_pixels[0]]
        loot_command, gather_command, _ = [val // 1.0 for val in data_pixels[1]]
        assistant_coordinates = data_pixels[2:4]
        assistant_combat_status, assistant_health, assistant_mana = data_pixels[4]
        player_coordinates_pixels = data_pixels[5:7]
        player_combat_status, player_health, player_mana = data_pixels[7]
        player_message = get_message(player_message_pixels)
        cursor_message = get_message(cursor_message_pixels)

        ### geometry calculation
        # assistant
        assistant_x, assistant_y, assistant_facing, assistant_pitch = coordinates_recalculation(
            assistant_coordinates)
        assistant_position = (assistant_x, assistant_y)
        assistant_facing_vector = vector_between_points(assistant_position,
                                                        second_point_of_vector(assistant_position,
                                                                               assistant_facing))
        # player
        player_x, player_y, _, _ = coordinates_recalculation(player_coordinates_pixels)
        player_position = (player_x, player_y)
        last_player_coordinates = [last_player_coordinates[1],
                                   player_position] if frame % number_of_calculation_frames == 0 else last_player_coordinates
        player_facing_vector = vector_between_points(last_player_coordinates[1], last_player_coordinates[0])
        player_facing_vector = None if player_facing_vector == [0, 0] else player_facing_vector

        # nearing point
        # if not should_calculate_nearing_point:
        #     nearing_x, nearing_y, nearing_position = player_x, player_y, player_position

        # assistant - player
        vector_between_assistant_and_player = vector_between_points(player_position,
                                                                    assistant_position)
        distance_from_assistant_to_player = distance_between_points(assistant_position, player_position)
        angle_between_assistant_facing_and_vector_to_player = angle_between_vectors(assistant_facing_vector,
                                                                                    vector_between_assistant_and_player)
        angle_between_assistant_facing_and_player_facing = angle_between_vectors(assistant_facing_vector,
                                                                                 player_facing_vector)

        # assistant - nearing point

        angle_between_assistant_facing_and_vector_to_nearing_point = None

        last_assistant_coordinates.append(np.sqrt(assistant_x ** 2 + assistant_y ** 2))
        last_assistant_coordinates.pop(0)

        assistant_average_velocity = np.average(np.abs(np.diff(last_assistant_coordinates)))

        coordinates_logger.debug(f"Assistant coordinates: {assistant_x}, {assistant_y}")
        coordinates_logger.debug(f"Assistant facing: {round(np.rad2deg(assistant_facing), 2)} degrees")
        coordinates_logger.debug(
            f"Assistant facing vector: {[round(float(val), 2) for val in assistant_facing_vector]}")
        coordinates_logger.debug(f"Player coordinates: {player_x}, {player_y}")
        if player_facing_vector:
            coordinates_logger.debug(
                f"Player facing vector: {[round(float(val), 2) for val in player_facing_vector]}")
        else:
            coordinates_logger.debug(
                f"Player facing vector is not defined.")
        coordinates_logger.debug(
            f"Vector between A-P: {[round(float(val), 2) for val in vector_between_assistant_and_player]}")
        coordinates_logger.debug(
            f"Distance between A facing and A-P (distance from assistant to player): {round(distance_from_assistant_to_player, 2)}")
        coordinates_logger.debug(
            f"Angle between A facing and A-P: {round(angle_between_assistant_facing_and_vector_to_player, 2)}")
        if angle_between_assistant_facing_and_player_facing:
            coordinates_logger.debug(
                f"Angle between A facing and P facing: {round(angle_between_assistant_facing_and_player_facing, 2)}")
        else:
            coordinates_logger.debug(
                f"Angle between A facing and P facing is not defined.")
        coordinates_logger.debug(
            f"Assistant mean velocity for the last {number_of_calculation_frames} frames: {assistant_average_velocity}")

        ##### define companion activities
        ### define BEHAVIOURS
        companion.set_default_behaviours()
        if follow_command:
            companion.set_moving_behaviour_to(Moving.FOLLOW)

        if assist_command:
            companion.set_combat_behaviour_to(Combat.ASSIST)

        if player_message:
            companion.set_action_behaviour_to(Action.RESPOND)
        elif loot_command:
            companion.set_action_behaviour_to(Action.LOOT)

        ### define DUTIES
        companion.clear_duties()
        # actions at script start
        if frame == 0:
            companion.add_duty(Duty.INITIALIZE)

        # response to a player message
        if companion.action_behaviour_is(Action.RESPOND):
            companion.add_duty(Duty.RESPOND)

        # help in combat
        if companion.combat_behaviour_is(Combat.ASSIST):
            if player_combat_status:
                companion.add_duty(Duty.HELP_IN_COMBAT)

        # looting
        if companion.action_behaviour_is(Action.LOOT):
            companion.add_duty(Duty.LOOT)

        # define distances and angles for nearing and rotation
        distance_delta = 0.15
        maximum_angle_distance_to_player = 1.2 * distance_delta
        # nearing_position = player_position
        if companion.action_behaviour_is(Action.LOOT):
            distance_delta = 0.08  # if make it closer - companion will run past and run around in circles
            maximum_angle_distance_to_player = 0.25 * distance_delta  # 0.01
            # if not companion.state_is(State.LOOTING):
            #     nearing_position = player_position
        # elif companion.combat_behaviour_is(Combat.ASSIST):
        #     rotation_angle_delta = 30

        rotation_angle_delta = np.rad2deg(
            np.arctan(maximum_angle_distance_to_player / distance_from_assistant_to_player))

        # nearing
        if companion.moving_behaviour_is(Moving.FOLLOW):
            if distance_between_points(player_position, assistant_position) >= distance_delta:
                companion.add_duty(Duty.NEARING_WITH_PLAYER)

        # avoid a low obstacle
        if companion.has_duty(Duty.NEARING_WITH_PLAYER):
            if assistant_average_velocity < 0.0002:
                if distance_from_assistant_to_player > distance_delta * 3:
                    companion.add_duty(Duty.AVOID_LOW_OBSTACLE)

        # rotation to player facing in combat
        if companion.has_duty(Duty.HELP_IN_COMBAT) and not companion.has_duty(Duty.NEARING_WITH_PLAYER):
            if angle_between_assistant_facing_and_player_facing:
                if angle_between_assistant_facing_and_player_facing > rotation_angle_delta:
                    companion.add_duty(Duty.ROTATE_TO_PLAYER_FACING)
                    if angle_between_assistant_facing_and_player_facing <= -rotation_angle_delta:
                        companion.add_duty(Duty.ROTATE_TO_PLAYER_FACING_LEFT)
                    elif angle_between_assistant_facing_and_player_facing > rotation_angle_delta:
                        companion.add_duty(Duty.ROTATE_TO_PLAYER_FACING_RIGHT)

        # rotation to player
        if companion.moving_behaviour_is(Moving.FOLLOW) and not companion.has_duty(Duty.ROTATE_TO_PLAYER_FACING):
            if abs(angle_between_assistant_facing_and_vector_to_player) > rotation_angle_delta:
                companion.add_duty(Duty.ROTATE_TO_PLAYER)
                if angle_between_assistant_facing_and_vector_to_player <= -rotation_angle_delta:
                    companion.add_duty(Duty.ROTATE_TO_PLAYER_LEFT)
                elif angle_between_assistant_facing_and_vector_to_player > rotation_angle_delta:
                    companion.add_duty(Duty.ROTATE_TO_PLAYER_RIGHT)

        ## define STATE based on BEHAVIOURS and DUTIES
        if companion.has_duty(Duty.INITIALIZE):
            companion.set_state_to(State.BUFFING)
        elif companion.has_duty(Duty.RESPOND):
            companion.set_state_to(State.RESPONDING)
        elif companion.has_duty(Duty.LOOT) and not companion.state_is(State.LOOTING):
            companion.set_state_to(State.LOOTING)
        elif companion.has_duty(Duty.HELP_IN_COMBAT) and not companion.has_duty(Duty.NEARING_WITH_PLAYER):
            if not (companion.state_is(State.ATTACKING) or companion.state_is(State.ENTERING_COMBAT)):
                companion.set_state_to(State.ENTERING_COMBAT)
            else:
                companion.set_state_to(State.ATTACKING)
        else:
            companion.set_state_to(State.NEUTRAL)

        logging.debug(f"Companion behaviours: {companion.get_behaviours()}")
        logging.debug(f"Companion duties: {companion.get_duties()}")
        logging.debug(f"Companion state: {companion.get_state()}")

        ###### companion logic
        ### cast buffs
        if companion.state_is(State.BUFFING):
            companion.cast_spell(spells['Power Word: Fortitude'])
            companion.cast_spell(spells['Inner Fire'])

        ### answer to message
        if companion.state_is(State.RESPONDING):
            companion.hands_away_from_keyboard()
            logging.info(f"Player message: {player_message}")
            companion.ai_companion_response(player_message)

        ### movement
        if not companion.state_is(State.RESPONDING):
            # rotation
            companion.rotate(duty=Duty.ROTATE_TO_PLAYER)
            # moving
            companion.move_to(duty=Duty.NEARING_WITH_PLAYER)
            # jump over low obstacles
            if companion.has_duty(Duty.AVOID_LOW_OBSTACLE):
                companion.jump()

        ### chat-commands based logic
        # looting
        if companion.state_is(State.LOOTING):
            inputs.move_mouse_to_default_position(game_window)
            if not companion.has_duty(Duty.NEARING_WITH_PLAYER) and not companion.has_duty(Duty.ROTATE_TO_PLAYER):
                companion.loot(looting_area={'x_length': 200, 'y_length': 200,
                                             'x_step': 35, 'y_step': 50})
            inputs.move_mouse_to_default_position(game_window)

        ### assist in combat
        if companion.state_is_one_of([State.ENTERING_COMBAT, State.ATTACKING]):
            # rotation to player facing
            companion.rotate(Duty.ROTATE_TO_PLAYER_FACING)

            # battle rotation
            if not companion.has_duty(Duty.ROTATE_TO_PLAYER_FACING):
                if companion.state_is(State.ENTERING_COMBAT):
                    logging.debug("Enter the combat state!")
                    companion.target_the_ally(target='player_pet')
                    companion.cast_spell(spells['Power Word: Shield'])

                elif companion.state_is(State.ATTACKING):
                    companion.target_the_enemy()
                    companion.cast_spell(spells['Penance'])
                    companion.cast_spell(spells['Smite'])

        for spell in spells.keys():
            if spells[spell]['cooldown']:
                companion.check_spell_timer(spells[spell])

        if not pause_script:
            pause_frame = None
            frame += 1

        logging.debug(f"Script work time is {round(time.time() - frame_start_time, 2)}s per frame")

except KeyboardInterrupt:
    HardwareInputSimulator().release_movement_keys()
    print("Monitoring stopped.")
