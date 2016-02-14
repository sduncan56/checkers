__author__ = ''

import math

import pygame
from pgu import gui


from State import State
from Board import Board, Tile, Piece
from Contacts import ContactsList

class PlayState(State):
    def __init__(self):
        super(PlayState, self).__init__()
        self.board = None #Board(40, 8, (50, 50))

        #self.addSendItem({'action':'playstart', 'start':True})
        self.addSendItem({'action':'getname'})

        self.squareSize = 40
        self.boardPosX = 50
        self.boardPosY = 100

        self.pieceRadius = 18

        self.pieces = pygame.sprite.Group()
        self.p = []

        self.selectedPiece = None
        self.targetTile = None

        self.colour = -1

        self.boardSize = 0

        #store gui elements so we can remove them later
        #should probably make a subclass of container and write a proper removeall method instead of this
        self.prechallengeGUI = []
        self.challengeGUI = []
        self.winGUI = []
        self.recordsGUI = []
        self.chatGUI = []

        self.inGame = False
        self.myTurn = False

        self.proposeMatchWith = None

        self.bgc = 0x000000
        self.txtColour = (255,255,255,255)

        #starting points for the challenge GUI
        self.challengeGUIsx = 100
        self.challengeGUIsy = 200

        self.inGameMsgLbl = None
        self.whoseTurnLbl = None

        self.forceSelectedPiece = False

        self.displayBar = None

        self.teamLabel = None


    def initGUI(self, app):
        """
        adds the contact list and permanent GUI stuff
        :param app:
        :return: container of GUI items
        """
        self.contactslist = ContactsList()
        cont = self.contactslist.makeList()


        self.nameTxt = gui.TextArea("", 200, 20)
        self.nameTxt.editable = False
        cont.add(self.nameTxt, 200, 0)

        self.addGUIItem(cont)

        self.addSendItem({'action':'getcontacts'})
        self.cont = cont

        showRecordBtn = gui.Button("Show Record")
        showRecordBtn.connect(gui.CLICK, self.reqRecord)

        cont.add(showRecordBtn, 600, 550)

        return cont

        #app.add(self.contactslist)


    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONUP and self.myTurn:
            pos = pygame.mouse.get_pos()

            selected = False
            for piece in self.pieces:
                #if we're double jumping, don't let other pieces be selected
                if self.forceSelectedPiece:
                    break
                #if mouse pointer is inside piece and it's our piece
                if piece.rect.collidepoint(pos[0], pos[1]) and piece.colour == self.colour:

                    if self.selectedPiece:
                        self.selectedPiece.deselect()
                    piece.select()
                    self.selectedPiece = piece
                    selected = True


            #If we weren't selecting a piece but rather clicking on a tile to move to
            #or, if a double-jump is in progress and we can only move one piece
            #check with server if move is valid
            if (selected == False and self.selectedPiece) or self.forceSelectedPiece:
                self.targetTile = self.board.getTileAt(pos, (self.boardPosX, self.boardPosY))

                if not self.targetTile:
                    return

                self.addSendItem({'action':'checkmove', 'tileid':self.targetTile.id,
                                  'piecetile':self.board.getTileAt((self.selectedPiece.rect.x,
                                                                    self.selectedPiece.rect.y),
                                                                   (self.boardPosX, self.boardPosY)).id,
                                  'colour':self.colour})

    def update(self):
        self.pieces.update()

        if self.inGame:
            #create/update the turn label if we're playing
            if not self.whoseTurnLbl:
                self.whoseTurnLbl = gui.Label(color=(255,255,255,255))
                self.cont.add(self.whoseTurnLbl, 50, 50)
            if self.myTurn:
                self.whoseTurnLbl.set_text("Your Turn")
            else:
                self.whoseTurnLbl.set_text("Opponent's Turn")

        #if we're not playing, can change the person selected in the contacts list
        if not self.inGame:
            name =  self.contactslist.checkSelected()
            if name:
                #self.removePrechallengeGUI()
                self.addSendItem(({'action':'getscore', 'name':name}))

        #checks if we've searched for a new contact to add
        if self.contactslist.searchName:
            self.addSendItem({'action':'searchcontact', 'name':self.contactslist.searchName})
            self.contactslist.searchName = None

        #checks if a new contact has been accepted
        if self.contactslist.newContact:
            self.addSendItem({'action':'contactaccepted', 'name':self.contactslist.newContact})
            self.contactslist.newContact = None

        #checks if we've challenged someone to a game
        if self.proposeMatchWith:
            self.addSendItem({'action':'challenge', 'name':self.proposeMatchWith})
            self.proposeMatchWith = None

    def render(self, screen):
        if self.board:
            self.board.drawBoard(screen)
            self.pieces.draw(screen)


