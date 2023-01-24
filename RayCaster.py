from Settings import *
from Player import Player
from Grid import Grid

import numpy as np
from kivy.graphics import Color, Line
from kivy.uix.relativelayout import RelativeLayout


class RayCast(RelativeLayout):
    # NOTE THAT GRID STARTS AT (0, 0) not (1, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player(self)
        self.grid = Grid(self)
        # RAY ATTRIBUTES
        self.shoot = False  # shoot a ray from point s to point e
        self.wall_hit = False  # holds the value whether the ray hits a wall
        # RUNNER FUNCTIONS
        self.grid.draw_grid()
        self.player.draw_points()

        self.ray = None  # single ray
        self.ray_drawn = False  # whether the single ray was drawn already
        self.beam_drawn = False  # whether the beam has been drawn already

        self.beam = False  #
        self.draw_beam = False  # used by the draw_rays thread to determine whether to draw the beam or not
        self.mouse_mode = True
        # For 3D conversion
        self.adjust_3D = False
        self.distances = np.array([])

    # ---------------------------- RAY HANDLING -----------------------------------------
    def draw_rays(self, dt):
        if self.draw_beam:
            theta = self.get_angle_on_the_screen()
            s_x, s_y = self.player.cent_s  # absolute x and y position of the starting point
            s_c_x, s_c_y = self.grid.translate_to_coord(s_x, s_y)  # tile position of the starting point

            if self.ray_drawn:
                self.canvas.remove(self.ray)
                self.ray_drawn = False

            self.distances = np.array([])
            self.canvas.remove_group('rays')
            self.beam_drawn = False

            with self.canvas:
                Color(1, 1, 0, .5)
                i = theta - FIELD_OF_VISION
                increment = FIELD_OF_VISION * 2 / NUM_OF_RAYS
                for _ in range(NUM_OF_RAYS):
                    w = self.shoot_ray(i, s_x, s_y, s_c_x, s_c_y)
                    x_1, y_1 = self.player.cent_s
                    x_2, y_2 = w[1]
                    Line(points=[x_1, y_1, x_2, y_2], width=1, group='rays')
                    self.distances = np.append(self.distances, w[0][2])
                    i += increment

            self.adjust_3D = True
            self.beam_drawn = True

            self.draw_beam = False

    def single_ray_cast(self):
        s_x, s_y = self.player.cent_s  # absolute x and y position of the starting point
        s_c_x, s_c_y = self.grid.translate_to_coord(s_x, s_y)  # tile position of the starting point

        # single ray cast
        w = self.shoot_ray(self.get_angle_on_the_screen(), s_x, s_y, s_c_x, s_c_y)
        if self.ray_drawn:
            self.canvas.remove(self.ray)
            self.ray_drawn = False

        if not w[0][0]:
            x_1, y_1 = s_x, s_y
            x_2, y_2 = self.player.cent_e
            with self.canvas:
                Color(1, 1, 0)
                self.ray = Line(points=[x_1, y_1, x_2, y_2], width=2, dash_offset=5, dash_length=10)
                self.ray_drawn = True
        else:
            x_1, y_1 = s_x, s_y
            x_2, y_2 = w[1]
            with self.canvas:
                Color(1, 1, 0)
                self.ray = Line(points=[x_1, y_1, x_2, y_2], width=2, dash_offset=5, dash_length=10)
                self.ray_drawn = True

    def complete_ray_cast(self):
        self.draw_beam = True

    def re_draw_rays(self):
        if not self.beam:
            self.single_ray_cast()
        else:
            self.complete_ray_cast()

    def get_angle_on_the_screen(self):
        # gets the angle of ray between the end point (green circle) and the starting point (red circle)
        a, o = self.player.cent_e - self.player.cent_s

        theta = PI / 2 if (a == 0 and o > 0) else (
            PI if (a == 0 and o < 0) else np.arctan(o / a))  # computes for the theta
        theta = abs(theta)
        # Translates the angle accordingly because the angle is in radians always
        if a < 0 and o > 0:
            theta = PI - theta
        elif o < 0 and a < 0:
            theta = PI + theta
        elif a > 0 and o < 0:
            theta = 2 * PI - theta

        return theta

    def shoot_ray(self, theta, s_x, s_y, s_c_x, s_c_y):
        # Casts a ray in a specific angle ( 0 - 360 degrees) relative to the horizon

        # angle between the end point and starting point
        sin = np.sin(theta)  # sin(theta)
        cos = np.cos(theta)  # cos(theta)

        d_n_t_x = abs(self.grid.d_to_next_x_tile / cos)  # distance to next tile by moving horizontally
        d_n_t_y = abs(self.grid.d_to_next_y_tile / sin)  # distance to next tile by moving vertically

        # d_h : total distance travelled of the ray by using horizontal movement on the tiles
        # d_v : total distance travelled of the ray by using vertical movement on the tiles
        t_h = []  # tile pos of intersection while moving horizontally on the tiles
        t_v = []  # tile pos of the intersection while moving vertically on the tiles
        p_i = []  # holds the absolute position of the intersection on the wall hit

        # get the initial d_h and initial d_v using d_x and d_y
        d_x = 0
        if cos > 0:
            d_x = self.grid.translate_to_abs_pos(s_c_x + 1, 0)[0] - s_x
            d_h = abs(d_x / cos)  # initial d_h
        elif cos < 0:
            d_x = s_x - self.grid.translate_to_abs_pos(s_c_x, 0)[0]
            d_h = abs(d_x / cos)  # initial d_h
        else:
            d_h = 0

        d_y = 0
        if sin > 0:
            d_y = self.grid.translate_to_abs_pos(0, s_c_y + 1)[1] - s_y
            d_v = abs(d_y / sin)  # initial d_y
        elif sin < 0:
            d_y = s_y - self.grid.translate_to_abs_pos(0, s_c_y)[1]
            d_v = abs(d_y / sin)  # initial d_y
        else:
            d_v = 0

        # Computes for the absolute position of the intersections
        x_i_h, y_i_h = self.get_abs(d_h, cos, sin)  # absolute position of the intersection while moving horizontally
        x_i_v, y_i_v = self.get_abs(d_v, cos, sin)  # absolute position of the intersection while moving vertically
        # adjusts the tile position
        t_h = self.grid.translate_to_coord(x_i_h, y_i_h)
        t_v = self.grid.translate_to_coord(x_i_v, y_i_v)

        # MAIN LOOP FOR THE RAY CASTING COMPUTATIONS
        # True if slope horizontally/vertically == 0 or ray already shat out

        h = True if cos == 0 else False
        v = True if sin == 0 else False
        # h and v will check whether the ray has shat out of the grid
        # wall_hit will tell whether a colored tile has been hit
        while not h or not v:
            while not h and (d_h <= d_v or sin == 0):
                # while the ray is not exceeding the grid and the d travelled while moving horizontally < d travelled while moving vertically
                c_x, c_y = t_h  # current x and y coordinate of the current position
                if self.grid.is_colored(c_x, c_y):  # if current tile position is colored
                    return [[True, t_h, d_h], (x_i_h,
                                               y_i_h)]  # returns the tile coordinates of the wall hit and the absolute position of the intersection
                # if not colored
                d_h += d_n_t_x
                x_i_h, y_i_h = self.get_abs(d_h, cos, sin)
                t_h = self.grid.translate_to_coord(x_i_h, y_i_h)

            while not v and (d_v <= d_h or cos == 0):
                # while the ray is not exceeding the grid and the d travelled while moving horizontally < d travelled while moving vertically
                c_x, c_y = t_v  # current x and y coordinate of the current position
                if self.grid.is_colored(c_x, c_y):  # if current tile position is colored
                    return [[True, t_v, d_v], (x_i_v,
                                               y_i_v)]  # returns the tile coordinates of the wall hit and the absolute position of the intersection

                d_v += d_n_t_y
                x_i_v, y_i_v = self.get_abs(d_v, cos, sin)
                t_v = self.grid.translate_to_coord(x_i_v, y_i_v)

        return [[False, t_h, d_h], (x_i_h, y_i_h)]

    def get_abs(self, d, cos, sin):
        # Returns the absolute position of a point with distance d, angle theta Relative to the s_point
        s_x, s_y = self.player.cent_s  # abs position of s_point
        # NOTE: We must add a tiny amount because computers cannot handle floating points well
        # this is to ensure that our computation will be as correct as it can get

        d_x = (d * cos + .0001) if cos > 0 else (
                d * cos - .0001)  # gets the horizontal distance between s_point and end_point
        d_y = (d * sin + .0001) if sin > 0 else (
                d * sin - .0001)  # # gets the vertical distance between s_point and end_point

        x = s_x + d_x  # gets the absolute y position of the end point
        y = s_y + d_y  # gets the absolute y position of the end point

        return x, y

    # ------------------------------ EVENT FUNCTIONS -----------------------------------------

    def on_size(self, *args):
        # will re_draw the grid incase the screen is resized

        with self.canvas:
            self.canvas.clear()

        self.grid.re_adjust()
        self.player.draw_points()