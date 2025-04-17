import numpy as np
import logging
import time

from library.miscellaneous import read_yaml_file
from library.constants import WOW_AREAS


class BasicGeometry:
    @staticmethod
    def coordinates_recalculation(input_data):
        pixel1 = input_data[0]
        pixel2 = input_data[1]
        x = (pixel1[0] * 255 + pixel1[1]) / 255 * 100
        y = (pixel2[0] * 255 + pixel2[1]) / 255 * 100
        facing = pixel1[2] * 7.0
        pitch = (pixel2[2] - 0.5) * 4
        return round(x, 2), round(y, 2), round(facing, 2), round(pitch, 2)

    @staticmethod
    def angle_between_vectors(v1, v2):
        if v1 is None or v2 is None:
            # geometry_logger.error("Cannot calculate angle between vectors: one or more vectors is not defined.")
            return None
        v1 = v1 / np.linalg.norm(v1) if np.linalg.norm(v1) != 0 else v1
        v2 = v2 / np.linalg.norm(v2) if np.linalg.norm(v2) != 0 else v2
        dot_product = np.dot(v1, v2)
        dot_product_clamped = np.clip(dot_product, -1.0, 1.0)
        angle_rad = np.arccos(dot_product_clamped)
        cross_product = np.cross(np.append(v1, 0), np.append(v2, 0))  # Convert to 3D for cross-product
        if cross_product[2] < 0:  # Check the z-component of the cross-product
            angle_rad = -angle_rad  # Make the angle negative if the cross-product is negative
        return np.degrees(angle_rad)

    @staticmethod
    def vector_between_points(point1, point2):
        if point1 is None or point2 is None:
            # logging.error("Cannot calculate vector between points: one or more points is not defined.")
            return None
        vector = [p2 - p1 for p1, p2 in zip(point1, point2)]
        return vector

    @staticmethod
    def second_point_of_vector(point1, vector, length=1):
        x1, y1 = point1
        return x1 + length * np.sin(vector), y1 + length * np.cos(vector)

    @staticmethod
    def distance_between_points(point1, point2):
        if point1 is None or point2 is None:
            # logging.error("Cannot calculate distance between points: one or more points is not defined.")
            return None
        return np.linalg.norm(np.array(point2) - np.array(point1))


