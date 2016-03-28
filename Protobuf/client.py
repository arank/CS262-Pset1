import cmd
import requests
import time
from build.protobufs import request_pb2 as RequestProtoBuf
from build.protobufs import response_pb2 as ResponseProtoBuf
from functools import wraps

#
# This file is the main client for our chat application. It exposes a command
# line interface and makes calls to the API (located at SERVER_HOST).
#

SERVER_HOST = 'http://127.0.0.1:5000/v1'

# This is a wrapper to "publish" methods on the Client object. Publishing a
# method will make it callable from the command line.
def published(method):
    method.published = True
    return method

# Typically the return value from a method in the Client object called from the
# command line (via a slash command) is printed directly to the command line.
#
# This wrapper calls the wrapped function, and interprets the response as a
# requests' library Response object (parsing the content as a protobuf) and
# prints a string representation of the content encoded in the response.
#
# Specifically this is useful when returning responses from our API, which will
# include protobufs in the body. This function will take the response, and if it
# had a status of 200 (HTTP OK) it will parse the response body with a protobuf
# of "expectedType" (which is passed as an argument). In the case the response
# has a status of 400 (HTTP BAD REQUEST), the content body is decoded with
# UserError. Once the protobuf object is parsed, we create a string
# representation of it and print it.
#
# NOTE: If the wrapped function returns None, this simply returns None and
#       doesn't attempt to parse. This allows wrapped functions to print an
#       error message in the case of error and then just return None (so nothing
#       additional is printed).

def protoapi(expectedType):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            response = f(*args, **kwargs)

            # There was a client error, and the request was never made, simply
            # return the error to the user.
            if response is None:
                return

            # Print the response object for the user to see (nice-to-have for
            # technical users, allows them to see things like response code)
            print response

            # if the response was okay (200), parse the content as expectedType
            if response.status_code == 200:
                obj = expectedType()
                obj.ParseFromString(response.content)
                print str(obj)

            # if the response was a bad request (400), parse as UserError
            elif response.status_code == 400:
                ue = ResponseProtoBuf.UserError()
                ue.ParseFromString(response.content)
                print str(ue)

        return wrapped
    return decorator

# The Client object, outlined below, is effectively exposed to the command line
# interface. When the user types in a slash command to the command line, such as
# "/METHODNAME ARG1 ARG2", we lookup METHODNAME on the Client object, and if it
# has published (Client.methodname.published == True) then we call that method
# with the provided arguments.
#
# This allows us to write an extendable interface, where adding one more command
# is a matter of adding a method to the Client object.
#
# NOTE: Not typing in a slash command (e.g. just typing "FOO BAR") will prepend
#       your command with "/send" (e.g. "FOO BAR" becomes "/send FOO BAR")

class Client(object):
    def __init__(self):
        # This is the current state for the clients. Allows you to send messages
        # to users and groups without having to specify who.

        # The user that is sending messages by default
        self.current_user = None

        # The entity name receiving messages, and whether that entity is a group
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
    def setuser(self, user):
        """Usage: /setuser <username> : Set current user to user"""
        self.current_user = user

    @published
    def login(self):
        """Usage: /login : Login to current user name"""
        if self.current_user is None:
            print "<Current user name not set>"
            return None

        # Poll the server for messages until user interrupt
        while True:
            try:
                # request server messages
                r = requests.get(SERVER_HOST + '/users/' + self.current_user + '/messages')

                # if the server returned Okay, print the list of messages if
                # there are any
                if r.status_code == 200:
                    obj = ResponseProtoBuf.MessageList()
                    obj.ParseFromString(r.content)
                    if len(obj.messages) > 0:
                        print str(obj)

                # should the server return an error, print the error to the user
                # and stop polling the server
                elif r.status_code == 400:
                    ue = ResponseProtoBuf.UserError()
                    ue.ParseFromString(r.content)
                    print str(ue)
                    break

                # Only poll the server every second, anything more is excessive
                time.sleep(1)

            except KeyboardInterrupt:
                # in the case of user interrupt (i.e. ctrl-c) then stop polling
                # for messages and return to prompt
                break

    @published
    def clearuser(self):
        """Usage: /clearuser : Set current user to None"""
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

#
# This is the actual code that constructs a Client object, takes user input and
# calls methods on the client objects
#

if __name__ == "__main__":
    client = Client()

    # take user input until the end of time (or at least until this program
    # stops)
    while True:
        # get user input, displaying their username as a prompt
        prompt = "[" + str(client.current_user if client.current_user is not None else "*not logged in*") + "]: "
        command = raw_input(prompt)

        # skip empty commands
        if command == "":
            continue

        if command[0] != "/":
            # If it's not a slash command, just directly call send with the cmd
            client.send(command)
        else:
            # is a slash command
            action = command.split(' ')
            method = getattr(client, action[0][1:], None)
            # check if it's a valid method
            if method and method.published:
                try:
                    method(*action[1:])
                except TypeError:
                    # see if they called function correctly (i.e. correct number
                    # of args)
                    print "<Invalid usage>"
            else:
                print "<Action Unknown>"
