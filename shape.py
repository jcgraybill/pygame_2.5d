import pygame

class Shape:
    def __init__(self, row):
        self.walls = list()
        for i, point in enumerate(row.split(';')):
            if i == 0:
                self.color = pygame.Color(point)
            else:
                x, y = point.split(',')
                self.walls.append((int(x),int(y)))

    def __str__(self):
        return("color: " + str(self.color.i1i2i3) + " points: " + str(self.walls))

class Wall:
    def __init__(self):
        return