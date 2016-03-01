import cmd
import requests
from build import request_pb2 as RequestProtoBuf
from functools import wraps
from build import response_pb2 as ResponseProtoBuf

SERVER_HOST = 'http://127.0.0.1:5000'

def published(method):
    method.published = True
    return method

def protoapi(expectedType):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            response = f(*args, **kwargs)

            print response

            if response.status_code == 200:
                obj = expectedType()
                obj.ParseFromString(response.content)
                print str(obj)

            elif response.status_code == 400:
                ue = ResponseProtoBuf.UserError()
                ue.ParseFromString(response.content)
                print str(ue)

        return wrapped
    return decorator

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
    def sendMessage(self, *args):
        message = (' ').join(args)
        if self.is_group:
            self.sendGroupMessage(self.current_user, self.current_room, message)
        else:
            self.sendDirectMessage(self.current_user, self.current_room, message)

    @published
    @protoapi(ResponseProtoBuf.UserList)
    def listUsers(self):
        return requests.get(SERVER_HOST + '/users')

    @published
    @protoapi(ResponseProtoBuf.User)
    def createUser(self, username):
        return requests.post(SERVER_HOST + '/users/' + username)

    @published
    def deleteUser(self, username):
        return requests.delete(SERVER_HOST + '/users/' + username)

    @published
    @protoapi(ResponseProtoBuf.GroupList)
    def listGroups(self):
        return requests.get(SERVER_HOST + '/groups')

    @published
    @protoapi(ResponseProtoBuf.Group)
    def createGroup(self, groupname):
        return requests.post(SERVER_HOST + '/groups/' + groupname)

    @published
    def addUserToGroup(self, groupname, username):
        return requests.put(SERVER_HOST + '/groups/' + groupname + '/users/' + username)

    @published
    @protoapi(ResponseProtoBuf.Message)
    def sendDirectMessage(self, from_name, to_name, *args):
        message = RequestProtoBuf.Message()
        message.frm = from_name
        message.msg = (' ').join(args)

        return requests.post(SERVER_HOST + '/users/' + to_name + '/messages', data=message.SerializeToString())


    @published
    @protoapi(ResponseProtoBuf.Message)
    def sendGroupMessage(self, from_name, to_name, *args):
        message = RequestProtoBuf.Message()
        message.frm = from_name
        message.msg = (' ').join(args)

        return requests.post(SERVER_HOST + '/groups/' + to_name + '/messages', data=message.SerializeToString())

    @published
    @protoapi(ResponseProtoBuf.MessageList)
    def listMessages(self, username):
        return requests.get(SERVER_HOST + '/users/' + username + '/messages')

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
