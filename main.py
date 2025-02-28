import logging
import time

import subprocess

import numpy as np
from statemachine.states import States

from library.inputs import InputController

from library.assistant_actions import AssistantActions

from library.game_window import GameWindow
from library.geometry import *
from library.gingham_processing import *

from companion import *

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

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

    # initialize assistant control class based on initialized GameWindow
    assistant = AssistantActions(game_window)

    ### initialize the companion with default behavior:
    # (Moving - STAY; Combat - ASSIST; Action - NONE)
    companion = Companion()
    companion.set_state_to(State.NEUTRAL)

    # assistant_state = 'following'

    time.sleep(1)

    forward_held = False
    forward_released = True
    left_held = False
    left_released = True
    right_held = False
    right_released = True
    nearing_position = (0, 0)

    frame = 0
    pause_frame = None
    assistant_control_start_time = time.time()

    while True:
        frame_start_time = time.time()

        logging.debug("." * 100)
        logging.debug(f"Frame #{frame}")

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

        # disable script from game
        if disable_script:
            logging.warning("Control script was disabled from game.")
            if frame == 0:
                logging.warning("Enable it by sending \'disable\' in the party chat.")
            inputs.release_movement_keys()
            exit(0)

        # pause script
        elif pause_script:
            if not pause_frame:
                pause_frame = frame
            if pause_frame == frame:
                logging.info("Control script was paused.")
                inputs.release_movement_keys()
                forward_released = True
                forward_held = False
                inputs.press_key("x")
            pause_frame += 1
            pass

        # end of the pause
        if not pause_script and pause_frame:
            logging.info("Control script is active.")
            inputs.press_key("x", pause=2.0)
            assistant.send_message(message="/salute", channel='/s', pause=4.0)

        ### main workflow
        if not disable_script and not pause_script:

            ###### recalculations
            # get input data
            _, follow_command, assist_command = [val // 1.0 for val in data_pixels[0]]
            loot_command, gather_command, _ = [val // 1.0 for val in data_pixels[1]]
            assistant_coordinates = data_pixels[2:4]
            assistant_combat_status, assistant_health, assistant_mana = data_pixels[4]
            player_coordinates_pixels = data_pixels[5:7]
            player_combat_status, player_health, player_mana = data_pixels[7]
            player_message = get_message(player_message_pixels)
            cursor_message = get_message(cursor_message_pixels)

            # geometry calculation
            assistant_x, assistant_y, assistant_facing, assistant_pitch = coordinates_recalculation(
                assistant_coordinates)
            player_x, player_y, _, _ = coordinates_recalculation(player_coordinates_pixels)
            assistant_position = (assistant_x, assistant_y)
            player_position = (player_x, player_y)
            assistant_facing_vector = vector_between_points(assistant_position,
                                                            second_point_of_vector(assistant_position,
                                                                                   assistant_facing))
            last_player_coordinates = [last_player_coordinates[1],
                                       player_position] if frame % number_of_frames == 0 else last_player_coordinates
            player_facing_vector = vector_between_points(last_player_coordinates[1], last_player_coordinates[0])
            vector_between_assistant_and_player = vector_between_points(player_position,
                                                                        assistant_position)
            distance_to_player = distance_between_points(assistant_position, player_position)
            angle_between_assistant_facing_and_vector_to_player = angle_between_vectors(assistant_facing_vector,
                                                                                        vector_between_assistant_and_player)
            angle_between_assistant_facing_and_player_facing = angle_between_vectors(assistant_facing_vector,
                                                                                     player_facing_vector)


            angle_between_assistant_facing_and_vector_to_nearing_point = None


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
            logging.debug(f"Distance between A facing and A-P (distance to player): {round(distance_to_player, 2)}")
            logging.debug(
                f"Angle between A facing and A-P: {round(angle_between_assistant_facing_and_vector_to_player, 2)}")
            logging.debug(
                f"Angle between A facing and P facing: {round(angle_between_assistant_facing_and_player_facing, 2)}")
            logging.debug(
                f"Assistant mean velocity for the last {number_of_frames} frames: {assistant_average_velocity}")

            ##### define companion activities
            companion.set_default_behaviours()
            companion.clear_duties()

            ### define BEHAVIOURS
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
            if frame == 0:
                companion.add_duty(Duty.INITIALIZE)

            if companion.action_behavior_is(Action.LOOT):
                distance_delta = 0.08  # if make it closer - companion will run past and run around in circles
                maximum_angle_distance_to_player = 0.5 * distance_delta  # 0.01
                if not companion.state_is(State.LOOTING):
                    nearing_position = [player_x, player_y]
            else:
                distance_delta = 0.15
                maximum_angle_distance_to_player = 1.2 * distance_delta
                nearing_position = [player_x, player_y]

            rotation_angle_delta = np.rad2deg(np.arctan(maximum_angle_distance_to_player / distance_to_player))

            if companion.combat_behavior_is(Combat.ASSIST):
                if player_combat_status:
                    companion.add_duty(Duty.HELP_IN_COMBAT)

            ### define DUTIES again
            if companion.moving_behavior_is(Moving.FOLLOW):
                if distance_between_points(nearing_position, [assistant_x, assistant_y]) >= distance_delta:
                    companion.add_duty(Duty.NEARING)

                if assistant_average_velocity < 0.001:
                    if distance_to_player > distance_delta * 2:
                        companion.add_duty(Duty.AVOID_LOW_OBSTACLE)

                if abs(angle_between_assistant_facing_and_vector_to_player) > rotation_angle_delta:
                    companion.add_duty(Duty.ROTATE)
                    if angle_between_assistant_facing_and_vector_to_player <= -rotation_angle_delta:
                        companion.add_duty(Duty.ROTATE_LEFT)
                    elif angle_between_assistant_facing_and_vector_to_player > rotation_angle_delta:
                        companion.add_duty(Duty.ROTATE_RIGHT)

            # if not loot_command:
            #     looting_position = None
            # if not looting_position:
            #     looting_position = [player_x, player_y]
            # distance_to_looting_point = distance_between_points([assistant_x, assistant_y], looting_position)

            ## define STATE
            if companion.action_behavior_is(Action.LOOT) and not companion.state_is(State.LOOTING):
                companion.set_state_to(State.LOOTING)
            elif companion.has_duty(Duty.HELP_IN_COMBAT) and not companion.state_is(State.IN_COMBAT):
                companion.set_state_to(State.IN_COMBAT)
            else:
                companion.set_state_to(State.NEUTRAL)

            logging.debug(f"Companion behaviours: {companion.get_behaviours()}")
            logging.debug(f"Companion duties: {companion.get_duties()}")
            logging.debug(f"Companion state: {companion.get_state()}")

            ###### companion logic

            ### initial actions
            if companion.has_duty(Duty.INITIALIZE):
                # buffs
                inputs.hold_key('shift')
                inputs.press_key("2", pause=0.1)
                inputs.release_key('shift')
                inputs.press_key("1", pause=2.0)
                inputs.press_key("2", pause=0.1)
                inputs.hold_key('shift')
                inputs.press_key("1", pause=0.1)
                inputs.release_key('shift')

            ### answer to message and start the new iteration
            if companion.action_behavior_is(Action.RESPOND):
                logging.info(f"Player message: {player_message}")
                inputs.release_movement_keys()
                assistant.assistant_response(player_message, context_file='context.txt')
                continue

            ### movement
            # rotation
            if companion.has_duty(Duty.ROTATE_RIGHT) and not right_held:
                right_held = True
                right_released = False
                inputs.hold_key("d")
            if not companion.has_duty(Duty.ROTATE_RIGHT) and not right_released:
                right_held = False
                right_released = True
                inputs.release_key("d")
            if companion.has_duty(Duty.ROTATE_LEFT) and not left_held:
                left_held = True
                left_released = False
                inputs.hold_key("a")
            if not companion.has_duty(Duty.ROTATE_LEFT) and not left_released:
                left_held = False
                left_released = True
                inputs.release_key("a")

            # moving
            if companion.has_duty(Duty.NEARING) and not forward_held:
                forward_held = True
                forward_released = False
                inputs.hold_key("w")
            if not companion.has_duty(Duty.NEARING) and not forward_released:
                forward_released = True
                forward_held = False
                inputs.release_key("w")

            # avoid low obstacles
            if companion.has_duty(Duty.NEARING) and companion.has_duty(Duty.AVOID_LOW_OBSTACLE):
                inputs.press_key('space', pause=1.5)

            ### chat-commands based logic
            # looting
            if companion.action_behavior_is(Action.LOOT):  # should_gather_resources or should_collect_loot:
                logging.debug("Going to collect resources.")
                inputs.move_mouse_to_default_position(game_window)
                if not companion.has_duty(Duty.NEARING) and not companion.has_duty(Duty.ROTATE):
                    assistant.find_and_click(area_x=200, area_y=300,
                                             area_shift_x=0, area_shift_y=0,
                                             step_x=35, step_y=50)
                    assistant.send_message("#loot", channel="/p", pause=1)
                inputs.move_mouse_to_default_position(game_window)

            ### assist in combat
            if companion.has_duty(Duty.HELP_IN_COMBAT) and not companion.has_duty(Duty.NEARING):
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
                    if companion.state_is(State.IN_COMBAT):
                        logging.debug("Enter the combat state!")
                        inputs.hold_key('shift')
                        inputs.press_key("F2", pause=0.1)
                        inputs.release_key('shift')

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
