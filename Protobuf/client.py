import cmd
import requests
from build.protobufs import request_pb2 as RequestProtoBuf
from build.protobufs import response_pb2 as ResponseProtoBuf
from functools import wraps

SERVER_HOST = 'http://127.0.0.1:5000/v1'

def published(method):
    method.published = True
    return method

def protoapi(expectedType):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            response = f(*args, **kwargs)

            # way for in handler error checking
            if response is None:
                return

            # print the response and contents
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
        self.current_user = None
        self.current_to = None
        self.current_to_is_group = False

    @published
    def mvg(self, group):
        """Usage: /mvg <group> : Set current recipient to group"""
        self.current_to = group
        self.current_to_is_group = True

    @published
    def mvu(self, user):
        """Usage: /mvg <user> : Set current recipient to user"""
        self.current_to = user
        self.current_to_is_group = False

    @published
    def mvo(self):
        """Usage: /mvo : Unset current recipient"""
        self.current_to = None

    @published
    def send(self, *args):
        """Usage: /send <message> : Send a message from the logged in user to the current recipient"""
        if self.current_to is None:
            print "<Not Sending To Anyone>"
            return None

        if self.current_to_is_group:
            self.gm(self.current_to, args)
        else:
            self.dm(self.current_to, args)

    @published
    def login(self, user):
        """Usage: /login <username> : Login"""
        self.current_user = user

    @published
    def logout(self):
        """Usage: /logout : Logout"""
        if self.current_user is None:
            print "<Not Logged In>"
            return None
        self.current_user = None

    @published
    @protoapi(ResponseProtoBuf.UserList)
    def listusers(self, *args):
        """Usage: /listusers <filter default=*> : List users"""
        query = {}
        if len(args) > 0:
            query['q'] = args[0]

        return requests.get(SERVER_HOST + '/users', params=query)

    @published
    @protoapi(ResponseProtoBuf.User)
    def adduser(self, username):
        """Usage: /adduser <username> : create user"""
        return requests.post(SERVER_HOST + '/users/' + username)

    @published
    def leaveforever(self):
        """"Usage: /leaveforever : delete the current logged in user"""
        if self.current_user is None:
            print "<Not Logged In>"
            return None
        return requests.delete(SERVER_HOST + '/users/' + self.current_user)

    @published
    @protoapi(ResponseProtoBuf.GroupList)
    def listgroups(self, *args):
        """Usage: /listgroups <filter default=*> : list all the groups"""
        query = {}
        if len(args) > 0:
            query['q'] = args[0]

        return requests.get(SERVER_HOST + '/groups', params=query)

    @published
    @protoapi(ResponseProtoBuf.Group)
    def group(self, groupname):
        """Usage: /group <groupname> : create group"""
        return requests.post(SERVER_HOST + '/groups/' + groupname)

    @published
    @protoapi(ResponseProtoBuf.Group)
    def invite(self, groupname, username):
        """Usage: /invite <groupname> <username> : add user to group"""
        return requests.put(SERVER_HOST + '/groups/' + groupname + '/users/' + username)

    @published
    @protoapi(ResponseProtoBuf.Message)
    def dm(self, to_name, *args):
        """Usage: /dm <username> <message> : send a message to user"""
        if self.current_user is None:
            print "<Not Logged In>"
            return None
        message = RequestProtoBuf.Message()
        message.frm = self.current_user
        message.msg = (' ').join(args)

        return requests.post(SERVER_HOST + '/users/' + to_name + '/messages', data=message.SerializeToString())


    @published
    @protoapi(ResponseProtoBuf.Message)
    def gm(self, to_name, *args):
        """Usage: /gm <groupname> <message> : send a message to group"""
        if self.current_user is None:
            print "<Not Logged In>"
            return None
        message = RequestProtoBuf.Message()
        message.frm = self.current_user
        message.msg = (' ').join(args)

        return requests.post(SERVER_HOST + '/groups/' + to_name + '/messages', data=message.SerializeToString())

    @published
    @protoapi(ResponseProtoBuf.MessageList)
    def get(self):
        """Usage: /get : get unread messages"""
        if self.current_user is None:
            print "<Not Logged In>"
            return None
        return requests.get(SERVER_HOST + '/users/' + self.current_user + '/messages')

    @published
    def help(self, function):
        """usage: /help [method] : get description of functions"""
        method = getattr(client, function, None)
        if method and method.published:
            print method.__doc__
        else:
            print "<Action Unknown>"

    @published
    def exit(self):
        """usage: /exit : close the client"""
        exit()

if __name__ == "__main__":
    client = Client()

    while True:
        prompt = "[" + str(client.current_user if client.current_user is not None else "*not logged in*") + "]: "
        command = raw_input(prompt)

        if command == "":
            continue

        # not a slash command
        if command[0] != "/":
            client.send(command)

        # is a slash command
        action = command.split(' ')
        method = getattr(client, action[0][1:], None)
        if method and method.published:
            method(*action[1:])
        else:
            print "<Action Unknown>"
