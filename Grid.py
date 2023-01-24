from Settings import *
from kivy.graphics import Line, Color, Rectangle


class Grid:
    def __init__(self, win):
        self.win = win # where to be drawn
        self.re_adjust()

    def draw_grid(self):
        # will draw the grid
        i = 0
        d = self.d_to_next_x_tile

        with self.win.canvas:
            while i < self.win.height:
                Line(points=[i, 0, i, self.win.height], width=1)
                Line(points=[0, i, self.win.height, i], width=1)
                i += d

    def translate_to_coord(self, x, y):
        # will translate the absolute x and y position to its corresponding grid position (c_x, c_y)
        c_x = int(x // self.d_to_next_x_tile)
        c_y = int(y // self.d_to_next_y_tile)

        return [c_x, c_y]

    def translate_to_abs_pos(self, c_x, c_y):
        # will translate a given coordinate to its absolute position on the screen
        x = c_x * self.d_to_next_x_tile
        y = c_y * self.d_to_next_y_tile

        return [x, y]

    def fill_tile(self, x, y):
        # x and y corresponds to where the user right_clicked on the screen
        # function responsible for coloring a tile if it is left-clicked
        c_x, c_y = self.translate_to_coord(x, y)
        with self.win.canvas:
            Color(.2, .3, .4)
            if not self.is_colored(c_x, c_y):
                new_rect = Rectangle(pos=(self.translate_to_abs_pos(c_x, c_y)),
                                     size=(self.d_to_next_x_tile, self.d_to_next_y_tile))  # draws on the tile
                self.coordinates[c_y, c_x] = new_rect  # stores the rect

    def fill_borders(self):
        # fills the border of the grid with colored tiles
        border = [0, ROWS-1]
        border1 = [0, COLUMNS-1]
        with self.win.canvas:
            for a in border:
                for b in range(0, COLUMNS):
                    c_x, c_y = b, a
                    Color(.2, .3, .4)
                    new_rect = Rectangle(pos=(self.translate_to_abs_pos(c_x, c_y)),
                                         size=(self.d_to_next_x_tile, self.d_to_next_y_tile))  # draws on the tile
                    self.coordinates[c_y, c_x] = new_rect  # stores the rect

                for c in border1:
                    for d in range(0, ROWS):
                        c_x, c_y = c, d
                        Color(.2, .3, .4)
                        new_rect = Rectangle(pos=(self.translate_to_abs_pos(c_x, c_y)),
                                             size=(
                                             self.d_to_next_x_tile, self.d_to_next_y_tile))  # draws on the tile
                        self.coordinates[c_y, c_x] = new_rect  # stores the rect

    def clear_tile(self, x, y):
        # x and y corresponds to where the user right_clicked on the screen
        # function responsible for clearing a tile if it's right-clicked
        c_x, c_y = self.translate_to_coord(x, y)
        with self.win.canvas:
            if self.is_colored(c_x, c_y):
                self.win.canvas.remove(self.coordinates[c_y, c_x])  # clears the tile
                self.coordinates[c_y, c_x] = 0  # removes the rect on the self.coordinates atr

    def is_colored(self, c_x, c_y):
        # checks whether a tile is colored i.g. self.coordinates[c_y][c_x] holds a rectangle
        if self.coordinates[c_y, c_x] != 0:
            return True
        else:
            return False

    def re_adjust(self):
        self.d_to_next_x_tile = self.win.width / COLUMNS
        self.d_to_next_y_tile = self.win.height / ROWS
        self.coordinates = np.zeros((ROWS, COLUMNS),
                                    dtype=object)  # holds the value of each tile. Either holds a 0 or a Rectangle object

        self.draw_grid()
        self.fill_borders()