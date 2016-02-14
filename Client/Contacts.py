__author__ = ''

import pygame
from pgu import gui

class cList(gui.List):
    def __init__(self, width, height, **params):
        super(cList, self).__init__(width, height, **params)
        self.statuses = {}


    def resetList(self):
        """
        clears then readds everythng to the list
        :return:
        """
        values = []
        for item in self.items:
            values.append(item.value)

        self.clear()
        for value in values:
            self.add(value, value=value)
            self.changeContactStatus(value, self.statuses[value])


        self.resize()
        self.repaint()

    def changeContactStatus(self, name, online):
        """
        changes offline/online status in list display and keeps track of if on or offline
        :param name: name of contact
        :param online: bool
        :return:
        """
        for item in self.items:
            if item.value == name:
                self.statuses[name] = online
                if online:
                    item.widget.set_text(name+"    "+"Online")
                else:
                    item.widget.set_text(name+"    "+"Offline")

        self.repaint()

    def addContacts(self, name, online):
        """
        adds contact to list, stores whether online or off
        :param name:
        :param online:
        :return:
        """
        self.statuses[name] = online

        self.add(name, value=name)
        self.changeContactStatus(name, online)

    def hasContact(self, name):
        """
        True if contact exists
        :param name:
        :return:
        """
        for item in self.items:
            if item.value == name:
                return True
        return False



class ContactsList(object):
    def __init__(self):
        self.searchName = None
        self.reqCont = None
        self.newContact = None
        self.proposeMatchWith = None

        self.friendReqGUIItems = []

        self.challengeBtn = None
        self.inGame = False



    def makeList(self):
        """
        Makes main contact list gui
        :return:
        """
        cont = gui.Container(width=800, height=600)
        cont.add(gui.Label("Contacts", cls="h1", color=(255,255,255,255), antialias=1), 550, 0)

        self.list = cList(width=200, height=300)
        cont.add(self.list, 500, 40)

        self.searchBox = gui.TextArea(width=100, height=30)
        cont.add(self.searchBox, 500, 350)

        searchBtn = gui.Button("Search")
        searchBtn.connect(gui.CLICK, self.search)
        cont.add(searchBtn, 650, 350)

        self.cont = cont

        return cont

    def matchStarted(self):
        """
        removes challenge button if the game starts
        (should be moved into PlayState, or better yet into a class with all the other gui stuff
        :return:
        """
        if self.challengeBtn:
            self.cont.remove(self.challengeBtn)
            self.challengeBtn = None

        self.inGame = True

    def checkSelected(self):
        """
        returns selected item on list
        :return:
        """
        if self.list.value:
            return self.list.value
        return False

    def search(self):
        """
        contact search box callback
        :return:
        """
        if not self.list.hasContact(self.searchBox.value):
            self.searchName = self.searchBox.value

    def friendRequest(self, name):
        """
        Friend request GUI
        :param name: player who sent request
        :return:
        """
        friendReqLbl = gui.Label("New Friend Request: "+name, color=(255,255,255,255), antialias=1)

        acceptBtn = gui.Button("Accept")
        acceptBtn.connect(gui.CLICK, self.acceptContact, name)

        rejectBtn = gui.Button("Reject")
        rejectBtn.connect(gui.CLICK, self.rejectContact, name)

        cont = gui.Container(width=200, height=200)
        cont.add(friendReqLbl, 0, 0)
        cont.add(acceptBtn, 0, 60)
        cont.add(rejectBtn, 80, 60)

        self.reqCont = cont

        self.cont.add(cont, 500, 450)

        self.friendReqGUIItems = [friendReqLbl, acceptBtn, rejectBtn]



    def populateContacts(self, contacts):
        """
        fills contact list when logging in
        :param contacts:
        :return:
        """
        for contact in contacts:
            self.list.addContacts(contact['name'], contact['online'])


    def clearFriendReqGUI(self):
        """
        remove friend request gui
        should be folded into PlayState/dedicated GUI class with the rest
        :return:
        """
        for item in self.friendReqGUIItems:
            self.reqCont.remove(item)
        self.cont.remove(self.reqCont)
        self.reqCont = None

        pygame.display.get_surface().fill(0x000000)
        self.cont.repaintall()


    def acceptContact(self, name):
        """
        accept contact button callback
        :param name:
        :return:
        """
        self.list.addContacts(name, True)
        self.newContact = name

        self.clearFriendReqGUI()
        self.list.resetList()

    def rejectContact(self, name):
        self.clearFriendReqGUI()

    def addContact(self, name):
        self.list.addContacts(name, True)
        self.list.resetList()

    def resetList(self):
        self.list.resetList()






