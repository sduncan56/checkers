__author__ = ''

from pgu import gui
import pygame
from State import State

class StartState(State):
    def __init__(self):
        super(StartState, self).__init__()
        self.msgLabel = None
        self.cont = None

        self.txtColour = (255,255,255,255)
        self.bgcolour = 0x000000

        self.firstItemY = 200

        self.connectGUI = []

        self.connect = False
        self.connectInfo = {}



    def initConnectGUI(self):
        """
        GUI for connecting to the server with hostname and port
        Should really be split into another State class
        :return:
        """
        cont = gui.Container(width=800, height=600)

        #server/port
        serverLbl = gui.Label("Host:", color=(255,255,255,255))
        portLbl = gui.Label("Port: ", color=(255,255,255,255))

        serverTxt = gui.TextArea(value="localhost")
        portTxt = gui.TextArea(value="31425")
        connectBtn = gui.Button("Connect")
        connectBtn.connect(gui.CLICK, self.connectToServer, serverTxt.value, portTxt.value)


        cont.add(serverLbl, 250, self.firstItemY)
        cont.add(portLbl, 250, self.firstItemY+50)
        cont.add(serverTxt, 300, self.firstItemY)
        cont.add(portTxt, 300, self.firstItemY+50)
        cont.add(connectBtn, 300, self.firstItemY+100)

        self.connectGUI.append(serverLbl)
        self.connectGUI.append(portLbl)
        self.connectGUI.append(serverTxt)
        self.connectGUI.append(portTxt)
        self.connectGUI.append(connectBtn)

        self.cont = cont

        return cont

    def clearConnectGUI(self):
        """
        Removes GUI for connecting to server
        :return:
        """
        for item in self.connectGUI:
            self.cont.remove(item)
        self.connectGUI = []
        pygame.display.get_surface().fill(0x000000)

    def connectToServer(self, server, port):
        """
        Saves information needed to connect to server and adds flag
        :param server:
        :param port:
        :return:
        """
        self.connectInfo = {'server':server, 'port':int(port)}
        self.connect = True

    def initGUI(self, app):
        """
        Creates initial GUI elements for the State
        :param app:
        :return:
        """
        cont = gui.Container(width=800, height=600)

        loginLbl = gui.Label("Username: ", color=self.txtColour)
        passwordLbl = gui.Label("Password: ", color=self.txtColour)

        self.nameTxt = gui.TextArea(value="", width=200, height=30)
        self.passwordTxt = gui.TextArea(value="", width=200, height=30)

        cont.add(loginLbl, 200, self.firstItemY)
        cont.add(passwordLbl, 200, self.firstItemY+50)
        cont.add(self.nameTxt, 300, self.firstItemY)
        cont.add(self.passwordTxt, 300, self.firstItemY+50)


        loginBtn = gui.Button("Log In")
        loginBtn.connect(gui.CLICK, self.login)
        cont.add(loginBtn, 300, self.firstItemY+100)

        registerBtn = gui.Button("Register")
        registerBtn.connect(gui.CLICK, self.register)
        cont.add(registerBtn, 400, self.firstItemY+100)

        self.addGUIItem(loginLbl)
        self.addGUIItem(passwordLbl)
        self.addGUIItem(loginBtn)
        self.addGUIItem(registerBtn)
        self.addGUIItem(self.nameTxt)
        self.addGUIItem(self.passwordTxt)

        self.cont = cont

        return cont



    def handleEvent(self, event):
        pass

    def update(self):
        pass

    def render(self, screen):
        pass

    def login(self):
        """
        callback for login button
        :return:
        """
        self.addSendItem({'action':'login', 'name':self.nameTxt.value, 'password':self.passwordTxt.value})

    def register(self):
        """
        callback for register button
        :return:
        """
        self.addSendItem({'action':'register', 'name':self.nameTxt.value, 'password':self.passwordTxt.value})

    def loginfail(self):
        """
        display message if login failed
        :return:
        """
        if self.msgLabel:
            self.cont.remove(self.msgLabel)
            pygame.display.get_surface().fill(self.bgcolour)

        self.msgLabel = gui.Label("Login failed. Check username and password.", color=self.txtColour)
        self.cont.add(self.msgLabel, 300, self.firstItemY+150)

    def regconfirm(self, success):
        """
        display messages for registering success or failure
        :param success: bool
        :return:
        """
        if self.msgLabel:
            self.cont.remove(self.msgLabel)
            pygame.display.get_surface().fill(self.bgcolour)

        if success:
            self.msgLabel = gui.Label("Registration successful. Please log in", color=self.txtColour)
        else:
            self.msgLabel = gui.Label("That name is already registered.", color=self.txtColour)

        self.cont.add(self.msgLabel, 300, self.firstItemY+150)


    def clean(self):
        """
        remove GUI items
        :return:
        """
        for item in self.guiItems:
            self.cont.remove(item)
        if self.msgLabel:
            self.cont.remove(self.msgLabel)
            self.msgLabel = None

