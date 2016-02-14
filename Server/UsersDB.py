__author__ = ''

import MySQLdb

from peewee import *

db = SqliteDatabase('users.db')
#db = MySQLDatabase('', user='root', passwd='')


class User(Model):
    name = CharField()
    password = CharField()
    score = IntegerField()
    gameslost = IntegerField()
    gamesplayed = IntegerField()

    class Meta:
        database = db

class Contact(Model):
    user = ForeignKeyField(User, related_name='contacts')
    contactName = CharField()

    class Meta:
        database = db

class UsersDB(object):
    def __init__(self):
        db.connect()


    def firstRun(self):
        """
        drops all tables and recreates them.
        :return:
        """
        db.drop_table(User)
        db.drop_table(Contact)

        db.create_table(User)
        db.create_table(Contact)

    def registerUser(self, name, password):
        """
        saves new user to database
        :param name:
        :param password:
        :return:
        """
        #make sure user is not registered already
        if self.hasUser(name):
            return False

        user = User(name=name, password=password, score=0, gameslost=0, gamesplayed=0)
        user.save()
        return True

    def registerContacts(self, nameOne, nameTwo):
        """
        saves contacts associated with a user
        :param nameOne:
        :param nameTwo:
        :return:
        """
        userOne = User.get(User.name == nameOne)
        userTwo = User.get(User.name == nameTwo)

        contactOne = Contact(user=userOne, contactName=nameTwo)
        contactTwo = Contact(user=userTwo, contactName=nameOne)

        contactOne.save()
        contactTwo.save()


    def authenticate(self, name, password):
        """
        checks if password matches the password stored in the database
        :param name:
        :param password:
        :return:
        """
        if not self.hasUser(name):
            return False

        user = User.get(User.name == name)

        if str(user.password) == password:
            return True

        return False

    def getContacts(self, name):
        """
        returns list of contacts of a user
        :param name:
        :return:
        """
        cList = []
        for contact in Contact.select().join(User).where(User.name==name):
            cList.append(contact.contactName)

        return cList

    def hasUser(self, name):
        """
        returns true if user by name exists in database
        :param name:
        :return:
        """
        user = User.select().where(User.name == name)
        if user.exists():
            return True

        return False


    def deleteUser(self, name):
        """
        remove user from database
        :param name:
        :return:
        """
        user = User.get(User.name == name)
        user.delete_instance()

    def updateRecords(self, name, won):
        """
        adds to user's score if they won
        :param name:
        :param won:
        :return:
        """
        user = User.get(User.name == name)
        if won:
            user.score += 1
        else:
            user.gameslost += 1
        user.gamesplayed += 1

        user.save()

    def getRecords(self, name):
        """
        returns records
        :param name:
        :return:
        """
        user = User.get(User.name == name)

        records = {"Score":int(user.score), "Games Lost":int(user.gameslost), "Games Played":int(user.gamesplayed)}

        return records

