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
# method will make it callable from the command line (see below).
def published(method):
    method.published = True
    return method

#
# This wrapper calls the wrapped function, and interprets the response as a
# requests' library Response object (parsing the content as a protobuf) and
# prints a string representation of the content encoded in the response.
#
# It is syntatic sugar so that wrapped functions may simply return what they
# want printed. This is used extensively in the client object.
#
# This is especially useful when returning responses from our API, which will
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

            # There was a client error, and the request was never made.
            # Don't print anything and return.
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
# NOTE: Not typing in a slash command (e.g. just typing "FOO BAR") will effectively prepend
#       your command with "/send" (e.g. "FOO BAR" becomes "/send FOO BAR")

class Client(object):
    def __init__(self):
        # This is the current state for the clients. Allows user to send messages
        # to other users and groups without having to specify who every time.

        # The user that is sending messages by default
        self.current_user = None

        # The entity name receiving messages, and whether that entity is a group
        self.current_to = None
        self.current_to_is_group = False

    @published
    def mvg(self, group):
        """
        Set current recipient to group
        Usage: /mvg <group>
        """
        self.current_to = group
        self.current_to_is_group = True

    @published
    def mvu(self, user):
        """
        Set current recipient to user
        Usage: /mvg <user>
        """
        self.current_to = user
        self.current_to_is_group = False

    @published
    def mvo(self):
        """
        Unset current recipient
        Usage: /mvo
        """
        self.current_to = None

    @published
    def send(self, *args):
        """
        Send a message from the logged in user to the current recipient
        Usage: /send <message>
        """

        # make sure there is a current user to send to
        if self.current_to is None:
            print "<Not Sending To Anyone>"
            return None

        if self.current_to_is_group:
            self.gm(self.current_to, args)
        else:
            self.dm(self.current_to, args)

    @published
    def setuser(self, user):
        """
        Set current user to user
        Usage: /setuser <username>
        """
        self.current_user = user

    @published
    def login(self):
        """
        Login to current user name (and poll for messages)
        Usage: /login
        """
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
        """
        Set current user to None
        Usage: /clearuser
        """
        if self.current_user is None:
            print "<Not Logged In>"
            return None
        self.current_user = None

    @published
    @protoapi(ResponseProtoBuf.UserList)
    def listusers(self, *args):
        """
        List users
        Usage: /listusers <filter default=*>
        """
        query = {}
        if len(args) > 0:
            query['q'] = args[0]

        return requests.get(SERVER_HOST + '/users', params=query)

    @published
    @protoapi(ResponseProtoBuf.User)
    def adduser(self, username):
        """
        Create user
        Usage: /adduser <username>
        """
        return requests.post(SERVER_HOST + '/users/' + username)

    @published
    def leaveforever(self):
        """"
        Delete the current logged in user
        Usage: /leaveforever
        """
        if self.current_user is None:
            print "<Not Logged In>"
            return None
        return requests.delete(SERVER_HOST + '/users/' + self.current_user)

    @published
    @protoapi(ResponseProtoBuf.GroupList)
    def listgroups(self, *args):
        """
        List all the groups
        Usage: /listgroups <filter default=*>
        """
        query = {}
        if len(args) > 0:
            query['q'] = args[0]

        return requests.get(SERVER_HOST + '/groups', params=query)

    @published
    @protoapi(ResponseProtoBuf.Group)
    def group(self, groupname):
        """
        Create a group
        Usage: /group <groupname>
        """
        return requests.post(SERVER_HOST + '/groups/' + groupname)

    @published
    @protoapi(ResponseProtoBuf.Group)
    def invite(self, groupname, username):
        """
        Add user to group
        Usage: /invite <groupname> <username>
        """
        return requests.put(SERVER_HOST + '/groups/' + groupname + '/users/' + username)

    @published
    @protoapi(ResponseProtoBuf.Message)
    def dm(self, to_name, *args):
        """
        Send a message to user
        Usage: /dm <username> <message>
        """
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
        """
        Send a message to group
        Usage: /gm <groupname> <message>
        """
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
        """
        Get unread messages
        Usage: /get
        """
        if self.current_user is None:
            print "<Not Logged In>"
            return None
        return requests.get(SERVER_HOST + '/users/' + self.current_user + '/messages')

    @published
    def help(self, function):
        """
        Get description of functions
        Usage: /help [method]
        """
        method = getattr(client, function, None)
        if method and method.published:
            print method.__doc__
        else:
            print "<Action Unknown>"

    @published
    def exit(self):
        """
        Close the client
        Usage: /exit
        """
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
            # is a slash command, figure out which command
            action = command.split(' ')
            method = getattr(client, action[0][1:], None)
            # check if it's a valid method
            if method and method.published:
                try:
                    method(*action[1:])
                except TypeError:
                    # catch if they called function correctly (i.e. correct number
                    # of args)
                    print "<Invalid usage>"
            else:
                print "<Action Unknown>"
