__author__ = ''

import pygame

class Piece(pygame.sprite.Sprite):
    def __init__(self, colour, king, radius, x, y, squareSize):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((squareSize, squareSize))
        self.rect = self.image.get_rect()


        self.image.fill((255,0,255))
        self.image.set_colorkey((255,0,255))


        self.rect.x = x
        self.rect.y = y

        self.colour = colour
        self.king = king
        self.radius = radius
        self.squareSize = squareSize
        self.selected = False

        self.colours = {0:0x663333, 1:0xffffff, 2:0xff4400, 3:0xFFD700}

        pygame.draw.circle(self.image, self.colours[self.colour], (squareSize/2, squareSize/2), self.radius)

        if self.king:
            pygame.draw.circle(self.image, self.colours[3], (squareSize/2, squareSize/2), self.radius/2)


    def update(self):
        pass


    def select(self):
        """
        when selected, draw orange circle
        :return:
        """
        pygame.draw.circle(self.image, self.colours[2], (self.squareSize/2, self.squareSize/2), self.radius)
        self.selected = True

    def deselect(self):
        """
        when unselected, back to normal colour
        :return:
        """
        pygame.draw.circle(self.image, self.colours[self.colour], (self.squareSize/2, self.squareSize/2), self.radius)
        self.selected = False




class Tile(object):
    def __init__(self, id, colour, pos, squareSize):
        self.id = id
        self.colour = colour
        self.piece = None


        self.rect = pygame.Rect(pos[0], pos[1], squareSize, squareSize)

class Board(object):
    def __init__(self, squareSize, boardSize, tiles, pos):
        self.squareSize = squareSize
        self.boardSize = boardSize
        self.tiles = tiles
        self.pos = pos

        self.colours = {0:0x111111, 1:0xffffff, 2:0x444444}

    def swapColour(self, colour):
        if colour == 0:
            colour = 1
        elif colour == 1:
            colour = 0

        return colour


    def drawBoard(self, surface):
        """
        draws tiles
        :param surface: pygame surface
        :return:
        """
        for x in xrange(0, self.boardSize):
            for y in xrange(0, self.boardSize):
                pygame.draw.rect(surface, self.colours[self.tiles[x][y].colour], self.tiles[x][y].rect)

        pygame.draw.rect(surface, 0x00ffff, pygame.Rect(self.pos[0], self.pos[1], self.boardSize*self.squareSize,
                                                        self.boardSize*self.squareSize), 2)


    def getTileAt(self, pos, boardOffset):
        """
        from mouse/screen coords, returns tile from the board
        :param pos:
        :param boardOffset:
        :return:
        """
        x = int((pos[0]-boardOffset[0])/self.squareSize)
        y = int((pos[1]-boardOffset[1])/self.squareSize)

        if x < 0 or x >= len(self.tiles) or y < 0 or y >= len(self.tiles):
            return False

        return self.tiles[x][y]