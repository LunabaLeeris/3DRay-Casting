from kivy.graphics import Color, Line
from Settings import *
import numpy as np


class Player:
    def __init__(self, win):
        self.win = win # Place where the player will be drawn
        self.s_point = None  # starting point of the ray
        self.cent_s = np.zeros(2)  # Center of self.s_point
        self.e_point = None  # end point of the ray
        self.cent_e = np.zeros(2)  # Center of self.e_point
        self.s_x = 0
        self.s_y = 0
        self.points_drawn = False

    def draw_points(self):
        if self.points_drawn:
            self.win.canvas.remove(self.s_point)
            self.win.canvas.remove(self.e_point)
            self.win.points_drawn = False

        with self.win.canvas:
            Color(1, 0, 0)
            self.s_point = Line(circle=(self.win.center_x - self.win.width, self.win.center_y, RADIUS), width=3)
            self.cent_s[0:2] = [self.win.center_x - self.win.width, self.win.center_y]  # adjusts the center of the circle
            Color(0, 1, 0)
            self.e_point = Line(circle=(self.win.center_x - self.win.width, self.win.center_y, RADIUS), width=3)
            self.cent_e[0:2] = [self.win.center_x - self.win.width, self.win.center_y]  # adjusts the center of the circle

    def move_e_point(self, me):
        x, y = me
        with self.win.canvas:
            Color(0, 1, 0)
            self.win.canvas.remove(self.e_point)  # deletes the e_points

            # adjusts the position of the e_point based on the position of the mouse
            self.e_point = Line(circle=(x, y, RADIUS), width=3)
            self.cent_e = (x, y)  # updates the center

    def move_s_point(self, dt):
        if self.s_x != 0 or self.s_y != 0:
            new_x = self.cent_s[0] + self.s_x * (dt * 60)
            new_y = self.cent_s[1] + self.s_y * (dt * 60)
            with self.win.canvas:
                Color(1, 0, 0)
                self.win.canvas.remove(self.s_point)  # deletes the s_point
                # adjusts the position of the s_point based on the amount of movement (x, y)
                self.s_point = Line(circle=(new_x, new_y, RADIUS), width=3)
                self.cent_s[0:2] = [new_x, new_y]  # updates the center

            if self.win.shoot:
                self.win.re_draw_rays()

    def re_adjust(self):
        self.draw_points()