class Navigator(BasicGeometry):

    def __init__(self, n_frames=20, config_file=None):
        super().__init__()
        self.n_frames = n_frames
        self.last_companion_coordinates = [(0, 0)] * n_frames
        self.last_player_coordinates = [(0, 0)] * n_frames
        self.last_companion_time = [0] * n_frames
        self.last_player_time = [0] * n_frames

        self.config_file = config_file
        self.predefined_navigation_constants = self.set_predefined_navigation_constants()

        self.logger = logging.getLogger('navigation')
        # if not self.logger.hasHandlers():
        #     handler = logging.StreamHandler()
        #     self.logger.addHandler(handler)
        #     self.logger.propagate = False


    def set_predefined_navigation_constants(self):
        predefined_navigation_constants = read_yaml_file(self.config_file).get('navigation', None)
        return predefined_navigation_constants

    def _calculate_velocity(self, position, coordinates_array, times_array):
        times_array.append(time.time())
        times_array.pop(0)
        coordinates_array.append(position)
        coordinates_array.pop(0)

        average_coord_delta = np.average(
            np.abs(np.diff([np.sqrt(coord[0] ** 2 + coord[1] ** 2) for coord in self.last_companion_coordinates])))
        time_delta = times_array[-1] - times_array[0]
        average_velocity = average_coord_delta / time_delta

        return average_velocity

    def game_state_geometry(self, data):
        companion_data = self._calculate_companion(data)
        player_data = self._calculate_player(data)
        companion_player_data = self._calculate_companion_player(companion_data, player_data)
        nearing_and_rotations_data = self._define_moving_constants(companion_player_data, data['map_id'])

        output_data = {}
        for d in [player_data, companion_data, companion_player_data, nearing_and_rotations_data]:
            output_data.update(d)

        self._geometry_logging(output_data)

        return output_data

    def _calculate_companion(self, data):
        companion_coordinates_pixels = data['companion_coordinates_pixels']
        companion_x, companion_y, companion_facing, companion_pitch = self.coordinates_recalculation(
            companion_coordinates_pixels)
        companion_position = (companion_x, companion_y)
        companion_facing_vector = self.vector_between_points(companion_position,
                                                             self.second_point_of_vector(companion_position,
                                                                                         companion_facing))

        companion_average_velocity = self._calculate_velocity(companion_position,
                                                              self.last_companion_coordinates,
                                                              self.last_companion_time)

        return {
            'companion_x': companion_x, 'companion_y': companion_y,
            'companion_facing': companion_facing, 'companion_pitch': companion_pitch,
            'companion_position': companion_position,
            'companion_facing_vector': companion_facing_vector,
            'companion_average_velocity': companion_average_velocity
        }

    def _calculate_player(self, data):
        player_coordinates_pixels = data['player_coordinates_pixels']
        player_x, player_y, _, _ = self.coordinates_recalculation(player_coordinates_pixels)
        player_position = (player_x, player_y)
        player_position = None if player_position == (0, 0) else player_position

        self.last_player_coordinates.append(player_position)
        self.last_player_coordinates.pop(0)
        player_facing_vector = self.vector_between_points(self.last_player_coordinates[-1],
                                                          self.last_player_coordinates[0])
        player_facing_vector = None if player_facing_vector == [0, 0] else player_facing_vector

        if None not in self.last_player_coordinates:
            player_average_velocity = self._calculate_velocity(player_position,
                                                               self.last_player_coordinates,
                                                               self.last_player_time)
        else:
            player_average_velocity = None

        return {
            'player_x': player_x, 'player_y': player_y,
            'player_facing': None, 'player_pitch': None,
            'player_position': player_position,
            'player_facing_vector': player_facing_vector,
            'player_average_velocity': player_average_velocity
        }

    def _calculate_companion_player(self, companion_data, player_data):
        vector_between_companion_and_player = self.vector_between_points(
            player_data['player_position'],
            companion_data['companion_position'])
        distance_from_companion_to_player = self.distance_between_points(
            companion_data['companion_position'],
            player_data['player_position'])
        angle_between_companion_facing_and_vector_to_player = self.angle_between_vectors(
            companion_data['companion_facing_vector'],
            vector_between_companion_and_player)
        angle_between_companion_facing_and_player_facing = self.angle_between_vectors(
            companion_data['companion_facing_vector'],
            player_data[
                'player_facing_vector'])
        return {
            'vector_between_companion_and_player': vector_between_companion_and_player,
            'distance_from_companion_to_player': distance_from_companion_to_player,
            'angle_between_companion_facing_and_vector_to_player': angle_between_companion_facing_and_vector_to_player,
            'angle_between_companion_facing_and_player_facing': angle_between_companion_facing_and_player_facing
        }

    def _define_moving_constants(self, input_data, map_id):

        if map_id in WOW_AREAS.keys():
            distance_to_player_delta = WOW_AREAS[map_id] * 0.15
        else:
            self.logger.debug(f"Cannot find map with map ID {map_id}.")
            distance_to_player_delta = 0.15

        mounted_distance_coefficient = 1.25
        looting_distance_coefficient = 0.5
        start_to_avoid_obstacles_distance_coefficient = 3.0
        start_to_wait_player_coefficient = 50.0

        if self.predefined_navigation_constants:
            mounted_distance_coefficient = self.predefined_navigation_constants.get('mounted_distance_coefficient',
                                                                                    mounted_distance_coefficient)
            looting_distance_coefficient = self.predefined_navigation_constants.get('looting_distance_coefficient',
                                                                                    looting_distance_coefficient)
            start_to_avoid_obstacles_distance_coefficient = self.predefined_navigation_constants.get(
                'start_to_avoid_obstacles_distance_coefficient', start_to_avoid_obstacles_distance_coefficient)
            start_to_wait_player_coefficient = self.predefined_navigation_constants.get(
                'start_to_wait_player_coefficient', start_to_avoid_obstacles_distance_coefficient)

        mounted_distance_to_player_delta = distance_to_player_delta * mounted_distance_coefficient
        looting_distance_to_player_delta = distance_to_player_delta * looting_distance_coefficient
        distance_to_start_avoid_obstacles = distance_to_player_delta * start_to_avoid_obstacles_distance_coefficient
        max_distance_from_companion_to_player = distance_to_player_delta * start_to_wait_player_coefficient

        # angles
        rotation_to_player_angle_delta_min = 10  # min angle (degrees in one side of rotation)
        rotation_to_player_angle_delta_max = 35  # max angle (degrees in one side of rotation)
        rotation_to_player_angle_delta = rotation_to_player_angle_delta_max  # defined by distance to player
        if input_data['distance_from_companion_to_player'] and input_data['distance_from_companion_to_player'] > 0:
            rotation_to_player_angle_delta = np.rad2deg(
                np.arctan(distance_to_player_delta / input_data['distance_from_companion_to_player']))
            rotation_to_player_angle_delta = np.clip(rotation_to_player_angle_delta,
                                                     rotation_to_player_angle_delta_min,
                                                     rotation_to_player_angle_delta_max)

        # velocities
        minimum_velocity_for_nearing = 0.001  # ingame meters per second

        return {'mounted_distance_to_player_delta': mounted_distance_to_player_delta,
                'distance_to_player_delta': distance_to_player_delta,
                'rotation_to_player_angle_delta': rotation_to_player_angle_delta,
                'minimum_velocity_for_nearing': minimum_velocity_for_nearing,
                'distance_to_start_avoid_obstacles': distance_to_start_avoid_obstacles,
                'looting_distance_to_player_delta': looting_distance_to_player_delta,
                'max_distance_from_companion_to_player': max_distance_from_companion_to_player}

    def _geometry_logging(self, data):
        self.logger.debug(f"Companion coordinates: {data['companion_x']}, {data['companion_y']}")
        self.logger.debug(f"Companion facing: {round(np.rad2deg(data['companion_facing']), 2)} degrees")
        self.logger.debug(
            f"Companion facing vector: {[round(float(val), 2) for val in data['companion_facing_vector']]}")
        self.logger.debug(f"Player coordinates: {data['player_x']}, {data['player_y']}")

        if data['player_facing_vector']:
            self.logger.debug(
                f"Player facing vector: {[round(float(val), 2) for val in data['player_facing_vector']]}")
        else:
            self.logger.debug(f"Player facing vector is not defined.")

        if data['vector_between_companion_and_player']:
            self.logger.debug(
                f"Vector between companion and player: {[round(float(val), 2) for val in data['vector_between_companion_and_player']]}")
        else:
            self.logger.debug(f"Vector between companion and player is not defined.")

        if data['distance_from_companion_to_player']:
            self.logger.debug(
                f"Distance from companion to player: {round(data['distance_from_companion_to_player'], 2)}")
        else:
            self.logger.debug("Distance between companion facing and player is not defined.")

        if data['angle_between_companion_facing_and_vector_to_player']:
            self.logger.debug(
                f"Angle between C facing and C-P: {round(data['angle_between_companion_facing_and_vector_to_player'], 2)}")
        else:
            self.logger.debug("Angle between companion facing and vector to player in not defined.")

        if data['angle_between_companion_facing_and_player_facing']:
            self.logger.debug(
                f"Angle between C facing and P facing: {round(data['angle_between_companion_facing_and_player_facing'], 2)}")
        else:
            self.logger.debug(
                f"Angle between C facing and P facing is not defined.")

        self.logger.debug(
            f"Companion's mean velocity for the last {self.n_frames} frames: {data['companion_average_velocity']}")
