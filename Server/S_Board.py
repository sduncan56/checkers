__author__ = ''

import math

class Piece(object):
    def __init__(self, colour):
        self.colour = colour
        self.king = False
        self.taken = False

class Tile(object):
    def __init__(self, id, colour, x, y):
        self.id = id
        self.colour = colour
        self.piece = None
        self.x = x
        self.y = y


class S_Board(object):
    def __init__(self, size, player1, player2):
        self.size = size #number of squares on a side i.e 8

        self.createBoard(size)
        self.setPieces()

        self.lastActiveTile = None

        self.player1 = player1
        self.player2 = player2

        self.gameOver = False


    def createBoard(self, size):
        """
        Creates board representation
        :param size: size of one side - i.e. 8
        :return:
        """
        colour = 0

        self.tiles = []

        id = 0

        for x in range(0, self.size):
            self.tiles.append([])
            for y in range(0, self.size):
                self.tiles[x].append(Tile(id, colour, x, y))
                colour = self.swapColour(colour)
                id += 1
            colour = self.swapColour(colour)

    def setPieces(self):
        """
        places pieces on board
        :return:
        """
        #white up top, black at bottom

        whiteNo = 12

        for y in range(0, self.size):
            for x in range(0, self.size):
                if self.tiles[x][y].colour == 0:
                    self.tiles[x][y].piece = Piece(1)
                    whiteNo-=1
                    if whiteNo <= 0:
                        break

            if whiteNo <= 0:
                break

        blackNo = 12

        for y in range(self.size-1, -1, -1):
            for x in range(self.size-1, -1, -1):
                if self.tiles[x][y].colour == 0:
                    self.tiles[x][y].piece = Piece(0)
                    blackNo-=1
                    if blackNo <= 0:
                        break

            if blackNo <= 0:
                break



    def swapColour(self, colour):
        if colour == 0:
            colour = 1
        elif colour == 1:
            colour = 0

        return colour

    def networkData(self):
        """
        gathers all the board information in format that can be sent over network
        :return:
        """
        data = {}
        data['tiles'] = {}

        for row in self.tiles:
            for tile in row:
                data['tiles'][tile.id] = {}
                data['tiles'][tile.id]['colour'] = tile.colour


                if tile.piece != None:
                    data['tiles'][tile.id]['piece'] = {'colour':tile.piece.colour,
                                                       'king':tile.piece.king}

        return data

    def calcydir(self, colour):
        if colour == 0:
            return -1
        elif colour == 1:
            return 1

    def getPossibleMoves(self, colour):
        """
        Gets all possible moves that one side can make
        :param colour:
        :return:
        """
        possibleMoves = []
        for x in xrange(0, len(self.tiles)):
            for y in xrange(0, len(self.tiles[x])):
                tile = self.tiles[x][y]

                if not tile.piece:
                    continue

                if tile.piece.colour == colour:
                    #check tiles around the tile
                    for sx in range(-1, 2):
                        for sy in range(-1, 2):
                            if x+sx < 0 or x+sx >= len(self.tiles) or sx==0 or y+sy < 0 or y+sy >= len(self.tiles[x]) or sy==0:
                                continue


                            if self.checkMove(colour, self.tiles[x+sx][y+sy],tile, tile.piece):
                                possibleMoves.append(('move',self.tiles[x+sx][y+sy]))
                            if self.tiles[x+sx][y+sy].piece:
                                if self.tiles[x+sx][y+sy].piece.colour != colour:
                                    if x + sx + int(math.copysign(1, sx)) < 0 or x+ sx + int(math.copysign(1, sx)) >= len(self.tiles) or \
                                        y+sy + int(math.copysign(1,sy)) < 0 or y+sy + int(math.copysign(1,sy)) >= len(self.tiles[sx]):
                                        continue

                                    if self.checkTake(colour,
                                                   self.tiles[x + sx + int(math.copysign(1,sx))][y + sy + int(math.copysign(1,sy))],
                                                   tile, tile.piece):
                                        possibleMoves.append(('take',self.tiles[x + sx + int(math.copysign(sx, 1))][y + sy + int(math.copysign(sy, 1))]))
        return possibleMoves



    def checkDoubleTake(self, colour, tile):
        """
        Checks if a piece that has just taken can take another
        :param colour:
        :param tile:
        :return:
        """
        for sx in range(-1, 2):
            for sy in range(-1, 2):
                if tile.x+sx+ int(math.copysign(1,sx)) < 0 or tile.x+sx+ int(math.copysign(1,sx)) >= len(self.tiles) or sx==0 or\
                                        tile.y+sy+ int(math.copysign(1,sy)) < 0 or tile.y+sy+ int(math.copysign(1,sy)) >= len(self.tiles) or sy==0:
                    continue


                if self.checkTake(colour,
                        self.tiles[tile.x + sx + int(math.copysign(1,sx))][tile.y + sy + int(math.copysign(1,sy))],
                        tile, tile.piece):
                    return True
        return False


    def checkTake(self, colour, targetTile, selectedPieceTile, selectedPiece):
        """
        Checks if player is trying to/can take a piece
        :param colour:
        :param targetTile:
        :param selectedPieceTile:
        :param selectedPiece:
        :return:
        """
        if targetTile.piece:
            return False

        ydir = self.calcydir(colour)

        xdir = 0
        if targetTile.x > selectedPieceTile.x:
            xdir = 1
        else:
            xdir = -1

        if selectedPiece.king:
            if targetTile.y > selectedPieceTile.y:
                ydir = 1
            else:
                ydir = -1
            if targetTile.x == selectedPieceTile.x + 2*xdir:
                attackTile = self.tiles[selectedPieceTile.x + xdir][selectedPieceTile.y+ydir]
                if attackTile.piece and attackTile.piece.colour != selectedPiece.colour:
                    #attackTile.piece = None
                    return (selectedPieceTile.x + xdir, selectedPieceTile.y+ydir)

        elif targetTile.x == selectedPieceTile.x + 2*xdir and targetTile.y == selectedPieceTile.y + 2*ydir:
            attackTile = self.tiles[selectedPieceTile.x + xdir][selectedPieceTile.y+ydir]
            if attackTile.piece and attackTile.piece.colour != selectedPiece.colour:
                #attackTile.piece = None
                return (selectedPieceTile.x + xdir, selectedPieceTile.y+ydir)
        return False

    def checkMove(self, colour, targetTile, selectedPieceTile, selectedPiece):
        """
        checks if player can move piece to given position
        :param colour:
        :param targetTile:
        :param selectedPieceTile:
        :param selectedPiece:
        :return:
        """
        ydir = self.calcydir(colour)

        if targetTile.piece:
            return False

        if selectedPiece.king:
            if targetTile.x == selectedPieceTile.x + 1 or targetTile.x == selectedPieceTile.x - 1:
                return True

        if (targetTile.x == selectedPieceTile.x + 1 or targetTile.x == selectedPieceTile.x - 1) and \
                        targetTile.y == selectedPieceTile.y + 1*ydir:
            return True

        return False

    def checkKinging(self, colour, pieceTile):
        """
        Check if piece has reached the end of the board/should become a king
        :param colour:
        :param pieceTile:
        :return:
        """
        if colour == 0:
            if pieceTile.y == 0:
                pieceTile.piece.king = True
        elif colour == 1:
            if pieceTile.y == 7:
                pieceTile.piece.king = True

    def checkIfTakePossible(self, colour):
        """
        check if there are pieces that can be taken by any piece on one side
        :param colour:
        :return:
        """
        moves = self.getPossibleMoves(colour)

        for move in moves:
            if move[0] == 'take':
                return True
        return False


    def handleMovement(self, targetTile, selectedPieceTile, colour):
        """
        Main method for piece movement.
        :param targetTile:
        :param selectedPieceTile:
        :param colour:
        :return:
        """
        if not selectedPieceTile.piece:
            raise Exception

        selectedPiece = selectedPieceTile.piece

        if selectedPiece.king:
            pass

        #check for diagonal movement
        if self.checkMove(colour, targetTile, selectedPieceTile ,selectedPiece):
            if self.checkIfTakePossible(colour):
                return "musttake"

            targetTile.piece = selectedPiece
            selectedPieceTile.piece = None
            self.lastActiveTile = targetTile
            return "move"
        #check for taking

        a = self.checkTake(colour, targetTile, selectedPieceTile, selectedPiece)
        if a:
            targetTile.piece = selectedPiece
            selectedPieceTile.piece = None
            self.lastActiveTile = targetTile
            self.tiles[a[0]][a[1]].piece = None

            if self.checkDoubleTake(colour, targetTile):
                return "doubletake"

            return "take"


        return "invalid"

    def getTargetSelTiles(self, tileid, piecetileid):
        """
        returns tiles from the tileID integers passed in from the client
        :param tileid:
        :param piecetileid:
        :return:
        """
        selectedPieceTile = None
        targetTile = None
        for row in self.tiles:
            for tile in row:
                if tile.id == tileid:
                    targetTile = tile
                if tile.id == piecetileid:
                    selectedPieceTile = tile

        return (targetTile, selectedPieceTile)










