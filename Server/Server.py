__author__ = ''

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
import sys
from time import sleep, localtime
from random import randint



from weakref import WeakKeyDictionary

from S_Board import S_Board
from UsersDB import UsersDB

class ServerChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        self.id = str(self._server.NextId())
        self.nickname = "something"
        self.gameNumber = None
        self.myTurn = False

    def PassOn(self, data):
        """
        sends to all players on server - not used.
        :param data:
        :return:
        """
        data.update({"id":self.id})
        self._server.SendToAll(data)

    def Close(self):
        self._server.delPlayer(self)

    def friendRequest(self, name):
        self.Send({'action':'friendrequest', 'name':name})

    def contactAccepted(self, name):
        self.Send({'action':'contactaccepted', 'name':name})

    def moveChecked(self, data, turnOver, gameOver):
        """
        After move is checked, passes on result to client. Also deals with winning/losing
        :param data:
        :param turnOver: bool
        :param gameOver: bool
        :return:
        """
        if self.myTurn and gameOver:
            data['winner'] = True
        elif not self.myTurn and gameOver:
            data['winner'] = False

        if gameOver:
            records = self._server.updateRecords(self.nickname, data['winner'])
            data['score'] = records['Score']

        if self.myTurn and turnOver:
            self.myTurn = False
        elif not self.myTurn and turnOver:
            self.myTurn = True


        data['myturn'] = self.myTurn

        self.Send(data)

    #being sent a challenge by someone else
    def sendChallenge(self, name):
        self.Send({'action':'challengereceived', 'name':name})

    def gameStart(self, opponentName, boardData, colour, myTurn, gameNumber):
        self.gameNumber = gameNumber
        self.myTurn = myTurn
        self.Send({'action':'gamestart', 'opponentname':opponentName, 'colour':colour,
                   'myturn':myTurn, 'boarddata':boardData})

    def gameRejected(self, name):
        self.Send({'action':'challengerejected', 'name':name})

    def updateContacts(self, name, online):
        self.Send({'action':'contactstatuschange', 'name':name, 'status':online})

    def deliverChat(self, fromName, text):
        self.Send({'action':'chatdelivered', 'from':fromName, 'text':text})

    #callbacks

    def Network_playstart(self, data):
        if data['start'] == True:
            print "Game Starting"
            self._server.setBoard()
            self._server.sendBoard()

    def Network_checkmove(self, data):
        ret = self._server.checkMove(data['tileid'], data['piecetile'], data['colour'], self.gameNumber)
        if ret:
            self.Send({'action':'invalidmove', 'verdict':ret})

    def Network_register(self, data):
        success = self._server.register(data['name'], data['password'])

        self.Send({'action':'regconfirm', 'success':success})

    def Network_login(self, data):
        res = self._server.login(data['name'], data['password'])
        self.Send({'action':'loginreturn', 'result':res})
        if res:
            self.nickname = data['name']

        self._server.sendOutstandingContactReqs(self.nickname)

    def Network_getcontacts(self, data):
        contacts = self._server.getContacts(self.nickname)
        self.Send({'action':'retcontacts', 'contacts':contacts})

    def Network_searchcontact(self, data):
        self._server.searchContact(self.nickname, data['name'])

    def Network_contactaccepted(self, data):
        self._server.contactAccepted(self.nickname, data['name'])

    def Network_getname(self, data):
        self.Send({'action':'returnname', 'name':self.nickname})
        print self.nickname

    def Network_challenge(self, data):
        ret = self._server.sendChallenge(self.nickname, data['name'])
        self.Send({'action':'confirmchallengesent', 'sent':ret})

    #whether challenge was accepted or rejected
    def Network_replytochallenge(self, data):
        self._server.replyToChallenge(data['accepted'], self.nickname, data['challenger'])

    def Network_getscore(self, data):
        """
        Get score of any player by name and sends it back
        Used to display score when contact's name is clicked on
        :param data:
        :return:
        """
        records = self._server.getRecords(data['name'])
        data['score'] = records['Score']

        self.Send(data)

    def Network_reqrequest(self, data):
        self.Send({'action':'retrecords', 'records':self._server.getRecords(self.nickname)})

    def Network_chatsent(self, data):
        self._server.sendChat(self.nickname, self.gameNumber, data['text'])


