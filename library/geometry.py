import numpy as np


def coordinates_recalculation(input_data):
    pixel1 = input_data[0]
    pixel2 = input_data[1]
    x = (pixel1[0] * 255 + pixel1[1]) / 255 * 100
    y = (pixel2[0] * 255 + pixel2[1]) / 255 * 100
    facing = pixel1[2] * 7.0
    pitch = (pixel2[2] - 0.5) * 4
    return round(x, 2), round(y, 2), round(facing, 2), round(pitch, 2)


def angle_between_vectors(v1, v2):
    if v1 is None or v2 is None:
        return None
    v1 = v1 / np.linalg.norm(v1) if np.linalg.norm(v1) != 0 else v1
    v2 = v2 / np.linalg.norm(v2) if np.linalg.norm(v2) != 0 else v2

    # Calculate the dot product
    dot_product = np.dot(v1, v2)

    # Clamp the value to prevent invalid inputs to arccos
    dot_product_clamped = np.clip(dot_product, -1.0, 1.0)

    # Calculate the angle in radians
    angle_rad = np.arccos(dot_product_clamped)

    # Calculate the cross-product to determine the sign
    cross_product = np.cross(np.append(v1, 0), np.append(v2, 0))  # Convert to 3D for cross-product

    if cross_product[2] < 0:  # Check the z-component of the cross-product
        angle_rad = -angle_rad  # Make the angle negative if the cross-product is negative

    return np.degrees(angle_rad)


def vector_between_points(point1, point2):
    # Subtract the coordinates of the first point from the second point
    vector = [p2 - p1 for p1, p2 in zip(point1, point2)]
    return vector


def second_point_of_vector(point1, vector, length=1):
    x1, y1 = point1
    return x1 + length * np.sin(vector), y1 + length * np.cos(vector)


def distance_between_points(point1, point2):
    return np.linalg.norm(np.array(point2) - np.array(point1))