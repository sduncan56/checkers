__author__ = ''

import pygame
from pgu import gui


from PodSixNet.Connection import connection, ConnectionListener

from PlayState import PlayState
from StartState import StartState

pygame.init()


class Client(ConnectionListener, gui.App):
    def __init__(self, host, port, state):
        super(Client, self).__init__()

        #self.Connect((host, port))
        self.players = {}
        self.state = state

        self.running = True

        self.connected = False


        #self.initGUI()
        self.cont = self.state.initConnectGUI()
        self.connect(gui.QUIT, self.quit, None)
        self.run(self.cont, screen)


    def initGUI(self):
        pass


    def loop(self):
        #super(Client, self).loop()

        self.set_global_app()

        pygame.display.get_surface().fill(0x000000)

        #connects to server when hostname/port is available
        if not self.connected:
            if self.state.connect:
                self.Connect((self.state.connectInfo['server'], self.state.connectInfo['port']))
                self.connected = True
                self.state.clearConnectGUI()
                self.cont.add(self.state.initGUI(self), 0, 0)

        #events
        for e in pygame.event.get():
            if not (e.type == gui.QUIT and self.mywindow):
                self.state.handleEvent(e)
                self.event(e)

        #send/recieve from server
        if self.connected:
            self.sendData()
            self.Pump()
            connection.Pump()

        self.state.update()
        self.state.render(screen)

        self.paint(screen)

        pygame.display.flip()

    def sendData(self):
        """
        Sends data to server
        :return:
        """
        for item in self.state.sendItems:
            connection.Send(item)

        del self.state.sendItems[:]

    ###
    #Callbacks from server
    ###

    def Network_setboard(self, data):
        self.state.setboard(data)


    def Network_movechecked(self, data):
        self.state.movechecked(data['verdict'], data['myturn'], data['board'], data['movedx'], data['movedy'])
        if 'winner' in data:
            self.state.gameover(data['winner'], data['score'])

    def Network_loginreturn(self, data):
        if data['result']:
            self.swapState(PlayState())
        else:
            self.state.loginfail()

    def Network_regconfirm(self, data):
        self.state.regconfirm(data['success'])


    def Network_retcontacts(self, data):
        self.state.populatecontacts(data['contacts'])

    def Network_friendrequest(self, data):
        self.state.friendrequest(data['name'])

    def Network_contactaccepted(self, data):
        self.state.contactaccepted(data['name'])

    def Network_returnname(self, data):
        self.state.setname(data['name'])

    #will fail if contact is not online or something went wrong anyway
    #should never be false
    def Network_confirmchallengesent(self, data):
        if data['sent']:

            print "challenge sent"
        else:
            print "challenge failed"

    def Network_challengereceived(self, data):
        self.state.challengereceived(data['name'])

    def Network_challengerejected(self, data):
        self.state.challengerejected(data['name'])

    def Network_gamestart(self, data):
        self.state.gamestart(data['opponentname'], data['colour'], data['myturn'], data['boarddata'])


    def Network_contactstatuschange(self, data):
        self.state.contactstatuschange(data['name'], data['status'])

    def Network_getscore(self, data):
        self.state.showcontactscore(data['name'], data['score'])


    def Network_invalidmove(self, data):
        self.state.invalidmove(data['verdict'])


    def Network_retrecords(self, data):
        self.state.retrecords(data['records'])

    def Network_chatdelivered(self, data):
        self.state.displaychat(data['from'], data['text'])


    def swapState(self, state):
        self.state.clean()

        screen.fill(0x000000)

        self.state = state
        self.cont.add(self.state.initGUI(self), 0, 0)





if __name__ == "__main__":
    screen = pygame.display.set_mode((800, 600), pygame.DOUBLEBUF, 32)
    pygame.display.set_caption("Checkers")

    #client = Client("localhost", 31425, PlayState())
    client = Client("localhost", 31425, StartState())