#    def movePiece(self):
#        self.selectedPiece.rect.x = self.targetTile.rect.x
#        self.selectedPiece.rect.y = self.targetTile.rect.y
#        self.targetTile.piece = self.selectedPiece
#
#        self.selectedPiece.deselect()
#        self.selectedPiece = None



    def initChat(self):
        """
        Chatbox. Doesn't work.
        :return:
        """

        displayBar = gui.VScrollBar(5,1, 100, 100)
        self.displayBar = displayBar


        chatbox = gui.TextArea(width = 300, height=12)
        sendBtn = gui.Button("Send")
        sendBtn.connect(gui.CLICK, self.addSendItem, {'action':'chatsent', 'text':chatbox.value})

        self.cont.add(displayBar, 10, 440)
        self.cont.add(chatbox, 10, 500)
        self.cont.add(sendBtn, 400, 500)

        self.chatGUI.append(displayBar)
        self.chatGUI.append(chatbox)
        self.chatGUI.append(sendBtn)

    def displaychat(self, fromName, text):
        self.displayBar.add(gui.Label(fromName+": "+text, color=0xff00ff))
        self.displayBar.tr()


    def gamestart(self, oppnName, colour, myTurn, boardData):
        """
        starts the game
        :param oppnName: not used, but could be for labels
        :param colour: 0 or 1 - black or white
        :param myTurn: True if it's this player's turn
        :param boardData: The state of the board
        :return:
        """
        self.setboard(boardData)
        self.clearGUI(self.challengeGUI)
        self.clearGUI(self.prechallengeGUI)
        self.clearGUI(self.recordsGUI)
        self.contactslist.matchStarted()

        #self.initChat()

        self.teamLabel = gui.Label(color=self.txtColour)
        if colour == 0:
            self.teamLabel.set_text("You are black")
        else:
            self.teamLabel.set_text("You are white")
        self.cont.add(self.teamLabel, 250, 50)


        self.colour = colour

        self.myTurn = myTurn
        self.inGame = True


    def setboard(self, data):
        """
        Draws board in its initial setup
        :param data:
        :return:
        """

        if not self.board:
            tiles = []

            boardSize = int(math.sqrt(len(data['tiles'])))
            self.boardSize = boardSize


            ids = []

            for id in data['tiles']:
                ids.append(id)
                #t = data['board']['tiles'][id]

            i = 0

            for x in range(0, boardSize):
                tiles.append([])
                for y in range(0, boardSize):
                    dTile = data['tiles'][ids[i]]

                    tiles[x].append(Tile(ids[i], dTile['colour'],
                                         (x*self.squareSize+self.boardPosX, y*self.squareSize+self.boardPosY),
                                         self.squareSize))
                    if 'piece' in dTile:
                        tiles[x][y].piece = Piece(dTile['piece']['colour'], dTile['piece']['king'],
                                                  self.pieceRadius, x*self.squareSize+self.boardPosX,
                                                  y*self.squareSize+self.boardPosY, self.squareSize)
                        self.pieces.add(tiles[x][y].piece)

                    i+=1

            self.board = Board(self.squareSize, boardSize, tiles, (self.boardPosX,self.boardPosY))

    def updatePiecePositions(self, boarddata):
        """
        Clears all the pieces and recreates them according to what's in boarddata, from the server
        :param boarddata:
        :return:
        """
        self.pieces.empty()
        for row in self.board.tiles:
            for tile in row:
                if 'piece' in boarddata['tiles'][tile.id]:
                    piecedata = boarddata['tiles'][tile.id]['piece']
                    tile.piece = Piece(piecedata['colour'], piecedata['king'], self.pieceRadius,
                                       tile.rect.x, tile.rect.y, self.squareSize)
                    self.pieces.add(tile.piece)
                else:
                    tile.piece = None


    def movechecked(self, verdict, myTurn, boarddata, movedx, movedy):
        """
        Implements what the server has told us should happen after the move
        :param verdict: Type of move that happend
        :param myTurn: True if this player's turn
        :param boarddata:
        :param movedx: Used for double-jumping - position of the tile we jumped to
        :param movedy: Used for double-jumping - position of the tile we jumped to
        :return:
        """
        self.forceSelectedPiece = False

        if self.inGameMsgLbl:
            self.cont.remove(self.inGameMsgLbl)
            self.inGameMsgLbl = None
        self.myTurn = myTurn

        if verdict == "move":
            self.updatePiecePositions(boarddata)
            self.selectedPiece = None
        elif verdict == "take":
            self.updatePiecePositions(boarddata)
            if not myTurn:
                self.selectedPiece = None
        elif verdict == "doubletake":
            self.updatePiecePositions(boarddata)
            if myTurn:
                tile = self.board.tiles[movedx][movedy]
                self.selectedPiece = tile.piece
                self.selectedPiece.select()
                self.forceSelectedPiece = True



    def invalidmove(self, verdict):
        """
        Called if move attempted was invalid
        :param verdict: Type of error
        :return:
        """
        if self.inGameMsgLbl:
            self.cont.remove(self.inGameMsgLbl)
            self.inGameMsgLbl = None

        if verdict == "musttake":
            self.inGameMsgLbl = gui.Label("Invalid Move: Must take piece", color=(255,255,255,255))
            self.cont.add(self.inGameMsgLbl, 300, 450)
        elif verdict == "invalid":
            self.inGameMsgLbl = gui.Label("Invalid Move", color=(255,255,255,255))
            self.cont.add(self.inGameMsgLbl, 300, 450)


    def populatecontacts(self, contacts):
        self.contactslist.populateContacts(contacts)

    def friendrequest(self, name):
        self.contactslist.friendRequest(name)


    def contactaccepted(self, name):
        self.contactslist.addContact(name)

    def setname(self, name):
        self.name = name
        self.nameTxt.value = name

    def acceptChallenge(self, accepted, name):
        """
        Sends acceptance of challenge to server
        :param accepted: True if will play, False if won't
        :param name: Name of player who challenged
        :return:
        """
        self.addSendItem({'action':'replytochallenge', 'accepted':accepted, 'challenger':name})

        if not accepted:
            self.clearGUI(self.challengeGUI)



    def challengereceived(self, name):
        """
        called when someone else has sent this player a request to play
        Adds GUI for accepting or rejecting request
        :param name: Name of player who challenged
        :return:
        """
        if self.inGame:
            self.acceptChallenge(False, name)
            return

        if self.challengeGUI:
            return

        line = name + " wants to play!"
        challengeLbl = gui.Label(line, color=(255,255,255,255))

        acceptBtn = gui.Button("Accept")
        acceptBtn.connect(gui.CLICK, self.acceptChallenge, True, name)

        refuseBtn = gui.Button("Refuse")
        refuseBtn.connect(gui.CLICK, self.acceptChallenge, False, name)

        self.cont.add(challengeLbl, self.challengeGUIsx, self.challengeGUIsy)
        self.cont.add(acceptBtn, self.challengeGUIsx, self.challengeGUIsy+100)
        self.cont.add(refuseBtn, self.challengeGUIsx+100, self.challengeGUIsy+100)

        self.challengeGUI = [challengeLbl, acceptBtn, refuseBtn]

    def challengerejected(self, name):
        #nothing happens
        print "challenge rejected"



    def gameover(self, winner, score):
        """
        :param winner: True if player won game, or False
        :param score: Current score of player
        :return:
        """
        if winner:
            winTxt = gui.Label("YOU WIN", cls="h1", color=(255,0,0,255))
            #winTxt = gui.TextArea("YOU WIN", 200, 200)


        else:
            winTxt = gui.Label("YOU LOSE", cls="h1", color=(0,0,255,255))
            #winTxt = gui.TextArea("YOU LOSE", 200, 200)

        #scoreTxt = gui.TextArea(str(score), 40, 40)
        scoreTxt = gui.Label("Score: "+str(score), size=25, color=(0,255,0,255))

        okayBtn = gui.Button("Okay")
        okayBtn.connect(gui.CLICK, self.resetAfterGame)

        #winTxt.editable = False
        #scoreTxt.editable = False


        self.cont.add(winTxt, 200, 440)
        self.cont.add(scoreTxt, 200, 470)
        self.cont.add(okayBtn, 200, 500)

        self.winGUI.append(winTxt)
        self.winGUI.append(scoreTxt)
        self.winGUI.append(okayBtn)

    def resetAfterGame(self):
        self.clearGUI(self.winGUI)
        self.clearGUI(self.chatGUI)

        self.cont.remove(self.whoseTurnLbl)
        self.whoseTurnLbl = None
        self.myTurn = False

        self.cont.remove(self.teamLabel)
        self.teamLabel = None

        self.contactslist.resetList()

        self.board = None

        self.pieces.empty()

        self.inGame = False

        pygame.display.get_surface().fill(self.bgc)

    def contactstatuschange(self, name, status):
        self.contactslist.list.changeContactStatus(name, status)

    def showcontactscore(self, name, score):
        """
        sets up the GUI to view contact details and challenge to a match
        :param name: contact name that we clicked
        :param score: contact's score
        :return:
        """

        self.clearGUI(self.recordsGUI)
        self.clearGUI(self.prechallengeGUI)

        nameLbl = gui.Label(name, color=(255,255,255,255))
        scoreLbl = gui.Label("Score: "+str(score), color=(255,255,255,255))


        challengeBtn = gui.Button("Challenge!")
        challengeBtn.connect(gui.CLICK, self.challenge, name)

        self.cont.add(nameLbl, 350, 200)
        self.cont.add(scoreLbl, 350, 250)
        self.cont.add(challengeBtn, 350, 300)

        self.contactslist.list.value = None

        self.prechallengeGUI.append(nameLbl)
        self.prechallengeGUI.append(scoreLbl)
        self.prechallengeGUI.append(challengeBtn)

    def challenge(self, opponent):
        self.proposeMatchWith = opponent



    def reqRecord(self):
        """
        Sent request for records
        :return:
        """
        if not self.inGame:
            self.addSendItem({'action':'reqrequest'})

    def retrecords(self, records):
        """
        Records recieved
        :param records: Dictionary - keys are fine to print as-are
        :return:
        """
        self.clearGUI(self.prechallengeGUI)

        firstX = 300
        firstY = 200
        for record in records:
            nLabel = gui.Label(record, color=self.txtColour)
            rLabel = gui.Label(str(records[record]), color=self.txtColour)

            self.cont.add(nLabel, firstX, firstY)
            self.cont.add(rLabel, firstX+150, firstY)
            firstY+=40

            self.recordsGUI.append(nLabel)
            self.recordsGUI.append(rLabel)

    def clearGUI(self, itemsList):
        """
        Clears GUI elements from screen
        :param itemsList:
        :return:
        """
        for item in itemsList:
            self.cont.remove(item)
        del itemsList[:]










