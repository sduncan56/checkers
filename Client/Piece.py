__author__ = ''

import pygame

class Piece(pygame.sprite):
    def __init__(self, squareSize, side, pos):
        pygame.sprite.Sprite.__init__(self)

        self.side = side #0 is black, 1 is white

        self.colour = 0x00ff00
        if side == 0:
            self.colour = 0x000000
        elif side == 1:
            self.colour = 0xffffff

        self.radius = squareSize/2

        self.x = pos[0]
        self.y = pos[1]


        self.image = pygame.Surface((squareSize, squareSize))
        pygame.draw.circle(self.image, self.colour, (int(self.x), int(self.y)), self.radius, 0)