class GameServer(Server):
    channelClass = ServerChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.id = 0
        self.players = WeakKeyDictionary()
        print "Server Launched"

        self.usersdb = UsersDB()

        self.boards = {}
        self.gamesCount = 0
        #self.usersdb.firstRun()

        self.outstandingContactRequests = []



    def NextId(self):
        self.id += 1
        return self.id

    def Connected(self, channel, addr):
        self.addPlayer(channel)
        print "connected"

    def addPlayer(self, player):
        print "New Player" + str(player.addr)
        self.players[player] = True
        self.sendPlayers()

    def delPlayer(self, player):
        print "Deleting Player" + str(player.addr)

        self.updateStatus(player.nickname, False)

        del self.players[player]
        self.sendPlayers()

    def register(self, name, password):
       return self.usersdb.registerUser(name, password)

    def login(self, name, password):
        valid = self.usersdb.authenticate(name, password)

        #fail if already logged in
        if self.getOnlinePlayer(name):
            return False

        self.updateStatus(name, True)

        return valid

    def updateStatus(self, name, online):
        """
        gets online status of player
        :param name:
        :param online:
        :return:
        """
        cNames = self.usersdb.getContacts(name)
        for contact in cNames:
            c = self.getOnlinePlayer(contact)
            if c:
                c.updateContacts(name, online)

    def sendOutstandingContactReqs(self, name):
        """
        when someone signs in, sends contact request that were sent when they were offline
        :param name:
        :return:
        """
        for req in self.outstandingContactRequests:
            if req['to'] == name:
                self.getOnlinePlayer(name).friendRequest(req['from'])
                self.outstandingContactRequests.remove(req)

    def getContacts(self, name):
        """
        returns list of contacts for a playe
        :param name:
        :return:
        """

        contacts = []
        cNames = self.usersdb.getContacts(name)
        for contact in cNames:
            if self.getOnlinePlayer(contact):
                contacts.append({'name':contact, 'online':True})
            else:
                contacts.append({'name':contact, 'online':False})

        return contacts


    def getOnlinePlayer(self, name):
        """
        If player is online, returns them. Otherwise false
        :param name:
        :return:
        """
        for player in self.players:
            if player.nickname == name:
                return player

        return None

    def searchContact(self, fromname, name):
        """
        Searches for a contact to add
        If they're online, send friend request
        If not online, add them to dictionary for friend request to be sent next time they log in
        :param fromname:
        :param name:
        :return:
        """
        if self.usersdb.hasUser(name):
            #check if player is online now
            player = self.getOnlinePlayer(name)
            if player:
                player.friendRequest(fromname)
            else:
                self.outstandingContactRequests.append({'from':fromname, 'to':name})


    def contactAccepted(self, fromname, name):
        """
        When contact accepted, informs player that requested adding and registers contact in database
        :param fromname:
        :param name:
        :return:
        """
        player = self.getOnlinePlayer(name)

        if player:
            player.contactAccepted(fromname)

        self.usersdb.registerContacts(fromname, name)

    def sendChallenge(self, fromname, name):
        """
        passes on challenge to challenged player
        :param fromname:
        :param name:
        :return:
        """
        challengee = self.getOnlinePlayer(name)
        if challengee:
           challengee.sendChallenge(fromname)
        else:
            return False
        return True

    def replyToChallenge(self, accepted, fromname, name):
        """
        If challenge accepted, creates board (serverside) and sets the player's colour
        :param accepted:
        :param fromname:
        :param name:
        :return:
        """
        challenger = self.getOnlinePlayer(name)
        challengee = self.getOnlinePlayer(fromname) #could pass this in, but w/e

        if accepted:
            board = S_Board(8, challenger, challengee)
            self.boards[self.gamesCount] = board

            challengerColour = randint(0,1)
            challengeeColour = -1
            if challengerColour == 1:
                challengeeColour = 0
            else:
                challengerColour = 1

            #Testing!
            challengerColour = 0
            challengeeColour = 1

            challenger.gameStart(fromname, board.networkData(), challengerColour, True, self.gamesCount)
            challengee.gameStart(name, board.networkData(), challengeeColour, False, self.gamesCount)


            self.gamesCount += 1

        else:
            challenger.gameRejected(fromname)


    def updateRecords(self, name, won):
        """
        Adds to player's score when they win and saves in database
        :param name:
        :param won: bool
        :return: Dictionary of records
        """
        self.usersdb.updateRecords(name, won)

        return self.usersdb.getRecords(name)

    def getRecords(self, name):
        return self.usersdb.getRecords(name)




    def checkMove(self, tileid, piecetileid, colour, boardNo):
        """
        Checks what kind of move was made and sends to players the appropriate response
        :param tileid: Int - tile that player is trying to move to
        :param piecetileid: Int - tile that player's piece is on
        :param colour: Int - 1 or 0
        :param boardNo:
        :return:
        """
        board = self.boards[boardNo]
        tarSel = board.getTargetSelTiles(tileid, piecetileid)

        result = board.handleMovement(tarSel[0], tarSel[1], colour)


        turnOver = False

        newKing = False
        if result == "move" or result == "take":
            if board.checkKinging(colour, tarSel[0]):
                newKing = True

        if result == "move":
            turnOver = True
        elif result == "musttake":
            turnOver = False
            return result
        elif result == "take":
            turnOver = True
        elif result == "doubletake":
            turnOver = False

        elif result == "invalid":
            return result

        #check if the other player has lost/has no further moves they can make
        if not board.getPossibleMoves(board.swapColour(colour)):
            board.gameOver = True

        self.sendToPlayers({'action':'movechecked', 'verdict':result, 'board':board.networkData(),
                         'newking':newKing, 'movedx':tarSel[0].x, 'movedy':tarSel[0].y}, board.player1,
                           board.player2, turnOver, board.gameOver)



    def sendToPlayers(self, data, player1, player2, turnOver, gameOver):
        """
        Sending move data to relevant players
        :param data:
        :param player1:
        :param player2:
        :param turnOver:
        :param gameOver:
        :return:
        """
        for player in self.players:
            if player == player1 or player == player2:
                player.moveChecked(data, turnOver, gameOver)

    def sendChat(self, fromname, gameNumber, text):
        board = self.boards[gameNumber]

        board.player1.deliverChat(fromname, text)
        board.player2.deliverChat(fromname, text)

    def sendNumPlayers(self, player):
        self.channelClass.Send({"action":"recNumPlayers", "message": len(self.players)})

    def sendPlayers(self):
        self.sendToAll({"action":"players","players": [p.nickname for p in self.players]})

    def sendToAll(self, data):
        [p.Send(data) for p in self.players]

    def launch(self):
        while True:
            self.Pump()
            sleep(0.0001)

if len(sys.argv) != 2:
    print "Usage:", sys.argv[0], "host:port"
    print "e.g.", sys.argv[0], "localhost:31425"
else:
    host, port = sys.argv[1].split(":")
    s = GameServer(localaddr=(host, int(port)))
    s.launch()


