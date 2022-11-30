""" Point module """
from typing import List
import numpy as np


class Point:
    """ Pooint class """
    __id = 0

    def __init__(self, var_x: int, var_y: int, str_id: str = None):
        self.var_x = var_x
        self.var_y = var_y
        if str_id is None:
            self.str_id = f"P{Point.__id}"
            Point.__id = Point.__id + 1
        else:
            self.str_id = str_id

    def get_coords(self):
        """ prints out coordinates """
        return f"x: {self.var_x}, y: {self.var_y}"

    def __repr__(self):
        return f"{self.str_id}"


def distance(point_a: Point, point_b: Point) -> float:
    """ Gets distance between points """
    return np.power(np.add(np.power(np.subtract(point_a.var_x, point_b.var_x), 2),
                    np.power(np.subtract(point_a.var_y, point_b.var_y), 2)), 0.5)


def route_length(route: List[Point]) -> float:
    """ Gets route length """
    length = 0
    for i in range(1, len(route)):
        length = np.add(length, distance(route[i - 1], route[i]))
    return length


def generate_new_random_point(minimum_x: int, maximum_x: int,
        minimum_y: int, maximum_y: int, seed: int = None, set_seed: bool = True):
    """ Generate random point """
    if set_seed:
        np.random.seed(seed)
    return Point(np.random.randint(minimum_x, maximum_x + 1),
                 np.random.randint(minimum_y, maximum_y + 1))


def generate_new_random_point_list(minimum_x: int, maximum_x: int,
        minimum_y: int, maximum_y: int, number: int, seed: int = None):
    """ Generates random points """
    point_list = []
    seed_not_set = True
    for _ in range(number):
        if seed_not_set:
            point_list.append(generate_new_random_point(minimum_x,
                maximum_x, minimum_y, maximum_y, seed))
            seed_not_set = False
        else:
            point_list.append(generate_new_random_point(minimum_x,
                maximum_x, minimum_y, maximum_y, set_seed=False))
    return point_list


def generate_random_route(points: List[Point], seed: int = None, set_seed: bool = True):
    """ Generates random route """
    if set_seed:
        np.random.seed(seed)
    var_n = len(points)
    index_list = []
    while len(index_list) < var_n:
        rnd = np.random.randint(0, var_n)
        if rnd not in index_list:
            index_list.append(rnd)
    route = []
    for i in index_list:
        route.append(points[i])
    route.append(route[0])
    return route
