from typing import List
import numpy as np


class Point:
    __id = 0

    def __init__(self, x: int, y: int, id: str = None):
        self.x = x
        self.y = y
        if id is None:
            self.id = f"P{Point.__id}"
            Point.__id = Point.__id + 1
        else:
            self.id = id

    def get_coords(self):
        return f"x: {self.x}, y: {self.y}"

    def __repr__(self):
        return f"{self.id}"


def distance(a: Point, b: Point) -> float:
    return np.power(np.add(np.power(np.subtract(a.x, b.x), 2), np.power(np.subtract(a.y, b.y), 2)), 0.5)


def route_length(r: List[Point]) -> float:
    length = 0
    for i in range(1, len(r)):
        length = np.add(length, distance(r[i - 1], r[i]))
    return length


def generate_new_random_point(minimum_x: int, maximum_x: int, minimum_y: int, maximum_y: int, seed: int = None, set_seed: bool = True):
    """ Generate random point """
    if set_seed:
        np.random.seed(seed)
    return Point(np.random.randint(minimum_x, maximum_x + 1), np.random.randint(minimum_y, maximum_y + 1))


def generate_new_random_point_list(minimum_x: int, maximum_x: int, minimum_y: int, maximum_y: int, number: int, seed: int = None):
    """ Generates random points """
    point_list = []
    seed_not_set = True
    for _ in range(number):
        if seed_not_set:
            point_list.append(generate_new_random_point(minimum_x, maximum_x, minimum_y, maximum_y, seed))
            seed_not_set = False
        else:
            point_list.append(generate_new_random_point(minimum_x, maximum_x, minimum_y, maximum_y, set_seed=False))
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
