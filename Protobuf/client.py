import cmd
import requests

SERVER_HOST = '127.0.0.1'

def do_createUser(self, username):
    r = requests.get(SERVER_HOST + '/users/' + username)
    print r

def published(method):
    method.published = True
    return method

class Client(object):
    def __init__(self):
        self.current_user = None
        self.current_room = None

    @published
    def adduser(self, uname):
        pass

    def send(self):
        pass

if __name__ == "__main__":
    client = Client()

    while True:
        prompt = "[" + str(current_user) + "," + str(current_room) + "]: "
        command = raw_input(prompt)

        # not a slash command
        if command.get(0) != "/":
            client.send(command)

        # is a slash command
        action = command.split(' ')
        method = client.getattr(action[0][1:], None)
        if method and method.published:
            method(*action[1:])
        else:
            print "<Action Unknown>"
