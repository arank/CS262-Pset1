# ********************************************
# TODO : What do we do if a user sends a message, then deletes themself?
#        (the unreceived message has a ref to a deleted user)
# ********************************************

from flask import Flask
import chat
from build import chat_pb2

app = Flask(__name__)

USERS = {}
GROUPS = {}

class APIError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


#
# Users
#

@app.get("/users")
def listUsers():
    return USERS.keys()

@app.post("/users/:username")
def createUser(username):
    if name in USERS:
        raise APIError("User Exists")
    newUser = User(name)
    USERS[name] = newUser
    return newUser

@app.delete("/users/:username")
def deleteUser(username):
    user = USERS.pop(username, None)

    if user is None:
        raise APIError("Missing User")

    user.cleanupGroups()

#
# Groups
#

@app.get("/groups")
def listGroups():
    return GROUPS.keys()

@app.post("/groups/:groupname")
def createGroup(groupname):
    if groupname in GROUPS:
        return APIError("Group Exists")

    members = [USERS.get(memberName, None) for memberName in memberNames]
    if None in members:
        raise APIError("Member does not exist")

    newGroup = Group(groupname, memberNames)
    GROUPS[groupname] = newGroup
    return newGroup

@app.put("/groups/:groupname/users/:username")
def addUserToGroup(groupname, username):
    # TODO
    pass

#
# Messages
#

@app.post("/users/:username/messages")
def sendDirectMessage(username):
    toUser = USERS.get(toname, None)
    if toUser is None:
        raise APIError("Missing To User")

    fromUser = USERS.get(fromname, None)
    if fromUser is None:
        raise APIError("Missing From User")

    newMessage = Message(toUser, fromUser, message)
    fromUser.receiveMessage(newMessage)

@app.post("/groups/:groupname/messages")
def sendGroupMessage(groupname):
    toGroup = GROUPS.get(toname, None)
    if toUser is None:
        raise APIError("Missing To Group")

    fromUser = USERS.get(fromname, None)
    if fromUser is None:
        raise APIError("Missing From User")

    newMessage = Message(toGroup, fromUser, message)
    toGroup.receiveMessage(newMessage)

@app.get("/users/:username/messages")
def listMessages(username):
    if name not in USERS:
        raise APIError("Missing User")
    return USERS.get(username).receiveMessage()

if __name__ == "__main__":
    app.run()
