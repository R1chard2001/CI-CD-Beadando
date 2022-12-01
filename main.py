""" Main module """
import time
import threading
from kivy.clock import mainthread
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.app import App
from kivy.lang import Builder
from kivy.graphics import Rectangle, Color, Line
from kivy.core.window import Window
import numpy as np
from src.point import route_length
from src.point import generate_new_random_point_list, generate_random_route


class MainWindow(BoxLayout):
    """ Base window class """


class TSPApp(App):
    """ App class """
    sleep_interval = 0.05
    number_of_points = 7
    can_run = True
    main_window = None
    thread = None
    stopping = False
    best_route = None
    best_route_length = None
    method_is_bruteforce = True
    generation = 0
    mutation_chance = 0.025
    reset_chance = 0.035
    points = None

    def build(self):
        self.main_window = MainWindow()
        Window.bind(on_request_close=self.stop_app)
        Window.size = (1500, 850)
        return self.main_window

    @staticmethod
    def stop_app():
        """ stops app """
        TSPApp.stopping = True

    def bruteforce_solving(self, points, starting_point: int = 0,
            current_route=None, sleep: float = 0, starter=True):
        """ Bruteforce solver """
        if len(points) < 2:
            self.draw_points(points)
            return None
        if current_route is None:
            current_route = [points[starting_point]]
        if len(current_route) == len(points):
            current_route.append(points[starting_point])
            cr_length = route_length(current_route)
            if TSPApp.best_route_length is None or TSPApp.best_route_length > cr_length:
                TSPApp.best_route = current_route
                TSPApp.best_route_length = cr_length
            self.clear_canvas()
            self.draw_best_route()
            self.draw_routes(current_route, alpha=0.5)
            self.draw_points(current_route[:-1])
            self.draw_best_route_length()
            time.sleep(sleep)
            return current_route, cr_length
        min_route = []
        min_distance = -1
        current_sub_route = current_route.copy()
        for point in points:
            if point not in current_route:
                current_route = current_sub_route.copy()
                current_route.append(point)
                if TSPApp.stopping:
                    return False
                result = self.bruteforce_solving(points,
                    starting_point, current_route, sleep, False)
                if result is False:
                    if starter:
                        TSPApp.can_run = True
                    return False
                if min_distance == -1 or min_distance > result[1]:
                    min_route = result[0]
                    min_distance = result[1]
        if starter:
            self.clear_canvas()
            self.draw_best_route(draw_points=True)
            self.draw_best_route_length()
            TSPApp.can_run = True
        return min_route, min_distance

    def genetic_solving(self, points, mutation_chance=0.05, reset_chance=0.1, sleep=0.01):
        """ Genetic solver """
        TSPApp.generation = 0
        route = generate_random_route(points)
        TSPApp.best_route = route
        TSPApp.best_route_length = route_length(route)
        while not TSPApp.stopping:
            var_i = 0
            while var_i < len(route) - 1 and not TSPApp.stopping:
                var_j = 0
                while var_j < len(route) - 1 and not TSPApp.stopping:
                    if var_i != var_j:

                        copy_of_route = route[:-1].copy()
                        new_route = []
                        index = 0
                        if var_j < var_i:
                            var_b = var_j
                            var_e = var_i
                        else:
                            var_e = var_j
                            var_b = var_i
                        while index < var_b:
                            new_route.append(copy_of_route[index])
                            index += 1
                        index = var_e
                        while index >= var_b:
                            new_route.append(copy_of_route[index])
                            index -= 1
                        index = var_e + 1
                        while index < len(copy_of_route):
                            new_route.append(copy_of_route[index])
                            index += 1
                        new_route.append(new_route[0])
                        new_route_length = route_length(new_route)
                        if new_route_length < route_length(route) or\
                                np.random.random() < mutation_chance:
                            if new_route_length < route_length(route):
                                self.main_window.ids.last_action.text = "New shortest route"
                            else:
                                self.main_window.ids.last_action.text = "Mutation"
                            route = new_route
                            if new_route_length < TSPApp.best_route_length:
                                TSPApp.best_route_length = new_route_length
                                TSPApp.best_route = route
                            TSPApp.generation += 1
                            self.clear_canvas()
                            self.draw_best_route()
                            self.draw_routes(route, alpha=0.5)
                            self.draw_points(route[:-1])
                            self.draw_best_route_length()
                            time.sleep(sleep)
                        if np.random.random() < reset_chance:
                            route = TSPApp.best_route.copy()
                            self.main_window.ids.last_action.text = "Route reseted"
                            time.sleep(sleep)
                    var_j = var_j + 1
                var_i = var_i + 1
        TSPApp.can_run = True

    @mainthread
    def clear_canvas(self):
        """ Clears canvas """
        time.sleep(0.008)
        self.main_window.ids.canvas_layout.canvas.clear()

    @mainthread
    def print_new_point(self, var_x: int = 0, var_y: int = 0,
            size=13, red=0.0, green=0.1, blue=0.0, alpha=1.0):
        """ draws a single point """
        center_x = int(self.main_window.ids.canvas_layout.size[0] / 2 - size / 2)
        center_y = int(self.main_window.ids.canvas_layout.size[1] / 2 - size / 2)
        with self.main_window.ids.canvas_layout.canvas:
            Rectangle(
                pos=(center_x + var_x, center_y + var_y),
                size=(size, size),
                color=Color(red, green, blue, alpha)
            )
            Color(0, 0, 0, 1)

    @mainthread
    def draw_points(self, points, size=13, red=0.0, green=0.7, blue=0.1, alpha=1.0):
        """ draws points """
        for point in points:
            self.print_new_point(point.var_x, point.var_y, size, red, green, blue, alpha)

    @mainthread
    def draw_routes(self, points, width=1.3, red=0.0, green=0.25, blue=1.0, alpha=1.0):
        """ draws route """
        coords = []
        center_x = int(self.main_window.ids.canvas_layout.size[0] / 2)
        center_y = int(self.main_window.ids.canvas_layout.size[1] / 2)
        for point in points:
            coords.append(center_x + point.var_x)
            coords.append(center_y + point.var_y)
        with self.main_window.ids.canvas_layout.canvas:
            Line(
                points=coords,
                width=width,
                color=Color(red, green, blue, alpha)
            )
            Color(0, 0, 0, 1)

    def draw_best_route(self, clear_canvas=False, draw_points=False):
        """ Draws best route to canvas """
        if clear_canvas:
            self.clear_canvas()
        self.draw_routes(TSPApp.best_route, red=0.8, green=0.5, blue=0)
        if draw_points:
            self.draw_points(TSPApp.best_route)

    def start_solving(self):
        """ Starts solving """
        if TSPApp.can_run:
            self.main_window.ids.canvas_layout.canvas.clear()
            if not self.set_sleep_interval():
                self.main_window.ids.shortest_route_length_label.text = ""
                with self.main_window.ids.canvas_layout.canvas:
                    Label(
                        markup=True,
                        text="[color=ff0000]Sleep interval must be a positive number![/color]",
                        pos=(
                            self.main_window.ids.canvas_layout.size[0] / 2 - 160,
                            self.main_window.ids.canvas_layout.size[1] - 40),
                        size=(330, 40),
                        font_size=20
                    )
                return
            if not self.set_number_of_points():
                self.main_window.ids.shortest_route_length_label.text = ""
                with self.main_window.ids.canvas_layout.canvas:
                    Label(
                        markup=True,
                        text="[color=ff0000]Number of points must be a positive number![/color]",
                        pos=(
                            self.main_window.ids.canvas_layout.size[0] / 2 - 160,
                            self.main_window.ids.canvas_layout.size[1] - 40),
                        size=(335, 40),
                        font_size=20,

                    )
                return
            if not self.set_mutation_chance():
                self.main_window.ids.shortest_route_length_label.text = ""
                with self.main_window.ids.canvas_layout.canvas:
                    Label(
                        markup=True,
                        text=
                        "[color=ff0000]Mutation chance must be a number between 0 and 1![/color]",
                        pos=(
                            self.main_window.ids.canvas_layout.size[0] / 2 - 162,
                            self.main_window.ids.canvas_layout.size[1] - 40),
                        size=(335, 40),
                        font_size=20,

                    )
                return
            if not self.set_reset_chance():
                self.main_window.ids.shortest_route_length_label.text = ""
                with self.main_window.ids.canvas_layout.canvas:
                    Label(
                        markup=True,
                        text="[color=ff0000]Reset chance must be a number between 0 and 1![/color]",
                        pos=(
                            self.main_window.ids.canvas_layout.size[0] / 2 - 162,
                            self.main_window.ids.canvas_layout.size[1] - 40),
                        size=(335, 40),
                        font_size=20,

                    )
                return
            TSPApp.stopping = False
            TSPApp.can_run = False
            TSPApp.best_route = None
            TSPApp.best_route_length = None

            var_x = int(self.main_window.ids.canvas_layout.size[0] / 2) - 20
            var_y = int(self.main_window.ids.canvas_layout.size[1] / 2) - 20
            if self.main_window.ids.keep_points.state == "normal" or TSPApp.points is None:
                TSPApp.points = generate_new_random_point_list(-var_x,
                    var_x, -var_y, var_y - 30, TSPApp.number_of_points)
            if TSPApp.method_is_bruteforce:
                TSPApp.thread = threading.Thread(
                    target=(lambda: self.bruteforce_solving(
                        TSPApp.points,
                        sleep=TSPApp.sleep_interval
                    ))
                )
            else:
                TSPApp.thread = threading.Thread(
                    target=(lambda: self.genetic_solving(
                        TSPApp.points,
                        sleep=TSPApp.sleep_interval,
                        mutation_chance=TSPApp.mutation_chance,
                        reset_chance=TSPApp.reset_chance
                    ))
                )
            TSPApp.thread.start()

    def stop_solving(self):
        """ Stops the solving thread """
        TSPApp.stopping = True
        while TSPApp.can_run is False:
            pass
        if TSPApp.best_route is not None:
            self.clear_canvas()
            self.draw_best_route(draw_points=True)
            self.draw_best_route_length()
            TSPApp.best_route = None
            TSPApp.best_route_length = None
        self.main_window.ids.last_action.text = ""

    def set_sleep_interval(self):
        """ Sets sleep interval """
        try:
            number = float(self.main_window.ids.sleep_interval_text_input.text)
            if number <= 0:
                return False
            TSPApp.sleep_interval = number
            return True
        except:
            return False

    def set_number_of_points(self):
        """ Sets number of points """
        try:
            number = int(self.main_window.ids.number_of_points_text_input.text)
            if number <= 0:
                return False
            TSPApp.number_of_points = number
            return True
        except:
            return False

    def set_method_bruteforce(self):
        """ Sets button state """
        self.main_window.ids.bruteforce_method.state = "down"
        TSPApp.method_is_bruteforce = True

    def set_method_genetic(self):
        """ Sets button state """
        self.main_window.ids.genetic_method.state = "down"
        TSPApp.method_is_bruteforce = False

    def set_mutation_chance(self):
        """ Sets mutation chance """
        try:
            number = float(self.main_window.ids.mutation_chance_text_input.text)
            if number < 0 or number > 1:
                return False
            TSPApp.mutation_chance = number
            return True
        except:
            return False

    def set_reset_chance(self):
        """ Sets reset chance """
        try:
            number = float(self.main_window.ids.reset_chance_text_input.text)
            if number < 0 or number > 1:
                return False
            TSPApp.reset_chance = number
            return True
        except:
            return False

    def draw_best_route_length(self):
        """ Changes best route label """
        self.main_window.ids.shortest_route_length_label.text =\
            "Shortest route length: {:.5f}".format(TSPApp.best_route_length)


Builder.load_file("kv_files/tsp_visualisation.kv")
app = TSPApp()
app.title = "Traveling salesman problem visualisation"
try:
    app.run()
except TypeError:
    pass
