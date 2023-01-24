from kivy.properties import Clock
from Settings import *
from RayCaster import RayCast
from ScreenView import ScreenView
from kivy import Config
from kivy.uix.boxlayout import BoxLayout

Config.set('graphics', 'width', WIDTH)
Config.set('graphics', 'height', HEIGHT)
Config.set('graphics', 'resizable', RESIZABLE)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.core.window import Window


# CONTROLS:
# W A S D = PLAYER MOVEMENT
# RIGHT-CLICK = TO COLOR A TILE
# LEFT_CLICK = CLEAR A TILE
# SPACE = SHOOT THE RAY (shoots a single ray)
# ENTER = SHOOT RAYS (render visual on left-screen)
# TAB = DESTROY THE FIRST COLORED TILE HIT BY THE RAY

# NOTES:
# NO COLLISION WAS IMPLEMENTED SO BE CAREFUL OF PASSING OUT OF THE MAP
# PRESS FIRST SPACE TO SHOOT THE RAY BEFORE PRESSING ENTER TO SHOW VISUAL ON LEFT_SCREEN
# ADJUST THE GRID SIZE ON self.grid_dimensions

class Main(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # CLASSES
        self.ray_cast = RayCast()
        self.player = self.ray_cast.player
        self.grid = self.ray_cast.grid
        self.screen_view = ScreenView(self.ray_cast)
        # ADD THE COMPONENTS
        self.add_components()
        # MOUSE LISTENER
        self.mouse = Window.bind(mouse_pos=self.mouse_pos)
        # KEYBOARD LISTENER
        self.keyboard = Window.request_keyboard(self.on_keyboard_closed, self)
        self.keyboard.bind(on_key_down=self.on_keyboard_down)
        self.keyboard.bind(on_key_up=self.on_keyboard_up)
        # THREADS
        Clock.schedule_interval(self.player.move_s_point, 1 / MOVE_S_P_FPS)
        Clock.schedule_interval(self.ray_cast.draw_rays, 1 / RAYS_DRAWING_FPS)

    def add_components(self):
        self.add_widget(self.screen_view)
        self.add_widget(self.ray_cast)

    # FOR KEY BOARD/MOUSE EVENTS

    def on_touch_down(self, touch):
        x, y = touch.pos
        if touch.button == "left":
            # if user left-clicked
            self.grid.fill_tile(x, y)
        elif touch.button == "right":
            # if user right-clicked
            self.grid.clear_tile(x, y)

    def on_touch_move(self, touch):
        # if user presses on the screen while moving the mouse
        x, y = touch.pos
        if touch.button == "left":
            # if user left-clicked
            self.grid.fill_tile(x, y)
        elif touch.button == "right":
            # if user right-clicked
            self.grid.clear_tile(x, y)

    def mouse_pos(self, etype, me):
        if self.ray_cast.mouse_mode:
            self.player.move_e_point(me)
            if self.ray_cast.shoot:
                self.ray_cast.re_draw_rays()

    def on_keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self.on_keyboard_down)
        self.keyboard.unbind(on_key_up=self.on_keyboard_up)
        self.keyboard = None

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):  # velocity
        movement_dict = {"w": (0, VELOCITY), "a": (-VELOCITY, 0), "s": (0, -VELOCITY), "d": (VELOCITY, 0)}
        if keycode[1] in movement_dict:
            self.player.s_x, self.player.s_y = movement_dict[keycode[1]]

        if keycode[1] == "spacebar":
            self.ray_cast.shoot = not self.ray_cast.shoot
            if not self.ray_cast.shoot:
                self.ray_cast.canvas.remove(self.ray_cast.ray)
        if keycode[1] == "tab":
            s_x, s_y = self.player.cent_s  # absolute x and y position of the starting point
            s_c_x, s_c_y = self.grid.translate_to_coord(s_x, s_y)  # tile position of the starting point

            w = self.ray_cast.shoot_ray(self.ray_cast.get_angle_on_the_screen(), s_x, s_y, s_c_x, s_c_y)
            if not w[0][0]:
                print("no wall was hit")
            else:
                x, y = w[0][1]
                self.ray_cast.canvas.remove(self.grid.coordinates[y][x])
                self.grid.coordinates[y][x] = 0

        if keycode[1] == "enter":
            self.ray_cast.beam = not self.ray_cast.beam
            if self.ray_cast.beam_drawn:
                self.ray_cast.canvas.remove_group('rays')

    def on_keyboard_up(self, keyboard, keycode):
        self.player.s_x, self.player.s_y = 0, 0


class RC(App):
    def build(self):
        return Main()


if __name__ == "__main__":
    RC().run()
