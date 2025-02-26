import logging
import time

import subprocess

from library.inputs import Key
from library.inputs import InputControllerXdotool as InputController

from library.assistant_actions import AssistantActions

from library.game_window import GameWindow
from library.geometry import *
from library.gingham_processing import *

from companion import *

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# 1 - monitoring column, 85 - letters
# script, interaction, assistant_(xy, condition), player_(xy, condition), message_len, cursor_info_len

number_of_frames = 20
last_assistant_coordinates = [0] * number_of_frames
last_player_coordinates = [[0, 0], [0, 0]]
rotate_per_second = 180

penance_cast_time = None
power_word_shield_cast_time = None

penance_ready = True
power_word_shield_ready = True

spells_info = {"penance": {"key": "q", "cooldown": 12, "cast_time": None},
               "power word: shield": {"key": "e", "cooldown": 15, "cast_time": 0},
               "holysmite": {"key": "1", "cooldown": 0, "cast_time": None}, }

try:
    subprocess.run(["pkill", "ydotoold"])
    _ = subprocess.Popen(["nohup", "ydotoold", "&"], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)  # pipes are using to suppress ydotoold info logging

    game_window = GameWindow()
    game_window.activate_window("World of Warcraft")
    logging.info("WoW Assistant Control Manager is activated.")

    inputs = InputController()
    logging.info("Input Controller is ready.")

    assistant_state = 'following'

    time.sleep(1)

    forward_held = False
    forward_released = False

    frame = 0
    pause_frame = None
    assistant_control_start_time = time.time()

    logging.debug("." * 100)
    logging.debug(f"Frame #{frame}")
    while True:
        frame_start_time = time.time()

        # initialize assistant control class based on initialized GameWindow
        assistant = AssistantActions(game_window)

        gingham_shirt = game_window.take_screenshot(savefig=True)
        data_pixels, player_message_pixels, cursor_message_pixels = pixels_analysis(data=gingham_shirt,
                                                                                    n_monitoring_pixels=
                                                                                    game_window.n_pixels['y'],
                                                                                    pixel_height=
                                                                                    game_window.pixel_size['y'],
                                                                                    pixel_width=
                                                                                    game_window.pixel_size['x'])

        ### script manipulation
        pause_script, disable_script = get_script_control_commands(data_pixels[0][0])

        if disable_script:
            logging.warning("Control script was disabled from game.")
            if frame == 0:
                logging.warning("Enable it by sending \'disable\' in the party chat.")
            inputs.release_movement_keys()
            exit(0)
        # pause
        elif pause_script:
            if not pause_frame:
                pause_frame = frame
            if pause_frame == frame:
                inputs.release_movement_keys()
                forward_released = True
                forward_held = False
                inputs.press_key("x")
                logging.info("Control script was paused.")
            pause_frame += 1
            pass
        if not pause_script and pause_frame:
            inputs.press_key("x", pause=2.0)
            assistant.send_message(message="/salute", channel='/s', pause=4.0)
            logging.info("Control script is active.")

        ### main workflow
        if not disable_script and not pause_script:

            ###### recalculations
            # get input data
            _, follow_command, assist_command = [val // 1.0 for val in data_pixels[0]]
            loot_command, gather_command, _ = [val // 1.0 for val in data_pixels[1]]
            assistant_coordinates = data_pixels[2:4]
            assistant_combat_status, assistant_health, assistant_mana = data_pixels[4]
            player_coordinates = data_pixels[5:7]
            player_combat_status, player_health, player_mana = data_pixels[7]
            player_message = get_message(player_message_pixels)
            cursor_message = get_message(cursor_message_pixels)

            # geometry calculation
            assistant_x, assistant_y, assistant_facing, assistant_pitch = coordinates_recalculation(
                assistant_coordinates)
            player_x, player_y, _, _ = coordinates_recalculation(player_coordinates)
            assistant_facing_vector = vector_between_points((assistant_x, assistant_y),
                                                            second_point_of_vector(assistant_x, assistant_y,
                                                                                   assistant_facing))
            last_player_coordinates = [last_player_coordinates[1], [player_x,
                                                                    player_y]] if frame % number_of_frames == 0 else last_player_coordinates
            player_facing_vector = vector_between_points(last_player_coordinates[1], last_player_coordinates[0])
            vector_between_assistant_and_player = vector_between_points((player_x, player_y),
                                                                        (assistant_x, assistant_y))
            distance_to_player = np.linalg.norm(np.array([player_x, player_y]) - np.array([assistant_x, assistant_y]))
            angle_between_assistant_facing_and_vector_to_player = angle_between_vectors(assistant_facing_vector,
                                                                                        vector_between_assistant_and_player)
            angle_between_assistant_facing_and_player_facing = angle_between_vectors(assistant_facing_vector,
                                                                                     player_facing_vector)

            last_assistant_coordinates.append(np.sqrt(assistant_x ** 2 + assistant_y ** 2))
            last_assistant_coordinates.pop(0)

            assistant_average_velocity = np.average(np.abs(np.diff(last_assistant_coordinates)))

            logging.debug(f"Assistant coordinates: {assistant_x}, {assistant_y}")
            logging.debug(f"Assistant facing: {round(np.rad2deg(assistant_facing), 2)} degrees")
            logging.debug(f"Assistant facing vector: {[round(float(val), 2) for val in assistant_facing_vector]}")
            logging.debug(f"Player coordinates: {player_x}, {player_y}")
            logging.debug(f"Player facing vector: {[round(float(val), 2) for val in player_facing_vector]}")
            logging.debug(
                f"Vector between A-P: {[round(float(val), 2) for val in vector_between_assistant_and_player]}")
            logging.debug(f"Distance between A facing and A-P: {round(distance_to_player, 2)}")
            logging.debug(
                f"Angle between A facing and A-P: {round(angle_between_assistant_facing_and_vector_to_player, 2)}")
            logging.debug(
                f"Angle between A facing and P facing: {round(angle_between_assistant_facing_and_player_facing, 2)}")
            logging.debug(
                f"Assistant mean velocity for the last {number_of_frames} frames: {assistant_average_velocity}")

            ##### define companion activities
            ### companion behavior and states
            companion = Companion()
            # behavior (defined by player commands and messages)
            companion.moving_behaviour = Moving.STAY
            companion.combat_behaviour = Combat.PASSIVE
            companion.action_behaviour = Action.NONE
            # should_collect_loot = False
            # should_gather_resources = False

            # states (based on behavior, time and geometry)
            should_move_closer = False
            should_do_initial_actions = False
            # should_follow = False
            should_avoid_low_obstacle = False
            should_rotate = False
            should_rotate_left = False
            should_rotate_right = False
            # should_be_assistable_in_combat = False
            should_help_to_player_in_combat = False

            if follow_command:
                # should_follow = True
                companion.moving_behaviour = Moving.FOLLOW

            if assist_command:
                companion.combat_behaviour = Combat.ASSIST
                # should_be_assistable_in_combat = True

            if player_message:
                companion.action_behaviour = Action.ASK_TO_MESSAGE
            elif loot_command:
                companion.action_behaviour = Action.LOOT

            if frame == 0:
                should_do_initial_actions = True

            # if gather_command:
            #     should_gather_resources = True

            if companion.action_behaviour is Action.LOOT:  # should_collect_loot or should_gather_resources:
                distance_delta = 0.08  # if make it closer - companion will run past and run around in circles
                angle_delta = 12
                delta_rotation_degree = 10
            else:
                distance_delta = 0.15
                angle_delta = 22.5
                delta_rotation_degree = 60

            rotation_time = np.abs(
                (angle_between_assistant_facing_and_vector_to_player + angle_delta) / (
                        rotate_per_second - delta_rotation_degree))

            if companion.moving_behaviour is Moving.FOLLOW:
                if distance_to_player >= distance_delta:
                    should_move_closer = True

                if assistant_average_velocity < 0.001:
                    if distance_to_player > distance_delta * 2:
                        should_avoid_low_obstacle = True

                if abs(angle_between_assistant_facing_and_vector_to_player) > angle_delta:
                    should_rotate = True
                    if angle_between_assistant_facing_and_vector_to_player <= -angle_delta:
                        should_rotate_right = True
                    elif angle_between_assistant_facing_and_vector_to_player > angle_delta:
                        should_rotate_left = True

            if companion.combat_behaviour is Combat.ASSIST:
                if player_combat_status:
                    should_help_to_player_in_combat = True

            ###### companion logic
            ### answer to message and start the new iteration
            if companion.action_behaviour is Action.ASK_TO_MESSAGE:
                logging.info(f"Player message: {player_message}")
                inputs.release_movement_keys()
                assistant.assistant_response(player_message, context_file='context.txt')
                continue

            ### initial actions
            if should_do_initial_actions:
                # buffs
                inputs.hold_key(Key.shift)
                inputs.press_key("2", pause=0.1)
                inputs.release_key(Key.shift)
                inputs.press_key("1", pause=2.0)
                inputs.press_key("2", pause=0.1)
                inputs.hold_key(Key.shift)
                inputs.press_key("1", pause=0.1)
                inputs.release_key(Key.shift)

            ### movement
            # rotation
            if should_rotate:
                if should_rotate_right:
                    inputs.hold_key_for_time("a", rotation_time)
                elif should_rotate_left:
                    inputs.hold_key_for_time("d", rotation_time)
                else:
                    inputs.release_key("a"), inputs.release_key("d")

            # moving
            if should_move_closer and not forward_held:
                forward_held = True
                forward_released = False
                inputs.hold_key("w")
            if not should_move_closer and not forward_released:
                forward_released = True
                forward_held = False
                inputs.release_key("w")

            # avoid low obstacles
            if should_move_closer and should_avoid_low_obstacle:
                inputs.press_key(Key.space, pause=1.5)

            ### chat-commands based logic
            # looting
            if companion.action_behaviour is Action.LOOT:  # should_gather_resources or should_collect_loot:
                logging.debug("Going to collect resources.")
                inputs.move_mouse(game_window.window_position[0] + game_window.window_size[0] - 50,
                                  game_window.window_position[1] + game_window.window_size[1] - 50)
                if not should_move_closer and not should_rotate:
                    assistant.find_and_click(area_x=200, area_y=300,
                                             area_shift_x=0, area_shift_y=0,
                                             step_x=35, step_y=50)
                    time.sleep(3)
                    assistant.send_message("#loot", channel="/p", pause=1)
                    # if should_gather_resources:
                    #     time.sleep(3)
                    #     assistant.send_message("#gather", channel="/p", pause=1)
                    #     should_gather_resources = False
                    # elif should_collect_loot:
                    #     assistant.send_message("#loot", channel="/p", pause=1)
                    #     should_collect_loot = False
                inputs.move_mouse(game_window.window_position[0] + game_window.window_size[0] - 50,
                                  game_window.window_position[1] + game_window.window_size[1] - 50)

            ### assist in combat
            if should_help_to_player_in_combat:
                logging.debug("Should assist in combat")
            else:
                logging.debug("Shouldn't assist in combat")

            if should_help_to_player_in_combat and not should_move_closer:
                angle_delta = 30
                if player_facing_vector != [0,
                                            0] and angle_between_assistant_facing_and_player_facing > angle_delta:
                    logging.debug("Should rotate to the player facing!")
                    if angle_between_assistant_facing_and_player_facing <= -angle_delta:
                        inputs.hold_key_for_time("a",
                                                 np.abs(angle_between_assistant_facing_and_player_facing / 180))
                    elif angle_between_assistant_facing_and_player_facing > angle_delta:
                        inputs.hold_key_for_time("d",
                                                 np.abs(angle_between_assistant_facing_and_player_facing / 180))
                else:
                    if should_help_to_player_in_combat and assistant_state != 'combat': # and companion.combat_behaviour is Combat.ASSIST
                        assistant_state = 'combat'
                        logging.debug("Enter the combat state!")
                        inputs.hold_key(Key.shift)
                        inputs.press_key("F2", pause=0.1)
                        inputs.release_key(Key.shift)

                        if power_word_shield_ready:
                            inputs.press_key(spells_info["power word: shield"]["key"], pause=1.0)
                            power_word_shield_cast_time = time.time()
                            power_word_shield_ready = False
                            logging.debug("Cast Power Word: Shield!")

                    # battle rotation
                    inputs.press_key("F2")
                    inputs.press_key("F", pause=0.5)

                    if penance_ready:
                        inputs.press_key(spells_info["penance"]["key"], pause=2.0)
                        penance_cast_time = time.time()
                        penance_ready = False
                        logging.debug("Cast \"Penance\"!")

                    inputs.press_key(spells_info['holysmite']["key"], pause=2.0)
                    logging.debug("Cast \"Holysmite!\"")

            if not should_help_to_player_in_combat:
                assistant_state = 'following'

            # spells timers
            if not penance_ready:
                if time.time() - penance_cast_time < spells_info["penance"]["cooldown"]:
                    logging.debug(
                        f"Penance cooldown. "
                        f"Should wait for {round(np.abs(time.time() - penance_cast_time - spells_info["penance"]["cooldown"]), 2)} seconds")
                    penance_ready = False
                else:
                    logging.debug("Penance ready")
                    penance_ready = True

            if not power_word_shield_ready:
                if time.time() - power_word_shield_cast_time < spells_info["power word: shield"]["cooldown"]:
                    logging.debug(
                        f"Power Word: Shield cooldown. "
                        f"Should wait for {round(np.abs(time.time() - power_word_shield_cast_time - spells_info["power word: shield"]["cooldown"]), 2)} seconds")
                    power_word_shield_ready = False
                else:
                    logging.debug("Power Word: Shield is ready")
                    power_word_shield_ready = True

        if not pause_script:
            pause_frame = None
            frame += 1

        logging.debug(f"Script work time is {round(time.time() - frame_start_time, 2)}s per frame")

        ############################################

        # else:
        #     press_key("Escape", pause=1)
        #
        # if not in_combat and previous_state == 'combat':
        #     previous_state = 'idle'

except KeyboardInterrupt:
    InputController().release_movement_keys()
    print("Monitoring stopped.")

InputController().release_movement_keys()
