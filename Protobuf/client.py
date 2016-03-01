import cmd
import requests
from model import Message
from build import response_pb2 as ResponseProtoBuf

SERVER_HOST = 'http://127.0.0.1:5000'

def published(method):
    method.published = True
    return method

class Client(object):
    def __init__(self):
        self.current_user = ""
        self.current_room = ""
        self.is_group = False

    @published
    def moveToGroup(self, group):
        self.current_room = group
        self.is_group = True

    @published
    def moveToUser(self, user):
        self.current_room = user
        self.is_group = False

    @published
    def loginAs(self, user):
        self.current_user = user

    @published
    def sendMessage(self, message):
        if self.is_group:
            self.sendGroupMessage(self.current_user, self.current_room, message)
        else:
            self.sendDirectMessage(self.current_user, self.current_room, message)

    @published
    def listUsers(self):
        r = requests.get(SERVER_HOST + '/users')
        print r

    @published
    def createUser(self, username):
        r = requests.post(SERVER_HOST + '/users/' + username)
        print r, r.text

    @published
    def deleteUser(self, username):
        r = requests.delete(SERVER_HOST + '/users/' + username)
        print r

    @published
    def listGroups(self):
        r = requests.get(SERVER_HOST + '/groups')
        print r

    @published
    def createGroup(self, groupname):
        r = requests.post(SERVER_HOST + '/groups/' + groupname)
        print r

    @published
    def addUserToGroup(self, groupname, username):
        r = requests.put(SERVER_HOST + '/groups/' + groupname + '/users/' + username)
        print r

    @published
    def sendDirectMessage(self, from_name, to_name, message):
        message = ResponseProtoBuf.Message()
        message.frm = from_name
        message.msg = message

        r = requests.post(SERVER_HOST + '/groups/' + to_name + '/messages', data=message)
        return r


    @published
    def sendGroupMessage(self, from_name, to_name, message):
        message = ResponseProtoBuf.Message()
        message.frm = from_name
        message.msg = message

        r = requests.post(SERVER_HOST + '/users/' + to_name + '/messages', data=message)
        return r

    @published
    def listMessages(self, username):
        r = requests.get(SERVER_HOST + '/users/' + username + '/messages')
        print r

    @published
    def help(self, function):
        """usage: help [method]"""
        method = getattr(client, function, None)
        if method and method.published:
            print method.__doc__
        else:
            print "<Action Unknown>"

    @published
    def exit(self):
        exit()

if __name__ == "__main__":
    client = Client()

    while True:
        prompt = "[" + str(client.current_user) + "," + str(client.current_room) + "]: "
        command = raw_input(prompt)

        if command == "":
            continue

        # not a slash command
        if command[0] != "/":
            client.sendMessage(command)

        # is a slash command
        action = command.split(' ')
        method = getattr(client, action[0][1:], None)
        if method and method.published:
            method(*action[1:])
        else:
            print "<Action Unknown>"
