from Settings import *
import numpy as np
from kivy.graphics import Color, Line, Rectangle
from kivy.properties import Clock
from kivy.uix.relativelayout import RelativeLayout


class ScreenView(RelativeLayout):
    def __init__(self, ray_cast, **kwargs):
        super().__init__(**kwargs)
        self.ray_cast = ray_cast

        Clock.schedule_interval(self.draw_3D, 1 / 60)

    def draw_3D(self, dt):
        if self.ray_cast.adjust_3D:
            self.canvas.clear()
            self.draw_floor()
            sh_half = self.height / 2

            partial_theta = PI / 2 - FIELD_OF_VISION
            increment = self.width / NUM_OF_RAYS
            angle_increment = FIELD_OF_VISION * 2 / NUM_OF_RAYS
            r = 0  # rays traced
            x = 0  # scale of screen

            with self.canvas:

                for d in reversed(self.ray_cast.distances):
                    theta = partial_theta + angle_increment * r
                    c = .6 - ((d / (POVD * .8)) ** 2)*.7
                    d *= np.sin(theta)
                    Color(c, c, 0)
                    h = SCALING_FACTOR / (d + .0001)
                    y = sh_half - (h / 2)
                    Line(points=[x, y, x, y + h], width=WALL_WIDTH)
                    x += increment
                    r += 1
                    Color(1, 1, 1)

            self.ray_cast.adjust_3D = False

    def draw_floor(self):
        with self.canvas:
            height = (self.height/2)/FLOOR_SHADES
            for i in range(FLOOR_SHADES):
                c = .7 - (i/50)*.9
                Color(c, c, 0)
                Rectangle(pos=(0, height*i), size=(self.width, height))

