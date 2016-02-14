__author__ = ''

class State(object):
    def __init__(self):
        self.guiItems = []
        self.sendItems = []

    def initGUI(self, app):
        raise NotImplementedError

    def handleEvent(self, event):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def render(self, screen):
        raise NotImplementedError

    def addGUIItem(self, item):
        self.guiItems.append(item)

    #item is a dictionary of actions to send to the server
    def addSendItem(self, item):
        self.sendItems.append(item)



