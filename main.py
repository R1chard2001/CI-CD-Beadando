import time
from kivy.clock import mainthread
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from src.point import generate_new_random_point_list, generate_random_route
from src.point import route_length
from kivy.app import App
from kivy.lang import Builder
from kivy.graphics import Rectangle, Color, Line
import threading
import numpy as np
from kivy.core.window import Window


class MainWindow(BoxLayout):
    pass


class TSPApp(App):
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
    def stop_app(*args):
        TSPApp.stopping = True

    def bruteforce_solving(self, points, starting_point: int = 0, current_route=None, sleep: float = 0, starter=True):
        if len(points) < 2:
            self.draw_points(points)
            return
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
            self.draw_routes(current_route, a=0.5)
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
                result = self.bruteforce_solving(points, starting_point, current_route, sleep, False)
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
        TSPApp.generation = 0
        route = generate_random_route(points)
        TSPApp.best_route = route
        TSPApp.best_route_length = route_length(route)
        while not TSPApp.stopping:
            i = 0
            while i < len(route) - 1 and not TSPApp.stopping:
                j = 0
                while j < len(route) - 1 and not TSPApp.stopping:
                    if i != j:

                        copy_of_route = route[:-1].copy()
                        new_route = []
                        index = 0
                        if j < i:
                            b = j
                            e = i
                        else:
                            e = j
                            b = i
                        while index < b:
                            new_route.append(copy_of_route[index])
                            index += 1
                        index = e
                        while index >= b:
                            new_route.append(copy_of_route[index])
                            index -= 1
                        index = e + 1
                        while index < len(copy_of_route):
                            new_route.append(copy_of_route[index])
                            index += 1
                        new_route.append(new_route[0])
                        new_route_length = route_length(new_route)
                        if new_route_length < route_length(route) or np.random.random() < mutation_chance:
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
                            self.draw_routes(route, a=0.5)
                            self.draw_points(route[:-1])
                            self.draw_best_route_length()
                            time.sleep(sleep)
                        if np.random.random() < reset_chance:
                            route = TSPApp.best_route.copy()
                            self.main_window.ids.last_action.text = "Route reseted"
                            time.sleep(sleep)
                    j = j + 1
                i = i + 1
        TSPApp.can_run = True

    @mainthread
    def clear_canvas(self):
        time.sleep(0.008)
        self.main_window.ids.canvas_layout.canvas.clear()

    @mainthread
    def print_new_point(self, x: int = 0, y: int = 0, size=13, r=0.0, g=0.1, b=0.0, a=1.0):
        center_x = int(self.main_window.ids.canvas_layout.size[0] / 2 - size / 2)
        center_y = int(self.main_window.ids.canvas_layout.size[1] / 2 - size / 2)
        with self.main_window.ids.canvas_layout.canvas:
            Rectangle(
                pos=(center_x + x, center_y + y),
                size=(size, size),
                color=Color(r, g, b, a)
            )
            Color(0, 0, 0, 1)

    @mainthread
    def draw_points(self, points, size=13, r=0.0, g=0.7, b=0.1, a=1.0):
        for p in points:
            self.print_new_point(p.x, p.y, size, r, g, b, a)
    @mainthread
    def draw_routes(self, points, width=1.3, r=0.0, g=0.25, b=1.0, a=1.0):
        coords = []
        center_x = int(self.main_window.ids.canvas_layout.size[0] / 2)
        center_y = int(self.main_window.ids.canvas_layout.size[1] / 2)
        for p in points:
            coords.append(center_x + p.x)
            coords.append(center_y + p.y)
        with self.main_window.ids.canvas_layout.canvas:
            Line(
                points=coords,
                width=width,
                color=Color(r, g, b, a)
            )
            Color(0, 0, 0, 1)

    def draw_best_route(self, clear_canvas=False, draw_points=False):
        if clear_canvas:
            self.clear_canvas()
        self.draw_routes(TSPApp.best_route, r=0.8, g=0.5, b=0)
        if draw_points:
            self.draw_points(TSPApp.best_route)

    def start_solving(self):
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
                        text="[color=ff0000]Mutation chance must be a number between 0 and 1![/color]",
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

            x = int(self.main_window.ids.canvas_layout.size[0] / 2) - 20
            y = int(self.main_window.ids.canvas_layout.size[1] / 2) - 20
            if self.main_window.ids.keep_points.state == "normal" or TSPApp.points is None:
                TSPApp.points = generate_new_random_point_list(-x, x, -y, y - 30, TSPApp.number_of_points)
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
        try:
            number = float(self.main_window.ids.sleep_interval_text_input.text)
            if number <= 0:
                return False
            TSPApp.sleep_interval = number
            return True
        except:
            return False

    def set_number_of_points(self):
        try:
            number = int(self.main_window.ids.number_of_points_text_input.text)
            if number <= 0:
                return False
            TSPApp.number_of_points = number
            return True
        except:
            return False

    def set_method_bruteforce(self):
        self.main_window.ids.bruteforce_method.state = "down"
        TSPApp.method_is_bruteforce = True
        pass

    def set_method_genetic(self):
        self.main_window.ids.number_of_points_text_input
        self.main_window.ids.genetic_method.state = "down"
        TSPApp.method_is_bruteforce = False
        pass

    def set_mutation_chance(self):
        try:
            number = float(self.main_window.ids.mutation_chance_text_input.text)
            if number < 0 or number > 1:
                return False
            TSPApp.mutation_chance = number
            return True
        except:
            return False

    def set_reset_chance(self):
        try:
            number = float(self.main_window.ids.reset_chance_text_input.text)
            if number < 0 or number > 1:
                return False
            TSPApp.reset_chance = number
            return True
        except:
            return False

    def draw_best_route_length(self):
        self.main_window.ids.shortest_route_length_label.text = "Shortest route length: {:.5f}".format(TSPApp.best_route_length)



Builder.load_file("kv_files/tsp_visualisation.kv")
app = TSPApp()
app.title = "Traveling salesman problem visualisation"
app.run()
